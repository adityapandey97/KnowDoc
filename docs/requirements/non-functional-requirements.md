# KnowDoc — Non-Functional Requirements Specification

## 1. Document Overview
This document specifies the architectural qualities, operational limits, security boundaries, performance criteria, and maintainability expectations for the **KnowDoc** platform.

---

## 2. Performance & Latency Targets
- **NFR-PERF-01 (API Response Time)**: Standard CRUD operations (user auth, document listing, conversation management) must complete within P95 < 150 ms under 100 concurrent requests.
- **NFR-PERF-02 (Vector Retrieval Latency)**: Vector similarity queries against PostgreSQL `pgvector` with HNSW indexing must execute within P95 < 60 ms for collections containing up to 500,000 vectors.
- **NFR-PERF-03 (End-to-End QA Latency)**: Conversational question-answering (retrieval + prompt construction + streaming first token from LLM) must deliver Time-to-First-Token (TTFT) within P95 < 1.8 seconds and full response completion within P95 < 4.5 seconds.
- **NFR-PERF-04 (Ingestion Throughput)**: A typical 50-page digital PDF (~25,000 words) must complete parsing, chunking, embedding generation, and vector persistence in under 30 seconds.
- **NFR-PERF-05 (Asynchronous Isolation)**: Uploading and queuing a document must complete in P99 < 300 ms; heavy parsing and vector generation must never block the main Express event loop or synchronous HTTP workers.

---

## 3. Scalability & Elasticity
- **NFR-SCALE-01 (Stateless API Servers)**: Express backend instances and FastAPI AI service instances must maintain zero sticky session state, enabling horizontal scaling behind a reverse proxy (e.g., NGINX / AWS ALB).
- **NFR-SCALE-02 (Worker Scaling)**: BullMQ ingestion workers must scale horizontally and independently from web servers based on Redis queue depth (`knowdoc:queue:ingestion`).
- **NFR-SCALE-03 (Database Partitioning & Growth)**:
  - Vector chunks table in PostgreSQL must support compound indexing on `(user_id, document_id)` to ensure vector index traversals scale linearly with per-user data volume rather than global platform volume.
  - MongoDB collections must utilize composite indexes on `(userId, createdAt)` to maintain stable pagination times regardless of collection size.

---

## 4. Reliability, Availability & Fault Tolerance
- **NFR-REL-01 (Target Availability)**: 99.9% uptime for core API querying and document retrieval.
- **NFR-REL-02 (Graceful Degradation)**:
  - If the vector database is temporarily degraded, conversational QA must fail gracefully with a structured error message (`SERVICE_UNAVAILABLE`) rather than hanging client connections.
  - If an external LLM provider experiences outages, the system must trigger a configurable retry with exponential backoff and support fallback provider routing.
- **NFR-REL-03 (Idempotent Ingestion)**: Ingestion jobs must be safe to retry. Re-running an ingestion job for an existing `document_id` must purge orphan chunk vectors before writing fresh ones, preventing vector duplication.
- **NFR-REL-04 (Database Connection Resilience)**: Both Express and FastAPI services must implement connection pooling with automatic reconnection backoffs for MongoDB, PostgreSQL, and Redis.

---

## 5. Security & Privacy
- **NFR-SEC-01 (Tenant Isolation)**: Every vector retrieval query, database query, and storage access must explicitly filter on authenticated `userId`. Vector queries lacking `user_id` scope must be rejected at the repository level.
- **NFR-SEC-02 (Input Sanitization & Injection Defense)**:
  - Strict schema validation using Zod (Express) and Pydantic (FastAPI).
  - PDF files checked via magic bytes (`%PDF-1.`) and parsed inside isolated sandboxes to mitigate malicious PDF buffer overflow exploits.
  - RAG prompt construction must use structured delimiters to prevent prompt injection from user inputs or untrusted document content.
- **NFR-SEC-03 (Data-at-Rest & In-Transit Encryption)**:
  - TLS 1.3 enforced for all external ingress and inter-service communication.
  - Storage provider abstraction must support server-side encryption (AES-256).
- **NFR-SEC-04 (Audit Logging & Zero-Leakage)**:
  - Passwords, JWT secrets, authorization tokens, raw document text, and vector embeddings must never appear in application logs.
  - Structured JSON logs must include correlation IDs (`X-Correlation-ID`) across Express, Redis, and FastAPI.

---

## 6. Observability & Maintainability
- **NFR-OBS-01 (Health Check Endpoints)**:
  - Express backend exposes `/api/v1/health` reporting Node process status, MongoDB connectivity, and Redis connectivity.
  - FastAPI service exposes `/internal/v1/health` reporting Python runtime status and PostgreSQL `pgvector` pool availability.
- **NFR-OBS-02 (Structured Logging)**: Winston/Morgan in Express and standard Python logging in FastAPI emit machine-readable JSON format with ISO 8601 timestamps, log level, trace ID, and operational metrics.
- **NFR-OBS-03 (Maintainability & Clean Architecture)**: Strict separation of concerns (Controllers -> Services -> Repositories -> Data Models) with zero cross-layer leakages. No TypeScript as required by project constraints; strict ES modules with linting.

