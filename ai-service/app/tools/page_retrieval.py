import time
from typing import Dict, Any
from pydantic import BaseModel, Field
from app.repositories.vector_repository import vector_repository
from app.core.exceptions import ToolExecutionError
from app.core.logging import logger

class PageRetrievalInput(BaseModel):
    document_id: str = Field(..., description="Target document ID")
    page_number: int = Field(..., ge=1, description="Physical page number to retrieve")
    user_id: str = Field(..., description="Tenant ID to enforce isolation")

async def retrieve_document_page_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent tool: Fetches all chunk passages located on a specific page of an authorized document.
    """
    start_time = time.time()
    try:
        args = PageRetrievalInput(**arguments)
    except Exception as e:
        raise ToolExecutionError(f"Invalid retrieve_document_page arguments: {str(e)}")

    page_chunks = await vector_repository.get_document_page_chunks(
        document_id=args.document_id,
        page_number=args.page_number,
        user_id=args.user_id
    )

    duration_ms = int((time.time() - start_time) * 1000)
    logger.info(
        f"Tool retrieve_document_page executed for doc {args.document_id} "
        f"page {args.page_number} ({len(page_chunks)} chunks found)"
    )

    combined_text = "\n\n".join([c.content for c in page_chunks])

    return {
        "tool": "retrieve_document_page",
        "document_id": args.document_id,
        "page_number": args.page_number,
        "found": len(page_chunks) > 0,
        "page_text": combined_text,
        "duration_ms": duration_ms
    }

