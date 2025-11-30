"""
Document models for database operations and API validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class DocumentBase(BaseModel):
    """Base document model."""
    filename: str = Field(..., min_length=1, max_length=255, description="Document filename")
    file_type: str = Field(..., description="Document file type")


class DocumentCreate(DocumentBase):
    """Model for creating a new document record."""
    file_path: str = Field(..., description="Path to the uploaded file")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    chunk_count: int = Field(..., ge=0, description="Number of text chunks")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Document metadata")


class DocumentInDB(DocumentBase):
    """Document model as stored in the database."""
    id: UUID
    user_id: UUID
    file_path: str
    file_size: Optional[int] = None
    chunk_count: Optional[int] = None
    uploaded_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DocumentResponse(DocumentBase):
    """Document model for API responses."""
    id: UUID
    file_size: Optional[int] = None
    chunk_count: Optional[int] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: UUID
    filename: str
    chunk_count: int
    status: str

