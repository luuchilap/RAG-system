"""
Database connection module using asyncpg for asynchronous PostgreSQL operations.
Provides connection pooling and transaction management.
"""
from typing import AsyncGenerator, Optional
import asyncpg
from asyncpg import Pool, Connection
from app.config import settings


class Database:
    """Database connection pool manager."""
    
    def __init__(self):
        self._pool: Optional[Pool] = None
    
    async def connect(self) -> None:
        """Initialize the database connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
    
    async def disconnect(self) -> None:
        """Close the database connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    async def get_connection(self) -> Connection:
        """Get a connection from the pool."""
        if self._pool is None:
            await self.connect()
        return await self._pool.acquire()
    
    async def release_connection(self, connection: Connection) -> None:
        """Release a connection back to the pool."""
        if self._pool:
            await self._pool.release(connection)
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query and return the result."""
        async with self._pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> list:
        """Execute a query and return all rows."""
        async with self._pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Execute a query and return a single row."""
        async with self._pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args) -> Optional[any]:
        """Execute a query and return a single value."""
        async with self._pool.acquire() as connection:
            return await connection.fetchval(query, *args)


# Global database instance
db = Database()


async def get_db() -> AsyncGenerator[Connection, None]:
    """
    Dependency function for FastAPI to get a database connection.
    Yields a connection and ensures it's properly released.
    """
    connection = await db.get_connection()
    try:
        yield connection
    finally:
        await db.release_connection(connection)


async def init_db() -> None:
    """Initialize the database connection pool."""
    await db.connect()


async def close_db() -> None:
    """Close the database connection pool."""
    await db.disconnect()
