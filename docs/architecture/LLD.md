# KnowDoc — Low-Level Design (LLD)

## 1. Document Purpose
This document provides implementation-level specifications for module interfaces, data structures, state machines, job payloads, and interaction contracts across the **KnowDoc** codebase.

---

## 2. Document Ingestion State Machine & Job Contracts

### 2.1 Document Entity Lifecycle State Machine

```
      ┌─────────────┐
      │   UPLOAD    │
      └──────┬──────┘
             │
             ▼
      ┌─────────────┐
      │   pending   │ ◄── Initial DB record created
      └──────┬──────┘
             │ BullMQ job picked up
             ▼
      ┌─────────────┐
      │ processing  │ ◄── Text extraction & page alignment
      └──────┬──────┘
             │
             ▼
      ┌─────────────┐
      │   chunked   │ ◄── Token/character windowing complete
      └──────┬──────┘
             │
             ▼
      ┌─────────────┐
      │  embedding  │ ◄── Batch vector generation
      └──────┬──────┘
             │
     ┌───────┴───────┐
     ▼               ▼
┌─────────┐    ┌──────────┐
│  ready  │    │  failed  │ ◄── On 3x retry exhaustion
└─────────┘    └──────────┘
```

#### State Definitions:
1. `pending`: File uploaded, stored on disk/S3, metadata recorded in MongoDB, BullMQ job enqueued.
2. `processing`: Worker consumed job, reading binary stream, extracting page-indexed text.
3. `chunked`: Text split into bounded chunks with metadata headers.
4. `embedding`: Vectors being computed through external or local embedding provider.
5. `ready`: Chunks and vectors committed to PostgreSQL with HNSW index; document accessible for RAG.
6. `failed`: Error during processing or embedding; `errorMessage` and `errorStack` recorded; retry count exceeded.

### 2.2 BullMQ Queue Contracts

**Queue Name**: `knowdoc:queue:ingestion`

**Job Name**: `process-document`

**Payload Schema**:
```json
{
  "jobId": "job_9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "documentId": "6543210987abcdef01234567",
  "userId": "6543210987abcdef01234588",
  "storageKey": "uploads/documents/6543210987abcdef01234588/9b1deb4d.pdf",
  "mimeType": "application/pdf",
  "originalFilename": "annual-report-2025.pdf",
  "attemptsMade": 0,
  "enqueuedAt": "2026-11-01T00:00:00.000Z"
}
```

**Worker Configuration**:
- Concurrency: 5 concurrent jobs per worker instance.
- Max Retries: 3 attempts.
- Backoff Strategy: Exponential (`delay: 5000, type: 'exponential'`).
- Lock Duration: 60,000 ms.

---

## 3. Storage Abstraction Layer

All file interactions must go through the storage abstraction interface, preventing filesystem coupling.

### 3.1 Interface Specification (`IStorageProvider`)
```javascript
export class IStorageProvider {
  /**
   * Save a binary buffer to storage
   * @param {string} key - Unique path/key identifier
   * @param {Buffer} buffer - File buffer
   * @param {string} contentType - MIME type
   * @returns {Promise<{ storageKey: string, sizeBytes: number }>}
   */
  async putObject(key, buffer, contentType) {
    throw new Error('Not implemented');
  }

  /**
   * Retrieve binary stream from storage
   * @param {string} key - Unique path/key identifier
   * @returns {Promise<ReadableStream|Buffer>}
   */
  async getObject(key) {
    throw new Error('Not implemented');
  }

  /**
   * Delete object permanently
   * @param {string} key - Unique path/key identifier
   * @returns {Promise<boolean>}
   */
  async deleteObject(key) {
    throw new Error('Not implemented');
  }

  /**
   * Generate an absolute local path or presigned URL
   * @param {string} key - Unique path/key identifier
   * @returns {Promise<string>}
   */
  async getUrl(key) {
    throw new Error('Not implemented');
  }
}
```

