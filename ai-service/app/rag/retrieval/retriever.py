from typing import List
from app.domain.models import SearchResult
from app.rag.embeddings.embedding_service import get_embedding_provider
from app.repositories.vector_repo import vector_repo
from app.rag.reranking.reranker import reranker
from app.core.logging import logger

class Retriever:
    """
    Coordinates query embedding, tenant-filtered vector search, and reranking.
    """
    def __init__(self):
        self.vector_repo = vector_repo
        self.reranker = reranker

    async def retrieve(
        self,
        query: str,
        user_id: str,
        document_ids: List[str],
        top_k: int = 5,
        threshold: float = 0.50
    ) -> List[SearchResult]:
        embedder = get_embedding_provider()
        query_embedding = await embedder.embed_query(query)

        candidates = await self.vector_repo.search_similar_chunks(
            query_embedding=query_embedding,
            user_id=user_id,
            document_ids=document_ids,
            top_k=top_k * 2, # Fetch over-sample for reranking
            threshold=threshold
        )

        logger.info(f"Retrieved {len(candidates)} candidate passages for user {user_id}")
        
        reranked = await self.reranker.rerank(query=query, results=candidates, top_n=top_k)
        return reranked

retriever = Retriever()

