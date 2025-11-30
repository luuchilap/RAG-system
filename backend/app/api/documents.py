"""
Document API endpoints.
Handles document upload, retrieval, and management.
"""
import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List
import asyncpg
from uuid import UUID

from app.services.document_service import DocumentService
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.document import DocumentResponse, DocumentUploadResponse
from app.repositories.document_repository import DocumentRepository


router = APIRouter()
document_service = DocumentService()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    summary="Upload and process a document",
    description="Upload a document (PDF, TXT, MD, or DOCX) for processing and indexing."
)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    current_user: dict = Depends(get_current_user),
    connection: asyncpg.Connection = Depends(get_db)
):
    """
    Upload a document for processing.
    
    The document will be:
    1. Saved to disk
    2. Text extracted
    3. Split into chunks
    4. Embedded and indexed in FAISS
    5. Metadata stored in database
    """
    # Validate file type
    allowed_extensions = [".pdf", ".txt", ".md", ".docx"]
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Process document
    try:
        user_id = UUID(current_user["id"])
        result = await document_service.process_document(file, user_id, connection)
        return DocumentUploadResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get(
    "/",
    response_model=dict,
    summary="Get user's documents",
    description="Retrieve a list of all documents uploaded by the current user."
)
async def get_documents(
    current_user: dict = Depends(get_current_user),
    connection: asyncpg.Connection = Depends(get_db)
):
    """
    Get all documents for the current user.
    """
    try:
        user_id = UUID(current_user["id"])
        documents = await document_service.get_user_documents(connection, user_id)
        
        # Convert to response format
        document_responses = [
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                chunk_count=doc.chunk_count,
                uploaded_at=doc.uploaded_at
            )
            for doc in documents
        ]
        
        return {"documents": document_responses}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}"
        )


@router.delete(
    "/{document_id}",
    response_model=dict,
    summary="Delete a document",
    description="Delete a document and its associated data."
)
async def delete_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    connection: asyncpg.Connection = Depends(get_db)
):
    """
    Delete a document.
    """
    try:
        user_id = UUID(current_user["id"])
        deleted = await document_service.delete_document(
            connection, document_id, user_id
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied"
            )
        
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )

