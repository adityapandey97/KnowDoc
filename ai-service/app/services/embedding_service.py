from typing import List
from app.providers.embedding_provider import get_embedding_provider
from app.core.config import settings
from app.core.logging import logger

class EmbeddingService:
    """
    Coordinates batch generation of dense embeddings using configured provider.
    """

    def __init__(self):
        self.provider = get_embedding_provider()
        self.batch_size = settings.embedding_batch_size

    async def compute_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        all_embeddings: List[List[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            logger.info(f"Computing embeddings batch {i // self.batch_size + 1} ({len(batch)} items)")
            batch_vectors = await self.provider.embed_texts(batch)
            all_embeddings.extend(batch_vectors)

        return all_embeddings

    async def compute_query_embedding(self, query: str) -> List[float]:
        return await self.provider.embed_query(query)

    @property
    def dimension(self) -> int:
        return self.provider.dimension

    @property
    def model_name(self) -> str:
        return self.provider.model_name

embedding_service = EmbeddingService()

