import asyncio
import pytest
from app.schemas.documents import DocumentChunk
from app.repositories.vector_repository import vector_repository
from app.providers.embedding_provider import MockEmbeddingProvider
from app.tools.document_search import search_documents_tool
from app.tools.document_summary import summarize_document_tool
from app.tools.page_retrieval import retrieve_document_page_tool
from app.services.agent_service import agent_service
from app.core.exceptions import ToolExecutionError

def _seed_docs():
    async def _seed():
        embedder = MockEmbeddingProvider()
        c1 = DocumentChunk(
            chunk_index=0,
            document_id="doc_handbook",
            document_name="Employee_Handbook.pdf",
            user_id="user_agent_test",
            page_number=1,
            content="Standard vacation allowance is 20 days per calendar year.",
            token_estimate=12
        )
        c2 = DocumentChunk(
            chunk_index=1,
            document_id="doc_handbook",
            document_name="Employee_Handbook.pdf",
            user_id="user_agent_test",
            page_number=2,
            content="Health insurance coverage commences on day one of employment.",
            token_estimate=11
        )
        embs = await embedder.embed_texts([c1.content, c2.content])
        await vector_repository.save_chunks_with_embeddings([c1, c2], embs)

    asyncio.run(_seed())

def test_search_documents_tool():
    _seed_docs()
    async def _run():
        res = await search_documents_tool({
            "query": "vacation allowance",
            "user_id": "user_agent_test",
            "document_ids": ["doc_handbook"],
            "top_k": 3
        })
        assert res["tool"] == "search_documents"
        assert res["matches_count"] >= 1
        assert "vacation" in res["passages"][0]["excerpt"].lower()

    asyncio.run(_run())

def test_tool_invalid_arguments_raises_error():
    async def _run():
        with pytest.raises(ToolExecutionError):
            await search_documents_tool({"query": "", "user_id": "user_agent_test"})

    asyncio.run(_run())

def test_retrieve_document_page_tool():
    _seed_docs()
    async def _run():
        res = await retrieve_document_page_tool({
            "document_id": "doc_handbook",
            "page_number": 2,
            "user_id": "user_agent_test"
        })
        assert res["found"] is True
        assert "Health insurance" in res["page_text"]

    asyncio.run(_run())

def test_agent_service_loop():
    _seed_docs()
    async def _run():
        response = await agent_service.execute_agent_loop(
            query="What is the vacation policy in the handbook?",
            user_id="user_agent_test",
            document_ids=["doc_handbook"]
        )
        assert response.answer
        assert len(response.tool_calls) >= 1
        assert response.tool_calls[0].tool_name in ("search_documents", "summarize_document")
        assert len(response.citations) >= 1

    asyncio.run(_run())
