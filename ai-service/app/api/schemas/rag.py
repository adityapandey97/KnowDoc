from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class IngestRequest(BaseModel):
    document_id: str
    user_id: str
    storage_path: str
    chunk_size: int = Field(default=800, ge=100, le=4000)
    chunk_overlap: int = Field(default=150, ge=0, le=1000)

class IngestResponse(BaseModel):
    document_id: str
    status: str
    total_pages: int
    total_chunks: int
    embedding_model: str
    embedding_dimension: int
    processing_duration_ms: int

class ChatMessage(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    user_id: str
    document_ids: List[str] = Field(..., min_items=1)
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.60, ge=0.0, le=1.0)
    conversation_history: List[ChatMessage] = Field(default_factory=list)

class QueryResponseCitation(BaseModel):
    citation_id: str
    document_id: str
    page_number: int
    chunk_id: Optional[str] = None
    similarity_score: float
    excerpt: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[QueryResponseCitation]
    prompt_tokens: int
    completion_tokens: int
    model_used: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    dependencies: Dict[str, Any]

