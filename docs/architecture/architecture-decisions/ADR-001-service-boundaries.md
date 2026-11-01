# ADR-001: Separation of Express API Gateway and FastAPI AI Service

## Status
Accepted

## Context
KnowDoc requires capabilities that fall into two fundamentally distinct computational domains:
1. **Web Application & Workflow Management**: User authentication, session management, tenancy enforcement, document upload and multipart streaming, CRUD on document metadata, conversation state tracking, and queue job dispatching.
2. **Artificial Intelligence & Document Engineering**: PDF binary text extraction, tokenization, semantic chunking, vector embedding calculation, high-dimensional vector similarity operations, prompt template synthesis, and LLM inference streaming.

We evaluated three potential architectural topologies:
1. **Single Monolith (Node.js/Express only)**: Running AI libraries via Node.js native bindings (e.g., ONNX runtime or LangChain.js).
2. **Single Monolith (Python/FastAPI only)**: Building the entire web backend, ORM, auth, and queue workers in Python.
3. **Decoupled Dual-Service Architecture**: Node.js/Express for application gateway/orchestration + Python/FastAPI for AI/RAG services.

## Decision
We adopted the **Decoupled Dual-Service Architecture**:
- **Node.js + Express (Backend Gateway)**: Owns HTTP client ingress, JWT security, MongoDB models, file upload validation, and BullMQ queue orchestration.
- **Python + FastAPI (AI Service)**: Owns text parsing, chunking algorithms, vector embedding generation, vector store operations in pgvector, and LLM communication.
- **Service Communication**: Authenticated HTTP REST requests over an internal Docker network, secured via shared high-entropy authorization headers (`X-Internal-Service-Key`).

## Rationale
1. **Ecosystem Fit**:
   - Python is the undisputed gold standard for AI/ML, PDF extraction (`pypdf`, `pdfplumber`, `fitz`), tokenization (`tiktoken`), embeddings (`sentence-transformers`), and vector operations.
   - Node.js excels at asynchronous I/O, rapid JSON API orchestration, concurrent streaming of file uploads, and lightweight job queue orchestration via Redis/BullMQ.
2. **Resource & Scaling Isolation**:
   - PDF parsing, chunking, and embedding generation are CPU and memory-intensive. Running them inside the same Node.js event loop would risk blocking event loops and stalling regular web requests.
   - Decoupled services allow the AI worker service to scale independently based on parsing/retrieval load without multiplying web gateway instances.
3. **Clear Security Boundaries**:
   - The FastAPI AI service has no direct exposure to the public internet. It can only be reached by authorized workers or the Express gateway.

## Consequences
- **Positive**:
  - Clear separation of operational concerns.
  - Ability to optimize Python runtime environments (NumPy, PyTorch/ONNX if needed) without polluting Node.js dependencies.
  - Granular horizontal auto-scaling based on CPU metrics.
- **Negative / Trade-offs**:
  - Two runtimes (Node.js and Python) to maintain in local development and CI pipelines.
  - Network hop between Express and FastAPI for query retrieval (mitigated by sub-5ms internal network latencies and connection reuse).

