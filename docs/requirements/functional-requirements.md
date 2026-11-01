# KnowDoc — Functional Requirements Specification

## 1. Document Overview
This document defines the functional capabilities for **KnowDoc**, an enterprise-grade AI Document Intelligence Platform. KnowDoc enables users to securely upload, index, query, analyze, and cite information from complex PDF documents using a Retrieval-Augmented Generation (RAG) architecture.

---

## 2. User & Tenant Roles
1. **Registered User (Tenant)**:
   - Self-registers or gets provisioned by an administrator.
   - Uploads, manages, and deletes their own documents.
   - Creates conversational threads, questions documents, and reviews citations.
   - Has strict private tenancy: users can never access or query other users' documents.
2. **System Administrator (Future Scope)**:
   - Manages tenant quotas, oversees system health, views audit logs, and monitors queue metrics.

---

## 3. Core Functional Modules

### 3.1 Authentication & Session Management
- **FR-AUTH-01**: User registration with email, full name, and password.
- **FR-AUTH-02**: Passwords hashed using `bcrypt` (work factor 12) before storage.
- **FR-AUTH-03**: Secure login issuing short-lived JSON Web Tokens (Access Token: 15-minute TTL) and secure HTTP-only refresh tokens (7-day TTL).
- **FR-AUTH-04**: Token validation on all protected endpoints with explicit 401 Unauthorized handling.
- **FR-AUTH-05**: Logout mechanism invalidating refresh tokens in Redis.

### 3.2 Document Upload & Validation
- **FR-DOC-01**: Support single and multi-file PDF uploads up to 25 MB per document.
- **FR-DOC-02**: Binary signature verification (Magic Bytes `%PDF` / `0x25 0x50 0x44 0x46`) prior to storage to prevent MIME spoofing.
- **FR-DOC-03**: File storage abstraction saving raw binaries to local disk (Phase 1) with an interface compatible with S3/GCS blob stores (Phase 2).
- **FR-DOC-04**: Generation of deterministic content hash (SHA-256) to detect duplicates within a tenant's workspace.
- **FR-DOC-05**: Immediate generation of document metadata record in MongoDB with initial status `pending`.

### 3.3 Asynchronous Ingestion & Document Processing
- **FR-INGEST-01**: Ingestion jobs dispatched to a Redis-backed BullMQ queue without blocking HTTP client threads.
- **FR-INGEST-02**: Multi-phase document lifecycle tracking:
  - `pending` -> `processing` -> `chunked` -> `embedding` -> `ready` (or `failed`).
- **FR-INGEST-03**: Text extraction preserving physical page numbers and structural metadata.
- **FR-INGEST-04**: Recursive chunking with configurable chunk size (default: 800 tokens / ~3200 characters) and overlap (default: 150 tokens / ~600 characters).
- **FR-INGEST-05**: Vector embedding generation via swappable provider interface (OpenAI `text-embedding-3-small`, local Sentence-Transformers, or mock embeddings).
- **FR-INGEST-06**: Vector persistence into PostgreSQL with `pgvector` index along with chunk text, page number, document ID, and tenant ID.
- **FR-INGEST-07**: Retry policy (exponential backoff, max 3 attempts) for transient failures, updating document status to `failed` with error reason if retries are exhausted.
- **FR-INGEST-08**: Scanned PDF detection: if a PDF yields fewer than 50 text characters across multiple pages, mark with `scanned_detected: true` and defer to the Phase 2 OCR pipeline.

### 3.4 Conversational Retrieval-Augmented Generation (RAG)
- **FR-RAG-01**: Conversational threads bound to one or more user-selected documents.
- **FR-RAG-02**: Multi-turn dialogue support maintaining contextual conversation history.
- **FR-RAG-03**: Query embedding generation matching the dimension of stored document vectors.
- **FR-RAG-04**: Cosine distance similarity search in `pgvector` scoped strictly to `user_id` and selected `document_id`(s).
- **FR-RAG-05**: Prompt synthesis enforcing strict grounding:
  - Untrusted context boundary delimiters (`<document_context>` ... `</document_context>`).
  - Explicit instruction to admit ignorance ("I do not have sufficient information in the provided document(s) to answer this question.") when evidence is missing.
- **FR-RAG-06**: LLM completion generation via swappable provider interface (OpenAI GPT-4o-mini / Anthropic Claude / Ollama).
- **FR-RAG-07**: Structured citation generation returning:
  - Source `documentId` and `documentName`.
  - Specific `pageNumber` where the supporting claim resides.
  - Verbatim supporting `excerpt` (up to 250 characters).
- **FR-RAG-08**: Conversation and message persistence in MongoDB including user query, assistant response, token usage, and citation payloads.

### 3.5 Document & Workspace Management
- **FR-MGMT-01**: Paginated list of documents with metadata (name, size, page count, status, created date, error details).
- **FR-MGMT-02**: Document deletion with cross-datastore cascade:
  - Remove file binary from storage provider.
  - Remove document record and metadata from MongoDB.
  - Delete all associated chunk vectors from PostgreSQL `pgvector`.
  - Prune references from active conversation records.
- **FR-MGMT-03**: Real-time or polling-based ingestion status checks for client responsiveness.

### 3.6 Document Summarization & Insights
- **FR-SUMM-01**: On-demand single document executive summary generation upon reaching `ready` status.
- **FR-SUMM-02**: Automatic extraction of key topics, key entities, and table-of-contents overview.

---

## 4. Future Research Capabilities (Phase 2 & Phase 3)
- **FR-FUT-01 (OCR Pipeline)**: Tesseract / AWS Textract integration for scanned non-digital PDFs.
- **FR-FUT-02 (Reranking Engine)**: Cross-encoder (Cohere Rerank / BGE-Reranker) for precision scoring before prompt injection.
- **FR-FUT-03 (Multi-Document Agentic Synthesis)**: Autonomous multi-step research agent decomposing complex multi-document questions into sub-queries.
- **FR-FUT-04 (Hybrid Web & Document Search)**: Dual-search merging enterprise internal documents with real-time web citations.
- **FR-FUT-05 (Workspace Collaboration)**: Role-based sharing of document libraries and chat transcripts across organizational teams.

