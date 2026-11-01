# ADR-003: Asynchronous Document Processing with Redis and BullMQ

## Status
Accepted

## Context
Document ingestion involves compute- and network-heavy steps:
1. Validating and storing PDF binary on disk or object storage.
2. Parsing page-by-page text across documents up to hundreds of pages.
3. Splitting text into hundreds of overlapping chunks.
4. Calling external embedding APIs across multiple batch requests (e.g. 50-100 chunks per batch).
5. Inserting embeddings and chunks into PostgreSQL `pgvector`.

Running this pipeline synchronously within an HTTP POST request would:
- Lead to client HTTP timeouts (gateway timeouts at 30s-60s).
- Tie up Node.js or FastAPI worker threads, preventing new requests from being served.
- Provide zero resilience against transient network blips or rate limits during embedding API calls.

We evaluated three options:
1. **Synchronous HTTP Pipeline**: Parse and embed inline before returning HTTP 201 Created.
2. **Kafka / RabbitMQ Enterprise Bus**: Heavyweight distributed event streaming broker.
3. **Redis-backed BullMQ Queue**: In-memory task queue with native Redis data structures, exponential backoff, job state transitions, and concurrency management.

## Decision
We adopted **BullMQ on top of Redis** (`knowdoc:queue:ingestion`):
- When a document upload succeeds, Express generates an initial MongoDB document record with status `pending`, pushes a job payload to the BullMQ queue, and immediately responds to the client with `HTTP 202 Accepted` along with the `documentId`.
- A dedicated BullMQ worker process consumes the job, triggers parsing and embedding via the FastAPI AI service, and tracks progress.
- Upon completion, the worker transitions the document status in MongoDB to `ready`.

## Idempotency & Failure Handling Strategy
1. **Deduplication**:
   - The job ID is constructed deterministically as `ingest_<document_id>`. BullMQ prevents enqueuing duplicate active jobs for the same document ID.
2. **Retry with Exponential Backoff**:
   - BullMQ is configured for `attempts: 3` with an exponential backoff strategy starting at 5 seconds.
   - If an embedding provider returns a 429 Rate Limit or transient 503, the worker backs off automatically.
3. **Partial Failure Cleanup**:
   - Before executing chunk insertions for a retry or re-indexing, the worker purges any existing chunks for `document_id` in PostgreSQL (`DELETE FROM document_chunks WHERE document_id = $1`). This guarantees that failed runs do not leave duplicate or orphaned vector records.
4. **Dead Letter & Terminal Failure**:
   - After 3 failed attempts, BullMQ routes the job to the failed state.
   - A global worker failure handler catches this transition, marks the MongoDB document record as `failed`, records the specific error code and message, and cleans up temporary working files.

## Rationale
- Redis is lightweight, ultra-fast, and already required for caching and rate-limiting.
- BullMQ provides enterprise queue semantics (delayed jobs, parent-child job dependencies, concurrency control, stalled job detection, automatic retry backoffs) with minimal operational complexity compared to Kafka or RabbitMQ.

## Consequences
- **Positive**:
  - Instantaneous client upload response (P99 < 300ms).
  - Robust retry handling and resilience against external API rate limits.
  - Granular queue monitoring (active, waiting, failed, completed).
- **Negative / Trade-offs**:
  - Requires clients to poll or listen via SSE/WebSockets for document readiness.
  - Requires Redis persistence (AOF/RDB) to prevent job loss upon Redis server restart.

