"""
User model for database operations and API validation.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str = Field(..., min_length=3, max_length=255, description="Username")
    email: EmailStr = Field(..., description="User email address")


class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(..., min_length=8, max_length=255, description="User password")


class UserInDB(UserBase):
    """User model as stored in the database."""
    id: UUID
    hashed_password: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User model for API responses (excludes sensitive data)."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Model for user login."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")

