import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.services.retrieval_service import retrieval_service
from app.core.exceptions import ToolExecutionError
from app.core.logging import logger

class DocumentSearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Semantic search query")
    user_id: str = Field(..., description="Tenant ID to enforce isolation")
    document_ids: Optional[List[str]] = Field(default=None, description="Scope search to specific documents")
    top_k: int = Field(default=5, ge=1, le=10, description="Maximum passages to retrieve")

async def search_documents_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent tool: Executes semantic vector retrieval against authorized user documents.
    """
    start_time = time.time()
    try:
        args = DocumentSearchInput(**arguments)
    except Exception as e:
        raise ToolExecutionError(f"Invalid search_documents arguments: {str(e)}")

    results = await retrieval_service.retrieve_relevant_chunks(
        query=args.query,
        user_id=args.user_id,
        document_ids=args.document_ids,
        top_k=args.top_k
    )

    duration_ms = int((time.time() - start_time) * 1000)
    logger.info(f"Tool search_documents executed in {duration_ms}ms (found {len(results)} matches)")

    return {
        "tool": "search_documents",
        "matches_count": len(results),
        "duration_ms": duration_ms,
        "passages": [
            {
                "document_id": r.document_id,
                "document_name": r.document_name,
                "page_number": r.page_number,
                "chunk_id": r.chunk_id,
                "excerpt": r.content[:300],
                "similarity_score": r.similarity_score
            }
            for r in results
        ]
    }

