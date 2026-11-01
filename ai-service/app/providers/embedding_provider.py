import hashlib
import numpy as np
from typing import List
from abc import ABC, abstractmethod
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import EmbeddingError

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text strings into dense float vectors."""
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """Embed a single query string into a dense float vector."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic unit-normalized embedding provider for testing and offline development.
    Generates consistent float vectors matching the target model dimension.
    """
    def __init__(self, dimension: int = 1536, model_name: str = "mock-embedding-v1"):
        self._dim = dimension
        self._model = model_name

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def model_name(self) -> str:
        return self._model

    def _generate_vector(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self._dim

        import re
        tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
        if not tokens:
            tokens = [text.strip().lower()]

        combined = np.zeros(self._dim, dtype=np.float32)

        # Base text seed component for deterministic uniqueness
        base_seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
        rng_base = np.random.default_rng(base_seed)
        combined += rng_base.standard_normal(self._dim).astype(np.float32) * 0.05

        # Subword and token features for semantic overlap matching
        features = set(tokens)
        for t in tokens:
            if len(t) >= 4:
                features.add(t[:3])
                features.add(t[-3:])

        for feat in features:
            f_seed = int(hashlib.sha256(feat.encode("utf-8")).hexdigest()[:8], 16)
            f_rng = np.random.default_rng(f_seed)
            combined += f_rng.standard_normal(self._dim).astype(np.float32)

        norm = np.linalg.norm(combined)
        if norm > 0:
            combined = combined / norm
        return combined.tolist()

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_vector(t) for t in texts]

    async def embed_query(self, query: str) -> List[float]:
        return self._generate_vector(query)


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """
    Hosted OpenAI embedding provider using httpx to call text-embedding-3-small.
    """
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", dimension: int = 1536):
        self.api_key = api_key
        self.model = model
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def model_name(self) -> str:
        return self.model

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        import httpx
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"input": texts, "model": self.model}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return [item["embedding"] for item in data["data"]]
        except Exception as e:
            logger.error(f"OpenAI embedding call failed: {str(e)}")
            raise EmbeddingError(f"Embedding provider error: {str(e)}")

    async def embed_query(self, query: str) -> List[float]:
        results = await self.embed_texts([query])
        return results[0]


def get_embedding_provider() -> BaseEmbeddingProvider:
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimension=settings.vector_dimension
        )
    return MockEmbeddingProvider(dimension=settings.vector_dimension)
