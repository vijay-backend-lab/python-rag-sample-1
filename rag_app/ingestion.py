import hashlib
import json
import uuid
from collections.abc import Iterator
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from elasticsearch.helpers import streaming_bulk
from .rag import ElasticsearchRAG


class ThirdPartyClient:
    """Adapter for {items: [{id, text, metadata}], next_cursor} APIs."""
    def __init__(self, url: str, api_key: str | None = None, page_size: int = 100, timeout: int = 30):
        self.url, self.api_key, self.page_size, self.timeout = url, api_key, page_size, timeout

    def pages(self) -> Iterator[list[dict]]:
        cursor = None
        while True:
            params = {"limit": self.page_size}
            if cursor: params["cursor"] = cursor
            request = Request(f"{self.url}?{urlencode(params)}", headers={"Accept": "application/json"})
            if self.api_key: request.add_header("Authorization", f"Bearer {self.api_key}")
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.load(response)
            items = payload.get("items", [])
            if not isinstance(items, list): raise ValueError("Third-party response 'items' must be a list")
            yield items
            cursor = payload.get("next_cursor")
            if not cursor: break


class ThirdPartyIngestionService:
    def __init__(self, client: ThirdPartyClient, rag: ElasticsearchRAG, source: str, batch_size: int = 100):
        self.client, self.rag, self.source, self.batch_size = client, rag, source, batch_size

    @classmethod
    def from_settings(cls, settings, batch_size: int = 100):
        if not settings.third_party_url: raise ValueError("THIRD_PARTY_URL is required")
        rag = ElasticsearchRAG(settings.elasticsearch_url, settings.elasticsearch_index,
                               settings.gemini_api_key, settings.embedding_model, settings.embedding_dimensions)
        return cls(ThirdPartyClient(settings.third_party_url, settings.third_party_api_key, batch_size),
                   rag, settings.third_party_source, batch_size)

    def documents(self) -> Iterator[dict]:
        for page in self.client.pages():
            for record in page:
                external_id = str(record.get("id", "")).strip()
                text = str(record.get("text", "")).strip()
                if not external_id or not text: raise ValueError("Every third-party item requires non-empty id and text")
                metadata = record.get("metadata") or {}
                if not isinstance(metadata, dict): raise ValueError(f"metadata for {external_id} must be an object")
                yield {"id": external_id, "text": text, "metadata": metadata}

    def run(self) -> dict:
        self.rag.ensure_index()
        run_id, indexed, failed = str(uuid.uuid4()), 0, []
        def actions():
            for doc in self.documents():
                vector = self.rag.embed(doc["text"])
                if vector is None: raise ValueError("GEMINI_API_KEY is required for vector ingestion")
                source = {"text": doc["text"], "metadata": doc["metadata"], "embedding": vector,
                          "content_hash": hashlib.sha256(doc["text"].encode()).hexdigest(),
                          "ingestion_source": self.source, "ingestion_run_id": run_id}
                yield {"_op_type": "index", "_index": self.rag.index,
                       "_id": f"{self.source}:{doc['id']}", "_source": source}
        for ok, result in streaming_bulk(self.rag.es, actions(), chunk_size=self.batch_size, raise_on_error=False):
            if ok: indexed += 1
            else: failed.append(result)
        deleted = 0
        if not failed:
            cleanup = self.rag.es.delete_by_query(index=self.rag.index, conflicts="proceed", refresh=True,
                query={"bool": {"filter": [{"term": {"ingestion_source": self.source}}],
                                "must_not": [{"term": {"ingestion_run_id": run_id}}]}})
            deleted = cleanup.get("deleted", 0)
        return {"source": self.source, "indexed": indexed, "deleted": deleted,
                "failed": len(failed), "errors": failed[:10]}
