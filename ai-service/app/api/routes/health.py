from fastapi import APIRouter, Depends
from app.api.schemas.rag import HealthResponse
from app.security.internal_auth import verify_internal_key
from app.integrations.vector_store.pgvector_client import pgvector_client
from app.core.config import settings

router = APIRouter(prefix="/internal/v1/health", tags=["Health"])

@router.get("", response_model=HealthResponse)
async def check_health(authorized: bool = Depends(verify_internal_key)):
    pg_healthy = await pgvector_client.is_healthy()
    return HealthResponse(
        status="healthy" if pg_healthy else "degraded",
        service=settings.service_name,
        version="1.0.0",
        dependencies={
            "pgvector": {"status": "connected" if pg_healthy else "disconnected"},
            "embedding_provider": {"model": settings.embedding_model, "status": "ready"}
        }
    )

