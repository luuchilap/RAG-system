"""
RAG models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    query: str = Field(..., min_length=1, description="Query text to search for in documents")
    top_k: int = Field(default=3, ge=1, le=20, description="Number of results to return (1-20)")


class RAGResult(BaseModel):
    """Model for a single RAG retrieval result."""
    text: str = Field(..., description="Retrieved document chunk text")
    metadata: Dict[str, Any] = Field(..., description="Metadata associated with the chunk")
    relevance_score: float = Field(..., description="Relevance score (lower is more relevant)")


class QueryResponse(BaseModel):
    """Response model for RAG queries."""
    results: List[RAGResult] = Field(..., description="List of retrieved document chunks")

