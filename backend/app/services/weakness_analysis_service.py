"""
Weakness Analysis Service.
Analyzes user's test history and generates practice questions using LLM.
"""
from typing import List, Dict, Any
from collections import defaultdict
import time
import json
from openai import AsyncOpenAI

from app.config import settings
from app.models.weakness_analysis import (
    WeaknessAnalysisRequest,
    WeaknessAnalysisResponse,
    WrongAnswerDetail,
    SkillBreakdown,
    GeneratedQuestion,
    Skill,
    Difficulty,
)
from app.mock_data.test_history import (
    MOCK_ATTEMPTS,
    MOCK_QUESTIONS,
    MOCK_EXAMS,
    MOCK_TAGS,
    MOCK_USER_GOAL,
    get_question_by_id,
    get_exam_by_id,
    get_tag_names,
    get_user_attempts,
)


class WeaknessAnalysisService:
    """Service for analyzing user weaknesses and generating practice questions."""

    def __init__(self):
        """Initialize the OpenAI client."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def _is_answer_wrong(self, user_answer: str, correct_answers: List[str]) -> bool:
        """Check if user's answer is incorrect."""
        user_answer_normalized = user_answer.strip().lower()
        for correct in correct_answers:
            if user_answer_normalized == correct.strip().lower():
                return False
        return True

    def extract_wrong_answers(
        self, user_id: str, limit: int = 5
    ) -> List[WrongAnswerDetail]:
        """
        Extract wrong answers from user's recent test attempts.
        
        Args:
            user_id: The user's ID
            limit: Number of recent attempts to analyze
            
        Returns:
            List of WrongAnswerDetail objects
        """
        user_attempts = get_user_attempts(user_id, limit)
        wrong_answers = []

        for attempt in user_attempts:
            exam = get_exam_by_id(attempt["examId"])

            for choice in attempt["choices"]:
                question = get_question_by_id(choice["questionId"])
                if not question:
                    continue

                if self._is_answer_wrong(
                    choice["answerIdx"], question["correctAnswer"]
                ):
                    wrong_answers.append(
                        WrongAnswerDetail(
                            questionId=question["id"],
                            questionContent=question["content"],
                            questionType=question["type"],
                            userAnswer=choice["answerIdx"],
                            correctAnswer=question["correctAnswer"],
                            tags=get_tag_names(question["tagIds"]),
                            skill=Skill(question["skill"]),
                            examTitle=exam["title"] if exam else "Unknown",
                        )
                    )

        return wrong_answers

    def calculate_skill_breakdown(
        self, wrong_answers: List[WrongAnswerDetail], user_id: str
    ) -> List[SkillBreakdown]:
        """
        Calculate error breakdown by skill and identify weak areas.
        
        Args:
            wrong_answers: List of wrong answer details
            user_id: The user's ID
            
        Returns:
            List of SkillBreakdown objects
        """
        # Count total questions attempted per skill
        skill_total: Dict[str, int] = defaultdict(int)
        user_attempts = get_user_attempts(user_id, 5)

        for attempt in user_attempts:
            for choice in attempt["choices"]:
                question = get_question_by_id(choice["questionId"])
                if question:
                    skill_total[question["skill"]] += 1

        # Group wrong answers by skill and count tags
        skill_wrong: Dict[str, int] = defaultdict(int)
        skill_tags: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for wa in wrong_answers:
            skill_wrong[wa.skill.value] += 1
            for tag in wa.tags:
                skill_tags[wa.skill.value][tag] += 1

        # Build breakdown for each skill with attempts
        breakdowns = []
        for skill in ["reading", "listening", "writing", "speaking"]:
            if skill_total[skill] > 0:
                wrong_count = skill_wrong[skill]
                error_rate = round(wrong_count / skill_total[skill] * 100, 1)

                # Get top 3 weak tags for this skill
                tag_counts = skill_tags[skill]
                weak_tags = sorted(
                    tag_counts.keys(), key=lambda x: tag_counts[x], reverse=True
                )[:3]

                breakdowns.append(
                    SkillBreakdown(
                        skill=Skill(skill),
                        wrongCount=wrong_count,
                        totalCount=skill_total[skill],
                        errorRate=error_rate,
                        weakTags=weak_tags,
                    )
                )

        return breakdowns

    def _build_analysis_prompt(
        self,
        wrong_answers: List[WrongAnswerDetail],
        skill_breakdown: List[SkillBreakdown],
        test_type: str,
        target_score: float,
    ) -> str:
        """Build the LLM prompt for analysis."""
        # Format wrong answers section
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

        # Format skill breakdown table
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
        test_type: str,
    ) -> Dict[str, Any]:
        """
        Send analysis data to LLM and get insights.
        
        Args:
            wrong_answers: List of wrong answer details
            skill_breakdown: Skill-level error breakdown
            test_type: The test type (ielts/toeic)
            
        Returns:
            Dict containing LLM analysis results
        """
        target_score = MOCK_USER_GOAL.get("target", 7.0)
        prompt = self._build_analysis_prompt(
            wrong_answers, skill_breakdown, test_type, target_score
        )

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert language test tutor. Always respond with valid JSON only, no markdown code blocks.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        return result

    async def analyze_weakness(
        self, request: WeaknessAnalysisRequest
    ) -> WeaknessAnalysisResponse:
        """
        Main method to perform weakness analysis.
        
        Args:
            request: WeaknessAnalysisRequest containing user and test info
            
        Returns:
            WeaknessAnalysisResponse with complete analysis
        """
        # Step 1: Extract wrong answers from recent attempts
        wrong_answers = self.extract_wrong_answers(
            request.userId, request.limitAttempts
        )

        # Step 2: Calculate skill breakdown statistics
        skill_breakdown = self.calculate_skill_breakdown(wrong_answers, request.userId)

        # Step 3: Get LLM analysis and practice questions
        llm_result = await self.analyze_with_llm(
            wrong_answers, skill_breakdown, request.testType.value
        )

        # Step 4: Format practice questions from LLM response
        practice_questions = []
        for i, pq in enumerate(llm_result.get("practiceQuestions", [])):
            # Determine target skill from tags
            target_skill = Skill.READING  # Default
            target_tags = pq.get("targetTags", [])
            for tag in target_tags:
                if "listening" in tag.lower():
                    target_skill = Skill.LISTENING
                    break
                elif "writing" in tag.lower():
                    target_skill = Skill.WRITING
                    break
                elif "speaking" in tag.lower():
                    target_skill = Skill.SPEAKING
                    break

            practice_questions.append(
                GeneratedQuestion(
                    id=f"gen-{int(time.time())}-{i}",
                    targetSkill=target_skill,
                    targetTags=target_tags,
                    type=pq.get("type", "multiple-choice"),
                    content=pq.get("content", ""),
                    options=pq.get("options"),
                    correctAnswer=pq.get("correctAnswer", []),
                    explanation=pq.get("explanation", ""),
                    difficulty=Difficulty.INTERMEDIATE,
                )
            )

        # Build and return response
        return WeaknessAnalysisResponse(
            userId=request.userId,
            testType=request.testType,
            analyzedAt=int(time.time() * 1000),
            totalQuestionsAnalyzed=sum(sb.totalCount for sb in skill_breakdown),
            totalWrongAnswers=len(wrong_answers),
            skillBreakdown=skill_breakdown,
            weaknessDescription=llm_result.get("weaknessDescription", ""),
            improvementSuggestions=llm_result.get("improvementSuggestions", []),
            practiceQuestions=practice_questions,
        )
