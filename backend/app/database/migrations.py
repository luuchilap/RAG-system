"""
Simple database migration system for managing schema changes.
"""
import os
import asyncpg
from pathlib import Path
from app.config import settings


async def run_migrations() -> None:
    """
    Run database migrations by executing the schema.sql file.
    This is a simple migration system suitable for local development.
    """
    # Get the path to schema.sql
    schema_path = Path(__file__).parent.parent.parent / "database" / "schema.sql"
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    # Read the schema SQL
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    # Connect to database and execute schema
    connection = await asyncpg.connect(settings.DATABASE_URL)
    try:
        # Execute the schema SQL
        await connection.execute(schema_sql)
        print("✓ Database migrations completed successfully")
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        await connection.close()


async def check_migration_status() -> dict:
    """
    Check the current migration status by verifying if tables exist.
    Returns a dictionary with table existence status.
    """
    connection = await asyncpg.connect(settings.DATABASE_URL)
    try:
        # Check if tables exist
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('users', 'chat_messages', 'documents')
        """
        existing_tables = await connection.fetch(query)
        table_names = [row['table_name'] for row in existing_tables]
        
        return {
            'users': 'users' in table_names,
            'chat_messages': 'chat_messages' in table_names,
            'documents': 'documents' in table_names,
            'all_tables_exist': len(table_names) == 3
        }
    finally:
        await connection.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_migrations())

