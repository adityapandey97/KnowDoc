from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import AIServiceException
from app.api.routes import health, ingestion, chat, retrieval

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"Starting {settings.service_name} on {settings.host}:{settings.port} "
        f"(env: {settings.environment}, embeddings: {settings.embedding_provider}, llm: {settings.llm_provider})"
    )
    yield
    logger.info(f"Shutting down {settings.service_name}")

app = FastAPI(
    title="KnowDoc AI Intelligence Service",
    description="Document parsing, pgvector semantic retrieval, and grounded AI agent reasoning",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global custom exception handler
@app.exception_handler(AIServiceException)
async def ai_service_exception_handler(request: Request, exc: AIServiceException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

# Register route modules
app.include_router(health.router)
app.include_router(ingestion.router)
app.include_router(chat.router)
app.include_router(retrieval.router)

@app.get("/")
async def root():
    return {
        "service": settings.service_name,
        "status": "online",
        "version": "1.0.0"
    }
