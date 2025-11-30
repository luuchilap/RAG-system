# Weakness Analysis Feature - Implementation Plan

## Overview

This feature analyzes a user's last 5 test attempts to identify weaknesses and generate personalized practice questions using LLM.

---

## Phase 1: Backend - Mock Data & Models

### Task 1.1: Create Mock Data File
**File:** `backend/app/mock_data/test_history.py`

```python
# Mock data representing user's test history from client.txt interfaces

MOCK_TAGS = [
    {"id": "tag-001", "name": "Grammar - Tenses", "tagType": "question"},
    {"id": "tag-002", "name": "Grammar - Articles", "tagType": "question"},
    {"id": "tag-003", "name": "Vocabulary - Academic", "tagType": "question"},
    {"id": "tag-004", "name": "Reading - Main Idea", "tagType": "question"},
    {"id": "tag-005", "name": "Reading - Detail Finding", "tagType": "question"},
    {"id": "tag-006", "name": "Listening - Note Completion", "tagType": "question"},
    {"id": "tag-007", "name": "Listening - Multiple Choice", "tagType": "question"},
]

MOCK_EXAMS = [
    {
        "id": "exam-001",
        "title": "IELTS Practice Test - Reading Module 1",
        "difficulty": "intermediate",
        "skill": "reading",
        "testType": "ielts",
    },
    {
        "id": "exam-002",
        "title": "IELTS Practice Test - Listening Section 1-2",
        "difficulty": "intermediate",
        "skill": "listening",
        "testType": "ielts",
    },
    {
        "id": "exam-003",
        "title": "IELTS Grammar Focus Test",
        "difficulty": "intermediate",
        "skill": "reading",
        "testType": "ielts",
    },
]

MOCK_QUESTIONS = [
    {
        "id": "q-001",
        "sectionId": "section-001",
        "examId": "exam-001",
        "type": "multiple-choice",
        "content": "What is the main purpose of the first paragraph?",
        "options": [
            "A) To introduce the topic of climate change",
            "B) To provide statistical data on emissions",
            "C) To argue against environmental policies",
            "D) To describe renewable energy sources"
        ],
        "correctAnswer": ["A"],
        "points": 1,
        "tagIds": ["tag-004"],
        "skill": "reading"
    },
    {
        "id": "q-002",
        "sectionId": "section-001",
        "examId": "exam-001",
        "type": "multiple-choice",
        "content": "According to the passage, which year saw the highest carbon emissions?",
        "options": ["A) 2018", "B) 2019", "C) 2020", "D) 2021"],
        "correctAnswer": ["B"],
        "points": 1,
        "tagIds": ["tag-005"],
        "skill": "reading"
    },
    {
        "id": "q-003",
        "sectionId": "section-001",
        "examId": "exam-001",
        "type": "fill-blank",
        "content": "The author suggests that _______ is the most effective solution.",
        "correctAnswer": ["renewable energy", "clean energy"],
        "points": 1,
        "tagIds": ["tag-005", "tag-003"],
        "skill": "reading"
    },
    {
        "id": "q-004",
        "sectionId": "section-002",
        "examId": "exam-002",
        "type": "fill-blank",
        "content": "The meeting is scheduled for _______ next week.",
        "correctAnswer": ["Thursday"],
        "points": 1,
        "tagIds": ["tag-006"],
        "skill": "listening"
    },
    {
        "id": "q-005",
        "sectionId": "section-002",
        "examId": "exam-002",
        "type": "multiple-choice",
        "content": "What does the speaker say about the deadline?",
        "options": [
            "A) It has been extended",
            "B) It cannot be changed",
            "C) It depends on the team's progress",
            "D) It was set by the client"
        ],
        "correctAnswer": ["B"],
        "points": 1,
        "tagIds": ["tag-007"],
        "skill": "listening"
    },
    {
        "id": "q-006",
        "sectionId": "section-003",
        "examId": "exam-003",
        "type": "multiple-choice",
        "content": "She _______ to the gym every morning before work.",
        "options": ["A) go", "B) goes", "C) going", "D) gone"],
        "correctAnswer": ["B"],
        "points": 1,
        "tagIds": ["tag-001"],
        "skill": "reading"
    },
    {
        "id": "q-007",
        "sectionId": "section-003",
        "examId": "exam-003",
        "type": "multiple-choice",
        "content": "I have been waiting here _______ two hours.",
        "options": ["A) since", "B) for", "C) during", "D) while"],
        "correctAnswer": ["B"],
        "points": 1,
        "tagIds": ["tag-001"],
        "skill": "reading"
    },
    {
        "id": "q-008",
        "sectionId": "section-003",
        "examId": "exam-003",
        "type": "multiple-choice",
        "content": "_______ University of Oxford is one of _______ oldest universities in the world.",
        "options": ["A) A / the", "B) The / the", "C) The / a", "D) - / the"],
        "correctAnswer": ["B"],
        "points": 1,
        "tagIds": ["tag-002"],
        "skill": "reading"
    },
]

# User's 5 latest attempts with wrong answers
MOCK_ATTEMPTS = [
    {
        "id": "attempt-001",
        "userId": "user-001",
        "examId": "exam-001",
        "startTime": 1732838400000,
        "score": 60,
        "choices": [
            {"questionId": "q-001", "answerIdx": "C"},  # Wrong (correct: A)
            {"questionId": "q-002", "answerIdx": "A"},  # Wrong (correct: B)
            {"questionId": "q-003", "answerIdx": "solar power"},  # Wrong
        ]
    },
    {
        "id": "attempt-002",
        "userId": "user-001",
        "examId": "exam-002",
        "startTime": 1732752000000,
        "score": 50,
        "choices": [
            {"questionId": "q-004", "answerIdx": "Wednesday"},  # Wrong (correct: Thursday)
            {"questionId": "q-005", "answerIdx": "A"},  # Wrong (correct: B)
        ]
    },
    {
        "id": "attempt-003",
        "userId": "user-001",
        "examId": "exam-003",
        "startTime": 1732665600000,
        "score": 33,
        "choices": [
            {"questionId": "q-006", "answerIdx": "A"},  # Wrong (correct: B)
            {"questionId": "q-007", "answerIdx": "A"},  # Wrong (correct: B)
            {"questionId": "q-008", "answerIdx": "A"},  # Wrong (correct: B)
        ]
    },
    {
        "id": "attempt-004",
        "userId": "user-001",
        "examId": "exam-003",
        "startTime": 1732579200000,
        "score": 67,
        "choices": [
            {"questionId": "q-006", "answerIdx": "B"},  # Correct
            {"questionId": "q-007", "answerIdx": "A"},  # Wrong (correct: B)
            {"questionId": "q-008", "answerIdx": "D"},  # Wrong (correct: B)
        ]
    },
    {
        "id": "attempt-005",
        "userId": "user-001",
        "examId": "exam-001",
        "startTime": 1732492800000,
        "score": 67,
        "choices": [
            {"questionId": "q-001", "answerIdx": "A"},  # Correct
            {"questionId": "q-002", "answerIdx": "C"},  # Wrong (correct: B)
            {"questionId": "q-003", "answerIdx": "renewable energy"},  # Correct
        ]
    },
]

MOCK_USER_GOAL = {
    "userId": "user-001",
    "testType": "ielts",
    "target": 7.0,
    "dueDate": 1735689600000
}
```

