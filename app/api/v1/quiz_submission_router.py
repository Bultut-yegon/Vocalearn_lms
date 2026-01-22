"""
Quiz Submission Router
Endpoint: /api/v1/submissions
Handles quiz submission with instant grading + recommendations
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.services.intergrated_quiz_submission_service import QuizSubmissionService
from app.core.logging_config import logger

router = APIRouter()

# Initialize service
submission_service = QuizSubmissionService()



# REQUEST/RESPONSE MODELS


class PerformanceRecord(BaseModel):
    """Historical performance record"""
    topic: str
    score: float
    max_score: float
    percentage: Optional[float] = None
    timestamp: Optional[str] = None
    module_id: Optional[str] = None
    week_number: Optional[int] = None


class QuizSubmissionRequest(BaseModel):
    """Complete quiz submission with optional history"""
    submission_id: str = Field(..., description="Unique submission ID")
    student_id: str = Field(..., description="Student identifier")
    quiz_data: Dict = Field(..., description="Quiz structure from generation service")
    student_answers: Dict[str, str] = Field(
        ...,
        description="Student's answers: {'mcq_0': 'B', 'tf_1': 'true', 'sa_2': 'answer text'}"
    )
    performance_history: Optional[List[PerformanceRecord]] = Field(
        default=None,
        description="Optional: Student's past performance for better recommendations"
    )


class ProgressSummaryRequest(BaseModel):
    """Request for student progress summary"""
    student_id: str
    performance_history: List[PerformanceRecord]



# ENDPOINTS


@router.post(
    "/submit-quiz",
    summary="Submit quiz and get instant feedback + recommendations",
    description="Complete submission flow: grading → recommendations → actionable insights"
)
async def submit_quiz(request: QuizSubmissionRequest):
    """
    **Complete Quiz Submission Flow**
    
    This endpoint:
    1. Grades the quiz (MCQ, T/F, Short Answer)
    2. Analyzes performance across question types
    3. Compares with historical performance (if provided)
    4. Generates personalized recommendations
    5. Provides actionable next steps
    
    **Request Example:**
    ```json
    {
      "submission_id": "sub_123",
      "student_id": "student_456",
      "quiz_data": {
        "quiz_id": "quiz_abc",
        "topic": "Week 1 - Circuit Breakers",
        "mcq_questions": [...],
        "true_false_questions": [...],
        "open_ended_questions": [...]
      },
      "student_answers": {
        "mcq_0": "B",
        "mcq_1": "A",
        "tf_0": "true",
        "sa_0": "Circuit breakers use bimetallic strips..."
      },
      "performance_history": [
        {
          "topic": "Safety Procedures",
          "score": 8,
          "max_score": 10,
          "percentage": 80,
          "week_number": 0
        }
      ]
    }
    ```
    
    **Returns:** Complete feedback package with grading, analysis, and personalized recommendations
    """
    try:
        logger.info(f" Quiz submission received: {request.submission_id}")
        
        # Convert performance history to dicts
        performance_history = None
        if request.performance_history:
            performance_history = [p.model_dump() for p in request.performance_history]
        
        # Process submission
        result = await submission_service.process_quiz_submission(
            submission_id=request.submission_id,
            student_id=request.student_id,
            quiz_data=request.quiz_data,
            student_answers=request.student_answers,
            performance_history=performance_history
        )
        
        logger.info(
            f" Submission processed: {request.submission_id} | "
            f"Score: {result['grading']['percentage']:.1f}% | "
            f"Recommendations: {len(result['recommendations']['priority_topics'])} topics"
        )
        
        return result
        
    except Exception as e:
        logger.error(f" Submission processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process quiz submission: {str(e)}"
        )


@router.post(
    "/student-progress",
    summary="Get comprehensive student progress summary",
    description="Overall performance analysis and long-term recommendations"
)
async def get_student_progress(request: ProgressSummaryRequest):
    """
    **Student Progress Dashboard**
    
    Analyzes complete performance history to provide:
    - Overall progress metrics
    - Improvement trends
    - Strengths and weaknesses
    - Comprehensive study plan
    
    **Use Case:** Student dashboard, progress reports, parent updates
    
    **Request Example:**
    ```json
    {
      "student_id": "student_456",
      "performance_history": [
        {
          "topic": "Week 1 - Circuit Breakers",
          "score": 45,
          "max_score": 51,
          "percentage": 88.2,
          "week_number": 1
        },
        {
          "topic": "Week 2 - Wiring Basics",
          "score": 38,
          "max_score": 48,
          "percentage": 79.2,
          "week_number": 2
        }
      ]
    }
    ```
    """
    try:
        logger.info(f" Progress summary requested for student: {request.student_id}")
        
        performance_history = [p.model_dump() for p in request.performance_history]
        
        summary = await submission_service.get_student_progress_summary(
            student_id=request.student_id,
            performance_history=performance_history
        )
        
        logger.info(
            f" Progress summary generated for {request.student_id}: "
            f"Avg: {summary.get('summary', {}).get('average_score', 0):.1f}%"
        )
        
        return summary
        
    except Exception as e:
        logger.error(f" Progress summary failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate progress summary: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check submission service health"""
    return {
        "status": "healthy",
        "service": "quiz_submission",
        "features": [
            "instant_grading",
            "performance_analysis",
            "personalized_recommendations",
            "progress_tracking",
            "ai_insights"
        ],
        "endpoints": {
            "submit_quiz": "/submit-quiz",
            "student_progress": "/student-progress"
        }
    }


