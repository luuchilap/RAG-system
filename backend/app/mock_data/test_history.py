"""
Mock data representing user's test history based on client.txt interfaces.
This data simulates the Exam, Question, Attempt, Tag interfaces.
"""
from typing import Dict, List, Optional

# Tags for categorizing questions
MOCK_TAGS = [
    {"id": "tag-001", "name": "Grammar - Tenses", "tagType": "question"},
    {"id": "tag-002", "name": "Grammar - Articles", "tagType": "question"},
    {"id": "tag-003", "name": "Vocabulary - Academic", "tagType": "question"},
    {"id": "tag-004", "name": "Reading - Main Idea", "tagType": "question"},
    {"id": "tag-005", "name": "Reading - Detail Finding", "tagType": "question"},
    {"id": "tag-006", "name": "Listening - Note Completion", "tagType": "question"},
    {"id": "tag-007", "name": "Listening - Multiple Choice", "tagType": "question"},
]

# Exam metadata
MOCK_EXAMS = [
    {
        "id": "exam-001",
        "createdBy": "admin-001",
        "status": "approved",
        "title": "IELTS Practice Test - Reading Module 1",
        "description": "Academic reading practice with 3 passages",
        "duration": 60,
        "difficulty": "intermediate",
        "skill": "reading",
        "testType": "ielts",
        "tagIds": ["tag-004", "tag-005"],
    },
    {
        "id": "exam-002",
        "createdBy": "admin-001",
        "status": "approved",
        "title": "IELTS Practice Test - Listening Section 1-2",
        "description": "Listening practice with conversations and monologues",
        "duration": 30,
        "difficulty": "intermediate",
        "skill": "listening",
        "testType": "ielts",
        "tagIds": ["tag-006", "tag-007"],
    },
    {
        "id": "exam-003",
        "createdBy": "admin-001",
        "status": "approved",
        "title": "IELTS Grammar Focus Test",
        "description": "Grammar-focused multiple choice questions",
        "duration": 45,
        "difficulty": "intermediate",
        "skill": "reading",
        "testType": "ielts",
        "tagIds": ["tag-001", "tag-002"],
    },
]

# Questions with correct answers
MOCK_QUESTIONS = [
    {
        "id": "q-001",
        "lastEditedBy": "admin-001",
        "sectionId": "section-001",
        "examId": "exam-001",
        "type": "multiple-choice",
        "content": "What is the main purpose of the first paragraph?",
        "options": [
            "A) To introduce the topic of climate change",
            "B) To provide statistical data on emissions",
            "C) To argue against environmental policies",
            "D) To describe renewable energy sources",
        ],
        "correctAnswer": ["A"],
        "points": 1,
        "tagIds": ["tag-004"],
        "skill": "reading",
    },
    {
        "id": "q-002",
        "lastEditedBy": "admin-001",
        "sectionId": "section-001",
        "examId": "exam-001",
        "type": "multiple-choice",
        "content": "According to the passage, which year saw the highest carbon emissions?",
        "options": ["A) 2018", "B) 2019", "C) 2020", "D) 2021"],
        "correctAnswer": ["B"],
        "points": 1,
        "tagIds": ["tag-005"],
        "skill": "reading",
    },
    {
        "id": "q-003",
        "lastEditedBy": "admin-001",
        "sectionId": "section-001",
        "examId": "exam-001",
        "type": "fill-blank",
        "content": "The author suggests that _______ is the most effective solution.",
        "options": None,
        "correctAnswer": ["renewable energy", "clean energy"],
        "points": 1,
        "tagIds": ["tag-005", "tag-003"],
        "skill": "reading",
    },
    {
        "id": "q-004",
        "lastEditedBy": "admin-001",
        "sectionId": "section-002",
        "examId": "exam-002",
        "type": "fill-blank",
        "content": "The meeting is scheduled for _______ next week.",
        "options": None,
        "correctAnswer": ["Thursday"],
        "points": 1,
        "tagIds": ["tag-006"],
        "skill": "listening",
    },
    {
        "id": "q-005",
        "lastEditedBy": "admin-001",
        "sectionId": "section-002",
        "examId": "exam-002",
        "type": "multiple-choice",
        "content": "What does the speaker say about the deadline?",
        "options": [
            "A) It has been extended",
            "B) It cannot be changed",
            "C) It depends on the team's progress",
            "D) It was set by the client",
        ],
        "correctAnswer": ["B"],
        "points": 1,
        "tagIds": ["tag-007"],
        "skill": "listening",
    },
    {
        "id": "q-006",
        "lastEditedBy": "admin-001",
        "sectionId": "section-003",
        "examId": "exam-003",
        "type": "multiple-choice",
        "content": "She _______ to the gym every morning before work.",
        "options": ["A) go", "B) goes", "C) going", "D) gone"],
        "correctAnswer": ["B"],
        "points": 1,
        "tagIds": ["tag-001"],
        "skill": "reading",
    },
    {
        "id": "q-007",
        "lastEditedBy": "admin-001",
        "sectionId": "section-003",
        "examId": "exam-003",
        "type": "multiple-choice",
        "content": "I have been waiting here _______ two hours.",
        "options": ["A) since", "B) for", "C) during", "D) while"],
        "correctAnswer": ["B"],
        "points": 1,
        "tagIds": ["tag-001"],
        "skill": "reading",
    },
    {
        "id": "q-008",
        "lastEditedBy": "admin-001",
        "sectionId": "section-003",
        "examId": "exam-003",
        "type": "multiple-choice",
        "content": "_______ University of Oxford is one of _______ oldest universities in the world.",
        "options": ["A) A / the", "B) The / the", "C) The / a", "D) - / the"],
        "correctAnswer": ["B"],
        "points": 1,
        "tagIds": ["tag-002"],
        "skill": "reading",
    },
]

