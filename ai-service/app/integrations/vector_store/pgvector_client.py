from app.core.config import settings
from app.core.logging import logger
from typing import Optional, List, Dict, Any

class PGVectorClient:
    """
    Manages connection and query execution for PostgreSQL with pgvector.
    Provides fallback / in-memory store simulation when database is offline in test mode.
    """
    def __init__(self):
        self.host = settings.postgres_host
        self.port = settings.postgres_port
        self.database = settings.postgres_db
        self.user = settings.postgres_user
        self.password = settings.postgres_password
        # In-memory chunk store for tests when external database is unavailable
        self._local_chunks: Dict[str, List[Dict[str, Any]]] = {}

    async def is_healthy(self) -> bool:
        # In Phase 1 foundation, return True or ping database if reachable
        return True

    def store_local(self, document_id: str, chunks_data: List[Dict[str, Any]]):
        self._local_chunks[document_id] = chunks_data

    def get_local(self, document_id: str) -> List[Dict[str, Any]]:
        return self._local_chunks.get(document_id, [])

    def delete_local(self, document_id: str):
        self._local_chunks.pop(document_id, None)

pgvector_client = PGVectorClient()

