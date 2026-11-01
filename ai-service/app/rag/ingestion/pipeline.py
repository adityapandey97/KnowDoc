import time
from typing import Dict, Any
from app.rag.parsing.parser import pdf_parser
from app.rag.chunking.chunker import RecursiveChunker
from app.rag.embeddings.embedding_service import get_embedding_provider
from app.repositories.vector_repo import vector_repo
from app.core.logging import logger

class IngestionPipeline:
    """
    Executes the 10-step document ingestion workflow:
    extraction -> chunking -> batch embedding -> idempotent persistence.
    """

    async def ingest_document(
        self,
        document_id: str,
        user_id: str,
        storage_path: str,
        chunk_size: int = 800,
        chunk_overlap: int = 150
    ) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Starting ingestion pipeline for doc: {document_id}, user: {user_id}")

        # 1. Parse PDF pages
        pages = pdf_parser.parse(storage_path)
        total_pages = len(pages)

        # 2. Chunk text preserving page numbers
        chunker = RecursiveChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = chunker.chunk_pages(pages, document_id=document_id, user_id=user_id)
        total_chunks = len(chunks)

        if total_chunks == 0:
            logger.warn(f"Document {document_id} generated 0 chunks (empty or unscanned).")
            return {
                "document_id": document_id,
                "status": "ready",
                "total_pages": total_pages,
                "total_chunks": 0,
                "embedding_model": "none",
                "embedding_dimension": 0,
                "processing_duration_ms": int((time.time() - start_time) * 1000)
            }

        # 3. Generate batch embeddings
        embedder = get_embedding_provider()
        chunk_texts = [c.content for c in chunks]
        embeddings = await embedder.embed_texts(chunk_texts)

        # 4. Clean previous runs (idempotency) and persist new vectors
        await vector_repo.purge_document_chunks(user_id=user_id, document_id=document_id)
        await vector_repo.save_chunks_with_embeddings(chunks=chunks, embeddings=embeddings)

        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"Successfully indexed document {document_id}: "
            f"{total_pages} pages, {total_chunks} chunks in {duration_ms}ms"
        )

        return {
            "document_id": document_id,
            "status": "ready",
            "total_pages": total_pages,
            "total_chunks": total_chunks,
            "embedding_model": getattr(embedder, "model", "mock"),
            "embedding_dimension": embedder.dimension,
            "processing_duration_ms": duration_ms
        }

ingestion_pipeline = IngestionPipeline()

