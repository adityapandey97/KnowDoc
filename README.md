# KnowDoc — AI Document Intelligence Platform

KnowDoc is an enterprise-grade AI Document Intelligence Platform engineered for conversational Retrieval-Augmented Generation (RAG), strict factual citation extraction, and asynchronous document indexing at scale.

Built on a decoupled polyglot architecture combining a **Node.js/Express** application gateway, a **Python/FastAPI** AI processing engine, **MongoDB** for flexible application state, **PostgreSQL with pgvector** for vector embeddings, and **Redis with BullMQ** for resilient background worker queues.

---

## Architecture Overview

```
[ React SPA (Vite + Tailwind) ]
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

---

## Repository Structure

```text
knowdoc/
├── frontend/               # React (Vite, Tailwind CSS, ES modules)
│   ├── assets/
│   ├── components/         # Reusable UI, chat, document, layout components
│   ├── features/           # Auth, chat, documents, research, settings
│   ├── hooks/              # Custom React hooks
│   ├── services/           # Centralized API clients
│   ├── store/              # State management
│   ├── styles/             # Tailwind & CSS styling
│   └── tests/              # Frontend component and unit tests
├── backend/                # Node.js + Express Gateway (ES modules)
│   ├── src/
│   │   ├── config/         # Environment, MongoDB, Redis, PG configs
│   │   ├── controllers/    # Thin HTTP route handlers
│   │   ├── services/       # Domain business logic
│   │   ├── repositories/   # Data access layer
│   │   ├── models/         # Mongoose schemas
│   │   ├── middleware/     # Auth, error, rate-limiting middleware
│   │   ├── validators/     # Zod request validators
│   │   ├── integrations/   # AI HTTP client, storage abstraction, BullMQ
│   │   ├── events/         # Event emitter for cross-cutting triggers
│   │   └── utils/          # Logger, API error, PDF magic byte validator
│   └── tests/              # Jest and Supertest suites
├── ai-service/             # Python + FastAPI RAG Engine
│   ├── app/
│   │   ├── api/            # Versioned internal routes & Pydantic schemas
│   │   ├── core/           # Configuration, logging, lifecycle
│   │   ├── domain/         # Domain models (Chunk, Citation, Metadata)
│   │   ├── services/       # RAG coordination services
│   │   ├── rag/            # Parsing, chunking, embeddings, retrieval, generation
│   │   ├── repositories/   # pgvector async repository
│   │   ├── integrations/   # Swappable LLM & vector store clients
│   │   ├── security/       # Internal service key validation
│   │   └── main.py         # FastAPI application entrypoint
│   └── tests/              # Pytest test suites
├── docs/                   # Complete architectural documentation
│   ├── requirements/       # Functional, non-functional, and MVP specifications
│   ├── architecture/       # HLD, LLD, ADRs, and Mermaid diagrams
│   ├── api/                # Formal REST API contracts
│   ├── database/           # Data models and indexing strategies
│   ├── security/           # Threat model, auth, and prompt defenses
│   └── deployment/         # Local development and runbooks
├── infra/                  # Infrastructure as Code
│   ├── docker/             # Production Dockerfiles (backend, ai-service, frontend)
│   ├── docker-compose.yml  # Local stack (MongoDB, pgvector, Redis, apps)
│   └── scripts/            # Database init and health checking scripts
├── tests/                  # Root-level E2E integration tests
├── .github/workflows/      # Continuous Integration workflows
├── .env.example            # Environment configuration template
└── README.md
```

---

## Technology Stack

- **Frontend**: React 18/19, Vite, Tailwind CSS, Lucide icons (Strict JavaScript ES modules, no TypeScript).
- **Backend**: Node.js 22 LTS, Express, Mongoose, ioredis, BullMQ, Zod, Multer, bcryptjs, jsonwebtoken (Strict JavaScript ES modules, no TypeScript).
- **AI Service**: Python 3.12+, FastAPI, Pydantic v2, PyPDF, asyncpg / psycopg2, NumPy.
- **Application Database**: MongoDB 7.0.
- **Vector Database**: PostgreSQL 16 with `pgvector` extension (HNSW indexing).
- **Asynchronous Task Broker**: Redis 7 Alpine with BullMQ.
- **Testing**: Jest, Supertest, Pytest, React Testing Library.

---

## Quickstart

### 1. Prerequisites
- Node.js `v20+` or `v22+`
- Python `3.12+`
- Docker and Docker Compose

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Start Datastores (MongoDB, PostgreSQL pgvector, Redis)
```bash
docker compose -f infra/docker-compose.yml up -d
```

### 4. Start Express Backend
```bash
cd backend
npm install
npm run dev
```

### 5. Start FastAPI AI Service
```bash
cd ai-service
python -m venv .venv
# On Windows: .\.venv\Scripts\Activate.ps1
# On Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```

### 6. Start React Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Testing

```bash
# Run backend tests
cd backend && npm test

# Run AI service tests
cd ai-service && pytest -v

# Run frontend tests
cd frontend && npm test
```

---

## Architecture Documentation

Deep dive into the architectural specifications in [`docs/`](docs/):
- [High-Level Design (HLD)](docs/architecture/HLD.md)
- [Low-Level Design (LLD)](docs/architecture/LLD.md)
- [ADR-001: Service Boundaries](docs/architecture/architecture-decisions/ADR-001-service-boundaries.md)
- [ADR-002: Hybrid Data Storage](docs/architecture/architecture-decisions/ADR-002-data-storage.md)
- [ADR-003: Asynchronous Document Processing](docs/architecture/architecture-decisions/ADR-003-document-processing.md)
- [API Contracts](docs/api/api-contracts.md)
- [Data Models](docs/database/data-model.md)
- [Indexing Strategy](docs/database/indexing-strategy.md)
- [Security Requirements](docs/security/security-requirements.md)
- [Local Development Runbook](docs/deployment/local-development.md)

