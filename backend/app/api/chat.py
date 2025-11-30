"""
Chat API endpoints.
Handles chat messages, streaming responses, and conversation history.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Optional, AsyncGenerator
from uuid import UUID
import asyncpg
from app.models.chat import ChatRequest, ChatMessageResponse, ConversationResponse
from app.services.chat_service import ChatService
from app.repositories.chat_repository import ChatMessageRepository
from app.database import get_db
from app.middleware.auth import get_current_user

router = APIRouter()
chat_service = ChatService()


@router.post("/", response_model=dict)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    connection: asyncpg.Connection = Depends(get_db)
):
    """
    Send a chat message and receive a streaming AI response.
    
    **Note:** This endpoint streams responses using Server-Sent Events (SSE).
    The response will be streamed token-by-token as the AI generates it.
    """
    from uuid import UUID, uuid4
    
    # Create a new conversation if not provided
    conversation_id = chat_request.conversation_id
    if not conversation_id:
        conversation_id = uuid4()
    
    user_id = UUID(current_user["id"])
    
    # Save user message to database
    await chat_service.create_message(
        connection, user_id, conversation_id, "user", chat_request.message
    )
    
    # Get conversation history
    history = await chat_service.get_conversation_history(
        connection, user_id, conversation_id
    )
    
    # Create streaming response with RAG
    # Note: We need to get a new connection for saving the assistant message
    # because the original connection may be released before streaming completes
    from app.database import db
    
    async def generate() -> AsyncGenerator[str, None]:
        collected_content = ""
        try:
            # Use RAG-enhanced response generation
            async for content_chunk in chat_service.generate_response_with_rag(
                user_id, chat_request.message, history
            ):
                # Format as SSE
                yield f"data: {content_chunk}\n\n"
                collected_content += content_chunk
            
            # Save assistant response to database after streaming completes
            # Get a new connection from the pool for this operation
            save_connection = await db.get_connection()
            try:
                await chat_service.create_message(
                    save_connection, user_id, conversation_id, "assistant", collected_content
                )
            finally:
                await db.release_connection(save_connection)
        except Exception as e:
            # Send error as SSE event
            yield f"data: [ERROR] {str(e)}\n\n"
            raise
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-Id": str(conversation_id)
        }
    )


@router.get("/history", response_model=dict)
async def get_history(
    conversation_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    connection: asyncpg.Connection = Depends(get_db)
):
    """
    Get chat history for a specific conversation or list all conversations.
    
    **Query Parameters:**
    - `conversation_id` (optional): Get messages for a specific conversation
    - If omitted, returns list of all user's conversations
    """
    from uuid import UUID
    user_id = UUID(current_user["id"])
    
    if conversation_id:
        # Get messages for specific conversation
        messages = await chat_service.get_conversation_history(
            connection, user_id, conversation_id
        )
        return {
            "conversation_id": str(conversation_id),
            "messages": messages
        }
    else:
        # Get all conversations for user
        conversations = await chat_service.get_user_conversations(connection, user_id)
        return {
            "conversations": conversations
        }


@router.delete("/conversation/{conversation_id}", response_model=dict)
async def delete_conversation(
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    connection: asyncpg.Connection = Depends(get_db)
):
    """
    Delete a conversation and all its messages.
    """
    from uuid import UUID
    from app.repositories.chat_repository import ChatMessageRepository
    
    user_id = UUID(current_user["id"])
    repo = ChatMessageRepository()
    
    deleted = await repo.delete_conversation(connection, user_id, conversation_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found or access denied"
        )
    
    return {"message": "Conversation deleted successfully"}
