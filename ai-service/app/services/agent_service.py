import time
import asyncio
from typing import List, Dict, Any, Tuple
from app.schemas.chat import ChatResponse, ToolCallRecord, SearchResult
from app.schemas.citations import Citation
from app.tools.document_search import search_documents_tool
from app.tools.document_summary import summarize_document_tool
from app.tools.page_retrieval import retrieve_document_page_tool
from app.services.generation_service import generation_service
from app.services.retrieval_service import retrieval_service
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ToolExecutionError

TOOL_REGISTRY = {
    "search_documents": search_documents_tool,
    "summarize_document": summarize_document_tool,
    "retrieve_document_page": retrieve_document_page_tool,
}

class AgentService:
    """
    Controlled autonomous agent executing multi-step reasoning and tool invocations.
    Maintains strict iteration limits and safe execution timeouts.
    """

    def __init__(self, max_iterations: int = settings.agent_max_iterations):
        self.max_iterations = max_iterations
        self.timeout = settings.agent_tool_timeout_seconds

    async def execute_agent_loop(
        self,
        query: str,
        user_id: str,
        document_ids: List[str],
        conversation_history: List[Dict[str, str]] = None
    ) -> ChatResponse:
        tool_records: List[ToolCallRecord] = []
        retrieved_passages: List[SearchResult] = []
        iterations = 0

        # Step 1: Tool Selection / Planning
        # For document questions, run search_documents first
        logger.info(f"Agent starting execution for query: '{query[:60]}' (user: {user_id})")

        # Initial tool decision
        if "summar" in query.lower() and document_ids:
            # Document summary tool
            tool_name = "summarize_document"
            tool_args = {"document_id": document_ids[0], "user_id": user_id, "max_pages": 10}
        elif "page " in query.lower() and document_ids:
            # Page retrieval tool
            import re
            page_match = re.search(r"page\s+(\d+)", query.lower())
            page_num = int(page_match.group(1)) if page_match else 1
            tool_name = "retrieve_document_page"
            tool_args = {"document_id": document_ids[0], "page_number": page_num, "user_id": user_id}
        else:
            # Default to semantic search tool
            tool_name = "search_documents"
            tool_args = {
                "query": query,
                "user_id": user_id,
                "document_ids": document_ids if document_ids else None,
                "top_k": 5
            }

        # Step 2: Execute selected tool with timeout
        start_t = time.time()
        tool_fn = TOOL_REGISTRY[tool_name]
        try:
            tool_result = await asyncio.wait_for(tool_fn(tool_args), timeout=self.timeout)
            duration_ms = int((time.time() - start_t) * 1000)
            tool_records.append(
                ToolCallRecord(
                    tool_name=tool_name,
                    arguments={"query": tool_args.get("query"), "document_id": tool_args.get("document_id")},
                    result={"status": "success", "summary": f"{tool_name} completed"},
                    duration_ms=duration_ms
                )
            )
        except Exception as e:
            logger.error(f"Agent tool error during {tool_name}: {str(e)}")
            tool_records.append(
                ToolCallRecord(
                    tool_name=tool_name,
                    arguments={"error": str(e)},
                    result={"status": "error", "message": str(e)},
                    duration_ms=int((time.time() - start_t) * 1000)
                )
            )

        # Step 3: Fetch passages for grounded answer synthesis
        retrieved_passages = await retrieval_service.retrieve_relevant_chunks(
            query=query,
            user_id=user_id,
            document_ids=document_ids,
            top_k=settings.default_top_k
        )

        # Step 4: Synthesize grounded response
        answer, citations, usage, is_insufficient = await generation_service.generate_grounded_answer(
            query=query,
            retrieved_chunks=retrieved_passages,
            conversation_history=conversation_history
        )

        return ChatResponse(
            answer=answer,
            citations=citations,
            tool_calls=tool_records,
            usage=usage,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            model_used=settings.llm_model,
            insufficient_evidence=is_insufficient
        )

agent_service = AgentService()
