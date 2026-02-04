
"""
Simple Grading Router 
Returns only grading results without extra analytics
Location: app/api/v1/grading_router.py
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict
from app.services.grading_service import GradingService
from app.core.logging_config import logger

router = APIRouter()

# Initialize service
try:
    grading_service = GradingService()
    logger.info(" Grading Service initialized")
except Exception as e:
    logger.error(f" Failed to initialize Grading Service: {e}")
    grading_service = None


# ============================================================================
# REQUEST MODEL
# ============================================================================

class SimpleGradingRequest(BaseModel):
    """Simple grading request - just quiz and answers."""
    submission_id: str
    student_id: str
    quiz_id: str
    topic: str = Field(default="General Assessment")
    quiz_data: Dict
    student_answers: Dict[str, str]


# ============================================================================
# ENDPOINT
# ============================================================================

def check_service():
    """Verify service is available."""
    if grading_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Grading service unavailable."
        )


@router.post(
    "/grade-quiz",
    status_code=status.HTTP_200_OK,
    summary="Grade quiz - Simple output"
)
async def grade_quiz(request: SimpleGradingRequest):
    """
    Grade a quiz and return clean, simple results.
    
    **Returns only:**
    - submission_id
    - student_id
    - topic
    - total_points
    - max_points
    - percentage
    - grade_letter
    - question_results
    - overall_feedback
    - topic_mastery
    - graded_at
    
    **No extra analytics, recommendations, or AI insights.**
    
    **Request Example:**
    ```json
    {
      "submission_id": "sub_001",
      "student_id": "student_123",
      "quiz_id": "quiz_abc",
      "topic": "Circuit Breakers",
      "quiz_data": {
        "quiz_id": "quiz_abc",
        "multiple_choice": [...],
        "true_false": [...],
        "short_answer": [...]
      },
      "student_answers": {
        "mcq_0": "B",
        "tf_0": "true",
        "sa_0": "answer text"
      }
    }
    ```
    """
    check_service()
    
    try:
        logger.info(f"Grading quiz for {request.student_id}")
        
        # Grade the quiz
        result = await grading_service.grade_quiz_from_generation_service(
            submission_id=request.submission_id,
            student_id=request.student_id,
            quiz_data=request.quiz_data,
            student_answers=request.student_answers
        )
        
        # Return ONLY the essential grading information
        clean_result = {
            "submission_id": result["submission_id"],
            "student_id": result["student_id"],
            "topic": result["topic"],
            "total_points": result["total_points"],
            "max_points": result["max_points"],
            "percentage": result["percentage"],
            "grade_letter": result["grade_letter"],
            "question_results": result["question_results"],
            "overall_feedback": result["overall_feedback"],
            "topic_mastery": result["topic_mastery"],
            "graded_at": result["graded_at"]
        }
        
        logger.info(
            f"Graded {request.submission_id}: "
            f"{clean_result['percentage']:.1f}% ({clean_result['grade_letter']})"
        )
        
        return clean_result
        
    except Exception as e:
        logger.error(f" Grading failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Grading failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check grading service health."""
    if grading_service is None:
        return {
            "status": "unavailable",
            "service": "grading"
        }
    
    return {
        "status": "healthy",
        "service": "grading",
        "format": "simple",
        "features": [
            "mcq_grading",
            "true_false_grading",
            "short_answer_grading_with_llm"
        ]
    }


@router.get("/example")
async def get_example():
    """Get example request and response."""
    return {
        "description": "Simple grading - clean output",
        "example_request": {
            "submission_id": "sub_001",
            "student_id": "student_123",
            "quiz_id": "quiz_abc",
            "topic": "Circuit Breakers",
            "quiz_data": {
                "quiz_id": "quiz_abc",
                "multiple_choice": [
                    {
                        "question": "What protects circuits?",
                        "options": {"A": "Fuses", "B": "Breakers", "C": "Wires", "D": "Switches"},
                        "correct_answer": "B",
                        "explanation": "Circuit breakers protect circuits."
                    }
                ],
                "true_false": [
                    {
                        "question": "Breakers can be reused.",
                        "correct_answer": True,
                        "explanation": "They can be reset."
                    }
                ],
                "short_answer": [
                    {
                        "question": "Explain thermal breakers.",
                        "key_points": ["bimetallic strip", "heat", "trip"],
                        "sample_answer": "Thermal breakers use bimetallic strips..."
                    }
                ]
            },
            "student_answers": {
                "mcq_0": "B",
                "tf_0": "true",
                "sa_0": "Thermal breakers use a strip that bends when hot."
            }
        },
        "expected_response": {
            "submission_id": "sub_001",
            "student_id": "student_123",
            "topic": "Circuit Breakers",
            "total_points": 3.8,
            "max_points": 4,
            "percentage": 95.0,
            "grade_letter": "A",
            "question_results": [
                {
                    "question_id": "mcq_0",
                    "question_type": "mcq",
                    "max_points": 1,
                    "awarded_points": 1,
                    "is_correct": True,
                    "feedback": "Correct! Well done.",
                    "strengths": ["Accurate response"],
                    "improvements": None
                }
            ],
            "overall_feedback": "Excellent work! You've demonstrated strong mastery.",
            "topic_mastery": {
                "Circuit Breakers": 95.0
            },
            "graded_at": "2026-01-25T..."
        }
    }