"""
Authentication API endpoints.
Handles user registration, login, and logout.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from datetime import datetime
import asyncpg
from app.models.user import UserCreate, UserResponse, UserLogin
from app.middleware.auth import get_current_user
from app.repositories.user_repository import UserRepository
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_token_for_user
)
from app.database import get_db

router = APIRouter()


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with username, email, and password. Returns an access token for immediate use.",
    responses={
        201: {
            "description": "User successfully registered",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "username": "johndoe",
                            "email": "john@example.com",
                            "created_at": "2024-01-01T00:00:00"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Username or email already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Username or email already registered"
                    }
                }
            }
        }
    }
)
async def register(
    user_data: UserCreate,
    connection: asyncpg.Connection = Depends(get_db)
):
    """
    Register a new user.
    
    **Example Request:**
    ```json
    {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "securepassword123"
    }
    ```
    """
    # Check if user already exists
    user_repo = UserRepository()
    
    if await user_repo.user_exists(connection, username=user_data.username, email=user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = await user_repo.create_user(connection, user_data, hashed_password)
    
    # Create access token
    access_token = create_token_for_user(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        ).dict()
    }


@router.post(
    "/login",
    response_model=dict,
    summary="Login user",
    description="Authenticate a user with username/email and password. Returns a JWT access token.",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect username or password"
                    }
                }
            }
        }
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    connection: asyncpg.Connection = Depends(get_db)
):
    """
    Authenticate user and return access token.
    
    **Note:** This endpoint uses OAuth2 password flow. In Swagger UI, click "Authorize" and enter:
    - Username: your username or email
    - Password: your password
    
    The token will be automatically included in subsequent requests.
    """
    user_repo = UserRepository()
    
    # Get user by username or email
    user = await user_repo.get_user_by_username_or_email(connection, form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_token_for_user(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post(
    "/logout",
    response_model=dict,
    summary="Logout user",
    description="Logout endpoint. For JWT tokens, logout is typically handled client-side by discarding the token.",
    responses={
        200: {
            "description": "Logout successful",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Successfully logged out"
                    }
                }
            }
        }
    }
)
async def logout():
    """
    Logout endpoint.
    
    **Note:** With JWT tokens, logout is handled client-side by discarding the token.
    This endpoint is provided for API consistency.
    """
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user information",
    description="Get information about the currently authenticated user.",
    responses={
        200: {
            "description": "User information",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "username": "johndoe",
                        "email": "john@example.com",
                        "created_at": "2024-01-01T00:00:00"
                    }
                }
            }
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Could not validate credentials"
                    }
                }
            }
        }
    }
)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    connection: asyncpg.Connection = Depends(get_db)
):
    """
    Get current user information.
    
    **Note:** Requires authentication. Use the "Authorize" button in Swagger UI to set your token.
    """
    # Get full user data from database
    user_repo = UserRepository()
    from uuid import UUID
    user = await user_repo.get_user_by_id(connection, UUID(current_user["id"]))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )
