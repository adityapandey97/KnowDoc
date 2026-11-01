from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.schemas.citations import Citation

class ChatMessage(BaseModel):
    role: str = Field(..., description="user, assistant, or system")
    content: str

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    user_id: str
    conversation_id: Optional[str] = None
    document_ids: List[str] = Field(default_factory=list)
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    use_agent: bool = Field(default=False, description="Enable autonomous agent tool execution")
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    top_k: int = Field(default=5, ge=1, le=20)

class ToolCallRecord(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    duration_ms: int

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    tool_calls: List[ToolCallRecord] = Field(default_factory=list)
    usage: Dict[str, int] = Field(default_factory=dict)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model_used: str
    insufficient_evidence: bool = False

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    user_id: str
    document_ids: List[str] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.50, ge=0.0, le=1.0)

class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    document_name: Optional[str] = None
    user_id: str
    page_number: int
    chunk_index: int
    content: str
    similarity_score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total_matches: int

class SummarizeRequest(BaseModel):
    document_id: str
    user_id: str
    max_pages: int = Field(default=10, ge=1, le=100)

class SummarizeResponse(BaseModel):
    document_id: str
    summary: str
    key_topics: List[str] = Field(default_factory=list)
    pages_analyzed: int