### Task 1.2: Create Pydantic Models
**File:** `backend/app/models/weakness_analysis.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class TestType(str, Enum):
    IELTS = "ielts"
    TOEIC = "toeic"

class Skill(str, Enum):
    READING = "reading"
    LISTENING = "listening"
    WRITING = "writing"
    SPEAKING = "speaking"

class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class WrongAnswerDetail(BaseModel):
    questionId: str
    questionContent: str
    questionType: str
    userAnswer: str
    correctAnswer: List[str]
    tags: List[str]
    skill: Skill
    examTitle: str

class SkillBreakdown(BaseModel):
    skill: Skill
    wrongCount: int
    totalCount: int
    errorRate: float
    weakTags: List[str]

class GeneratedQuestion(BaseModel):
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
    userId: str
    testType: TestType = TestType.IELTS
    limitAttempts: int = Field(default=5, ge=1, le=10)

class WeaknessAnalysisResponse(BaseModel):
    userId: str
    testType: TestType
    analyzedAt: int
    totalQuestionsAnalyzed: int
    totalWrongAnswers: int
    skillBreakdown: List[SkillBreakdown]
    weaknessDescription: str
    improvementSuggestions: List[str]
    practiceQuestions: List[GeneratedQuestion]
```

---

## Phase 2: Backend - Analysis Service

