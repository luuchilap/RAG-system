"""
Authentication middleware for protecting API endpoints.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import asyncpg
from app.services.auth_service import decode_access_token
from app.repositories.user_repository import UserRepository
from app.database import get_db, db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> dict:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        connection: Database connection (injected by FastAPI dependency)
    
    Returns:
        Dictionary containing user information
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Extract user ID from token
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database to verify they still exist
    # We'll get a connection from the pool
    connection = await db.get_connection()
    try:
        user_repo = UserRepository()
        from uuid import UUID
        user = await user_repo.get_user_by_id(connection, UUID(user_id))
        
        if not user:
            raise credentials_exception
        
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email
        }
    finally:
        await db.release_connection(connection)

