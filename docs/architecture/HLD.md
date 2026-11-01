# KnowDoc — High-Level Design (HLD)

## 1. System Overview
**KnowDoc** is a production-oriented AI Document Intelligence Platform built on a decoupled, micro-service-inspired polyglot architecture. It separates client-facing web application concerns (routing, session orchestration, tenancy, metadata storage, file validation) from computational AI concerns (PDF parsing, text chunking, embedding generation, vector similarity search, and LLM inference).

---

## 2. System Architecture & Boundaries

```
[ Client Browser / Single Page App ]
               │
               ▼ HTTPS (REST / SSE)
   ┌────────────────────────────────────────────────────────┐
   │                  Express API Gateway                   │
   │   (Auth, Metadata, Queue Orchestration, File Ingress)  │
   └───┬───────────────────┬────────────────────┬───────────┘
       │                   │                    │
       ▼                   ▼                    ▼
┌──────────────┐   ┌───────────────┐   ┌────────────────────┐
│   MongoDB    │   │ Local/S3 Disk │   │   Redis / BullMQ   │
│ (App State)  │   │ (Raw Binaries)│   │ (Ingestion Queue)  │
└──────────────┘   └───────────────┘   └─────────┬──────────┘
                                                 │
                                                 ▼
                                       ┌────────────────────┐
                                       │   BullMQ Worker    │
                                       └─────────┬──────────┘
                                                 │ HTTP (Internal Key)
                                                 ▼
                                       ┌────────────────────┐
                                       │ FastAPI AI Service │
                                       └───┬────────────┬───┘
                                           │            │
                                           ▼            ▼
                                 ┌───────────────┐ ┌──────────────┐
                                 │  PostgreSQL   │ │ External LLM │
                                 │  (pgvector)   │ │  (OpenAI/etc)│
                                 └───────────────┘ └──────────────┘
```

### 2.1 Component Breakdown

1. **Frontend (React + Vite + Tailwind CSS)**:
   - Client Single-Page Application (SPA) communicating strictly with the Express API Gateway.
   - Built with modern JavaScript ES modules (no TypeScript).
   - Features modular layout: Document Manager, Upload Drawer, Real-time Ingestion Tracker, and Split-screen Conversational Chat with Citations.
2. **Application Gateway & Backend (Node.js + Express)**:
   - Owns authentication, authorization, session management, user profile data, document metadata, and chat history.
   - Validates uploads (magic bytes, MIME type, size limit) and persists raw binaries via the storage abstraction.
   - Enqueues ingestion jobs into BullMQ and polls/receives progress events.
   - Dispatches authenticated question-answering requests to the internal FastAPI service.
   - Written in standard ES modules (`import`/`export`) without TypeScript.
3. **AI & RAG Service (Python + FastAPI)**:
   - Owns document parsing, page-aware chunking, vector embedding generation, vector similarity search, prompt construction, and LLM generation.
   - Exposes versioned internal endpoints protected by `X-Internal-Service-Key`.
   - Directly interfaces with PostgreSQL (`pgvector`) for vector storage and cosine distance similarity queries.
   - Abstracts embedding and generation providers (OpenAI, HuggingFace, Anthropic, Ollama).
4. **Primary Application Database (MongoDB)**:
   - Stores users, organizational metadata, document records (status, storage key, file hash, page count), conversations, and messages.
5. **Vector Database (PostgreSQL + pgvector)**:
   - Dedicated vector repository storing chunk text, token counts, physical page numbers, and vector embeddings (`vector(1536)`).
   - Enforces user-level partition filtering to eliminate cross-tenant leakage.
6. **Task Broker & Cache (Redis & BullMQ)**:
   - Manages asynchronous ingestion job queues (`knowdoc:queue:ingestion`), job retries, exponential backoffs, and rate-limiting counters.
7. **Storage Provider**:
   - Stores immutable raw PDF binaries via a clean interface (`IStorageProvider`), supporting local directory storage for development and S3-compatible cloud storage for production.