### Task 2.1: Create Weakness Analysis Service
**File:** `backend/app/services/weakness_analysis_service.py`

```python
"""
Weakness Analysis Service
Analyzes user's test history and generates practice questions using LLM.
"""
from typing import List, Dict, Any
from collections import defaultdict
import time
from openai import AsyncOpenAI

from app.config import settings
from app.models.weakness_analysis import (
    WeaknessAnalysisRequest,
    WeaknessAnalysisResponse,
    WrongAnswerDetail,
    SkillBreakdown,
    GeneratedQuestion,
    Skill,
    Difficulty
)
from app.mock_data.test_history import (
    MOCK_ATTEMPTS,
    MOCK_QUESTIONS,
    MOCK_EXAMS,
    MOCK_TAGS,
    MOCK_USER_GOAL
)


class WeaknessAnalysisService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    def _get_question_by_id(self, question_id: str) -> Dict[str, Any]:
        """Get question details by ID from mock data."""
        for q in MOCK_QUESTIONS:
            if q["id"] == question_id:
                return q
        return None
    
    def _get_exam_by_id(self, exam_id: str) -> Dict[str, Any]:
        """Get exam details by ID from mock data."""
        for e in MOCK_EXAMS:
            if e["id"] == exam_id:
                return e
        return None
    
    def _get_tag_names(self, tag_ids: List[str]) -> List[str]:
        """Convert tag IDs to tag names."""
        tag_map = {t["id"]: t["name"] for t in MOCK_TAGS}
        return [tag_map.get(tid, tid) for tid in tag_ids]
    
    def _is_answer_wrong(self, user_answer: str, correct_answers: List[str]) -> bool:
        """Check if user's answer is wrong."""
        user_answer_normalized = user_answer.strip().lower()
        for correct in correct_answers:
            if user_answer_normalized == correct.strip().lower():
                return False
        return True
    
    def extract_wrong_answers(self, user_id: str, limit: int = 5) -> List[WrongAnswerDetail]:
        """Extract wrong answers from user's recent attempts."""
        # Filter attempts for user and sort by time (most recent first)
        user_attempts = [a for a in MOCK_ATTEMPTS if a["userId"] == user_id]
        user_attempts.sort(key=lambda x: x["startTime"], reverse=True)
        user_attempts = user_attempts[:limit]
        
        wrong_answers = []
        
        for attempt in user_attempts:
            exam = self._get_exam_by_id(attempt["examId"])
            
            for choice in attempt["choices"]:
                question = self._get_question_by_id(choice["questionId"])
                if not question:
                    continue
                
                if self._is_answer_wrong(choice["answerIdx"], question["correctAnswer"]):
                    wrong_answers.append(WrongAnswerDetail(
                        questionId=question["id"],
                        questionContent=question["content"],
                        questionType=question["type"],
                        userAnswer=choice["answerIdx"],
                        correctAnswer=question["correctAnswer"],
                        tags=self._get_tag_names(question["tagIds"]),
                        skill=Skill(question["skill"]),
                        examTitle=exam["title"] if exam else "Unknown"
                    ))
        
        return wrong_answers
    
    def calculate_skill_breakdown(
        self, 
        wrong_answers: List[WrongAnswerDetail],
        user_id: str
    ) -> List[SkillBreakdown]:
        """Calculate breakdown of errors by skill and tags."""
        # Count wrong answers by skill
        skill_wrong = defaultdict(list)
        skill_total = defaultdict(int)
        
        # Get all questions attempted
        user_attempts = [a for a in MOCK_ATTEMPTS if a["userId"] == user_id]
        
        for attempt in user_attempts[:5]:
            for choice in attempt["choices"]:
                question = self._get_question_by_id(choice["questionId"])
                if question:
                    skill_total[question["skill"]] += 1
        
        # Group wrong answers by skill
        for wa in wrong_answers:
            skill_wrong[wa.skill.value].extend(wa.tags)
        
        breakdowns = []
        for skill in ["reading", "listening", "writing", "speaking"]:
            if skill_total[skill] > 0:
                wrong_count = len([wa for wa in wrong_answers if wa.skill.value == skill])
                # Get most common weak tags
                tag_counts = defaultdict(int)
                for wa in wrong_answers:
                    if wa.skill.value == skill:
                        for tag in wa.tags:
                            tag_counts[tag] += 1
                
                weak_tags = sorted(tag_counts.keys(), key=lambda x: tag_counts[x], reverse=True)[:3]
                
                breakdowns.append(SkillBreakdown(
                    skill=Skill(skill),
                    wrongCount=wrong_count,
                    totalCount=skill_total[skill],
                    errorRate=round(wrong_count / skill_total[skill] * 100, 1),
                    weakTags=weak_tags
                ))
        
        return breakdowns
    
    def _build_analysis_prompt(
        self,
        wrong_answers: List[WrongAnswerDetail],
        skill_breakdown: List[SkillBreakdown],
        test_type: str,
        target_score: float
    ) -> str:
        """Build the prompt for LLM analysis."""
        
        # Format wrong answers
        wa_text = ""
        for i, wa in enumerate(wrong_answers, 1):
            wa_text += f"""
{i}. Question: "{wa.questionContent}"
   - Your answer: {wa.userAnswer}
   - Correct answer: {', '.join(wa.correctAnswer)}
   - Tags: {', '.join(wa.tags)}
   - Skill: {wa.skill.value}
   - From: {wa.examTitle}
"""
        
        # Format skill breakdown
        breakdown_text = "| Skill | Wrong | Total | Error Rate | Weak Areas |\n"
        breakdown_text += "|-------|-------|-------|------------|------------|\n"
        for sb in skill_breakdown:
            breakdown_text += f"| {sb.skill.value} | {sb.wrongCount} | {sb.totalCount} | {sb.errorRate}% | {', '.join(sb.weakTags)} |\n"
        
        prompt = f"""You are an expert {test_type.upper()} tutor. Analyze this student's performance.

## Student Profile
- Test Type: {test_type.upper()}
- Target Score: {target_score}
- Attempts Analyzed: 5 most recent

## Wrong Answers Detail
{wa_text}

## Error Statistics
{breakdown_text}

## Your Tasks

1. **Weakness Analysis**: Provide a 2-3 sentence summary of the student's main weaknesses.

2. **Improvement Suggestions**: Give exactly 5 specific, actionable suggestions.

3. **Practice Questions**: Generate exactly 5 practice questions targeting the weak areas.
   Each question must include:
   - type (multiple-choice or fill-blank)
   - content (the question text)
   - options (for multiple-choice, 4 options labeled A-D)
   - correctAnswer (array of correct answers)
   - explanation (why this is correct, 2-3 sentences)
   - targetTags (which weakness it addresses)
   - difficulty (intermediate)

Respond in this exact JSON format:
{{
  "weaknessDescription": "...",
  "improvementSuggestions": ["...", "...", "...", "...", "..."],
  "practiceQuestions": [
    {{
      "type": "multiple-choice",
      "content": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correctAnswer": ["B"],
      "explanation": "...",
      "targetTags": ["Grammar - Tenses"],
      "difficulty": "intermediate"
    }}
  ]
}}
"""
        return prompt
    
    async def analyze_with_llm(
        self,
        wrong_answers: List[WrongAnswerDetail],
        skill_breakdown: List[SkillBreakdown],
        test_type: str
    ) -> Dict[str, Any]:
        """Send analysis to LLM and get response."""
        
        target_score = MOCK_USER_GOAL.get("target", 7.0)
        prompt = self._build_analysis_prompt(
            wrong_answers, skill_breakdown, test_type, target_score
        )
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert language test tutor. Always respond with valid JSON only, no markdown."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    async def analyze_weakness(
        self,
        request: WeaknessAnalysisRequest
    ) -> WeaknessAnalysisResponse:
        """Main method to perform weakness analysis."""
        
        # Step 1: Extract wrong answers
        wrong_answers = self.extract_wrong_answers(
            request.userId, 
            request.limitAttempts
        )
        
        # Step 2: Calculate skill breakdown
        skill_breakdown = self.calculate_skill_breakdown(
            wrong_answers, 
            request.userId
        )
        
        # Step 3: Get LLM analysis
        llm_result = await self.analyze_with_llm(
            wrong_answers,
            skill_breakdown,
            request.testType.value
        )
        
        # Step 4: Format practice questions
        practice_questions = []
        for i, pq in enumerate(llm_result.get("practiceQuestions", [])):
            practice_questions.append(GeneratedQuestion(
                id=f"gen-{int(time.time())}-{i}",
                targetSkill=Skill.READING,  # Default, could be parsed from tags
                targetTags=pq.get("targetTags", []),
                type=pq.get("type", "multiple-choice"),
                content=pq.get("content", ""),
                options=pq.get("options"),
                correctAnswer=pq.get("correctAnswer", []),
                explanation=pq.get("explanation", ""),
                difficulty=Difficulty.INTERMEDIATE
            ))
        
        return WeaknessAnalysisResponse(
            userId=request.userId,
            testType=request.testType,
            analyzedAt=int(time.time() * 1000),
            totalQuestionsAnalyzed=sum(sb.totalCount for sb in skill_breakdown),
            totalWrongAnswers=len(wrong_answers),
            skillBreakdown=skill_breakdown,
            weaknessDescription=llm_result.get("weaknessDescription", ""),
            improvementSuggestions=llm_result.get("improvementSuggestions", []),
            practiceQuestions=practice_questions
        )
```