# User's 5 latest test attempts with their choices (including wrong answers)
MOCK_ATTEMPTS = [
    {
        "id": "attempt-001",
        "userId": "user-001",
        "examId": "exam-001",
        "startTime": 1732838400000,  # Nov 29, 2025
        "timeLeft": 0,
        "isPaused": False,
        "score": 60,
        "choices": [
            {"questionId": "q-001", "answerIdx": "C"},  # Wrong (correct: A)
            {"questionId": "q-002", "answerIdx": "A"},  # Wrong (correct: B)
            {"questionId": "q-003", "answerIdx": "solar power"},  # Wrong (correct: renewable energy)
        ],
    },
    {
        "id": "attempt-002",
        "userId": "user-001",
        "examId": "exam-002",
        "startTime": 1732752000000,  # Nov 28, 2025
        "timeLeft": 0,
        "isPaused": False,
        "score": 50,
        "choices": [
            {"questionId": "q-004", "answerIdx": "Wednesday"},  # Wrong (correct: Thursday)
            {"questionId": "q-005", "answerIdx": "A"},  # Wrong (correct: B)
        ],
    },
    {
        "id": "attempt-003",
        "userId": "user-001",
        "examId": "exam-003",
        "startTime": 1732665600000,  # Nov 27, 2025
        "timeLeft": 0,
        "isPaused": False,
        "score": 33,
        "choices": [
            {"questionId": "q-006", "answerIdx": "A"},  # Wrong (correct: B)
            {"questionId": "q-007", "answerIdx": "A"},  # Wrong (correct: B)
            {"questionId": "q-008", "answerIdx": "A"},  # Wrong (correct: B)
        ],
    },
    {
        "id": "attempt-004",
        "userId": "user-001",
        "examId": "exam-003",
        "startTime": 1732579200000,  # Nov 26, 2025
        "timeLeft": 0,
        "isPaused": False,
        "score": 67,
        "choices": [
            {"questionId": "q-006", "answerIdx": "B"},  # Correct
            {"questionId": "q-007", "answerIdx": "A"},  # Wrong (correct: B)
            {"questionId": "q-008", "answerIdx": "D"},  # Wrong (correct: B)
        ],
    },
    {
        "id": "attempt-005",
        "userId": "user-001",
        "examId": "exam-001",
        "startTime": 1732492800000,  # Nov 25, 2025
        "timeLeft": 0,
        "isPaused": False,
        "score": 67,
        "choices": [
            {"questionId": "q-001", "answerIdx": "A"},  # Correct
            {"questionId": "q-002", "answerIdx": "C"},  # Wrong (correct: B)
            {"questionId": "q-003", "answerIdx": "renewable energy"},  # Correct
        ],
    },
]

# User's goal
MOCK_USER_GOAL = {
    "id": "goal-001",
    "userId": "user-001",
    "testType": "ielts",
    "target": 7.0,
    "dueDate": 1735689600000,  # Dec 31, 2025
}


def get_question_by_id(question_id: str) -> Optional[Dict]:
    """Helper function to get question by ID."""
    for q in MOCK_QUESTIONS:
        if q["id"] == question_id:
            return q
    return None


def get_exam_by_id(exam_id: str) -> Optional[Dict]:
    """Helper function to get exam by ID."""
    for e in MOCK_EXAMS:
        if e["id"] == exam_id:
            return e
    return None


def get_tag_names(tag_ids: List[str]) -> List[str]:
    """Helper function to convert tag IDs to names."""
    tag_map = {t["id"]: t["name"] for t in MOCK_TAGS}
    return [tag_map.get(tid, tid) for tid in tag_ids]


def get_user_attempts(user_id: str, limit: int = 5) -> List[Dict]:
    """Get user's most recent attempts."""
    user_attempts = [a for a in MOCK_ATTEMPTS if a["userId"] == user_id]
    user_attempts.sort(key=lambda x: x["startTime"], reverse=True)
    return user_attempts[:limit]
