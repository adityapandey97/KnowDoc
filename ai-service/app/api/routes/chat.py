from fastapi import APIRouter, Depends, status
from app.schemas.chat import ChatRequest, ChatResponse
from app.security.permissions import verify_internal_key
from app.services.generation_service import generation_service
from app.services.retrieval_service import retrieval_service
from app.services.conversation_service import conversation_service
from app.services.agent_service import agent_service
from app.core.config import settings

router = APIRouter(prefix="/internal/v1", tags=["Chat"])

async def execute_chat(request: ChatRequest) -> ChatResponse:
    # Prepare bounded history
    history = conversation_service.prepare_bounded_history(
        history=request.conversation_history,
        current_query=request.query
    )

    # If autonomous agent tool calling is requested
    if request.use_agent:
        return await agent_service.execute_agent_loop(
            query=request.query,
            user_id=request.user_id,
            document_ids=request.document_ids,
            conversation_history=history
        )

    # Standard Direct Grounded RAG
    passages = await retrieval_service.retrieve_relevant_chunks(
        query=request.query,
        user_id=request.user_id,
        document_ids=request.document_ids,
        top_k=request.top_k or settings.default_top_k
    )

    answer, citations, usage, is_insufficient = await generation_service.generate_grounded_answer(
        query=request.query,
        retrieved_chunks=passages,
        conversation_history=history,
        temperature=request.temperature
    )

    return ChatResponse(
        answer=answer,
        citations=citations,
        tool_calls=[],
        usage=usage,
        prompt_tokens=usage.get("prompt_tokens", 0),
        completion_tokens=usage.get("completion_tokens", 0),
        model_used=settings.llm_model,
        insufficient_evidence=is_insufficient
    )

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(
    request: ChatRequest,
    authorized: bool = Depends(verify_internal_key)
):
    return await execute_chat(request)

@router.post("/rag/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def rag_query_alias(
    request: ChatRequest,
    authorized: bool = Depends(verify_internal_key)
):
    """Backward compatibility alias for Phase 1 Express callers."""
    return await execute_chat(request)