### Task 2.2: Create API Endpoint
**File:** `backend/app/api/analysis.py`

```python
"""
Weakness Analysis API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.weakness_analysis import (
    WeaknessAnalysisRequest,
    WeaknessAnalysisResponse
)
from app.services.weakness_analysis_service import WeaknessAnalysisService
from app.middleware.auth import get_current_user

router = APIRouter()
analysis_service = WeaknessAnalysisService()


@router.post("/weakness", response_model=WeaknessAnalysisResponse)
async def analyze_weakness(
    request: WeaknessAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze user's weakness based on their last N test attempts.
    
    - Extracts wrong answers from recent attempts
    - Calculates error statistics by skill and tag
    - Uses LLM to generate insights and practice questions
    """
    try:
        # Override userId with authenticated user for security
        request.userId = current_user["id"]
        
        result = await analysis_service.analyze_weakness(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weakness/mock")
async def get_mock_analysis():
    """
    Get a mock weakness analysis without authentication (for testing).
    """
    request = WeaknessAnalysisRequest(
        userId="user-001",
        testType="ielts",
        limitAttempts=5
    )
    
    result = await analysis_service.analyze_weakness(request)
    return result
```

### Task 2.3: Register Router in Main App
**Update:** `backend/app/main.py`

```python
# Add this import
from app.api import analysis

# Add this router registration
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
```

