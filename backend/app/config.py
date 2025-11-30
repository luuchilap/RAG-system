"""
Application configuration using Pydantic settings.
Loads configuration from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database configuration
    DATABASE_URL: str = "postgresql://postgres:lap@localhost:5432/mydb"
    
    # Authentication configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # File storage configuration
    UPLOAD_FOLDER: str = "./uploaded_documents"
    FAISS_INDEX_FOLDER: str = "./faiss_indexes"
    
    # OpenAI configuration (user provides their own API key)
    OPENAI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

