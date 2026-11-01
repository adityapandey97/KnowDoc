# KnowDoc — API Contracts & Specifications

## 1. Overview & Conventions
This document defines the REST API contracts for:
1. **Public/Client Gateway**: Node.js/Express (`/api/v1/*`)
2. **Private/Internal AI Service**: Python/FastAPI (`/internal/v1/*`)

### 1.1 HTTP Standards
- All request payloads and responses use `application/json`, except file uploads which use `multipart/form-data`.
- Authentication is passed via standard headers:
  - Client -> Express: `Authorization: Bearer <JWT_ACCESS_TOKEN>`
  - Express -> FastAPI: `X-Internal-Service-Key: <SECRET_KEY>` and `X-Correlation-ID: <UUID>`

### 1.2 Standardized Response & Error Envelopes

#### Success Response Envelope (Paginated)
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "totalPages": 3,
    "hasMore": true
  }
}
```

#### Standard Error Envelope
All error responses return a standardized structure:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters provided.",
    "correlationId": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "details": [
      {
        "field": "email",
        "issue": "Must be a valid email address."
      }
    ]
  }
}
```

Standard Error Codes:
- `UNAUTHORIZED` (401): Missing or expired authentication token.
- `FORBIDDEN` (403): User lacks permission to access target resource.
- `NOT_FOUND` (404): Resource does not exist or does not belong to user.
- `VALIDATION_ERROR` (400): Schema or type validation failed.
- `FILE_TOO_LARGE` (413): Upload exceeds maximum size limit (25 MB).
- `INVALID_FILE_TYPE` (415): File is not a valid PDF binary.
- `SERVICE_UNAVAILABLE` (503): Downstream database or LLM provider failure.

---

## 2. Express Backend API Contracts (`/api/v1`)

### 2.1 System Health
#### `GET /api/v1/health`
- **Description**: Verifies API gateway status and connectivity to databases.
- **Auth**: None (Public)
- **Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "knowdoc-backend",
  "version": "1.0.0",
  "timestamp": "2026-11-01T00:00:00.000Z",
  "uptimeSeconds": 1420.5,
  "dependencies": {
    "mongodb": { "status": "connected" },
    "redis": { "status": "connected" }
  }
}
```

---

### 2.2 Authentication & Profile

#### `POST /api/v1/auth/register`
- **Description**: Registers a new user account.
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "Jane Doe"
}
```
- **Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "6543210987abcdef01234588",
      "email": "user@example.com",
      "name": "Jane Doe",
      "createdAt": "2026-11-01T00:00:00.000Z"
    },
    "tokens": {
      "accessToken": "eyJhbGciOiJIUzI1NiIs...",
      "expiresIn": 900
    }
  }
}
```

#### `POST /api/v1/auth/login`
- **Description**: Authenticates user credentials and issues tokens.
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
- **Response (200 OK)**: Same schema as register response; refresh token set via HTTP-only cookie.

---

### 2.3 Document Management

#### `POST /api/v1/documents`
- **Description**: Uploads a PDF document and enqueues ingestion.
- **Auth**: Required (`Bearer <token>`)
- **Headers**: `Content-Type: multipart/form-data`
- **Form Data**:
  - `file`: PDF binary (max 25MB).
- **Response (202 Accepted)**:
```json
{
  "success": true,
  "data": {
    "id": "6543210987abcdef01234567",
    "filename": "quarterly-report.pdf",
    "status": "pending",
    "sizeBytes": 2048500,
    "fileHash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "createdAt": "2026-11-01T00:00:00.000Z"
  }
}
```

#### `GET /api/v1/documents`
- **Description**: Lists authenticated user's documents with pagination and status filters.
- **Auth**: Required (`Bearer <token>`)
- **Query Params**:
  - `page` (optional, default: 1)
  - `limit` (optional, default: 20)
  - `status` (optional: `pending` | `processing` | `ready` | `failed`)
- **Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "6543210987abcdef01234567",
      "filename": "quarterly-report.pdf",
      "status": "ready",
      "sizeBytes": 2048500,
      "pageCount": 38,
      "chunkCount": 112,
      "createdAt": "2026-11-01T00:00:00.000Z",
      "updatedAt": "2026-11-01T00:01:15.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "totalPages": 1,
    "hasMore": false
  }
}
```