---

## Phase 3: Frontend Components (Optional for MVP)

### Task 3.1: Create Analysis Hook
**File:** `LLM/apps/web/hooks/useWeaknessAnalysis.tsx`

```typescript
import { useState } from 'react';
import { analyzeWeakness } from '@/lib/api';

export interface SkillBreakdown {
  skill: string;
  wrongCount: number;
  totalCount: number;
  errorRate: number;
  weakTags: string[];
}

export interface GeneratedQuestion {
  id: string;
  type: string;
  content: string;
  options?: string[];
  correctAnswer: string[];
  explanation: string;
  targetTags: string[];
}

export interface WeaknessAnalysis {
  userId: string;
  testType: string;
  analyzedAt: number;
  totalQuestionsAnalyzed: number;
  totalWrongAnswers: number;
  skillBreakdown: SkillBreakdown[];
  weaknessDescription: string;
  improvementSuggestions: string[];
  practiceQuestions: GeneratedQuestion[];
}

export function useWeaknessAnalysis() {
  const [analysis, setAnalysis] = useState<WeaknessAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalysis = async (testType: string = 'ielts') => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await analyzeWeakness({ testType, limitAttempts: 5 });
      setAnalysis(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  return { analysis, isLoading, error, fetchAnalysis };
}
```

