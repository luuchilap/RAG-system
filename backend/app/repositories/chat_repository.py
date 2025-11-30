"""
Chat message repository for database operations.
Handles CRUD operations for chat message entities.
"""
from typing import List, Optional
from uuid import UUID
import asyncpg
from app.models.chat import ChatMessageCreate, ChatMessageInDB


class ChatMessageRepository:
    """Repository for chat message database operations."""
    
    @staticmethod
    async def create_message(
        connection: asyncpg.Connection,
        user_id: UUID,
        conversation_id: UUID,
        role: str,
        content: str
    ) -> ChatMessageInDB:
        """Create a new chat message in the database."""
        query = """
            INSERT INTO chat_messages (user_id, conversation_id, role, content)
            VALUES ($1, $2, $3, $4)
            RETURNING id, user_id, conversation_id, role, content, timestamp
        """
        row = await connection.fetchrow(
            query,
            user_id,
            conversation_id,
            role,
            content
        )
        return ChatMessageInDB(
            id=row['id'],
            user_id=row['user_id'],
            conversation_id=row['conversation_id'],
            role=row['role'],
            content=row['content'],
            timestamp=row['timestamp']
        )
    
    @staticmethod
    async def get_conversation_history(
        connection: asyncpg.Connection,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 50
    ) -> List[ChatMessageInDB]:
        """Get conversation history for a specific conversation."""
        query = """
            SELECT id, user_id, conversation_id, role, content, timestamp
            FROM chat_messages
            WHERE user_id = $1 AND conversation_id = $2
            ORDER BY timestamp ASC
            LIMIT $3
        """
        rows = await connection.fetch(query, user_id, conversation_id, limit)
        return [
            ChatMessageInDB(
                id=row['id'],
                user_id=row['user_id'],
                conversation_id=row['conversation_id'],
                role=row['role'],
                content=row['content'],
                timestamp=row['timestamp']
            )
            for row in rows
        ]
    
    @staticmethod
    async def get_user_conversations(
        connection: asyncpg.Connection,
        user_id: UUID,
        limit: int = 20
    ) -> List[dict]:
        """Get list of conversations for a user."""
        query = """
            SELECT 
                conversation_id,
                MAX(timestamp) as last_timestamp,
                COUNT(*) as message_count,
                MAX(CASE WHEN role = 'assistant' THEN content END) as last_message
            FROM chat_messages
            WHERE user_id = $1
            GROUP BY conversation_id
            ORDER BY last_timestamp DESC
            LIMIT $2
        """
        rows = await connection.fetch(query, user_id, limit)
        return [
            {
                'conversation_id': row['conversation_id'],
                'last_timestamp': row['last_timestamp'],
                'message_count': row['message_count'],
                'last_message': row['last_message']
            }
            for row in rows
        ]
    
    @staticmethod
    async def delete_conversation(
        connection: asyncpg.Connection,
        user_id: UUID,
        conversation_id: UUID
    ) -> bool:
        """Delete a conversation and all its messages."""
        query = """
            DELETE FROM chat_messages
            WHERE user_id = $1 AND conversation_id = $2
        """
        result = await connection.execute(query, user_id, conversation_id)
        return result == "DELETE"

