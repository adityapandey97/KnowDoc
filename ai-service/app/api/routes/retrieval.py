from fastapi import APIRouter, Depends, status
from app.schemas.chat import SearchRequest, SearchResponse
from app.security.permissions import verify_internal_key
from app.services.retrieval_service import retrieval_service

router = APIRouter(prefix="/internal/v1/retrieval", tags=["Retrieval"])

@router.post("", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def semantic_search(
    request: SearchRequest,
    authorized: bool = Depends(verify_internal_key)
):
    results = await retrieval_service.retrieve_relevant_chunks(
        query=request.query,
        user_id=request.user_id,
        document_ids=request.document_ids,
        top_k=request.top_k,
        threshold=request.threshold
    )

    return SearchResponse(
        results=results,
        query=request.query,
        total_matches=len(results)
    )