#### `GET /api/v1/documents/:id`
- **Description**: Retrieves single document metadata by ID.
- **Auth**: Required (`Bearer <token>`)
- **Response (200 OK)**: Full document metadata entity including processing timestamps.

#### `DELETE /api/v1/documents/:id`
- **Description**: Cascading delete for document (MongoDB metadata, S3/local file, PostgreSQL chunks).
- **Auth**: Required (`Bearer <token>`)
- **Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "id": "6543210987abcdef01234567",
    "deleted": true
  }
}
```

---

### 2.4 Conversations & Question-Answering

#### `POST /api/v1/conversations`
- **Description**: Initializes a new conversation thread bound to one or more documents.
- **Auth**: Required (`Bearer <token>`)
- **Request Body**:
```json
{
  "title": "Quarterly Financial Analysis",
  "documentIds": ["6543210987abcdef01234567"]
}
```
- **Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "id": "6543210987abcdef01234599",
    "title": "Quarterly Financial Analysis",
    "documentIds": ["6543210987abcdef01234567"],
    "createdAt": "2026-11-01T00:00:00.000Z"
  }
}
```

#### `POST /api/v1/conversations/:id/messages`
- **Description**: Asks a question within the conversation thread.
- **Auth**: Required (`Bearer <token>`)
- **Request Body**:
```json
{
  "query": "What were the operating margins for Europe in Q2?"
}
```
- **Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "messageId": "msg_0123456789abcdef",
    "role": "assistant",
    "content": "Operating margins for Europe in Q2 were reported at 18.2% [Doc: 6543210987abcdef01234567, Page: 12].",
    "citations": [
      {
        "documentId": "6543210987abcdef01234567",
        "documentName": "quarterly-report.pdf",
        "pageNumber": 12,
        "excerpt": "Operating margins in the European region showed strong resilience, closing Q2 at 18.2%."
      }
    ],
    "createdAt": "2026-11-01T00:00:05.000Z"
  }
}
```

---

## 3. Internal FastAPI Service Contracts (`/internal/v1`)

### 3.1 AI Service Health
#### `GET /internal/v1/health`
- **Headers**: `X-Internal-Service-Key: <key>`
- **Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "knowdoc-ai-service",
  "version": "1.0.0",
  "dependencies": {
    "pgvector": { "status": "connected" },
    "embedding_provider": { "model": "text-embedding-3-small", "status": "ready" }
  }
}
```

### 3.2 Index Document
#### `POST /internal/v1/rag/index`
- **Headers**: `X-Internal-Service-Key: <key>`
- **Request Body**:
```json
{
  "document_id": "6543210987abcdef01234567",
  "user_id": "6543210987abcdef01234588",
  "storage_path": "/app/data/storage/uploads/documents/6543210987abcdef01234588/file.pdf",
  "chunk_size": 800,
  "chunk_overlap": 150
}
```
- **Response (200 OK)**:
```json
{
  "document_id": "6543210987abcdef01234567",
  "status": "ready",
  "total_pages": 38,
  "total_chunks": 112,
  "embedding_model": "text-embedding-3-small",
  "embedding_dimension": 1536,
  "processing_duration_ms": 2840
}
```

### 3.3 Query Knowledge Base
#### `POST /internal/v1/rag/query`
- **Headers**: `X-Internal-Service-Key: <key>`
- **Request Body**:
```json
{
  "query": "What were the operating margins for Europe in Q2?",
  "user_id": "6543210987abcdef01234588",
  "document_ids": ["6543210987abcdef01234567"],
  "top_k": 5,
  "similarity_threshold": 0.65,
  "conversation_history": [
    { "role": "user", "content": "Summary of regional performance?" },
    { "role": "assistant", "content": "Here is the regional performance breakdown..." }
  ]
}
```
- **Response (200 OK)**:
```json
{
  "answer": "Operating margins for Europe in Q2 were reported at 18.2% [Doc: 6543210987abcdef01234567, Page: 12].",
  "citations": [
    {
      "citation_id": "cit_1",
      "document_id": "6543210987abcdef01234567",
      "page_number": 12,
      "chunk_id": "chk_c0a80101-0012",
      "similarity_score": 0.892,
      "excerpt": "Operating margins in the European region showed strong resilience, closing Q2 at 18.2%."
    }
  ],
  "prompt_tokens": 940,
  "completion_tokens": 48,
  "model_used": "gpt-4o-mini"
}
```

