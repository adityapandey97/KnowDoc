import hmac
from fastapi import Header, HTTPException, status
from app.core.config import settings

def verify_internal_key(x_internal_service_key: str = Header(..., alias="X-Internal-Service-Key")):
    """
    Validates internal service key header to ensure requests originate
    exclusively from authorized internal microservices (Express gateway or BullMQ workers).
    Uses constant-time comparison to prevent timing attacks.
    """
    expected_key = settings.internal_service_key.encode("utf-8")
    provided_key = x_internal_service_key.encode("utf-8")

    if not hmac.compare_digest(expected_key, provided_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid internal service authorization key"
        )
    return True

