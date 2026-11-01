# ADR-002: Hybrid Data Storage — MongoDB for Application State and PostgreSQL with pgvector for Embeddings

## Status
Accepted

## Context
KnowDoc manages two distinct data access patterns:
1. **Document & Conversational Entities**: Semi-structured, hierarchically nested data that evolves frequently. This includes user profiles, dynamic document metadata (processing states, extracted tags, page counts), conversation sessions, and multi-turn message histories containing variable citation trees.
2. **Vector Embeddings & Semantic Search**: High-dimensional dense float vectors (e.g., 1536-dimensional vectors for OpenAI `text-embedding-3-small` or 768-dimensional vectors for BGE/local embeddings) requiring Approximate Nearest Neighbor (ANN) indexing (HNSW / IVFFlat), exact cosine distance operators, and relational compound filters.

## Decision
We adopted a **Hybrid Polyglot Persistence Architecture**:
- **MongoDB (via Mongoose)**: Serves as the primary operational datastore for application state:
  - Collections: `users`, `documents`, `conversations`, `messages`.
  - MongoDB's flexible BSON document model is ideal for nested conversation histories, flexible document tags, and schema evolution without downtime.
- **PostgreSQL with `pgvector`**: Serves as the dedicated vector datastore:
  - Table: `document_chunks` (storing chunk text, page number, chunk index, metadata, and `embedding vector(N)`).
  - Table: `rag_evaluations` (storing retrieval confidence metrics, user feedback, and ground-truth evaluation logs).
- **Identifier Mapping Strategy**:
  - The canonical document identifier originates in MongoDB as an `ObjectId` (represented as a 24-character hexadecimal string, e.g., `"6543210987abcdef01234567"`).
  - In PostgreSQL, this identifier is persisted in `document_chunks.document_id` as `VARCHAR(64)` with a foreign-index constraint and B-Tree index.
  - The tenant identifier (`user_id`) is similarly persisted in PostgreSQL as `VARCHAR(64)` to enforce strict multi-tenant partition filtering on every vector query.
- **Configurable Vector Dimensions**:
  - Vector dimensions are not hardcoded into application queries. The column definition in PostgreSQL uses configurable dimensions (defaulting to 1536, with migration scripts supporting model changes).
- **Cross-Datastore Cascade & Cleanup Protocol**:
  - Deletion of a document in MongoDB immediately triggers an asynchronous deletion event:
    1. SQL command: `DELETE FROM document_chunks WHERE user_id = $1 AND document_id = $2;`
    2. File binary deletion via `IStorageProvider.deleteObject(storageKey)`.
    3. Removal of document reference from active conversations in MongoDB.

## Rationale
- Pure SQL with JSONB for conversational data leads to rigid migrations for deeply nested messages and citation arrays.
- Pure NoSQL (e.g., MongoDB Atlas Vector Search) introduces vendor lock-in to Atlas cloud services and prevents seamless local development with open-source Docker instances.
- PostgreSQL + `pgvector` provides rock-solid, open-source, standards-compliant vector indexing (HNSW) that can run anywhere via Docker or managed RDS/Cloud SQL.

## Consequences
- **Positive**:
  - Optimal database engine for each specific workload.
  - No vendor lock-in for vector search.
  - Fast JSON document reads for conversations in Express.
- **Negative / Trade-offs**:
  - Dual datastore management: Two databases to run, back up, and monitor.
  - No distributed 2-Phase Commit (2PC): Handled by compensating transactions and idempotent deletion cascades.

