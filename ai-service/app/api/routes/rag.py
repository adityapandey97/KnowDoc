from fastapi import APIRouter, Depends, status
from app.api.schemas.rag import (
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    QueryResponseCitation
)
from app.security.internal_auth import verify_internal_key
from app.services.rag_service import rag_service

router = APIRouter(prefix="/internal/v1/rag", tags=["RAG"])

@router.post("/index", response_model=IngestResponse, status_code=status.HTTP_200_OK)
async def index_document(
    request: IngestRequest,
    authorized: bool = Depends(verify_internal_key)
):
    result = await rag_service.index_document(
        document_id=request.document_id,
        user_id=request.user_id,
        storage_path=request.storage_path,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap
    )
    return IngestResponse(**result)

@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_knowledge_base(
    request: QueryRequest,
    authorized: bool = Depends(verify_internal_key)
):
    history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
    
    rag_answer = await rag_service.answer_query(
        query=request.query,
        user_id=request.user_id,
        document_ids=request.document_ids,
        top_k=request.top_k,
        threshold=request.similarity_threshold,
        conversation_history=history_dicts
    )

    citations = [
        QueryResponseCitation(
            citation_id=c.citation_id,
            document_id=c.document_id,
            page_number=c.page_number,
            chunk_id=c.chunk_id,
            similarity_score=c.similarity_score,
            excerpt=c.excerpt
        )
        for c in rag_answer.citations
    ]

    return QueryResponse(
        answer=rag_answer.answer,
        citations=citations,
        prompt_tokens=rag_answer.prompt_tokens,
        completion_tokens=rag_answer.completion_tokens,
        model_used=rag_answer.model_used
    )

