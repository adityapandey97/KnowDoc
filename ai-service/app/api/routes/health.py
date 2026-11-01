from fastapi import APIRouter, Depends
from app.core.config import settings
from app.security.permissions import verify_internal_key

router = APIRouter(tags=["Health"])

@router.get("/health")
async def public_health():
    """Liveness probe for container orchestrators."""
    return {
        "status": "healthy",
        "service": settings.service_name,
        "environment": settings.environment
    }

@router.get("/internal/v1/health")
async def internal_health(authorized: bool = Depends(verify_internal_key)):
    """Deep readiness probe for internal services."""
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": "1.0.0",
        "embedding_provider": settings.embedding_provider,
        "llm_provider": settings.llm_provider,
        "vector_dimension": settings.vector_dimension
    }
