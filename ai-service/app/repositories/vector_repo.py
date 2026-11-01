import numpy as np
from typing import List
from app.domain.models import TextChunk, SearchResult
from app.integrations.vector_store.pgvector_client import pgvector_client
from app.core.logging import logger

class VectorRepository:
    """
    Data access layer for vector chunks and similarity operations.
    Enforces tenant partition isolation on all queries.
    """

    async def purge_document_chunks(self, user_id: str, document_id: str) -> None:
        logger.info(f"Purging existing vector chunks for doc: {document_id}")
        pgvector_client.delete_local(document_id)

    async def save_chunks_with_embeddings(
        self,
        chunks: List[TextChunk],
        embeddings: List[List[float]]
    ) -> int:
        if not chunks:
            return 0

        document_id = chunks[0].document_id
        chunk_records = []

        for chunk, emb in zip(chunks, embeddings):
            chunk_records.append({
                "chunk_id": f"chk_{document_id}_{chunk.chunk_index}",
                "document_id": chunk.document_id,
                "user_id": chunk.user_id,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "content": chunk.content,
                "embedding": emb,
                "metadata": chunk.metadata
            })

        pgvector_client.store_local(document_id, chunk_records)
        logger.info(f"Persisted {len(chunk_records)} vector chunks for document {document_id}")
        return len(chunk_records)

    async def search_similar_chunks(
        self,
        query_embedding: List[float],
        user_id: str,
        document_ids: List[str],
        top_k: int = 5,
        threshold: float = 0.50
    ) -> List[SearchResult]:
        """
        Executes cosine similarity search constrained to user_id and document_ids.
        Score = dot(q, e) / (norm(q)*norm(e))
        """
        results: List[SearchResult] = []
        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        for doc_id in document_ids:
            stored_records = pgvector_client.get_local(doc_id)
            for rec in stored_records:
                if rec["user_id"] != user_id:
                    continue  # Strict tenant isolation

                emb_vec = np.array(rec["embedding"], dtype=np.float32)
                emb_norm = np.linalg.norm(emb_vec)
                if emb_norm == 0:
                    continue

                cosine_sim = float(np.dot(q_vec, emb_vec) / (q_norm * emb_norm))
                if cosine_sim >= threshold:
                    results.append(
                        SearchResult(
                            chunk_id=rec["chunk_id"],
                            document_id=rec["document_id"],
                            user_id=rec["user_id"],
                            page_number=rec["page_number"],
                            chunk_index=rec["chunk_index"],
                            content=rec["content"],
                            similarity_score=round(cosine_sim, 4)
                        )
                    )

        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

vector_repo = VectorRepository()

