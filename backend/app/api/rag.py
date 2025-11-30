"""
RAG API endpoints.
Handles document retrieval queries for RAG functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.services.rag_service import RAGService
from app.middleware.auth import get_current_user
from app.models.rag import QueryRequest, QueryResponse, RAGResult


router = APIRouter()
rag_service = RAGService()


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Query documents using RAG",
    description="Search through uploaded documents to find relevant chunks based on a query."
)
async def query_rag(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Query documents using RAG retrieval.
    
    This endpoint searches through the user's uploaded documents to find
    relevant chunks that match the query. Results are ranked by relevance.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    try:
        user_id = UUID(current_user["id"])
        results = await rag_service.query_documents(
            user_id,
            request.query,
            request.top_k
        )
        
        # Convert to response model
        rag_results = [
            RAGResult(
                text=result["text"],
                metadata=result["metadata"],
                relevance_score=result["relevance_score"]
            )
            for result in results
        ]
        
        return QueryResponse(results=rag_results)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying documents: {str(e)}"
        )