@router.get("/example-submission")
async def get_example_submission():
    """
    Get example submission request format.
    Useful for testing and integration.
    """
    return {
        "description": "Complete quiz submission with recommendations",
        "example_request": {
            "submission_id": "sub_20250117_001",
            "student_id": "student_456",
            "quiz_data": {
                "quiz_id": "quiz_abc123",
                "topic": "Week 1 - Circuit Breakers",
                "difficulty_level": "intermediate",
                "mcq_questions": [
                    {
                        "question_text": "What is the primary function of a circuit breaker?",
                        "options": [
                            {"option_id": "A", "text": "Store electricity"},
                            {"option_id": "B", "text": "Protect from overcurrent"},
                            {"option_id": "C", "text": "Convert voltage"},
                            {"option_id": "D", "text": "Generate power"}
                        ],
                        "correct_answer": "B",
                        "explanation": "Circuit breakers protect circuits from overcurrent",
                        "difficulty": "intermediate",
                        "topic": "Week 1",
                        "points": 5.0
                    }
                ],
                "true_false_questions": [
                    {
                        "question_text": "Thermal breakers use a bimetallic strip.",
                        "correct_answer": True,
                        "explanation": "Correct - thermal breakers use bimetallic strips",
                        "difficulty": "intermediate",
                        "topic": "Week 1",
                        "points": 3.0
                    }
                ],
                "open_ended_questions": [
                    {
                        "question_text": "Explain how a thermal circuit breaker works.",
                        "rubric": "Should mention bimetallic strip, heat, bending, circuit interruption",
                        "sample_answer": "A thermal breaker uses a bimetallic strip...",
                        "keywords": ["bimetallic", "heat", "trip", "current"],
                        "difficulty": "intermediate",
                        "topic": "Week 1",
                        "points": 10.0
                    }
                ],
                "generation_metadata": {
                    "course_id": "TVET-ELEC-101",
                    "week_number": 1
                }
            },
            "student_answers": {
                "mcq_0": "B",
                "tf_0": "true",
                "sa_0": "A thermal circuit breaker uses a bimetallic strip that heats up when current flows. The strip bends due to different expansion rates, which trips the breaker."
            },
            "performance_history": [
                {
                    "topic": "Week 0 - Introduction",
                    "score": 8,
                    "max_score": 10,
                    "percentage": 80,
                    "week_number": 0
                }
            ]
        },
        "expected_response_structure": {
            "submission_id": "string",
            "student_id": "string",
            "grading": {
                "total_points": "number",
                "max_points": "number",
                "percentage": "number",
                "grade_letter": "string",
                "overall_feedback": "string"
            },
            "question_results": "array",
            "performance_analysis": {
                "current_score": "number",
                "strengths": "array",
                "areas_for_improvement": "array",
                "urgent_review_needed": "array"
            },
            "recommendations": {
                "priority_topics": "array",
                "study_plan": "object",
                "next_steps": "array"
            },
            "ai_insights": {
                "explanation": "string",
                "motivational_message": "string"
            }
        }
    }