### Task 3.2: Add API Function
**Update:** `LLM/apps/web/lib/api.ts`

```typescript
// Add this function
export async function analyzeWeakness(params: { 
  testType: string; 
  limitAttempts?: number 
}) {
  const response = await fetch(`${API_BASE_URL}/api/analysis/weakness`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      userId: '', // Will be set by backend from auth
      testType: params.testType,
      limitAttempts: params.limitAttempts || 5,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to analyze weakness');
  }

  return response.json();
}
```

---

## Phase 4: Testing

### Task 4.1: Test the Mock Endpoint

```bash
# Start the backend server
cd backend
uvicorn app.main:app --reload

# Test the mock endpoint (no auth required)
curl http://localhost:8000/api/analysis/weakness/mock
```

### Task 4.2: Expected Response Structure

```json
{
  "userId": "user-001",
  "testType": "ielts",
  "analyzedAt": 1732924800000,
  "totalQuestionsAnalyzed": 13,
  "totalWrongAnswers": 11,
  "skillBreakdown": [
    {
      "skill": "reading",
      "wrongCount": 9,
      "totalCount": 11,
      "errorRate": 81.8,
      "weakTags": ["Grammar - Tenses", "Grammar - Articles", "Reading - Detail Finding"]
    },
    {
      "skill": "listening",
      "wrongCount": 2,
      "totalCount": 2,
      "errorRate": 100.0,
      "weakTags": ["Listening - Note Completion", "Listening - Multiple Choice"]
    }
  ],
  "weaknessDescription": "Your primary weaknesses are in grammar fundamentals...",
  "improvementSuggestions": [
    "Master the since/for distinction...",
    "Review article rules for institutions...",
    "..."
  ],
  "practiceQuestions": [
    {
      "id": "gen-1732924800-0",
      "type": "multiple-choice",
      "content": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correctAnswer": ["B"],
      "explanation": "...",
      "targetTags": ["Grammar - Tenses"],
      "difficulty": "intermediate"
    }
  ]
}
```

---

## Implementation Checklist

| # | Task | Priority | Status |
|---|------|----------|--------|
| 1 | Create `backend/app/mock_data/` directory | High | ⬜ |
| 2 | Create `test_history.py` with mock data | High | ⬜ |
| 3 | Create `models/weakness_analysis.py` | High | ⬜ |
| 4 | Create `services/weakness_analysis_service.py` | High | ⬜ |
| 5 | Create `api/analysis.py` endpoint | High | ⬜ |
| 6 | Register router in `main.py` | High | ⬜ |
| 7 | Test mock endpoint | High | ⬜ |
| 8 | (Optional) Create frontend hook | Medium | ⬜ |
| 9 | (Optional) Add API function to frontend | Medium | ⬜ |
| 10 | (Optional) Create UI component | Low | ⬜ |

---

## File Structure After Implementation

```
backend/
├── app/
│   ├── api/
│   │   ├── analysis.py          # NEW
│   │   └── ...
│   ├── mock_data/               # NEW FOLDER
│   │   └── test_history.py      # NEW
│   ├── models/
│   │   ├── weakness_analysis.py # NEW
│   │   └── ...
│   ├── services/
│   │   ├── weakness_analysis_service.py  # NEW
│   │   └── ...
│   └── main.py                  # UPDATED
```

---

## Notes

1. **Mock Data Only**: This plan uses hardcoded mock data. In production, you'd query a real database.

2. **No Database Changes**: No schema changes needed for MVP with mock data.

3. **LLM Integration**: Uses existing OpenAI setup from `chat_service.py`.

4. **Authentication**: The authenticated endpoint uses `get_current_user`, mock endpoint skips auth for testing.

5. **Extensibility**: The service is designed to easily swap mock data for real database queries later.
