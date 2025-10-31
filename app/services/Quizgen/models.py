# app/services/quizgen/models.py
from pydantic import BaseModel
from typing import List, Optional

class GenerateQuizRequest(BaseModel):
    course_id: Optional[int] = None        # optional content source id (if backend provides)
    seed_text: Optional[str] = None        # short text to focus questions on
    num_questions: int = 5
    difficulty: Optional[str] = "medium"  # "easy" | "medium" | "hard"
    question_types: Optional[List[str]] = None  # e.g. ["mcq","short","true_false"]

class MCQItem(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_index: int
    difficulty: Optional[str] = None
    rationale: Optional[str] = None

class ShortQItem(BaseModel):
    id: str
    question: str
    answer: str
    difficulty: Optional[str] = None

class TrueFalseItem(BaseModel):
    id: str
    question: str
    answer: bool
    difficulty: Optional[str] = None

class GenerateQuizResponse(BaseModel):
    quiz_id: str
    questions: List[BaseModel]   # contains MCQItem / ShortQItem / TrueFalseItem (serialized)
    metadata: dict
