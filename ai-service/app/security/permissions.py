import hmac
from typing import List
from fastapi import Header
from app.core.config import settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.logging import logger

def verify_internal_key(x_internal_service_key: str = Header(..., alias="X-Internal-Service-Key")):
    """
    Validates the shared high-entropy secret between Express and FastAPI.
    Uses hmac.compare_digest to prevent side-channel timing attacks.
    """
    expected = settings.internal_service_key.encode("utf-8")
    provided = x_internal_service_key.encode("utf-8")

    if not hmac.compare_digest(expected, provided):
        logger.warn("Unauthorized attempt to access internal AI service endpoint")
        raise AuthenticationError("Invalid internal service authorization key.")
    return True


def enforce_document_authorization(user_id: str, document_ids: List[str], allowed_doc_ids: List[str]):
    """
    Blocks cross-user document access and document enumeration.
    """
    if not user_id or not user_id.strip():
        raise PermissionDeniedError("Valid tenant user_id is strictly required.")

    if not document_ids:
        return

    allowed_set = set(allowed_doc_ids)
    for doc_id in document_ids:
        if doc_id not in allowed_set:
            logger.warn(f"Unauthorized document access attempt by user {user_id} for doc {doc_id}")
            raise PermissionDeniedError(f"Access to document {doc_id} is denied.")

