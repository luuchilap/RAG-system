"""
Weakness Analysis API endpoints.
Analyzes user's test history to identify weaknesses and generate practice questions.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.weakness_analysis import (
    WeaknessAnalysisRequest,
    WeaknessAnalysisResponse,
)
from app.services.weakness_analysis_service import WeaknessAnalysisService
from app.middleware.auth import get_current_user

router = APIRouter()
analysis_service = WeaknessAnalysisService()


@router.post("/weakness", response_model=WeaknessAnalysisResponse)
async def analyze_weakness(
    request: WeaknessAnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Analyze user's weakness based on their last N test attempts.
    
    This endpoint:
    - Extracts wrong answers from recent test attempts
    - Calculates error statistics by skill and tag
    - Uses LLM to generate insights and personalized practice questions
    
    **Authentication required.**
    """
    try:
        # Override userId with authenticated user for security
        request.userId = current_user["id"]

        result = await analysis_service.analyze_weakness(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weakness/mock", response_model=WeaknessAnalysisResponse)
async def get_mock_analysis():
    """
    Get a mock weakness analysis without authentication.
    
    **For testing purposes only.**
    
    Uses mock user "user-001" and analyzes their last 5 IELTS test attempts.
    """
    try:
        request = WeaknessAnalysisRequest(
            userId="user-001",
            testType="ielts",
            limitAttempts=5,
        )

        result = await analysis_service.analyze_weakness(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
