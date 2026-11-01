from typing import List, Dict, Any
from app.rag.ingestion.pipeline import ingestion_pipeline
from app.rag.retrieval.retriever import retriever
from app.rag.generation.generator import generator
from app.domain.models import RAGAnswer

class RAGService:
    """
    High-level domain service orchestrating RAG indexing and conversational queries.
    """

    async def index_document(
        self,
        document_id: str,
        user_id: str,
        storage_path: str,
        chunk_size: int = 800,
        chunk_overlap: int = 150
    ) -> Dict[str, Any]:
        return await ingestion_pipeline.ingest_document(
            document_id=document_id,
            user_id=user_id,
            storage_path=storage_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    async def answer_query(
        self,
        query: str,
        user_id: str,
        document_ids: List[str],
        top_k: int = 5,
        threshold: float = 0.50,
        conversation_history: List[Dict[str, str]] = None
    ) -> RAGAnswer:
        # 1. Retrieve top-k passages matching query constrained to authorized documents
        search_results = await retriever.retrieve(
            query=query,
            user_id=user_id,
            document_ids=document_ids,
            top_k=top_k,
            threshold=threshold
        )

        # 2. Generate grounded answer with citations
        return await generator.generate_answer(
            query=query,
            search_results=search_results,
            conversation_history=conversation_history
        )

rag_service = RAGService()

