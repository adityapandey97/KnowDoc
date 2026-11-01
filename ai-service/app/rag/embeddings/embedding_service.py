import hashlib
import numpy as np
from typing import List
from abc import ABC, abstractmethod
from app.core.config import settings
from app.core.logging import logger

class IEmbeddingProvider(ABC):
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass


class MockEmbeddingProvider(IEmbeddingProvider):
    """
    Deterministic unit-normalized embedding provider for Phase 1 testing and local development.
    Generates consistent float vectors matching the target model dimension.
    """
    def __init__(self, dimension: int = 1536):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def _generate_vector(self, text: str) -> List[float]:
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self._dim).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_vector(t) for t in texts]

    async def embed_query(self, query: str) -> List[float]:
        return self._generate_vector(query)


class OpenAIEmbeddingProvider(IEmbeddingProvider):
    """
    OpenAI embedding provider using httpx to call text-embedding-3-small or configured model.
    """
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", dimension: int = 1536):
        self.api_key = api_key
        self.model = model
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        import httpx
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"input": texts, "model": self.model}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

    async def embed_query(self, query: str) -> List[float]:
        results = await self.embed_texts([query])
        return results[0]


def get_embedding_provider() -> IEmbeddingProvider:
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimension=settings.vector_dimension
        )
    return MockEmbeddingProvider(dimension=settings.vector_dimension)

