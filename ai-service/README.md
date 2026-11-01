# KnowDoc AI Intelligence Service (Phase 4)

The KnowDoc AI Service is a high-performance Python FastAPI microservice responsible for document extraction, recursive semantic chunking, dense vector embedding calculation, PostgreSQL `pgvector` similarity search, and grounded conversational AI reasoning.

---

## Key Capabilities

1. **Document Ingestion Pipeline**:
   - Page-preserving text extraction supporting PyMuPDF (`fitz`), `pypdf`, and native stream decoding.
   - Automatic scanned document detection (< 50 text characters).
   - Recursive character and boundary chunking with configurable overlap.
   - Batched embedding generation.
   - Idempotent storage in PostgreSQL `pgvector` with automatic purge on re-indexing.

2. **Grounded RAG Answer Generation**:
   - Zero-hallucination grounding: answers are constrained strictly to retrieved passages.
   - Defense against prompt injection: document text is treated as untrusted reference material inside XML delimiters (`<context_passages>`).
   - Insufficient evidence admission: strictly returns `"I do not have sufficient information in the provided document(s) to answer this question."` when evidence is missing.
   - Verifiable page citations matching actually retrieved chunk evidence.

3. **Autonomous Agent Tool Registry**:
   - `search_documents`: Semantic similarity search across authorized user documents.
   - `summarize_document`: Executive summary aggregation over indexed document passages.
   - `retrieve_document_page`: Full chunk retrieval for a specific page of an authorized document.
   - Controlled iteration loops and execution timeouts.

4. **Multi-Tenant Security**:
   - All queries and tool executions require `user_id` parameter binding.
   - Cross-user retrieval is strictly rejected at the repository level.
   - Inter-service communication is authorized via `X-Internal-Service-Key`.

---

## Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Public liveness probe |
| `GET` | `/internal/v1/health` | Authenticated readiness probe |
| `POST` | `/internal/v1/ingest` | Parse, chunk, embed, and index document |
| `POST` | `/internal/v1/chat` | Conversational RAG with optional agent tool calling |
| `POST` | `/internal/v1/retrieval` | Semantic vector similarity search |

---

## Local Development & Testing

```bash
# Navigate to directory
cd ai-service

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run Pytest suite
pytest -v

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

