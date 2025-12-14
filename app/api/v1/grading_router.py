from fastapi import APIRouter, HTTPException, status
from app.models.grading_models import (
    GradingRequest,
    GradingResult,
    QuestionGradeResult
)
from app.services.grading_service import GradingService
from app.core.logging_config import logger

router = APIRouter()
grading_service = GradingService()

@router.post(
    "/grade",
    response_model=GradingResult,
    summary="Grade student submission",
    description="Auto-grade both closed and open-ended questions with AI-powered evaluation"
)
async def grade_submission(request: GradingRequest):
    """
    Comprehensive auto-grading for student submissions.
    
    Features:
    - Fast deterministic grading for MCQs and True/False
    - LLM-powered evaluation for open-ended questions
    - Partial credit for open-ended responses
    - Detailed feedback per question
    - Overall performance analysis
    - Topic mastery breakdown
    
    Returns complete grading results with scores, feedback, and recommendations.
    """
    try:
        logger.info(f"Grading submission {request.submission_id} for student {request.student_id}")
        
        # Convert Pydantic models to dicts
        closed_questions = [q.model_dump() for q in request.closed_ended_questions]
        open_questions = [q.model_dump() for q in request.open_ended_questions]
        
        # Grade the submission
        result = await grading_service.grade_submission(
            submission_id=request.submission_id,
            student_id=request.student_id,
            topic=request.topic,
            closed_ended_questions=closed_questions,
            open_ended_questions=open_questions
        )
        
        logger.info(f"Successfully graded submission {request.submission_id}: {result['percentage']:.1f}%")
        return GradingResult(**result)
        
    except Exception as e:
        logger.error(f"Grading failed for submission {request.submission_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to grade submission: {str(e)}"
        )

@router.post(
    "/grade-batch",
    summary="Grade multiple submissions in batch",
    description="Process multiple student submissions efficiently"
)
async def grade_batch(requests: list[GradingRequest]):
    """
    Batch grading for multiple submissions.
    Useful for grading entire class assessments.
    """
    try:
        results = []
        
        for request in requests:
            closed_questions = [q.model_dump() for q in request.closed_ended_questions]
            open_questions = [q.model_dump() for q in request.open_ended_questions]
            
            result = await grading_service.grade_submission(
                submission_id=request.submission_id,
                student_id=request.student_id,
                topic=request.topic,
                closed_ended_questions=closed_questions,
                open_ended_questions=open_questions
            )
            
            results.append(result)
            logger.info(f"Batch graded: {request.submission_id}")
        
        return {
            "total_graded": len(results),
            "results": results,
            "batch_summary": {
                "average_score": sum(r["percentage"] for r in results) / len(results) if results else 0,
                "highest_score": max((r["percentage"] for r in results), default=0),
                "lowest_score": min((r["percentage"] for r in results), default=0)
            }
        }
        
    except Exception as e:
        logger.error(f"Batch grading failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch grading failed: {str(e)}"
        )

@router.get(
    "/health",
    summary="Check grading service health"
)
async def health_check():
    """Health check endpoint for grading service."""
    return {
        "status": "healthy",
        "service": "auto-grading",
        "features": [
            "closed_ended_grading",
            "open_ended_grading",
            "llm_evaluation",
            "partial_credit",
            "detailed_feedback",
            "topic_mastery_analysis",
            "batch_processing"
        ],
        "supported_question_types": [
            "mcq",
            "true_false",
            "short_answer",
            "essay",
            "practical"
        ]
    }