from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    retriever_type: str = "hybrid"  # "semantic" | "keyword" | "hybrid"

class Citation(BaseModel):
    """Citation metadata for source documents."""
    page_number: Optional[int] = None
    pdf_name: str  # Original PDF filename (not UUID)
    chunk_text: str  # The actual text chunk that was used
    confidence_score: Optional[float] = None  # How relevant this chunk is to the query

class ChatResponse(BaseModel):
    """Response with answer and citations."""
    query: str
    answer: str
    citations: List[Citation]
    total_sources: int
    processing_time_ms: Optional[float] = None
