"""
Chat service for handling OpenAI API integration and streaming responses.
"""
from typing import AsyncGenerator, List, Optional
from uuid import UUID
from openai import AsyncOpenAI
from fastapi import HTTPException
from app.config import settings
from app.repositories.chat_repository import ChatMessageRepository
from app.services.rag_service import RAGService
import asyncpg


class ChatService:
    """Service for chat operations with OpenAI API."""
    
    def __init__(self):
        """Initialize the OpenAI client and RAG service."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.repository = ChatMessageRepository()
        self.rag_service = RAGService()
    
    async def create_message(
        self,
        connection: asyncpg.Connection,
        user_id: UUID,
        conversation_id: UUID,
        role: str,
        content: str
    ) -> dict:
        """
        Create a new chat message in the database.
        
        Args:
            connection: Database connection
            user_id: User ID
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
        
        Returns:
            Dictionary containing the created message
        """
        message = await self.repository.create_message(
            connection, user_id, conversation_id, role, content
        )
        return {
            "id": str(message.id),
            "user_id": str(message.user_id),
            "conversation_id": str(message.conversation_id),
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.isoformat()
        }
    
    async def get_conversation_history(
        self,
        connection: asyncpg.Connection,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 50
    ) -> List[dict]:
        """
        Get conversation history from the database.
        
        Args:
            connection: Database connection
            user_id: User ID
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of message dictionaries
        """
        messages = await self.repository.get_conversation_history(
            connection, user_id, conversation_id, limit
        )
        return [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    
    async def get_user_conversations(
        self,
        connection: asyncpg.Connection,
        user_id: UUID,
        limit: int = 20
    ) -> List[dict]:
        """
        Get list of conversations for a user.
        
        Args:
            connection: Database connection
            user_id: User ID
            limit: Maximum number of conversations to retrieve
        
        Returns:
            List of conversation dictionaries
        """
        conversations = await self.repository.get_user_conversations(
            connection, user_id, limit
        )
        return [
            {
                "conversation_id": str(conv["conversation_id"]),
                "last_timestamp": conv["last_timestamp"].isoformat() if conv["last_timestamp"] else None,
                "message_count": conv["message_count"],
                "last_message": conv["last_message"]
            }
            for conv in conversations
        ]
    
    async def generate_stream(
        self,
        messages: List[dict],
        model: str = "gpt-4o-mini"
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from OpenAI.
        
        Args:
            messages: List of message dictionaries formatted for OpenAI API
            model: OpenAI model to use (default: gpt-4o-mini)
        
        Yields:
            Content chunks as they arrive from OpenAI
        
        Raises:
            HTTPException: If OpenAI API call fails
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=0.7,
            )
            
            async for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI API error: {str(e)}"
            )
    
    def format_messages_for_openai(
        self,
        history: List[dict]
    ) -> List[dict]:
        """
        Format conversation history for OpenAI API.
        
        Args:
            history: List of message dictionaries from database
        
        Returns:
            List of messages formatted for OpenAI API
        """
        return [
            {
                "role": msg["role"],
                "content": msg["content"]
            }
            for msg in history
        ]
    
    def _create_system_message(self, rag_results: List[dict]) -> str:
        """
        Create a system message with document context if available.
        
        Args:
            rag_results: List of RAG retrieval results
        
        Returns:
            System message string
        """
        if not rag_results:
            return "You are a helpful assistant. Respond concisely and accurately to the user's questions."
        
        # Format document context
        context_parts = []
        for i, result in enumerate(rag_results, 1):
            text = result.get("text", "")
            metadata = result.get("metadata", {})
            doc_id = metadata.get("document_id", "Unknown")
            chunk_index = metadata.get("chunk_index", "")
            
            context_parts.append(f"[Document {doc_id[:8]}... - Chunk {chunk_index}]\n{text}")
        
        context_str = "\n\n".join(context_parts)
        
        return f"""You are a helpful assistant with access to the following document context. 
Use this information to answer the user's questions accurately and cite the source when possible.
If the documents don't contain relevant information, answer based on your knowledge but make it clear you're not using the document context.

DOCUMENT CONTEXT:
{context_str}

Answer the user's questions based on the above context when relevant, or use your general knowledge otherwise."""
    
    async def generate_response_with_rag(
        self,
        user_id: UUID,
        query: str,
        conversation_history: List[dict],
        model: str = "gpt-4o-mini",
        top_k: int = 3
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response with RAG context.
        
        Args:
            user_id: User ID for document retrieval
            query: User's query message
            conversation_history: Previous conversation messages
            model: OpenAI model to use
            top_k: Number of document chunks to retrieve
        
        Yields:
            Content chunks as they arrive from OpenAI
        """
        # Retrieve relevant documents using RAG
        rag_results = await self.rag_service.query_documents(
            user_id, query, top_k=top_k
        )
        
        # Create system message with document context
        system_message = self._create_system_message(rag_results)
        
        # Format messages for OpenAI (system message + conversation history)
        formatted_messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        for msg in conversation_history:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Generate streaming response
        async for chunk in self.generate_stream(formatted_messages, model):
            yield chunk