### 3.2 Concrete Providers
1. `LocalStorageProvider`: Saves binaries to `data/storage/...` on local disk with directory auto-creation and safe path normalization checking against directory traversal (`..` path attacks).
2. `S3StorageProvider` (Phase 2): Uses `@aws-sdk/client-s3` for AWS S3 or MinIO/Cloudflare R2.

---

## 4. Internal AI Service Contracts (`FastAPI`)

The FastAPI service exposes private endpoints restricted to the internal network and authorized via `X-Internal-Service-Key`.

### 4.1 Indexing Endpoint: `POST /internal/v1/rag/index`

**Request Payload (`IngestRequest`)**:
```json
{
  "document_id": "6543210987abcdef01234567",
  "user_id": "6543210987abcdef01234588",
  "storage_path": "/app/data/storage/uploads/documents/6543210987abcdef01234588/9b1deb4d.pdf",
  "chunk_size": 800,
  "chunk_overlap": 150
}
```

**Response Payload (`IngestResponse`)**:
```json
{
  "document_id": "6543210987abcdef01234567",
  "status": "ready",
  "total_pages": 42,
  "total_chunks": 118,
  "embedding_model": "text-embedding-3-small",
  "embedding_dimension": 1536,
  "processing_duration_ms": 3410
}
```

### 4.2 Query Endpoint: `POST /internal/v1/rag/query`

**Request Payload (`QueryRequest`)**:
```json
{
  "query": "What were the total Q3 revenues and operating margins?",
  "user_id": "6543210987abcdef01234588",
  "document_ids": ["6543210987abcdef01234567"],
  "top_k": 5,
  "similarity_threshold": 0.65,
  "conversation_history": [
    { "role": "user", "content": "Tell me about the 2025 financial report." },
    { "role": "assistant", "content": "The 2025 financial report covers Q1 through Q4 earnings..." }
  ]
}
```

**Response Payload (`QueryResponse`)**:
```json
{
  "answer": "In Q3, total revenues reached $4.2B with an operating margin of 24.5% [Doc: 6543210987abcdef01234567, Page: 14].",
  "citations": [
    {
      "citation_id": "cit_1",
      "document_id": "6543210987abcdef01234567",
      "page_number": 14,
      "chunk_id": "chk_c0a80101-0001",
      "similarity_score": 0.884,
      "excerpt": "Consolidated Q3 revenues increased to $4,200M representing an operating margin of 24.5% driven by SaaS expansion."
    }
  ],
  "prompt_tokens": 1280,
  "completion_tokens": 85,
  "model_used": "gpt-4o-mini"
}
```

---

## 5. RAG Pipeline Components Design

### 5.1 PDF Parser (`app/rag/parsing/parser.py`)
- Reads PDF stream using `pypdf` / `pdfplumber`.
- Extracts text per page:
  ```python
  class ExtractedPage(BaseModel):
      page_number: int
      text: str
      char_count: int
      is_empty_or_scanned: bool
  ```
- Flags documents where total character yield is less than 50 across the entire file (`scanned_detected = True`).

### 5.2 Recursive Text Chunker (`app/rag/chunking/chunker.py`)
- Splits page text while preserving page number references in chunk metadata.
- Splitting hierarchy: `\n\n` (paragraphs) -> `\n` (lines) -> `. ` (sentences) -> ` ` (words).
- Appends chunk sequence number and page ranges:
  ```python
  class TextChunk(BaseModel):
      chunk_index: int
      document_id: str
      user_id: str
      page_number: int
      content: str
      token_estimate: int
  ```

### 5.3 Vector Repository (`app/repositories/vector_repo.py`)
- Interacts with PostgreSQL using async connection pooling.
- SQL for Cosine Distance Search:
  ```sql
  SELECT 
      id, document_id, chunk_index, page_number, content,
      1 - (embedding <=> $1::vector) AS similarity_score
  FROM document_chunks
  WHERE user_id = $2
    AND document_id = ANY($3::varchar[])
    AND 1 - (embedding <=> $1::vector) >= $4
  ORDER BY embedding <=> $1::vector ASC
  LIMIT $5;
  ```

