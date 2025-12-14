# from fastapi import APIRouter, HTTPException
# from app.models.recommendation_models import RecommendationRequest, RecommendationResult
# from app.services.recommendation_service import RecommendationService

# router = APIRouter(prefix="/recommendation", tags=["Recommendation"])
# service = RecommendationService()


# @router.post("/generate", response_model=RecommendationResult)
# async def generate_recommendation(request: RecommendationRequest):
#     try:
#         return await service.generate_recommendations(request)

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail="Recommendation engine failure. Contact system admin."
#         )

from fastapi import APIRouter, HTTPException, status
from app.models.recommendation_models import (
    RecommendationRequest,
    RecommendationResult
)
from app.services.recommendation_service import RecommendationService
from app.core.logging_config import logger

router = APIRouter()
recommendation_service = RecommendationService()

@router.post(
    "/analyze",
    response_model=RecommendationResult,
    summary="Generate personalized recommendations",
    description="Analyzes student performance and generates personalized learning recommendations"
)
async def analyze_performance(request: RecommendationRequest):
    """
    Generates AI-powered recommendations based on student performance.
    
    Returns:
    - Prioritized topic recommendations
    - Customized study plan
    - Identified strengths
    - Performance trends
    - Motivational message
    - LLM-generated insights
    """
    try:
        logger.info(f"Analyzing performance for {len(request.performance_history)} records")
        
        # Convert Pydantic models to dicts for processing
        performance_history = [
            record.model_dump() for record in request.performance_history
        ]
        
        # Generate recommendations
        result = await recommendation_service.generate_recommendations(
            performance_history=performance_history,
            topic_scores=request.topic_scores
        )
        
        logger.info("Successfully generated recommendations")
        return RecommendationResult(**result)
        
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@router.get(
    "/health",
    summary="Check recommendation service health"
)
async def health_check():
    """Health check endpoint for recommendation service."""
    return {
        "status": "healthy",
        "service": "recommendation",
        "features": [
            "performance_analysis",
            "trend_detection",
            "study_plan_generation",
            "llm_insights"
        ]
    }