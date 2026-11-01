import pytest
import numpy as np
from app.rag.embeddings.embedding_service import MockEmbeddingProvider

@pytest.mark.asyncio
async def test_mock_embedding_provider_dimension_and_norm():
    provider = MockEmbeddingProvider(dimension=1536)
    assert provider.dimension == 1536

    vector = await provider.embed_query("What were the 2025 earnings?")
    assert len(vector) == 1536

    # Verify unit normalization (norm ≈ 1.0)
    norm = np.linalg.norm(np.array(vector))
    assert pytest.approx(norm, 0.001) == 1.0

@pytest.mark.asyncio
async def test_mock_embedding_provider_deterministic():
    provider = MockEmbeddingProvider(dimension=1536)
    vec1 = await provider.embed_query("Identical query string")
    vec2 = await provider.embed_query("Identical query string")
    assert vec1 == vec2

