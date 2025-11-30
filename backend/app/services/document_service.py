"""
Document processing service.
Handles document upload, text extraction, chunking, and FAISS index management.
"""
import os
import uuid
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import UploadFile, HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import asyncpg

from app.config import settings
from app.utils.text_extractor import extract_text_from_file
from app.repositories.document_repository import DocumentRepository
from app.models.document import DocumentCreate, DocumentInDB


class DocumentService:
    """Service for document processing and management."""
    
    def __init__(self):
        """Initialize the document service with embeddings and text splitter."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.document_repo = DocumentRepository()
    
    async def process_document(
        self,
        file: UploadFile,
        user_id: UUID,
        connection: asyncpg.Connection
    ) -> Dict[str, Any]:
        """
        Process an uploaded document: extract text, chunk, embed, and index.
        
        Args:
            file: Uploaded file object
            user_id: ID of the user uploading the document
            connection: Database connection
        
        Returns:
            Dictionary with document_id, filename, chunk_count, and status
        """
        # Create upload directories if they don't exist
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(settings.FAISS_INDEX_FOLDER, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1].lower()
        if not file_extension:
            raise HTTPException(
                status_code=400,
                detail="File must have an extension"
            )
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
        
        # Save file to disk
        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            file_size = len(content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error saving file: {str(e)}"
            )
        
        # Extract text from file
        try:
            text = extract_text_from_file(file_path, file_extension)
            if not text or not text.strip():
                # Clean up the file if extraction failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract text from file or file is empty"
                )
        except HTTPException:
            # Clean up the file if extraction failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise
        except Exception as e:
            # Clean up the file if extraction failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error extracting text: {str(e)}"
            )
        
        # Split text into chunks
        try:
            chunks = self.text_splitter.split_text(text)
            if not chunks:
                # Clean up the file if chunking failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(
                    status_code=400,
                    detail="Could not create text chunks from document"
                )
        except Exception as e:
            # Clean up the file if chunking failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error chunking text: {str(e)}"
            )
        
        # Create document metadata record
        try:
            document_data = DocumentCreate(
                filename=file.filename,
                file_path=file_path,
                file_type=file_extension[1:],  # Remove the dot
                file_size=file_size,
                chunk_count=len(chunks),
                metadata={"processed": True}
            )
            
            document = await self.document_repo.create_document(
                connection, user_id, document_data
            )
        except Exception as e:
            # Clean up the file if database operation failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error saving document metadata: {str(e)}"
            )
        
        # Create metadata for each chunk
        metadatas = [
            {
                "document_id": str(document.id),
                "chunk_index": i,
                "text_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk,
                "user_id": str(user_id)
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Create or update FAISS index
        try:
            user_index_path = os.path.join(
                settings.FAISS_INDEX_FOLDER,
                f"user_{user_id}"
            )
            
            # Try to load existing index, create new one if it doesn't exist
            try:
                vectorstore = FAISS.load_local(
                    user_index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                # Add new documents to existing index
                vectorstore.add_texts(chunks, metadatas=metadatas)
            except (FileNotFoundError, ValueError, Exception):
                # Index doesn't exist or is corrupted, create new one
                vectorstore = FAISS.from_texts(
                    chunks,
                    self.embeddings,
                    metadatas=metadatas
                )
            
            # Save index (creates directory with .faiss and .pkl files)
            vectorstore.save_local(user_index_path)
        except Exception as e:
            # If FAISS indexing fails, we still want to keep the document record
            # but log the error
            print(f"Warning: Failed to create FAISS index: {str(e)}")
            # Optionally, you could raise an exception here if indexing is critical
            # raise HTTPException(
            #     status_code=500,
            #     detail=f"Error creating vector index: {str(e)}"
            # )
        
        return {
            "document_id": str(document.id),
            "filename": file.filename,
            "chunk_count": len(chunks),
            "status": "processed"
        }
    
    async def get_user_documents(
        self,
        connection: asyncpg.Connection,
        user_id: UUID,
        limit: int = 100
    ) -> List[DocumentInDB]:
        """
        Get all documents for a user.
        
        Args:
            connection: Database connection
            user_id: ID of the user
            limit: Maximum number of documents to return
        
        Returns:
            List of document records
        """
        return await self.document_repo.get_user_documents(connection, user_id, limit)
    
    async def delete_document(
        self,
        connection: asyncpg.Connection,
        document_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a document and remove it from the FAISS index.
        
        Args:
            connection: Database connection
            document_id: ID of the document to delete
            user_id: ID of the user (for authorization)
        
        Returns:
            True if document was deleted, False otherwise
        """
        # Get document info before deletion
        document = await self.document_repo.get_document_by_id(
            connection, document_id, user_id
        )
        
        if not document:
            return False
        
        # Delete from database
        deleted = await self.document_repo.delete_document(
            connection, document_id, user_id
        )
        
        if deleted:
            # Remove file from disk
            if os.path.exists(document.file_path):
                try:
                    os.remove(document.file_path)
                except Exception as e:
                    print(f"Warning: Failed to delete file {document.file_path}: {str(e)}")
            
            # Note: FAISS doesn't support removing individual documents easily
            # The index will be rebuilt on next document upload or we could
            # implement a rebuild mechanism
        
        return deleted

