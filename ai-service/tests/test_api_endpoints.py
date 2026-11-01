import asyncio
import pytest
from app.api.routes.health import public_health, internal_health
from app.api.routes.chat import chat_endpoint
from app.api.routes.retrieval import semantic_search
from app.schemas.chat import ChatRequest, SearchRequest
from app.schemas.documents import DocumentChunk
from app.repositories.vector_repository import vector_repository
from app.providers.embedding_provider import MockEmbeddingProvider
from app.security.permissions import verify_internal_key
from app.core.exceptions import AuthenticationError

def test_public_health_route():
    async def _run():
        res = await public_health()
        assert res["status"] == "healthy"
        assert res["service"] == "knowdoc-ai-service"
    asyncio.run(_run())

def test_internal_health_route():
    async def _run():
        res = await internal_health(authorized=True)
        assert res["status"] == "healthy"
        assert res["service"] == "knowdoc-ai-service"
        assert res["vector_dimension"] == 1536
    asyncio.run(_run())

def test_verify_internal_key_security():
    # Valid key passes
    assert verify_internal_key("dev-internal-secret-change-in-production") is True

    # Invalid key raises AuthenticationError (401)
    with pytest.raises(AuthenticationError):
        verify_internal_key("invalid-secret-key")

def test_chat_route():
    async def _run():
        # Seed test chunk
        embedder = MockEmbeddingProvider()
        chunk = DocumentChunk(
            chunk_index=0,
            document_id="doc_chat_api_test",
            document_name="architecture.pdf",
            user_id="user_api_1",
            page_number=3,
            content="KnowDoc uses pgvector for high dimensional semantic retrieval.",
            token_estimate=10
        )
        embs = await embedder.embed_texts([chunk.content])
        await vector_repository.save_chunks_with_embeddings([chunk], embs)

        req = ChatRequest(
            query="What does KnowDoc use for semantic retrieval?",
            user_id="user_api_1",
            document_ids=["doc_chat_api_test"],
            use_agent=False
        )
        res = await chat_endpoint(req, authorized=True)
        assert res.answer
        assert len(res.citations) == 1
        assert res.citations[0].document_id == "doc_chat_api_test"
        assert res.citations[0].page_number == 3
    asyncio.run(_run())

def test_retrieval_route():
    async def _run():
        req = SearchRequest(
            query="pgvector semantic retrieval",
            user_id="user_api_1",
            document_ids=["doc_chat_api_test"],
            top_k=2
        )
        res = await semantic_search(req, authorized=True)
        assert res.total_matches >= 1
        assert res.results[0].document_id == "doc_chat_api_test"
    asyncio.run(_run())
