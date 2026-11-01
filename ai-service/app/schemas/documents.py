from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class IngestDocumentRequest(BaseModel):
    document_id: str = Field(..., description="Unique document ID (UUID/string)")
    user_id: str = Field(..., description="Owner tenant ID")
    storage_path: str = Field(..., description="Filesystem or blob store location of the raw PDF")
    document_name: Optional[str] = Field(default=None, description="Original filename")
    chunk_size: int = Field(default=800, ge=100, le=4000)
    chunk_overlap: int = Field(default=150, ge=0, le=1000)

class IngestDocumentResponse(BaseModel):
    document_id: str
    status: str
    total_pages: int
    total_chunks: int
    processing_duration_ms: int
    embedding_model: str
    embedding_dimension: int
    is_scanned: bool = False

class ExtractedPage(BaseModel):
    page_number: int
    text: str
    char_count: int
    is_empty_or_scanned: bool = False

class DocumentChunk(BaseModel):
    chunk_index: int
    document_id: str
    document_name: Optional[str] = None
    user_id: str
    page_number: int
    content: str
    token_estimate: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

