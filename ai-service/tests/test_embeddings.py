import asyncio
import pytest
import numpy as np
from app.providers.embedding_provider import MockEmbeddingProvider
from app.services.embedding_service import EmbeddingService

def test_mock_embedding_provider_properties():
    async def _run():
        provider = MockEmbeddingProvider(dimension=1536)
        assert provider.dimension == 1536
        assert provider.model_name == "mock-embedding-v1"

        query_vec = await provider.embed_query("Financial analysis for Q3")
        assert len(query_vec) == 1536

        # Verify unit normalization: ||vec|| ≈ 1.0
        norm = np.linalg.norm(np.array(query_vec))
        assert pytest.approx(norm, 0.001) == 1.0

    asyncio.run(_run())

def test_mock_embedding_provider_deterministic():
    async def _run():
        provider = MockEmbeddingProvider(dimension=1536)
        v1 = await provider.embed_query("Consistent string")
        v2 = await provider.embed_query("Consistent string")
        assert v1 == v2

        v_diff = await provider.embed_query("Different string")
        assert v1 != v_diff

    asyncio.run(_run())

def test_embedding_service_batching():
    async def _run():
        service = EmbeddingService()
        texts = [f"Sample sentence number {i}" for i in range(10)]
        vectors = await service.compute_embeddings(texts)
        assert len(vectors) == 10
        assert len(vectors[0]) == service.dimension

    asyncio.run(_run())
