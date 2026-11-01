import asyncio
from app.schemas.documents import DocumentChunk
from app.repositories.vector_repository import vector_repository
from app.services.retrieval_service import retrieval_service
from app.providers.embedding_provider import MockEmbeddingProvider

def test_tenant_isolation_blocks_cross_user_retrieval():
    async def _run():
        embedder = MockEmbeddingProvider(dimension=1536)

        # 1. Index document for User A
        chunk_a = DocumentChunk(
            chunk_index=0,
            document_id="doc_secret_a",
            document_name="UserA_Secrets.pdf",
            user_id="user_alice",
            page_number=1,
            content="Confidential project details belonging exclusively to Alice.",
            token_estimate=12
        )
        emb_a = await embedder.embed_texts([chunk_a.content])
        await vector_repository.save_chunks_with_embeddings([chunk_a], emb_a)

        # 2. Index document for User B
        chunk_b = DocumentChunk(
            chunk_index=0,
            document_id="doc_public_b",
            document_name="UserB_Public.pdf",
            user_id="user_bob",
            page_number=1,
            content="General public market trends analyzed by Bob.",
            token_estimate=10
        )
        emb_b = await embedder.embed_texts([chunk_b.content])
        await vector_repository.save_chunks_with_embeddings([chunk_b], emb_b)

        # 3. User B queries for Alice's confidential data
        bob_results = await retrieval_service.retrieve_relevant_chunks(
            query="Confidential project details",
            user_id="user_bob",
            top_k=5,
            threshold=0.0 # Match all
        )

        # MUST NOT contain Alice's document
        assert len(bob_results) >= 0
        for r in bob_results:
            assert r.user_id == "user_bob"
            assert r.document_id != "doc_secret_a"

        # 4. User A queries and receives their document
        alice_results = await retrieval_service.retrieve_relevant_chunks(
            query="Confidential project details",
            user_id="user_alice",
            top_k=5,
            threshold=0.0
        )
        assert len(alice_results) == 1
        assert alice_results[0].document_id == "doc_secret_a"
        assert alice_results[0].user_id == "user_alice"

    asyncio.run(_run())
