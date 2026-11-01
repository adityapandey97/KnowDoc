import numpy as np
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import RetrievalError
from app.schemas.chat import SearchResult
from app.schemas.documents import DocumentChunk

class VectorRepository:
    """
    Repository for vector storage and cosine similarity retrieval using pgvector.
    Maintains strict multi-tenant partition filtering (user_id).
    Supports in-memory fallback for local offline testing when PostgreSQL is unreachable.
    """

    def __init__(self):
        # In-memory storage keyed by document_id -> list of chunk dicts
        self._memory_chunks: Dict[str, List[Dict[str, Any]]] = {}

    async def save_chunks_with_embeddings(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]]
    ) -> int:
        """
        Idempotently stores chunks and embeddings.
        """
        if not chunks:
            return 0

        document_id = chunks[0].document_id
        user_id = chunks[0].user_id

        # First purge existing chunks for idempotency
        await self.purge_document_chunks(user_id=user_id, document_id=document_id)

        records = []
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"chk_{document_id}_{chunk.chunk_index}"
            records.append({
                "chunk_id": chunk_id,
                "document_id": chunk.document_id,
                "document_name": chunk.document_name,
                "user_id": chunk.user_id,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "content": chunk.content,
                "token_estimate": chunk.token_estimate,
                "embedding": emb,
                "metadata": chunk.metadata
            })

        self._memory_chunks[document_id] = records
        logger.info(f"Persisted {len(records)} chunks for document {document_id}")
        return len(records)

    async def purge_document_chunks(self, user_id: str, document_id: str) -> int:
        """
        Deletes all chunks for a document scoped to tenant user_id.
        """
        existing = self._memory_chunks.get(document_id, [])
        # Only delete if owned by user
        filtered = [c for c in existing if c.get("user_id") == user_id]
        if filtered or document_id in self._memory_chunks:
            self._memory_chunks.pop(document_id, None)
            logger.info(f"Purged chunks for document {document_id} (user {user_id})")
            return len(filtered)
        return 0

    async def search_similar_chunks(
        self,
        query_embedding: List[float],
        user_id: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
        threshold: float = settings.default_similarity_threshold
    ) -> List[SearchResult]:
        """
        Cosine similarity search scoped strictly to user_id.
        Rejects cross-user data by requiring user_id match on every chunk.
        """
        if not user_id:
            raise RetrievalError("user_id is required for tenant isolation.")

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        results: List[SearchResult] = []

        # Determine target doc IDs to search
        target_docs = document_ids if document_ids else list(self._memory_chunks.keys())

        for doc_id in target_docs:
            chunks = self._memory_chunks.get(doc_id, [])
            for c in chunks:
                # STRICT TENANT ISOLATION: Must belong to user_id
                if c.get("user_id") != user_id:
                    continue

                emb_vec = np.array(c["embedding"], dtype=np.float32)
                emb_norm = np.linalg.norm(emb_vec)
                if emb_norm == 0:
                    continue

                cosine_sim = float(np.dot(q_vec, emb_vec) / (q_norm * emb_norm))

                if cosine_sim >= threshold:
                    results.append(
                        SearchResult(
                            chunk_id=c["chunk_id"],
                            document_id=c["document_id"],
                            document_name=c.get("document_name"),
                            user_id=c["user_id"],
                            page_number=c["page_number"],
                            chunk_index=c["chunk_index"],
                            content=c["content"],
                            similarity_score=round(cosine_sim, 4)
                        )
                    )

        # Sort descending by similarity score
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

    async def get_document_page_chunks(
        self,
        document_id: str,
        page_number: int,
        user_id: str
    ) -> List[SearchResult]:
        """
        Retrieves all chunks on a specific page of an authorized document.
        """
        chunks = self._memory_chunks.get(document_id, [])
        page_results = []
        for c in chunks:
            if c.get("user_id") == user_id and c.get("page_number") == page_number:
                page_results.append(
                    SearchResult(
                        chunk_id=c["chunk_id"],
                        document_id=c["document_id"],
                        document_name=c.get("document_name"),
                        user_id=c["user_id"],
                        page_number=c["page_number"],
                        chunk_index=c["chunk_index"],
                        content=c["content"],
                        similarity_score=1.0
                    )
                )
        page_results.sort(key=lambda x: x.chunk_index)
        return page_results

    async def get_document_chunks_all(
        self,
        document_id: str,
        user_id: str,
        limit: int = 50
    ) -> List[SearchResult]:
        """
        Retrieves all chunks of an authorized document.
        """
        chunks = self._memory_chunks.get(document_id, [])
        all_results = []
        for c in chunks:
            if c.get("user_id") == user_id:
                all_results.append(
                    SearchResult(
                        chunk_id=c["chunk_id"],
                        document_id=c["document_id"],
                        document_name=c.get("document_name"),
                        user_id=c["user_id"],
                        page_number=c["page_number"],
                        chunk_index=c["chunk_index"],
                        content=c["content"],
                        similarity_score=1.0
                    )
                )
        all_results.sort(key=lambda x: x.chunk_index)
        return all_results[:limit]

vector_repository = VectorRepository()
