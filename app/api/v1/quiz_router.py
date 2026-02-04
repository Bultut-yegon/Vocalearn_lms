
"""
Quiz Router 
Returns simple dict structure 
Location: app/api/v1/quiz_router.py
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Literal, Optional
from app.services.quiz_generation_service import QuizGenerationService
from app.core.logging_config import logger
import os

router = APIRouter()

# Initialize service
try:
    groq_api_key = os.getenv("GROQAPI_KEY")
    if not groq_api_key:
        logger.error(" GROQAPI_KEY not found")
        quiz_service = None
    else:
        quiz_service = QuizGenerationService(groq_api_key=groq_api_key)
        logger.info(" Quiz Generation Service initialized (Legacy Format)")
except Exception as e:
    logger.error(f" Failed to initialize Quiz Service: {e}")
    quiz_service = None



# REQUEST MODEL (Simplified - Legacy Format)


class QuizGenerationRequest(BaseModel):
    """Simple request model matching your original format."""
    content: str = Field(
        ...,
        min_length=100,
        description="The learning content"
    )
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = Field(
        default="intermediate"
    )
    num_mcq: int = Field(default=5, ge=0, le=20)
    num_true_false: int = Field(default=5, ge=0, le=20)
    num_short_answer: int = Field(default=2, ge=0, le=10)
    num_of_options: int = Field(default=4, ge=2, le=6)


class WeeklyQuizRequest(BaseModel):
    """Weekly quiz request - simplified."""
    course_id: str
    week_number: int = Field(..., ge=1)
    modules: list[str]
    combined_content: str = Field(..., min_length=100)
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    num_mcq: int = Field(default=5, ge=0, le=20)
    num_true_false: int = Field(default=5, ge=0, le=20)
    num_short_answer: int = Field(default=2, ge=0, le=10)



# HELPER CLASS (for internal use)


class _InternalRequest:
    """Internal wrapper to match service expectations."""
    def __init__(self, combined_content, difficulty_level, num_mcq, num_true_false, num_short_answer):
        self.combined_content = combined_content
        self.difficulty_level = difficulty_level
        self.num_mcq = num_mcq
        self.num_true_false = num_true_false
        self.num_short_answer = num_short_answer



# ENDPOINTS

def check_service():
    """Verify service is available."""
    if quiz_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Quiz generation service unavailable. Check GROQAPI_KEY."
        )


@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
    summary="Generate quiz (Legacy format)"
)
async def generate_quiz(request: QuizGenerationRequest):
    """
    Generate quiz from content - returns LEGACY format.
    
    **Request Example:**
    ```json
    {
      "content": "Circuit breakers are automatic electrical switches...",
      "difficulty_level": "intermediate",
      "num_mcq": 5,
      "num_true_false": 5,
      "num_short_answer": 2,
      "num_of_options": 4
    }
    ```
    
    **Returns:** Quiz in legacy format (simple dicts)
    """
    check_service()
    
    try:
        logger.info(f" Generating quiz (Legacy): MCQ={request.num_mcq}, T/F={request.num_true_false}, SA={request.num_short_answer}")
        
        # Create internal request
        internal_req = _InternalRequest(
            combined_content=request.content,
            difficulty_level=request.difficulty_level,
            num_mcq=request.num_mcq,
            num_true_false=request.num_true_false,
            num_short_answer=request.num_short_answer
        )
        
        # Generate quiz
        quiz = await quiz_service.generate_weekly_quiz(internal_req)
        
        logger.info(f" Quiz generated: {quiz['quiz_id']} ({quiz['total_questions']} questions)")
        
        return quiz
        
    except ValueError as ve:
        logger.error(f" Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f" Quiz generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quiz generation failed: {str(e)}"
        )


@router.post(
    "/generate-weekly",
    status_code=status.HTTP_201_CREATED,
    summary="Generate weekly quiz (Legacy format)"
)
async def generate_weekly_quiz(request: WeeklyQuizRequest):
    """
    Generate weekly quiz - returns LEGACY format.
    
    **Request Example:**
    ```json
    {
      "course_id": "TVET-ELEC-101",
      "week_number": 1,
      "modules": ["Circuit Breakers", "Safety"],
      "combined_content": "Circuit breakers are...",
      "difficulty_level": "intermediate",
      "num_mcq": 5,
      "num_true_false": 5,
      "num_short_answer": 2
    }
    ```
    """
    check_service()
    
    try:
        logger.info(f" Generating weekly quiz: Course={request.course_id}, Week={request.week_number}")
        
        # Create internal request
        internal_req = _InternalRequest(
            combined_content=request.combined_content,
            difficulty_level=request.difficulty_level,
            num_mcq=request.num_mcq,
            num_true_false=request.num_true_false,
            num_short_answer=request.num_short_answer
        )
        
        # Generate quiz
        quiz = await quiz_service.generate_weekly_quiz(internal_req)
        
        logger.info(f"Weekly quiz generated: {quiz['quiz_id']}")
        
        return quiz
        
    except Exception as e:
        logger.error(f"Weekly quiz generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weekly quiz: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check service health."""
    if quiz_service is None:
        return {
            "status": "unavailable",
            "service": "quiz_generation",
            "error": "GROQAPI_KEY not configured"
        }
    
    return {
        "status": "healthy",
        "service": "quiz_generation",
        "format": "legacy",
        "model": quiz_service.model
    }


@router.get("/example")
async def get_example():
    """Get example request."""
    return {
        "description": "Quiz generation request (Legacy format)",
        "example": {
            "content": "Circuit breakers are automatic electrical switches designed to protect electrical circuits from damage caused by overcurrent. When excessive current flows through a circuit, the circuit breaker trips and interrupts the flow of electricity. There are three main types of circuit breakers: Thermal circuit breakers use a bimetallic strip that bends when heated by excessive current, triggering the breaker to trip. Magnetic circuit breakers use an electromagnet that becomes strong enough to pull contacts apart when current exceeds safe levels. Thermal-magnetic circuit breakers combine both mechanisms for comprehensive protection against overloads and short circuits.",
            "difficulty_level": "intermediate",
            "num_mcq": 5,
            "num_true_false": 5,
            "num_short_answer": 2,
            "num_of_options": 4
        },
        "expected_response": {
            "quiz_id": "quiz_abc123",
            "generated_at": "2025-01-17T...",
            "difficulty_level": "intermediate",
            "total_questions": 12,
            "multiple_choice": [
                {
                    "question": "What is the primary function of circuit breakers?",
                    "options": {
                        "A": "To increase voltage",
                        "B": "To protect circuits from overcurrent",
                        "C": "To reduce current",
                        "D": "To replace fuses"
                    },
                    "correct_answer": "B",
                    "explanation": "Circuit breakers protect circuits from overcurrent damage."
                }
            ],
            "true_false": [
                {
                    "question": "Circuit breakers can be reset and reused.",
                    "correct_answer": True,
                    "explanation": "Unlike fuses, circuit breakers are reusable."
                }
            ],
            "short_answer": [
                {
                    "question": "Explain the main types of circuit breakers.",
                    "key_points": ["Thermal", "Magnetic", "Thermal-magnetic"],
                    "sample_answer": "The main types are thermal, magnetic, and thermal-magnetic..."
                }
            ]
        }
    }