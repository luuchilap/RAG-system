"""
User repository for database operations.
Handles CRUD operations for user entities.
"""
from typing import Optional
from uuid import UUID
import asyncpg
from app.models.user import UserCreate, UserInDB
from app.database import get_db


class UserRepository:
    """Repository for user database operations."""
    
    @staticmethod
    async def create_user(
        connection: asyncpg.Connection,
        user_data: UserCreate,
        hashed_password: str
    ) -> UserInDB:
        """Create a new user in the database."""
        query = """
            INSERT INTO users (username, email, hashed_password)
            VALUES ($1, $2, $3)
            RETURNING id, username, email, hashed_password, created_at
        """
        row = await connection.fetchrow(
            query,
            user_data.username,
            user_data.email,
            hashed_password
        )
        return UserInDB(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            hashed_password=row['hashed_password'],
            created_at=row['created_at']
        )
    
    @staticmethod
    async def get_user_by_id(
        connection: asyncpg.Connection,
        user_id: UUID
    ) -> Optional[UserInDB]:
        """Get a user by ID."""
        query = """
            SELECT id, username, email, hashed_password, created_at
            FROM users
            WHERE id = $1
        """
        row = await connection.fetchrow(query, user_id)
        if not row:
            return None
        return UserInDB(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            hashed_password=row['hashed_password'],
            created_at=row['created_at']
        )
    
    @staticmethod
    async def get_user_by_username(
        connection: asyncpg.Connection,
        username: str
    ) -> Optional[UserInDB]:
        """Get a user by username."""
        query = """
            SELECT id, username, email, hashed_password, created_at
            FROM users
            WHERE username = $1
        """
        row = await connection.fetchrow(query, username)
        if not row:
            return None
        return UserInDB(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            hashed_password=row['hashed_password'],
            created_at=row['created_at']
        )
    
    @staticmethod
    async def get_user_by_email(
        connection: asyncpg.Connection,
        email: str
    ) -> Optional[UserInDB]:
        """Get a user by email."""
        query = """
            SELECT id, username, email, hashed_password, created_at
            FROM users
            WHERE email = $1
        """
        row = await connection.fetchrow(query, email)
        if not row:
            return None
        return UserInDB(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            hashed_password=row['hashed_password'],
            created_at=row['created_at']
        )
    
    @staticmethod
    async def get_user_by_username_or_email(
        connection: asyncpg.Connection,
        username_or_email: str
    ) -> Optional[UserInDB]:
        """Get a user by username or email (for login)."""
        query = """
            SELECT id, username, email, hashed_password, created_at
            FROM users
            WHERE username = $1 OR email = $1
        """
        row = await connection.fetchrow(query, username_or_email)
        if not row:
            return None
        return UserInDB(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            hashed_password=row['hashed_password'],
            created_at=row['created_at']
        )
    
    @staticmethod
    async def user_exists(
        connection: asyncpg.Connection,
        username: Optional[str] = None,
        email: Optional[str] = None
    ) -> bool:
        """Check if a user exists with the given username or email."""
        if username and email:
            query = """
                SELECT EXISTS(SELECT 1 FROM users WHERE username = $1 OR email = $2)
            """
            return await connection.fetchval(query, username, email)
        elif username:
            query = """
                SELECT EXISTS(SELECT 1 FROM users WHERE username = $1)
            """
            return await connection.fetchval(query, username)
        elif email:
            query = """
                SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)
            """
            return await connection.fetchval(query, email)
        return False

