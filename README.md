# Clinical Trial Hybrid RAG API

Flask reference service that routes questions to validated MySQL queries (`STRUCTURED`), Elasticsearch retrieval (`RAG`), or both. The LLM can only propose an allowlisted `StructuredQueryPlan`; it never supplies SQL. Pydantic and `PlanValidator` reject unknown fields, invalid operation/entity pairs, unsupported enums, and excessive limits before SQLAlchemy builds parameterized queries.

MySQL is an external, read-only system of record maintained by another application. This project does not create tables, run migrations, or write relational data. Structured questions always query MySQL directly, so counts and statuses reflect current source data. Elasticsearch is a derived, eventually consistent index used for semantic retrieval.

## Run

```powershell
Copy-Item .env.example .env
# Set MYSQL_URL in .env to the existing database using a SELECT-only account.
docker compose up -d elasticsearch
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py
```

`GEMINI_API_KEY` is required for vector ingestion and RAG queries. Gemini produces schema-constrained query plans and `gemini-embedding-001` generates document and query vectors. The deterministic structured parser can still serve supported MySQL-only questions without Gemini.

## Third-party vector ingestion service

The ingestion job does not read MySQL. It consumes a third-party HTTP API, generates Gemini embeddings, and publishes the text, vector, and metadata into Elasticsearch. Deterministic IDs make re-runs safe. A successful full run removes stale documents belonging to the same provider; cleanup is skipped if a bulk operation fails.

Expected provider response:

```json
{
  "items": [
    {"id": "doc-123", "text": "Clinical trial guidance...", "metadata": {"study_id": "ABC"}}
  ],
  "next_cursor": "optional-next-page-token"
}
```

The client sends `limit` and optional `cursor` query parameters and supports a bearer token through `THIRD_PARTY_API_KEY`. Adapt `ThirdPartyClient` when the real provider uses a different contract.

Run locally:

```powershell
.venv\Scripts\python ingest.py --batch-size 100
```

Or run the one-shot Docker service:

```powershell
docker compose --profile ingestion run --rm ingestion
```

Set `THIRD_PARTY_URL`, `THIRD_PARTY_SOURCE`, and `GEMINI_API_KEY` in `.env`. Vector ingestion rejects runs without a Gemini key. If the Elasticsearch index was previously created with a different embedding dimension, create a new index name or reindex it before switching dimensions.

Use a MySQL account with only `SELECT` privileges for live structured questions. The application additionally sets each MySQL session to `TRANSACTION READ ONLY` as defense in depth. MySQL is not part of the Elasticsearch ingestion flow. The SQL file under `sql/` is reference documentation only.

## API examples

```bash
curl -X POST http://localhost:5000/api/v1/query -H "Content-Type: application/json" -d '{"question":"How many participants were recruited in Germany for Study ABC this quarter?"}'
curl -X POST http://localhost:5000/api/v1/documents -H "Content-Type: application/json" -d '{"id":"protocol-abc-1","text":"Study ABC recruitment guidance...","metadata":{"study_id":"ABC","type":"protocol"}}'
```

Run `pytest -q` for unit tests. Production deployments should add authentication and row-level study access, PHI redaction, audit logging, TLS/API-key security for Elasticsearch, request timeouts/retries, migrations, and answer synthesis constrained to returned source IDs.
