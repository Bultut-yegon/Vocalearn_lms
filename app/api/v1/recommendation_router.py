"""
Module-Based Recommendation Router 
Location: app/api/v1/recommendation_router.py
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from app.models.recommendation_models import (
    RecommendationRequest,
    RecommendationResult,
    ModuleReview,
    CollectiveFeedback,
    OverallPerformance,
    WeakQuestionType
)

from app.services.recommendation_service import RecommendationService
from app.core.logging_config import logger

router = APIRouter()

# Initialize service
try:
    recommendation_service = RecommendationService()
    logger.info(" Module-Based Recommendation Service initialized")
except Exception as e:
    logger.error(f"Failed to initialize Recommendation Service: {e}")
    recommendation_service = None


def check_service():
    """Verify service is available"""
    if recommendation_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation service unavailable. Check logs for initialization errors."
        )


@router.post(
    "/analyze",
    response_model=RecommendationResult,
    status_code=status.HTTP_200_OK,
    summary="Generate specific, actionable learning recommendations",
    description="Analyzes student quiz performance and provides targeted feedback on specific content to study"
)
async def analyze_performance(request: RecommendationRequest):
    """
    **Generate Content-Specific Recommendations**
    
    Provides two levels of feedback:
    
    **Individual Module Reviews:**
    -  Score, percentage, and performance level
    -  AI-generated specific feedback
    -  Concepts to review from failed questions
    
    **Collective Feedback:**
    -  Overall performance summary
    -  Critical gaps - SPECIFIC topics and concepts needing study
    -  Recommendations - CONCRETE study actions (what content to review and how)
    -  Question types to practice
    
    **Key Features:**
    - References actual content (e.g., "PPE requirements", "RMS calculations")
    - No generic "review module 1" - tells you exactly what to study
    - Actionable steps based on what you got wrong
    """
    check_service()
    
    try:
        logger.info(
            f"Analyzing performance for {request.student_id}: "
            f"{len(request.modules)} module(s)"
        )
        
        # Convert to dicts for processing
        modules = [
            {
                "module_id": module.module_id,
                "module_name": module.module_name,
                "module_content": module.module_content,
                "max_score": module.max_score,
                "question_results": [q.model_dump() for q in module.question_results]
            }
            for module in request.modules
        ]
        
        # Generate recommendations
        result = await recommendation_service.generate_recommendations(modules)
        
        # Build response with proper nested models

        
        individual_reviews = [
            ModuleReview(**review)
            for review in result["individual_module_reviews"]
        ]
        
        collective = result["collective_feedback"]
        collective_feedback = CollectiveFeedback(
            overall_performance=OverallPerformance(**collective["overall_performance"]),
            critical_gaps=collective["critical_gaps"],
            recommendations=collective["recommendations"],
            weak_question_types=[WeakQuestionType(**qt) for qt in collective["weak_question_types"]],
            total_failed_questions=collective["total_failed_questions"]
        )
        
        response = RecommendationResult(
            student_id=request.student_id,
            individual_module_reviews=individual_reviews,
            collective_feedback=collective_feedback,
            generated_at=datetime.now().isoformat()
        )
        
        logger.info(
            f"Recommendations generated for {request.student_id}: "
            f"{len(individual_reviews)} module(s), "
            f"Overall: {collective_feedback.overall_performance.percentage:.1f}%"
        )
        
        return response
        
    except ValueError as ve:
        logger.error(f" Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get("/health", summary="Check recommendation service health")
async def health_check():
    """Health check endpoint"""
    if recommendation_service is None:
        return {
            "status": "unavailable",
            "service": "module-recommendation",
            "error": "Service not initialized"
        }
    
    return {
        "status": "healthy",
        "service": "module-recommendation",
        "features": [
            "content_specific_analysis",
            "actionable_recommendations",
            "no_generic_module_references",
            "question_level_feedback",
            "ai_powered_insights"
        ]
    }


@router.get("/example", summary="Get example request format")
async def get_example():
    """Get example showing correct input format"""
    return {
        "description": "Module-based recommendation request format",
        "note": "Provide actual learning content, not summaries",
        "example": {
            "student_id": "student_123",
            "modules": [
                {
                    "module_id": "safety_101",
                    "module_name": "Electrical Safety",
                    "module_content": "Full learning material text here. Include all concepts, definitions, procedures...",
                    "max_score": 25,
                    "question_results": [
                        {
                            "question_text": "What is LOTO?",
                            "student_answer": "Lockout Tagout",
                            "correct_answer": "Lockout/Tagout - procedure to ensure energy sources are isolated",
                            "awarded_marks": 4,
                            "max_marks": 5,
                            "question_type": "short_answer",
                            "is_correct": True
                        }
                    ]
                }
            ]
        },
        "output_features": {
            "individual_reviews": "Feedback per module with specific concepts to review",
            "collective_feedback": {
                "critical_gaps": "Specific topics and concepts needing study (not 'module 1, module 2')",
                "recommendations": "Concrete study actions - exactly what content to review and how",
                "no_module_lists": "Removed redundant weak_modules and strong_modules lists"
            }
        }
    }