import time
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.repositories.vector_repository import vector_repository
from app.core.exceptions import ToolExecutionError
from app.core.logging import logger

class DocumentSummaryInput(BaseModel):
    document_id: str = Field(..., description="Target document ID to summarize")
    user_id: str = Field(..., description="Tenant ID to enforce isolation")
    max_pages: int = Field(default=10, ge=1, le=50, description="Max pages to scan")

async def summarize_document_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent tool: Aggregates initial chunk passages to construct a document executive overview.
    """
    start_time = time.time()
    try:
        args = DocumentSummaryInput(**arguments)
    except Exception as e:
        raise ToolExecutionError(f"Invalid summarize_document arguments: {str(e)}")

    chunks = await vector_repository.get_document_chunks_all(
        document_id=args.document_id,
        user_id=args.user_id,
        limit=args.max_pages * 3
    )

    if not chunks:
        return {
            "tool": "summarize_document",
            "document_id": args.document_id,
            "summary": "No accessible content found for this document.",
            "pages_analyzed": 0,
            "duration_ms": int((time.time() - start_time) * 1000)
        }

    # Extract distinct topics / opening content
    sample_text = " ".join([c.content for c in chunks[:5]])[:1000]
    duration_ms = int((time.time() - start_time) * 1000)
    logger.info(f"Tool summarize_document executed in {duration_ms}ms")

    return {
        "tool": "summarize_document",
        "document_id": args.document_id,
        "document_name": chunks[0].document_name,
        "summary": f"Document overview based on {len(chunks)} indexed passages: {sample_text}...",
        "pages_analyzed": len(set(c.page_number for c in chunks)),
        "duration_ms": duration_ms
    }

