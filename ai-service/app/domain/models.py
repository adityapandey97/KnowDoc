from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ExtractedPage(BaseModel):
    page_number: int
    text: str
    char_count: int
    is_empty_or_scanned: bool = False

class TextChunk(BaseModel):
    chunk_index: int
    document_id: str
    user_id: str
    page_number: int
    content: str
    token_estimate: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Citation(BaseModel):
    citation_id: str
    document_id: str
    page_number: int
    chunk_id: Optional[str] = None
    similarity_score: float = 0.0
    excerpt: str

class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    user_id: str
    page_number: int
    chunk_index: int
    content: str
    similarity_score: float

class RAGAnswer(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model_used: str = ""

