"""
Chat message models for database operations and API validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class ChatMessageBase(BaseModel):
    """Base chat message model."""
    role: str = Field(..., pattern="^(user|assistant)$", description="Message role")
    content: str = Field(..., min_length=1, description="Message content")


class ChatMessageCreate(ChatMessageBase):
    """Model for creating a new chat message."""
    conversation_id: Optional[UUID] = Field(None, description="Conversation ID (optional for new conversations)")


class ChatMessageInDB(ChatMessageBase):
    """Chat message model as stored in the database."""
    id: UUID
    user_id: UUID
    conversation_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatMessageResponse(ChatMessageBase):
    """Chat message model for API responses."""
    id: UUID
    conversation_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Model for chat API requests."""
    message: str = Field(..., min_length=1, description="User message")
    conversation_id: Optional[UUID] = Field(None, description="Conversation ID (optional for new conversations)")


class ConversationResponse(BaseModel):
    """Model for conversation list responses."""
    conversation_id: UUID
    last_message: Optional[str] = None
    last_timestamp: Optional[datetime] = None
    message_count: int

