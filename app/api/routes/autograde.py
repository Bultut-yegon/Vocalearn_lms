# app/api/routes/autograde.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.autograder.scoring import grade_short_answer

router = APIRouter(prefix="/api/autograde", tags=["AutoGrader"])

class RubricItem(BaseModel):
    id: str
    max_score: float
    description: str

class ShortGradeRequest(BaseModel):
    student_id: int
    question_id: str
    answer_text: str
    rubric: List[RubricItem]
    context: Optional[str] = None
    request_feedback: bool = True

@router.post("/short")
async def short_answer_autograde(req: ShortGradeRequest):
    try:
        result = grade_short_answer(req.dict())
        return {
            "student_id": req.student_id,
            "question_id": req.question_id,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
