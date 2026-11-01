from typing import List
from app.domain.models import SearchResult

class IReranker:
    async def rerank(self, query: str, results: List[SearchResult], top_n: int = 5) -> List[SearchResult]:
        raise NotImplementedError

class PassThroughReranker(IReranker):
    """
    Phase 1 default: preserves top-k vector similarity order.
    Extensible in Phase 3 for Cohere / BGE cross-encoders.
    """
    async def rerank(self, query: str, results: List[SearchResult], top_n: int = 5) -> List[SearchResult]:
        return results[:top_n]

reranker = PassThroughReranker()

