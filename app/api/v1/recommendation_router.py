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

# """recommendation router"""

# from fastapi import APIRouter, HTTPException, status
# from app.models.recommendation_models import (
#     RecommendationRequest,
#     RecommendationResult
# )
# from app.services.recommendation_service import RecommendationService
# from app.core.logging_config import logger

# router = APIRouter()
# recommendation_service = RecommendationService()

# @router.post(
#     "/analyze",
#     response_model=RecommendationResult,
#     summary="Generate personalized recommendations",
#     description="Analyzes student performance and generates personalized learning recommendations"
# )
# async def analyze_performance(request: RecommendationRequest):
#     """
#     Generates AI-powered recommendations based on student performance.
    
#     Returns:
#     - Prioritized topic recommendations
#     - Customized study plan
#     - Identified strengths
#     - Performance trends
#     - Motivational message
#     - LLM-generated insights
#     """
#     try:
#         logger.info(f"Analyzing performance for {len(request.performance_history)} records")
        
#         # Convert Pydantic models to dicts for processing
#         performance_history = [
#             record.model_dump() for record in request.performance_history
#         ]

#         result = await recommendation_service.generate_recommendations(performance_history=performance_history,topic_scores=request.topic_scores)

#         return RecommendationResult(**result)

        
#     except Exception as e:
#         logger.error(f"Recommendation generation failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate recommendations: {str(e)}"
#         )

# @router.get(
#     "/health",
#     summary="Check recommendation service health"
# )
# async def health_check():
#     """Health check endpoint for recommendation service."""
#     return {
#         "status": "healthy",
#         "service": "recommendation",
#         "features": [
#             "performance_analysis",
#             "trend_detection",
#             "study_plan_generation",
#             "llm_insights"
#         ]
#     }







# VERSION 2