---

## 3. End-to-End Information Flows

### 3.1 Document Ingestion Flow (Asynchronous)
1. **Upload Request**: Client sends a `multipart/form-data` request containing the PDF binary and JWT bearer token to `POST /api/v1/documents`.
2. **Signature & Size Verification**: Express verifies user authorization, checks file size (≤ 25 MB), and confirms magic bytes (`%PDF`).
3. **Binary Storage**: Raw binary is saved via `IStorageProvider` under a collision-resistant key (`uploads/documents/<userId>/<uuid>.pdf`).
4. **Metadata Initialization**: A document entity is written to MongoDB with status `pending`.
5. **Enqueue Job**: A job containing `{ documentId, storageKey, userId, mimeType }` is pushed to BullMQ. Express immediately returns HTTP 202 Accepted.
6. **Worker Processing**: A BullMQ worker consumes the job, changes MongoDB status to `processing`, and calls FastAPI internal endpoint `POST /internal/v1/rag/index`.
7. **Extraction & Chunking**: FastAPI reads the binary, extracts text page-by-page, and chunks it into overlapping token windows while preserving page markers.
8. **Embeddings Generation**: Chunks are batched and embedded via the configured embedding adapter.
9. **Vector Persistence**: Chunks and embeddings are stored in PostgreSQL with indexed `user_id` and `document_id`.
10. **State Completion**: FastAPI returns success; the worker updates MongoDB status to `ready` with page and chunk counts.

### 3.2 Question-Answering Flow (Synchronous / Streaming)
1. **Query Request**: Client sends a question targeting one or more documents to `POST /api/v1/conversations/:id/messages`.
2. **Ownership Check**: Express verifies user access to the conversation and all referenced `documentIds`.
3. **Internal AI Request**: Express forwards the query and document scope to FastAPI `POST /internal/v1/rag/query` with internal authorization headers.
4. **Query Embedding**: FastAPI computes the vector representation of the query.
5. **pgvector Retrieval**: Cosine similarity search (`<=>`) retrieves top-k chunks strictly constrained to `user_id` and the authorized `document_id` list.
6. **Grounding & Prompt Injection Defense**: FastAPI constructs a system prompt enclosing retrieved chunks within strict XML-like delimiters, instructing the LLM to treat document text as untrusted reference data and cite page numbers.
7. **LLM Generation**: The LLM synthesizes an answer referencing the passages.
8. **Citation Extraction**: Citations are structured into objects containing `documentId`, `pageNumber`, and `excerpt`.
9. **Storage & Response**: Express saves the user message and assistant reply with citations to MongoDB, returning the response to the client.

---

## 4. Cross-Cutting Concerns

### 4.1 Tenancy & Data Isolation
- Application-level tenancy is enforced at the Express API layer via JWT claims.
- Vector-level tenancy is enforced at the PostgreSQL layer where all chunk queries MUST contain `WHERE user_id = $1`.
- Raw file storage paths are partitioned by `user_id`.

### 4.2 Security Boundaries
- **External Network**: Only the Express API and Frontend are exposed to external clients via HTTPS.
- **Internal Network**: FastAPI, MongoDB, PostgreSQL, and Redis reside within an isolated internal Docker/VPC network.
- **Service-to-Service Auth**: Express authenticates to FastAPI using a shared high-entropy secret (`X-Internal-Service-Key`).

### 4.3 Error Handling & Resilience
- **Exponential Backoff**: BullMQ retries failed ingestion jobs up to 3 times before moving them to a Dead Letter Queue (DLQ) and setting document status to `failed`.
- **Atomic Rollback on Deletion**: When a user deletes a document, deletion triggers a cascade across MongoDB, PostgreSQL chunks, and storage binaries.
- **Graceful Shutdown**: On `SIGTERM` or `SIGINT`, servers stop accepting new connections, wait for in-flight requests to complete, close database pools, and cleanly disconnect Redis.

