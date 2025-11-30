"""
Pydantic models for Weakness Analysis feature.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class TestType(str, Enum):
    """Supported test types."""
    IELTS = "ielts"
    TOEIC = "toeic"


class Skill(str, Enum):
    """Language skills."""
    READING = "reading"
    LISTENING = "listening"
    WRITING = "writing"
    SPEAKING = "speaking"


class Difficulty(str, Enum):
    """Question difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class WrongAnswerDetail(BaseModel):
    """Details of a single wrong answer."""
    questionId: str
    questionContent: str
    questionType: str
    userAnswer: str
    correctAnswer: List[str]
    tags: List[str]
    skill: Skill
    examTitle: str


class SkillBreakdown(BaseModel):
    """Breakdown of errors by skill."""
    skill: Skill
    wrongCount: int
    totalCount: int
    errorRate: float
    weakTags: List[str]


class GeneratedQuestion(BaseModel):
    """LLM-generated practice question."""
    id: str
    targetSkill: Skill
    targetTags: List[str]
    type: str
    content: str
    options: Optional[List[str]] = None
    correctAnswer: List[str]
    explanation: str
    difficulty: Difficulty


class WeaknessAnalysisRequest(BaseModel):
    """Request model for weakness analysis."""
    userId: str = Field(default="", description="User ID (will be set from auth)")
    testType: TestType = Field(default=TestType.IELTS, description="Test type to analyze")
    limitAttempts: int = Field(default=5, ge=1, le=10, description="Number of recent attempts to analyze")


class WeaknessAnalysisResponse(BaseModel):
    """Response model for weakness analysis."""
    userId: str
    testType: TestType
    analyzedAt: int  # Unix timestamp in milliseconds
    totalQuestionsAnalyzed: int
    totalWrongAnswers: int
    skillBreakdown: List[SkillBreakdown]
    weaknessDescription: str
    improvementSuggestions: List[str]
    practiceQuestions: List[GeneratedQuestion]
