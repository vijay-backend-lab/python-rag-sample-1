from elasticsearch import Elasticsearch
from google import genai
from google.genai import types
from .models import SearchHit

class ElasticsearchRAG:
    def __init__(self, url, index, api_key, embedding_model, dimensions):
        self.es, self.index = Elasticsearch(url), index
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.embedding_model, self.dimensions = embedding_model, dimensions

    def ensure_index(self):
        if not self.es.indices.exists(index=self.index):
            self.es.indices.create(index=self.index, mappings={"properties": {"text": {"type": "text"}, "metadata": {"type": "object"}, "content_hash": {"type": "keyword"}, "ingestion_source": {"type": "keyword"}, "ingestion_run_id": {"type": "keyword"}, "embedding": {"type": "dense_vector", "dims": self.dimensions, "index": True, "similarity": "cosine"}}})

    def embed(self, text):
        if not self.client: return None
        result = self.client.models.embed_content(model=self.embedding_model, contents=text,
            config=types.EmbedContentConfig(output_dimensionality=self.dimensions))
        return result.embeddings[0].values

    def index_document(self, document):
        self.ensure_index()
        body = {"text": document["text"], "metadata": document.get("metadata", {})}
        vector = self.embed(document["text"])
        if vector is None: raise ValueError("GEMINI_API_KEY is required for vector indexing")
        body["embedding"] = vector
        self.es.index(index=self.index, id=str(document["id"]), document=body, refresh="wait_for")

    def search(self, question, size=5):
        self.ensure_index()
        vector = self.embed(question)
        if vector is None: raise ValueError("GEMINI_API_KEY is required for vector search")
        request = {"knn": {"field": "embedding", "query_vector": vector, "k": size, "num_candidates": 50}, "query": {"match": {"text": question}}}
        hits = self.es.search(index=self.index, size=size, **request)["hits"]["hits"]
        return [SearchHit(id=h["_id"], text=h["_source"]["text"], score=h.get("_score"), metadata=h["_source"].get("metadata", {})).model_dump() for h in hits]
