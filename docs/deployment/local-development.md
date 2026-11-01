# KnowDoc — Local Development Guide

## 1. Prerequisites
Before setting up KnowDoc locally, ensure you have the following installed:
- **Node.js**: `v20.x` or `v22.x` (LTS)
- **Python**: `3.12.x` or `3.13.x`
- **Docker & Docker Compose**: Docker Desktop or Docker Engine with compose plugin
- **Package Managers**: `npm` (v10+) and `pip`

---

## 2. Quickstart Overview

KnowDoc consists of three application services and three infrastructure datastores:
- **Infrastructure**: MongoDB, PostgreSQL (with `pgvector`), Redis
- **Backend API**: Node.js/Express (Port 5000)
- **AI Service**: Python/FastAPI (Port 8000)
- **Frontend UI**: React/Vite (Port 5173)

---

## 3. Step-by-Step Local Setup

### Step 3.1: Environment Configuration
Copy the provided `.env.example` file to create your local `.env`:
```bash
cp .env.example .env
```
Inspect `.env` and configure your local passwords, secrets, and (optionally) an `OPENAI_API_KEY` if testing real LLM responses. For development without an OpenAI key, the AI service defaults to a local mock embedding and generation adapter.

### Step 3.2: Start Datastores via Docker Compose
Start MongoDB, PostgreSQL with pgvector, and Redis in the background:
```bash
docker compose -f infra/docker-compose.yml up -d
```

Verify all three datastores are healthy:
```bash
docker compose -f infra/docker-compose.yml ps
```

The PostgreSQL container automatically runs `infra/scripts/init-pgvector.sql` on initial startup, enabling the `vector` extension and creating required tables.

### Step 3.3: Setup & Run Express Backend
1. Navigate to the backend directory and install dependencies:
   ```bash
   cd backend
   npm install
   ```
2. Start the Express development server:
   ```bash
   npm run dev
   ```
   The backend will start at `http://localhost:5000`. You can test health at:
   ```bash
   curl http://localhost:5000/api/v1/health
   ```

### Step 3.4: Setup & Run FastAPI AI Service
1. Open a new terminal and navigate to `ai-service`:
   ```bash
   cd ai-service
   ```
2. Create and activate a Python virtual environment:
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server with hot-reloading:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Test the AI service health at:
   ```bash
   curl -H "X-Internal-Service-Key: dev-internal-secret-change-in-production" http://localhost:8000/internal/v1/health
   ```

### Step 3.5: Setup & Run React Frontend
1. Open a new terminal and navigate to `frontend`:
   ```bash
   cd frontend
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The application will be accessible in your browser at `http://localhost:5173`.

---

## 4. Running Automated Tests

### 4.1 Backend Tests (Jest & Supertest)
```bash
cd backend
npm test
```

### 4.2 AI Service Tests (Pytest)
```bash
cd ai-service
pytest -v
```

### 4.3 Frontend Tests (React Testing Library)
```bash
cd frontend
npm test
```

---

## 5. Troubleshooting & FAQ

### Issue: PostgreSQL container fails with `vector extension not found`
- **Cause**: Standard `postgres:16` image lacks pgvector binaries.
- **Fix**: Verify your `docker-compose.yml` specifies `image: pgvector/pgvector:pg16`, which bundles precompiled pgvector binaries.

### Issue: Express cannot connect to Redis
- **Cause**: Redis container is not running or port 6379 is occupied.
- **Fix**: Run `docker compose -f infra/docker-compose.yml logs redis` to check logs, and ensure port 6379 is free.

### Issue: Upload fails with `415 Unsupported Media Type`
- **Cause**: The uploaded file is missing the standard `%PDF` binary magic bytes.
- **Fix**: Ensure the test file is a genuine PDF document, not a text file renamed to `.pdf`.

