from pydantic import BaseModel, Field
from typing import Optional

class Citation(BaseModel):
    citation_id: str
    document_id: str
    document_name: Optional[str] = None
    page_number: int = Field(..., ge=1)
    chunk_id: Optional[str] = None
    excerpt: str = Field(..., description="Verbatim passage from the referenced document")
    similarity_score: float = Field(default=0.0, ge=0.0, le=1.0)