"""
Recommendation Router - PRODUCTION READY
Endpoint: /api/v1/recommendations
Location: app/api/v1/recommendation_router.py
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.services.recommendation_service import RecommendationService
from app.core.logging_config import logger

router = APIRouter()

# Initialize service
try:
    recommendation_service = RecommendationService()
    logger.info(" Recommendation Service initialized")
except Exception as e:
    logger.error(f" Failed to initialize Recommendation Service: {e}")
    recommendation_service = None



# REQUEST/RESPONSE MODELS


class PerformanceRecord(BaseModel):
    """Single performance record from student history"""
    topic: str = Field(..., description="Topic or module name")
    score: float = Field(..., ge=0, description="Points earned")
    max_score: float = Field(..., gt=0, description="Total possible points")
    percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage score")
    timestamp: Optional[str] = Field(None, description="When quiz was taken")
    module_id: Optional[str] = Field(None, description="Course/module identifier")
    week_number: Optional[int] = Field(None, ge=0, description="Week number")


class RecommendationRequest(BaseModel):
    """Request for generating recommendations"""
    student_id: str = Field(..., description="Student identifier")
    performance_history: List[PerformanceRecord] = Field(
        ...,
        min_items=1,
        description="Student's quiz performance history"
    )
    topic_scores: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional: Additional topic scores (0-1 normalized)"
    )


class StudyPlanSection(BaseModel):
    """Section of personalized study plan"""
    topics: List[str]
    reason: str
    suggested_hours: float


class StudyPlan(BaseModel):
    """Complete study plan"""
    urgent_review: StudyPlanSection
    skill_building: StudyPlanSection
    advancement: StudyPlanSection


class RecommendationResult(BaseModel):
    """Complete recommendation response"""
    student_id: str
    topic_recommendations: List[str] = Field(description="Prioritized list of topics to focus on")
    study_plan: StudyPlan
    strengths: List[str] = Field(description="Topics where student excels")
    trends: Dict[str, str] = Field(description="Performance trends per topic")
    motivational_message: str
    llm_explanation: str
    generated_at: str



# ENDPOINTS


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
    summary="Generate personalized learning recommendations",
    description="Analyzes student performance and generates AI-powered personalized recommendations"
)
async def analyze_performance(request: RecommendationRequest):
    """
    **Generate Personalized Recommendations**
    
    Analyzes student's performance history to provide:
    -  Performance strengths and weaknesses
    -  Trend analysis (improving/declining/stable)
    -  Prioritized study plan
    -  AI-generated insights and motivation
    -  Actionable next steps
    
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
          "week_number": 1,
          "timestamp": "2025-01-10T10:00:00"
        },
        {
          "topic": "Week 2 - Wiring Basics",
          "score": 30,
          "max_score": 48,
          "percentage": 62.5,
          "week_number": 2,
          "timestamp": "2025-01-15T10:00:00"
        }
      ],
      "topic_scores": {
        "Circuit Breakers": 0.88,
        "Wiring Basics": 0.62
      }
    }
    ```
    
    **Returns:** Complete recommendation package with study plan and AI insights
    """
    check_service()
    
    try:
        logger.info(
            f"Analyzing performance for {request.student_id}: "
            f"{len(request.performance_history)} records"
        )
        
        # Convert Pydantic models to dicts for processing
        performance_history = [record.model_dump() for record in request.performance_history]
        
        # Generate recommendations
        result = await recommendation_service.generate_recommendations(
            performance_history=performance_history,
            topic_scores=request.topic_scores
        )
        
        # Add metadata
        from datetime import datetime
        response = RecommendationResult(
            student_id=request.student_id,
            topic_recommendations=result["topic_recommendations"],
            study_plan=StudyPlan(**result["study_plan"]),
            strengths=result["strengths"],
            trends=result["trends"],
            motivational_message=result["motivational_message"],
            llm_explanation=result["llm_explanation"],
            generated_at=datetime.now().isoformat()
        )
        
        logger.info(
            f"Recommendations generated for {request.student_id}: "
            f"{len(response.topic_recommendations)} priority topics, "
            f"{len(response.strengths)} strengths identified"
        )
        
        return response
        
    except ValueError as ve:
        logger.error(f" Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f" Recommendation generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get(
    "/health",
    summary="Check recommendation service health"
)
async def health_check():
    """Health check endpoint"""
    if recommendation_service is None:
        return {
            "status": "unavailable",
            "service": "recommendation",
            "error": "Service not initialized"
        }
    
    return {
        "status": "healthy",
        "service": "recommendation",
        "features": [
            "performance_analysis",
            "trend_detection",
            "personalized_study_plans",
            "ai_insights",
            "strength_weakness_identification"
        ],
        "endpoints": {
            "analyze": "/analyze",
            "health": "/health",
            "example": "/example"
        }
    }


@router.get(
    "/example",
    summary="Get example request format"
)
async def get_example():
    """
    Get example request format for recommendation generation.
    Useful for testing and API integration.
    """
    return {
        "description": "Recommendation generation request format",
        "example_request": {
            "student_id": "student_456",
            "performance_history": [
                {
                    "topic": "Week 1 - Circuit Breakers",
                    "score": 45.0,
                    "max_score": 51.0,
                    "percentage": 88.2,
                    "week_number": 1,
                    "module_id": "TVET-ELEC-101",
                    "timestamp": "2025-01-10T10:00:00"
                },
                {
                    "topic": "Week 2 - Wiring Basics",
                    "score": 30.0,
                    "max_score": 48.0,
                    "percentage": 62.5,
                    "week_number": 2,
                    "module_id": "TVET-ELEC-101",
                    "timestamp": "2025-01-15T10:00:00"
                },
                {
                    "topic": "Week 3 - Safety Procedures",
                    "score": 42.0,
                    "max_score": 45.0,
                    "percentage": 93.3,
                    "week_number": 3,
                    "module_id": "TVET-ELEC-101",
                    "timestamp": "2025-01-17T10:00:00"
                }
            ],
            "topic_scores": {
                "Circuit Breakers": 0.88,
                "Wiring Basics": 0.62,
                "Safety Procedures": 0.93
            }
        },
        "expected_response": {
            "student_id": "student_456",
            "topic_recommendations": [
                "Wiring Basics"
            ],
            "study_plan": {
                "urgent_review": {
                    "topics": [],
                    "reason": "Performance is declining - immediate attention needed",
                    "suggested_hours": 0
                },
                "skill_building": {
                    "topics": ["Wiring Basics"],
                    "reason": "Below mastery threshold - foundational work needed",
                    "suggested_hours": 2
                },
                "advancement": {
                    "topics": ["Circuit Breakers", "Safety Procedures"],
                    "reason": "Strong foundation - ready for advanced concepts",
                    "suggested_hours": 3.0
                }
            },
            "strengths": ["Circuit Breakers", "Safety Procedures"],
            "trends": {
                "Week 1 - Circuit Breakers": "stable",
                "Week 2 - Wiring Basics": "stable",
                "Week 3 - Safety Procedures": "improving"
            },
            "motivational_message": "Great progress! Keep up the excellent work!",
            "llm_explanation": "You're showing strong mastery in most areas...",
            "generated_at": "2025-01-17T14:30:00"
        },
        "field_descriptions": {
            "student_id": "Unique student identifier",
            "performance_history": "Array of quiz results (min 1 required)",
            "topic_scores": "Optional: normalized scores 0-1 for additional topics",
            "topic": "Name of topic/module/week",
            "score": "Points earned (must be >= 0)",
            "max_score": "Total possible points (must be > 0)",
            "percentage": "Optional: percentage score 0-100",
            "week_number": "Optional: week number in course",
            "module_id": "Optional: course/module identifier",
            "timestamp": "Optional: ISO format timestamp"
        }
    }