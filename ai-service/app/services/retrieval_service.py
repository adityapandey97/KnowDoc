from typing import List, Optional
from app.services.embedding_service import embedding_service
from app.repositories.vector_repository import vector_repository
from app.schemas.chat import SearchResult
from app.core.config import settings
from app.core.logging import logger

class RetrievalService:
    """
    Coordinates semantic vector retrieval, score filtering, and chunk deduplication.
    Strictly verifies user_id tenancy on all queries.
    """

    def __init__(self):
        self.embedder = embedding_service
        self.repo = vector_repository

    async def retrieve_relevant_chunks(
        self,
        query: str,
        user_id: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = settings.default_top_k,
        threshold: float = settings.default_similarity_threshold
    ) -> List[SearchResult]:
        if not query or not query.strip():
            return []

        # 1. Generate query embedding
        query_vector = await self.embedder.compute_query_embedding(query.strip())

        # 2. Retrieve from repository with tenant filtering
        raw_results = await self.repo.search_similar_chunks(
            query_embedding=query_vector,
            user_id=user_id,
            document_ids=document_ids,
            top_k=top_k * 2,  # Oversample for deduplication
            threshold=threshold
        )

        # 3. Deduplicate by content hash / exact overlap
        deduped: List[SearchResult] = []
        seen_contents = set()

        for res in raw_results:
            content_key = res.content.strip()[:100]
            if content_key not in seen_contents:
                seen_contents.add(content_key)
                deduped.append(res)
            if len(deduped) >= top_k:
                break

        logger.info(
            f"Retrieved {len(deduped)} deduplicated passages for user {user_id} "
            f"(target docs: {document_ids or 'all'})"
        )
        return deduped

retrieval_service = RetrievalService()

