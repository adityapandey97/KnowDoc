from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.routes import health, rag

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.service_name} on port {settings.port} (env: {settings.environment})")
    yield
    logger.info(f"Shutting down {settings.service_name}")

app = FastAPI(
    title="KnowDoc AI & RAG Service",
    description="Document parsing, chunking, pgvector search, and grounded LLM generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (strictly for local development if needed; production uses internal networking)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(health.router)
app.include_router(rag.router)

@app.get("/")
async def root():
    return {
        "service": settings.service_name,
        "status": "online",
        "docs": "/docs"
    }

