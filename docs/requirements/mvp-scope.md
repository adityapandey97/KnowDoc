# KnowDoc — MVP Scope & Phase Matrix

## 1. Overview
To ensure rapid, rock-solid engineering delivery without premature optimization or scope bloat, the KnowDoc development lifecycle is structured into distinct phases. This document defines the exact boundaries of **Phase 1 (Engineering & Architectural Foundation)**, **Phase 2 (Core MVP)**, and **Phase 3 (Enterprise & Advanced Intelligence)**.

---

## 2. Phase 1: Architecture, Repository & Engineering Foundation (CURRENT SCOPE)

### In-Scope Deliverables
1. **Architectural Blueprints & Specifications**:
   - Comprehensive High-Level Design (HLD) and Low-Level Design (LLD).
   - Architectural Decision Records (ADRs) for Service Boundaries, Hybrid Storage, and Asynchronous Processing.
   - Formal API contracts for Express (client-facing) and FastAPI (internal AI service).
   - Data models for MongoDB (document metadata, users, chat history) and PostgreSQL (pgvector chunks, embeddings, evaluations).
   - Production security, local development, and indexing strategies.
2. **Standardized Directory Layout**:
   - Exact monorepo layout matching the platform specification with zero extraneous root files.
   - Frontend: React + Vite + JavaScript (ES modules) + Tailwind CSS architecture.
   - Backend: Node.js + Express + JavaScript (ES modules) layered architecture.
   - AI Service: Python 3.12+ + FastAPI clean domain-driven architecture.
   - Infrastructure: Docker Compose with MongoDB, PostgreSQL (pgvector), and Redis.
3. **Core Scaffolding & Shared Interfaces**:
   - Express server lifecycle with graceful shutdown, configuration validation, centralized error handling, and health check routes.
   - FastAPI server lifecycle with configuration via Pydantic settings, internal service authentication middleware, and health check routes.
   - Storage abstraction interface with a local disk implementation.
   - PDF validation utility with magic byte verification.
   - Database connection singletons (Mongoose, PostgreSQL pool, Redis client).
   - Runnable starter tests (Jest for Node.js, Pytest for FastAPI, React Testing Library for frontend).
   - Containerization definitions and GitHub Actions CI starter workflow.

### Excluded in Phase 1
- Full React UI component library and end-to-end user flows.
- Production OAuth / Social Login integrations.
- Heavy OCR optical character recognition engine (Tesseract/Textract).
- Live third-party billing, multi-region database clustering, or external cloud deployment.

---

## 3. Phase 2: Core Document Intelligence MVP

### Feature Roadmap
- **End-to-End PDF Ingestion**:
  - Full BullMQ background worker pipeline connecting Express to FastAPI AI Service.
  - PyPDF / pdfplumber extraction preserving exact physical page numbers.
  - Recursive text chunking with configurable overlap.
  - Embedding pipeline using OpenAI `text-embedding-3-small` or local HuggingFace embeddings.
  - Vector storage in PostgreSQL with HNSW vector index.
- **Conversational RAG Pipeline**:
  - Contextual question-answering with citation extraction (page number, snippet, document ID).
  - Multi-turn conversation persistence in MongoDB.
  - Prompt injection mitigation and untrusted context boundary fencing.
- **Frontend User Interface**:
  - Drag-and-drop PDF upload with progress bars.
  - Document status drawer (pending, processing, ready, failed).
  - Split-view chat interface: conversation thread on the left, PDF viewer with highlighted citation pages on the right.
- **Tenancy & Security**:
  - JWT auth flow with refresh token rotation and cookie storage.
  - User-scoped vector retrieval enforcement.

---

## 4. Phase 3: Advanced Intelligence & Enterprise Platform

### Feature Roadmap
- **OCR Engine for Scanned Documents**:
  - Automatic detection of scanned/non-digital PDFs.
  - Asynchronous OCR pipeline utilizing Tesseract / AWS Textract / DocTR.
- **Precision Reranking**:
  - Two-stage retrieval adding a cross-encoder reranker (e.g., Cohere Rerank or BGE-Reranker-Large) for top-k refinement.
- **Agentic Multi-Document Synthesis**:
  - Multi-agent research workflows: decompose complex queries into sub-questions across dozens of enterprise documents.
  - Cross-document comparison matrix generator.
- **Production Cloud Infrastructure**:
  - AWS S3 or Cloudflare R2 object storage provider integration.
  - Kubernetes / ECS deployment with auto-scaling BullMQ worker pools.
  - Enterprise SSO (SAML 2.0 / OIDC) and team workspace permissions.

---

## 5. Scope Traceability Matrix

| Feature Domain | Phase 1 (Foundation) | Phase 2 (Core MVP) | Phase 3 (Advanced) |
| :--- | :--- | :--- | :--- |
| **Architecture & Docs** | Comprehensive specifications, ADRs, schemas | Updated API docs & operational runbooks | Enterprise SLA & security compliance docs |
| **Document Parsing** | PDF signature check, parser interface & scaffolding | PyPDF text extraction + page preservation | Tesseract OCR + image table extraction |
| **Embeddings & Vector** | Pgvector schema, HNSW index strategy, client | Batch embedding generation & vector insertion | Multi-model embedding routing & quantization |
| **Retrieval & RAG** | Retrieval contracts, prompt boundary design | Top-k vector retrieval + grounded LLM answering | Cross-encoder reranking + agentic RAG |
| **Background Processing**| Redis config, BullMQ queue definitions, worker shell | Live queue orchestration & retry handling | Distributed worker scaling & priority queues |
| **Frontend UI** | Vite + React + Tailwind structure, theme, layout | Interactive document viewer & chat interface | Multi-doc comparative workspace & annotations |
| **Auth & Security** | Data model, password hashing & JWT design | Full JWT auth flow, rate limiting, middleware | SSO, RBAC, team workspaces, audit logs |

