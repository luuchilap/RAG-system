"""
Document repository for database operations.
Handles CRUD operations for document entities.
"""
import json
from typing import List, Optional, Dict, Any
from uuid import UUID
import asyncpg
from app.models.document import DocumentCreate, DocumentInDB


class DocumentRepository:
    """Repository for document database operations."""
    
    @staticmethod
    async def create_document(
        connection: asyncpg.Connection,
        user_id: UUID,
        document_data: DocumentCreate
    ) -> DocumentInDB:
        """Create a new document record in the database."""
        query = """
            INSERT INTO documents (user_id, filename, file_path, file_type, file_size, chunk_count, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
            RETURNING id, user_id, filename, file_path, file_type, file_size, chunk_count, uploaded_at, metadata
        """
        # Convert metadata dict to JSON string for JSONB column
        metadata_json = json.dumps(document_data.metadata) if document_data.metadata else None
        
        row = await connection.fetchrow(
            query,
            user_id,
            document_data.filename,
            document_data.file_path,
            document_data.file_type,
            document_data.file_size,
            document_data.chunk_count,
            metadata_json
        )
        
        # Parse JSONB metadata back to dict (asyncpg returns it as string)
        metadata = row['metadata']
        if isinstance(metadata, str):
            metadata = json.loads(metadata) if metadata else None
        
        return DocumentInDB(
            id=row['id'],
            user_id=row['user_id'],
            filename=row['filename'],
            file_path=row['file_path'],
            file_type=row['file_type'],
            file_size=row['file_size'],
            chunk_count=row['chunk_count'],
            uploaded_at=row['uploaded_at'],
            metadata=metadata
        )
    
    @staticmethod
    async def get_document_by_id(
        connection: asyncpg.Connection,
        document_id: UUID,
        user_id: UUID
    ) -> Optional[DocumentInDB]:
        """Get a document by ID (ensuring it belongs to the user)."""
        query = """
            SELECT id, user_id, filename, file_path, file_type, file_size, chunk_count, uploaded_at, metadata
            FROM documents
            WHERE id = $1 AND user_id = $2
        """
        row = await connection.fetchrow(query, document_id, user_id)
        if not row:
            return None
        
        # Parse JSONB metadata back to dict (asyncpg returns it as string)
        metadata = row['metadata']
        if isinstance(metadata, str):
            metadata = json.loads(metadata) if metadata else None
        
        return DocumentInDB(
            id=row['id'],
            user_id=row['user_id'],
            filename=row['filename'],
            file_path=row['file_path'],
            file_type=row['file_type'],
            file_size=row['file_size'],
            chunk_count=row['chunk_count'],
            uploaded_at=row['uploaded_at'],
            metadata=metadata
        )
    
    @staticmethod
    async def get_user_documents(
        connection: asyncpg.Connection,
        user_id: UUID,
        limit: int = 100
    ) -> List[DocumentInDB]:
        """Get all documents for a user."""
        query = """
            SELECT id, user_id, filename, file_path, file_type, file_size, chunk_count, uploaded_at, metadata
            FROM documents
            WHERE user_id = $1
            ORDER BY uploaded_at DESC
            LIMIT $2
        """
        rows = await connection.fetch(query, user_id, limit)
        result = []
        for row in rows:
            # Parse JSONB metadata back to dict (asyncpg returns it as string)
            metadata = row['metadata']
            if isinstance(metadata, str):
                metadata = json.loads(metadata) if metadata else None
            
            result.append(
                DocumentInDB(
                    id=row['id'],
                    user_id=row['user_id'],
                    filename=row['filename'],
                    file_path=row['file_path'],
                    file_type=row['file_type'],
                    file_size=row['file_size'],
                    chunk_count=row['chunk_count'],
                    uploaded_at=row['uploaded_at'],
                    metadata=metadata
                )
            )
        return result
    
    @staticmethod
    async def delete_document(
        connection: asyncpg.Connection,
        document_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a document (ensuring it belongs to the user)."""
        query = """
            DELETE FROM documents
            WHERE id = $1 AND user_id = $2
        """
        result = await connection.execute(query, document_id, user_id)
        return result == "DELETE"
    
    @staticmethod
    async def update_document_metadata(
        connection: asyncpg.Connection,
        document_id: UUID,
        user_id: UUID,
        metadata: Dict[str, Any]
    ) -> Optional[DocumentInDB]:
        """Update document metadata."""
        query = """
            UPDATE documents
            SET metadata = $1::jsonb
            WHERE id = $2 AND user_id = $3
            RETURNING id, user_id, filename, file_path, file_type, file_size, chunk_count, uploaded_at, metadata
        """
        # Convert metadata dict to JSON string for JSONB column
        metadata_json = json.dumps(metadata) if metadata else None
        
        row = await connection.fetchrow(query, metadata_json, document_id, user_id)
        if not row:
            return None
        
        # Parse JSONB metadata back to dict (asyncpg returns it as string)
        metadata = row['metadata']
        if isinstance(metadata, str):
            metadata = json.loads(metadata) if metadata else None
        
        return DocumentInDB(
            id=row['id'],
            user_id=row['user_id'],
            filename=row['filename'],
            file_path=row['file_path'],
            file_type=row['file_type'],
            file_size=row['file_size'],
            chunk_count=row['chunk_count'],
            uploaded_at=row['uploaded_at'],
            metadata=metadata
        )

