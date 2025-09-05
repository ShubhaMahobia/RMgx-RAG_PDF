from pydantic import BaseModel
from typing import List, Optional


class DeleteRequest(BaseModel):
    """Request model for deleting files."""
    s3_key: str  # The S3 key of the file to delete

class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    message: str
    deleted_file: str
    s3_key: str
    success: bool

class ResetRequest(BaseModel):
    """Request model for resetting the entire index."""
    confirm: bool = False  # Safety flag to confirm reset operation

class ResetResponse(BaseModel):
    """Response model for reset operations."""
    message: str
    s3_files_deleted: int
    pinecone_vectors_deleted: int
    success: bool
    details: dict