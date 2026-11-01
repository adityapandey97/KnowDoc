-- ==============================================================================
-- KnowDoc pgvector Initialization Script
-- Executed on initial PostgreSQL container setup
-- ==============================================================================

-- 1. Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create document_chunks table
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(1536), -- Configurable dimension (1536 for OpenAI text-embedding-3-small)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_document_chunk UNIQUE (document_id, chunk_index)
);

-- 3. Create rag_evaluations table
CREATE TABLE IF NOT EXISTS rag_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(64) NOT NULL,
    message_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    query TEXT NOT NULL,
    retrieved_chunk_ids UUID[] NOT NULL,
    retrieval_latency_ms INTEGER NOT NULL,
    generation_latency_ms INTEGER NOT NULL,
    citation_precision_score FLOAT,
    user_rating SMALLINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create Indexes
-- 4.1 HNSW index on embedding vectors using cosine distance operator
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- 4.2 Compound index for tenant + document lookup
CREATE INDEX IF NOT EXISTS idx_chunks_tenant_doc 
ON document_chunks (user_id, document_id);

-- 4.3 Sequential ordering index
CREATE INDEX IF NOT EXISTS idx_chunks_doc_page_idx 
ON document_chunks (document_id, page_number, chunk_index);

-- 4.4 Evaluation records index
CREATE INDEX IF NOT EXISTS idx_evals_user_created 
ON rag_evaluations (user_id, created_at DESC);

