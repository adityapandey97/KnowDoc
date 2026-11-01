# KnowDoc AI Service Boundary (Phase 4 Preparation)

This directory serves as the architecture contract and staging area for the Phase 4 Artificial Intelligence & Retrieval-Augmented Generation (RAG) capabilities.

## Architecture Boundary

KnowDoc cleanly decouples the application gateway (Node.js/Express in `backend/`) from heavy AI and ML execution:

1. **Backend Role (`backend/src/modules/ai/`)**:
   - Exposes internal AI orchestrator endpoints:
     - `POST /api/v1/ai/generate`
     - `POST /api/v1/ai/stream`
     - `POST /api/v1/ai/context`
   - Defines `AIProviderInterface` with contract methods:
     - `generateResponse({ messages, context, model, temperature })`
     - `streamResponse({ messages, context, onChunk, onComplete, onError })`
     - `retrieveContext({ query, userId, documentIds, repositoryIds, topK })`
   - Manages message history persistence, token accounting, latency metrics, and tenant isolation.

2. **Phase 4 Implementation Scope**:
   - Python FastAPI AI microservice (or embedded adapter) providing:
     - Text chunking (recursive, syntax-aware)
     - Tree-sitter AST parsing for source code repositories
     - Dense embeddings generation (`text-embedding-3-small`, BGE, local ONNX models)
     - High-dimensional vector similarity search in PostgreSQL (`pgvector`)
     - Grounded LLM generation with XML boundary fencing against prompt injections
     - Fine-grained source citations with line and page numbers.

3. **Status in Phase 3**:
   - In accordance with Phase 3 constraints, the backend contains clean interface definitions and returns documented unavailable/placeholder responses (`503 Service Unavailable` or `pending` status) rather than returning fake or misleading AI outputs.

