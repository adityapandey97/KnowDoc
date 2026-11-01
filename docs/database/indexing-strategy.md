# KnowDoc — Indexing Strategy & Vector Performance Optimization

## 1. Overview
High-performance Retrieval-Augmented Generation requires low-latency retrieval across both relational/document metadata and high-dimensional vector embeddings. This document details the indexing architecture for both MongoDB and PostgreSQL (`pgvector`).

---

## 2. MongoDB Indexing Strategy

MongoDB manages user authentication, document state, and conversation histories. Indexes are tuned for user-partitioned queries and descending chronological sorting.

| Collection | Index Keys | Type | Purpose |
| :--- | :--- | :--- | :--- |
| `users` | `{ email: 1 }` | Unique B-Tree | Fast lookup for authentication and duplicate email prevention. |
| `documents` | `{ userId: 1, createdAt: -1 }` | Compound B-Tree | Supports paginated listing of a user's documents ordered by recency. |
| `documents` | `{ userId: 1, fileHash: 1 }` | Compound B-Tree | Detects duplicate document uploads within a specific user's library. |
| `documents` | `{ storageKey: 1 }` | Unique B-Tree | Ensures zero collisions in blob storage keys. |
| `documents` | `{ status: 1 }` | Single B-Tree | Enables queue monitoring and background health scrapers to query stuck jobs. |
| `conversations` | `{ userId: 1, lastMessageAt: -1 }` | Compound B-Tree | Retrieves recent user conversation threads with zero in-memory sorting. |
| `messages` | `{ conversationId: 1, createdAt: 1 }` | Compound B-Tree | Retrieves entire conversation transcripts in sequential chronological order. |

---

## 3. PostgreSQL & pgvector Indexing Strategy

### 3.1 Vector Index Selection: HNSW vs. IVFFlat
PostgreSQL `pgvector` provides two main indexing strategies for vector similarity search:

1. **IVFFlat (Inverted File Flat)**:
   - Divides vector space into centroids/lists. Requires training on an existing dataset.
   - Slower query times at scale; degrades when new vectors are inserted without re-indexing.
2. **HNSW (Hierarchical Navigable Small World)**:
   - Builds a multi-layer graph of vectors.
   - No training phase required; vectors can be inserted incrementally without performance collapse.
   - Significantly higher query recall and sub-15ms search latencies.

**Decision**: KnowDoc utilizes **HNSW with Cosine Distance (`vector_cosine_ops`)**.

### 3.2 HNSW Index DDL & Tuning Parameters
```sql
-- Create HNSW index on embeddings using cosine distance
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);
```

#### Parameter Rationale:
- `m = 16`: The number of bi-directional links created per node. 16 balances recall accuracy (>98%) with index build memory consumption.
- `ef_construction = 64`: The size of the dynamic candidate list during graph construction. 64 provides high index quality without excessive write delays during ingestion.
- **Query-time parameter**: `SET hnsw.ef_search = 40;` ensures fast candidate exploration while maintaining high top-k recall.

### 3.3 Relational & Tenant Filtering Indexes
Vector similarity search must always be scoped to the authenticated tenant and specific document(s). Without compound relational indexes, the database performs slow post-filtering.

```sql
-- Compound B-Tree index for tenant + document lookup
CREATE INDEX IF NOT EXISTS idx_chunks_tenant_doc 
ON document_chunks (user_id, document_id);

-- Index for ordering chunks sequentially by page and index
CREATE INDEX IF NOT EXISTS idx_chunks_doc_page_idx 
ON document_chunks (document_id, page_number, chunk_index);

-- Index for rag evaluation queries
CREATE INDEX IF NOT EXISTS idx_evals_user_created 
ON rag_evaluations (user_id, created_at DESC);
```

---

## 4. Query Execution Plan: Partitioned Vector Search

When an authenticated user queries KnowDoc, the query is planned as follows:

```sql
EXPLAIN ANALYZE
SELECT 
    id, document_id, page_number, content,
    1 - (embedding <=> $1::vector) AS similarity_score
FROM document_chunks
WHERE user_id = '6543210987abcdef01234588'
  AND document_id = ANY(ARRAY['6543210987abcdef01234567'])
ORDER BY embedding <=> $1::vector ASC
LIMIT 5;
```

### Plan Optimization:
1. `pgvector` uses the HNSW index to locate the nearest neighbors in the vector space.
2. Filter predicates `user_id = ...` and `document_id = ANY(...)` prune candidates outside the tenant's authorization boundary.
3. Because vector space queries scale with the candidate graph, filtering by tenant and document guarantees sub-50ms execution times even with millions of total vectors in the table.

---

## 5. Maintenance & Index Health Guidelines
1. **Vacuuming**:
   - `pgvector` produces dead tuples upon document deletion. Enable autovacuum or run regular maintenance:
     ```sql
     VACUUM (ANALYZE) document_chunks;
     ```
2. **Re-indexing on Model Upgrades**:
   - If changing the embedding model (e.g. from 1536-dim OpenAI to 768-dim BGE), drop and recreate the table or migration column to avoid vector dimension mismatches.

