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









# """
# Recommendation Router - PRODUCTION READY
# Endpoint: /api/v1/recommendations
# Location: app/api/v1/recommendation_router.py
# """

# from fastapi import APIRouter, HTTPException, status
# from pydantic import BaseModel, Field
# from typing import List, Dict, Optional
# from app.services.recommendation_service import RecommendationService
# from app.core.logging_config import logger

# router = APIRouter()

# # Initialize service
# try:
#     recommendation_service = RecommendationService()
#     logger.info(" Recommendation Service initialized")
# except Exception as e:
#     logger.error(f" Failed to initialize Recommendation Service: {e}")
#     recommendation_service = None



# # REQUEST/RESPONSE MODELS


# class PerformanceRecord(BaseModel):
#     """Single performance record from student history"""
#     topic: str = Field(..., description="Topic or module name")
#     score: float = Field(..., ge=0, description="Points earned")
#     max_score: float = Field(..., gt=0, description="Total possible points")
#     percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage score")
#     timestamp: Optional[str] = Field(None, description="When quiz was taken")
#     module_id: Optional[str] = Field(None, description="Course/module identifier")
#     week_number: Optional[int] = Field(None, ge=0, description="Week number")


# class RecommendationRequest(BaseModel):
#     """Request for generating recommendations"""
#     student_id: str = Field(..., description="Student identifier")
#     performance_history: List[PerformanceRecord] = Field(
#         ...,
#         min_items=1,
#         description="Student's quiz performance history"
#     )
#     topic_scores: Optional[Dict[str, float]] = Field(
#         default=None,
#         description="Optional: Additional topic scores (0-1 normalized)"
#     )


# class StudyPlanSection(BaseModel):
#     """Section of personalized study plan"""
#     topics: List[str]
#     reason: str
#     suggested_hours: float


# class StudyPlan(BaseModel):
#     """Complete study plan"""
#     urgent_review: StudyPlanSection
#     skill_building: StudyPlanSection
#     advancement: StudyPlanSection


# class RecommendationResult(BaseModel):
#     """Complete recommendation response"""
#     student_id: str
#     topic_recommendations: List[str] = Field(description="Prioritized list of topics to focus on")
#     study_plan: StudyPlan
#     strengths: List[str] = Field(description="Topics where student excels")
#     trends: Dict[str, str] = Field(description="Performance trends per topic")
#     motivational_message: str
#     llm_explanation: str
#     generated_at: str



# # ENDPOINTS


# def check_service():
#     """Verify service is available"""
#     if recommendation_service is None:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="Recommendation service unavailable. Check logs for initialization errors."
#         )


# @router.post(
#     "/analyze",
#     response_model=RecommendationResult,
#     status_code=status.HTTP_200_OK,
#     summary="Generate personalized learning recommendations",
#     description="Analyzes student performance and generates AI-powered personalized recommendations"
# )
# async def analyze_performance(request: RecommendationRequest):
#     """
#     **Generate Personalized Recommendations**
    
#     Analyzes student's performance history to provide:
#     -  Performance strengths and weaknesses
#     -  Trend analysis (improving/declining/stable)
#     -  Prioritized study plan
#     -  AI-generated insights and motivation
#     -  Actionable next steps
    
#     **Request Example:**
#     ```json
#     {
#       "student_id": "student_456",
#       "performance_history": [
#         {
#           "topic": "Week 1 - Circuit Breakers",
#           "score": 45,
#           "max_score": 51,
#           "percentage": 88.2,
#           "week_number": 1,
#           "timestamp": "2025-01-10T10:00:00"
#         },
#         {
#           "topic": "Week 2 - Wiring Basics",
#           "score": 30,
#           "max_score": 48,
#           "percentage": 62.5,
#           "week_number": 2,
#           "timestamp": "2025-01-15T10:00:00"
#         }
#       ],
#       "topic_scores": {
#         "Circuit Breakers": 0.88,
#         "Wiring Basics": 0.62
#       }
#     }
#     ```
    
#     **Returns:** Complete recommendation package with study plan and AI insights
#     """
#     check_service()
    
#     try:
#         logger.info(
#             f"Analyzing performance for {request.student_id}: "
#             f"{len(request.performance_history)} records"
#         )
        
#         # Convert Pydantic models to dicts for processing
#         performance_history = [record.model_dump() for record in request.performance_history]
        
#         # Generate recommendations
#         result = await recommendation_service.generate_recommendations(
#             performance_history=performance_history,
#             topic_scores=request.topic_scores
#         )
        
#         # Add metadata
#         from datetime import datetime
#         response = RecommendationResult(
#             student_id=request.student_id,
#             topic_recommendations=result["topic_recommendations"],
#             study_plan=StudyPlan(**result["study_plan"]),
#             strengths=result["strengths"],
#             trends=result["trends"],
#             motivational_message=result["motivational_message"],
#             llm_explanation=result["llm_explanation"],
#             generated_at=datetime.now().isoformat()
#         )
        
#         logger.info(
#             f"Recommendations generated for {request.student_id}: "
#             f"{len(response.topic_recommendations)} priority topics, "
#             f"{len(response.strengths)} strengths identified"
#         )
        
#         return response
        
#     except ValueError as ve:
#         logger.error(f" Validation error: {ve}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(ve)
#         )
#     except Exception as e:
#         logger.error(f" Recommendation generation failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate recommendations: {str(e)}"
#         )


# @router.get(
#     "/health",
#     summary="Check recommendation service health"
# )
# async def health_check():
#     """Health check endpoint"""
#     if recommendation_service is None:
#         return {
#             "status": "unavailable",
#             "service": "recommendation",
#             "error": "Service not initialized"
#         }
    
#     return {
#         "status": "healthy",
#         "service": "recommendation",
#         "features": [
#             "performance_analysis",
#             "trend_detection",
#             "personalized_study_plans",
#             "ai_insights",
#             "strength_weakness_identification"
#         ],
#         "endpoints": {
#             "analyze": "/analyze",
#             "health": "/health",
#             "example": "/example"
#         }
#     }


# @router.get(
#     "/example",
#     summary="Get example request format"
# )
# async def get_example():
#     """
#     Get example request format for recommendation generation.
#     Useful for testing and API integration.
#     """
#     return {
#         "description": "Recommendation generation request format",
#         "example_request": {
#             "student_id": "student_456",
#             "performance_history": [
#                 {
#                     "topic": "Week 1 - Circuit Breakers",
#                     "score": 45.0,
#                     "max_score": 51.0,
#                     "percentage": 88.2,
#                     "week_number": 1,
#                     "module_id": "TVET-ELEC-101",
#                     "timestamp": "2025-01-10T10:00:00"
#                 },
#                 {
#                     "topic": "Week 2 - Wiring Basics",
#                     "score": 30.0,
#                     "max_score": 48.0,
#                     "percentage": 62.5,
#                     "week_number": 2,
#                     "module_id": "TVET-ELEC-101",
#                     "timestamp": "2025-01-15T10:00:00"
#                 },
#                 {
#                     "topic": "Week 3 - Safety Procedures",
#                     "score": 42.0,
#                     "max_score": 45.0,
#                     "percentage": 93.3,
#                     "week_number": 3,
#                     "module_id": "TVET-ELEC-101",
#                     "timestamp": "2025-01-17T10:00:00"
#                 }
#             ],
#             "topic_scores": {
#                 "Circuit Breakers": 0.88,
#                 "Wiring Basics": 0.62,
#                 "Safety Procedures": 0.93
#             }
#         },
#         "expected_response": {
#             "student_id": "student_456",
#             "topic_recommendations": [
#                 "Wiring Basics"
#             ],
#             "study_plan": {
#                 "urgent_review": {
#                     "topics": [],
#                     "reason": "Performance is declining - immediate attention needed",
#                     "suggested_hours": 0
#                 },
#                 "skill_building": {
#                     "topics": ["Wiring Basics"],
#                     "reason": "Below mastery threshold - foundational work needed",
#                     "suggested_hours": 2
#                 },
#                 "advancement": {
#                     "topics": ["Circuit Breakers", "Safety Procedures"],
#                     "reason": "Strong foundation - ready for advanced concepts",
#                     "suggested_hours": 3.0
#                 }
#             },
#             "strengths": ["Circuit Breakers", "Safety Procedures"],
#             "trends": {
#                 "Week 1 - Circuit Breakers": "stable",
#                 "Week 2 - Wiring Basics": "stable",
#                 "Week 3 - Safety Procedures": "improving"
#             },
#             "motivational_message": "Great progress! Keep up the excellent work!",
#             "llm_explanation": "You're showing strong mastery in most areas...",
#             "generated_at": "2025-01-17T14:30:00"
#         },
#         "field_descriptions": {
#             "student_id": "Unique student identifier",
#             "performance_history": "Array of quiz results (min 1 required)",
#             "topic_scores": "Optional: normalized scores 0-1 for additional topics",
#             "topic": "Name of topic/module/week",
#             "score": "Points earned (must be >= 0)",
#             "max_score": "Total possible points (must be > 0)",
#             "percentage": "Optional: percentage score 0-100",
#             "week_number": "Optional: week number in course",
#             "module_id": "Optional: course/module identifier",
#             "timestamp": "Optional: ISO format timestamp"
#         }
#     }









"""
Recommendation Router - PRODUCTION READY
Endpoint: /api/v1/recommendations
Location: app/api/v1/recommendation_router.py
"""

# from fastapi import APIRouter, HTTPException, status
# from typing import Dict
# from datetime import datetime

# # IMPORT MODELS FROM MODELS FILE (NOT DEFINE HERE!)
# from app.models.recommendation_models import (
#     PerformanceRecord,
#     RecommendationRequest,
#     RecommendationResult,
#     StudyPlan,
#     StudyPlanSection,
#     FailureAnalysis
# )

# from app.services.recommendation_service import RecommendationService
# from app.core.logging_config import logger

# router = APIRouter()

# # Initialize service
# try:
#     recommendation_service = RecommendationService()
#     logger.info("✅ Recommendation Service initialized")
# except Exception as e:
#     logger.error(f"❌ Failed to initialize Recommendation Service: {e}")
#     recommendation_service = None


# # Helper function
# def check_service():
#     """Verify service is available"""
#     if recommendation_service is None:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="Recommendation service unavailable. Check logs for initialization errors."
#         )


# @router.post(
#     "/analyze",
#     response_model=RecommendationResult,
#     status_code=status.HTTP_200_OK,
#     summary="Generate personalized learning recommendations",
#     description="Analyzes student performance and generates AI-powered personalized recommendations"
# )
# async def analyze_performance(request: RecommendationRequest):
#     """
#     **Generate Personalized Recommendations**
    
#     Analyzes student's performance history to provide:
#     - 📊 Performance strengths and weaknesses
#     - 📈 Trend analysis (improving/declining/stable)
#     - 📋 Prioritized study plan
#     - 🤖 AI-generated insights and motivation
#     - 🎯 Actionable next steps
#     """
#     check_service()
    
#     try:
#         logger.info(
#             f"Analyzing performance for {request.student_id}: "
#             f"{len(request.performance_history)} records"
#         )
        
#         # Convert Pydantic models to dicts for processing
#         performance_history = [record.model_dump() for record in request.performance_history]
        
#         # Convert question results if provided
#         question_results = None
#         if request.question_results:
#             question_results = [q.model_dump() for q in request.question_results]
        
#         # Generate recommendations
#         result = await recommendation_service.generate_recommendations(
#             performance_history=performance_history,
#             topic_scores=request.topic_scores,
#             question_results=question_results
#         )
        
#         # Build response with proper nested models
#         study_plan = StudyPlan(
#             urgent_review=StudyPlanSection(**result["study_plan"]["urgent_review"]),
#             skill_building=StudyPlanSection(**result["study_plan"]["skill_building"]),
#             advancement=StudyPlanSection(**result["study_plan"]["advancement"])
#         )
        
#         # Build failure analysis if present
#         failure_analysis = None
#         if result.get("failure_analysis"):
#             failure_analysis = FailureAnalysis(**result["failure_analysis"])
        
#         response = RecommendationResult(
#             student_id=request.student_id,
#             topic_recommendations=result["topic_recommendations"],
#             study_plan=study_plan,
#             strengths=result["strengths"],
#             weaknesses=result.get("weaknesses", []),
#             trends=result["trends"],
#             motivational_message=result["motivational_message"],
#             llm_explanation=result["llm_explanation"],
#             failure_analysis=failure_analysis,
#             generated_at=datetime.now().isoformat()
#         )
        
#         logger.info(
#             f"✅ Recommendations generated for {request.student_id}: "
#             f"{len(response.topic_recommendations)} priority topics, "
#             f"{len(response.strengths)} strengths identified"
#         )
        
#         return response
        
#     except ValueError as ve:
#         logger.error(f"⚠️ Validation error: {ve}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(ve)
#         )
#     except Exception as e:
#         logger.error(f"❌ Recommendation generation failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate recommendations: {str(e)}"
#         )


# @router.get("/health", summary="Check recommendation service health")
# async def health_check():
#     """Health check endpoint"""
#     if recommendation_service is None:
#         return {
#             "status": "unavailable",
#             "service": "recommendation",
#             "error": "Service not initialized"
#         }
    
#     return {
#         "status": "healthy",
#         "service": "recommendation",
#         "features": [
#             "performance_analysis",
#             "trend_detection",
#             "personalized_study_plans",
#             "ai_insights",
#             "strength_weakness_identification",
#             "failure_analysis"
#         ]
#     }


# @router.get("/example", summary="Get example request format")
# async def get_example():
#     """Get example request format"""
#     return {
#         "description": "Recommendation generation request format",
#         "example_request": {
#             "student_id": "student_456",
#             "performance_history": [
#                 {
#                     "topic": "Week 1 - Circuit Breakers",
#                     "score": 45.0,
#                     "max_score": 51.0,
#                     "percentage": 88.2,
#                     "week_number": 1,
#                     "timestamp": "2025-01-10T10:00:00"
#                 }
#             ],
#             "topic_scores": {
#                 "Circuit Breakers": 0.88
#             }
#         }
#     }







"""
Content-Based Recommendation Router
Location: app/api/v1/recommendation_router.py
"""

# from fastapi import APIRouter, HTTPException, status
# from datetime import datetime

# from app.models.recommendation_models import (
#     RecommendationRequest,
#     RecommendationResult,
#     StudyPlan,
#     StudyPlanSection,
#     ContentArea,
#     ContentRecommendation,
#     StrengthWeakness,
#     FailureAnalysis
# )

# from app.services.recommendation_service import RecommendationService
# from app.core.logging_config import logger

# router = APIRouter()

# # Initialize service
# try:
#     recommendation_service = RecommendationService()
#     logger.info("Content-Aware Recommendation Service initialized")
# except Exception as e:
#     logger.error(f" Failed to initialize Recommendation Service: {e}")
#     recommendation_service = None


# def check_service():
#     """Verify service is available"""
#     if recommendation_service is None:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="Recommendation service unavailable. Check logs for initialization errors."
#         )


# @router.post(
#     "/analyze",
#     response_model=RecommendationResult,
#     status_code=status.HTTP_200_OK,
#     summary="Generate content-aware learning recommendations",
#     description="Analyzes student performance on specific learning content and provides targeted recommendations"
# )
# async def analyze_performance(request: RecommendationRequest):
#     """
#     **Generate Content-Aware Recommendations**
    
#     Analyzes student's performance on actual learning materials to provide:
#     -  Content-specific strengths and weaknesses
#     -  Targeted study plan based on actual material
#     -  Specific concepts to review
#     - AI-generated insights about content gaps
#     - Time-based study recommendations
    
#     **No week numbers or generic topics** - recommendations are based on the 
#     actual content the student studied.
#     """
#     check_service()
    
#     try:
#         logger.info(
#             f" Analyzing content-based performance for {request.student_id}: "
#             f"{len(request.performance_history)} content areas"
#         )
        
#         # Convert to dicts
#         performance_history = [record.model_dump() for record in request.performance_history]
#         question_results = None
#         if request.question_results:
#             question_results = [q.model_dump() for q in request.question_results]
        
#         # Generate recommendations
#         result = await recommendation_service.generate_recommendations(
#             performance_history=performance_history,
#             question_results=question_results
#         )
        
#         # Build response with proper nested models
#         study_plan = StudyPlan(
#             urgent_review=StudyPlanSection(
#                 content_areas=[ContentArea(**area) for area in result["study_plan"]["urgent_review"]["content_areas"]],
#                 reason=result["study_plan"]["urgent_review"]["reason"],
#                 suggested_hours=result["study_plan"]["urgent_review"]["suggested_hours"],
#                 specific_actions=result["study_plan"]["urgent_review"]["specific_actions"]
#             ),
#             skill_building=StudyPlanSection(
#                 content_areas=[ContentArea(**area) for area in result["study_plan"]["skill_building"]["content_areas"]],
#                 reason=result["study_plan"]["skill_building"]["reason"],
#                 suggested_hours=result["study_plan"]["skill_building"]["suggested_hours"],
#                 specific_actions=result["study_plan"]["skill_building"]["specific_actions"]
#             ),
#             advancement=StudyPlanSection(
#                 content_areas=[ContentArea(**area) for area in result["study_plan"]["advancement"]["content_areas"]],
#                 reason=result["study_plan"]["advancement"]["reason"],
#                 suggested_hours=result["study_plan"]["advancement"]["suggested_hours"],
#                 specific_actions=result["study_plan"]["advancement"]["specific_actions"]
#             )
#         )
        
#         # Build failure analysis if present
#         failure_analysis = None
#         if result.get("failure_analysis"):
#             failure_analysis = FailureAnalysis(**result["failure_analysis"])
        
#         response = RecommendationResult(
#             student_id=request.student_id,
#             content_recommendations=[ContentRecommendation(**rec) for rec in result["content_recommendations"]],
#             study_plan=study_plan,
#             strengths=[StrengthWeakness(**s) for s in result["strengths"]],
#             weaknesses=[StrengthWeakness(**w) for w in result["weaknesses"]],
#             analysis=result["analysis"],
#             encouragement=result["encouragement"],
#             failure_analysis=failure_analysis,
#             generated_at=datetime.now().isoformat()
#         )
        
#         logger.info(
#             f" Content-aware recommendations for {request.student_id}: "
#             f"{len(response.weaknesses)} weak areas, {len(response.strengths)} strong areas"
#         )
        
#         return response
        
#     except ValueError as ve:
#         logger.error(f" Validation error: {ve}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(ve)
#         )
#     except Exception as e:
#         logger.error(f" Recommendation generation failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate recommendations: {str(e)}"
#         )


# @router.get("/health", summary="Check recommendation service health")
# async def health_check():
#     """Health check endpoint"""
#     if recommendation_service is None:
#         return {
#             "status": "unavailable",
#             "service": "content-aware-recommendation",
#             "error": "Service not initialized"
#         }
    
#     return {
#         "status": "healthy",
#         "service": "content-aware-recommendation",
#         "features": [
#             "content_based_analysis",
#             "specific_content_recommendations",
#             "question_failure_analysis",
#             "ai_content_insights",
#             "time_based_study_plans"
#         ]
#     }


# @router.get("/example", summary="Get example request format")
# async def get_example():
#     """Get example request showing content-based format"""
#     return {
#         "description": "Content-aware recommendation request format",
#         "note": "Pass actual learning content, not just topic names",
#         "example_request": {
#             "student_id": "student_789",
#             "performance_history": [
#                 {
#                     "content_id": "intro_electricity_basics",
#                     "content": "Electricity fundamentals: Voltage is electrical pressure measured in volts (V). Current is the flow of electrons measured in amperes (A). Resistance opposes current flow, measured in ohms (Ω). Ohm's Law: V = I × R. Power: P = V × I.",
#                     "score": 8,
#                     "max_score": 10,
#                     "percentage": 80,
#                     "timestamp": "2025-01-10T10:00:00"
#                 },
#                 {
#                     "content_id": "circuit_breakers_protection",
#                     "content": "Circuit breakers are safety devices that automatically interrupt electrical flow when overload or fault conditions occur. Thermal breakers use bimetallic strips that bend with heat. Magnetic breakers use electromagnets that trip instantly. Proper sizing based on wire gauge and load requirements is critical for safety.",
#                     "score": 18,
#                     "max_score": 31,
#                     "percentage": 58.06,
#                     "timestamp": "2025-01-25T10:00:00"
#                 }
#             ],
#             "question_results": [
#                 {
#                     "question_id": "mcq_1",
#                     "question_type": "mcq",
#                     "awarded_points": 0,
#                     "max_points": 5,
#                     "is_correct": False,
#                     "feedback": "Review thermal breaker operation",
#                     "improvements": [
#                         "Bimetallic strip mechanism",
#                         "Heat detection in overcurrent"
#                     ]
#                 }
#             ]
#         }
#     }








"""
Module-Based Recommendation Router
Location: app/api/v1/recommendation_router.py
"""

# from fastapi import APIRouter, HTTPException, status
# from datetime import datetime

# from app.models.recommendation_models import (
#     QuestionResult,
#     ModuleInput,
#     RecommendationRequest,
#     ModuleReview,
#     WeakQuestionType,
#     OverallPerformance,
#     CollectiveFeedback,
#     RecommendationResult
# )
# """
# Module-Based Recommendation Models - SIMPLIFIED
# Location: app/models/recommendation_model.py
# """

# from typing import List, Optional
# from pydantic import BaseModel, Field


# class QuestionResult(BaseModel):
#     """Individual question result with student answer"""
#     question_text: str = Field(..., description="The actual question text")
#     student_answer: str = Field(..., description="What the student answered")
#     correct_answer: str = Field(..., description="The correct answer")
#     awarded_marks: float = Field(..., ge=0, description="Marks awarded for this question")
#     max_marks: float = Field(..., gt=0, description="Maximum marks for this question")
#     question_type: str = Field(..., description="Type: mcq, true_false, short_answer, essay")
#     is_correct: bool = Field(..., description="Whether the answer was correct")


# class ModuleInput(BaseModel):
#     """Single module input with content and quiz results"""
#     module_id: str = Field(..., description="Unique identifier for the module")
#     module_name: str = Field(..., description="Name/title of the module")
#     module_content: str = Field(..., description="The actual learning content/material of the module")
#     max_score: float = Field(..., gt=0, description="Maximum possible score for this module's quiz")
#     question_results: List[QuestionResult] = Field(..., min_items=1, description="List of question results")


# class RecommendationRequest(BaseModel):
#     """Request for module-based recommendations"""
#     student_id: str = Field(..., description="Student identifier")
#     modules: List[ModuleInput] = Field(..., min_items=1, description="List of modules to analyze")


# class ModuleReview(BaseModel):
#     """Individual module review and feedback"""
#     module_id: str = Field(description="Module identifier")
#     module_name: str = Field(description="Module name/title")
#     score: str = Field(description="Score achieved (e.g., '45/50')")
#     percentage: float = Field(description="Percentage score")
#     performance_level: str = Field(description="Excellent, Good, Satisfactory, or Needs Improvement")
#     feedback: str = Field(description="AI-generated feedback for this module")
#     failed_questions: int = Field(description="Number of questions failed")
#     concepts_to_review: List[str] = Field(description="Specific concepts needing review")


# class WeakQuestionType(BaseModel):
#     """Question type with poor performance"""
#     type: str = Field(description="Question type")
#     percentage: float = Field(description="Success rate percentage")
#     attempted: int = Field(description="Number of questions attempted")


# class OverallPerformance(BaseModel):
#     """Overall performance across all modules"""
#     total_score: float = Field(description="Total score across all modules")
#     total_max: float = Field(description="Total maximum possible score")
#     percentage: float = Field(description="Overall percentage")
#     level: str = Field(description="Overall performance level")


# class CollectiveFeedback(BaseModel):
#     """Collective feedback across all modules - SPECIFIC AND ACTIONABLE"""
#     overall_performance: OverallPerformance
#     critical_gaps: str = Field(description="Specific topics and concepts needing study")
#     recommendations: str = Field(description="Concrete actions - what content to review and how")
#     weak_question_types: List[WeakQuestionType] = Field(description="Question types to practice")
#     total_failed_questions: int = Field(description="Total number of failed questions")


# class RecommendationResult(BaseModel):
#     """Complete recommendation result"""
#     student_id: str
#     individual_module_reviews: List[ModuleReview] = Field(
#         description="Individual feedback for each module"
#     )
#     collective_feedback: CollectiveFeedback = Field(
#         description="Overall feedback with specific study recommendations"
#     )
#     generated_at: str
    



# from app.services.recommendation_service import RecommendationService
# from app.core.logging_config import logger

# router = APIRouter()

# # Initialize service
# try:
#     recommendation_service = RecommendationService()
#     logger.info("Module-Based Recommendation Service initialized")
# except Exception as e:
#     logger.error(f"Failed to initialize Recommendation Service: {e}")
#     recommendation_service = None


# def check_service():
#     """Verify service is available"""
#     if recommendation_service is None:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="Recommendation service unavailable. Check logs for initialization errors."
#         )


# @router.post(
#     "/analyze",
#     response_model=RecommendationResult,
#     status_code=status.HTTP_200_OK,
#     summary="Generate module-based learning recommendations",
#     description="Analyzes student performance on specific modules and provides individual + collective feedback"
# )
# async def analyze_performance(request: RecommendationRequest):
#     """
#     **Generate Module-Based Recommendations**
    
#     Analyzes student's quiz performance on learning modules to provide:
    
#     **Individual Module Reviews:**
#     - Performance feedback for each module
#     - Score and percentage
#     - Specific concepts to review
#     - AI-generated constructive feedback
    
#     **Collective Feedback:**
#     - Critical gaps across all modules
#     - Weak modules needing attention
#     - Strong modules (well understood)
#     - Question types to practice
#     - Actionable recommendations
    
#     **Input Required:**
#     - Module content (actual learning material)
#     - Max score for the module quiz
#     - Question results (question text, student answer, correct answer, marks)
#     """
#     check_service()
    
#     try:
#         logger.info(
#             f"Analyzing performance for {request.student_id}: "
#             f"{len(request.modules)} module(s)"
#         )
        
#         # Convert to dicts for processing
#         modules = [
#             {
#                 "module_content": module.module_content,
#                 "max_score": module.max_score,
#                 "question_results": [q.model_dump() for q in module.question_results]
#             }
#             for module in request.modules
#         ]
        
#         # Generate recommendations
#         result = await recommendation_service.generate_recommendations(modules)
        
#         # Build response with proper nested models
#         individual_reviews = [
#             ModuleReview(**review)
#             for review in result["individual_module_reviews"]
#         ]
        
#         collective = result["collective_feedback"]
#         collective_feedback = CollectiveFeedback(
#             overall_performance=OverallPerformance(**collective["overall_performance"]),
#             critical_gaps=collective["critical_gaps"],
#             recommendations=collective["recommendations"],
#             weak_modules=[WeakModule(**m) for m in collective["weak_modules"]],
#             strong_modules=[StrongModule(**m) for m in collective["strong_modules"]],
#             weak_question_types=[WeakQuestionType(**qt) for qt in collective["weak_question_types"]],
#             total_failed_questions=collective["total_failed_questions"]
#         )
        
#         response = RecommendationResult(
#             student_id=request.student_id,
#             individual_module_reviews=individual_reviews,
#             collective_feedback=collective_feedback,
#             generated_at=datetime.now().isoformat()
#         )
        
#         logger.info(
#             f"Recommendations generated for {request.student_id}: "
#             f"{len(individual_reviews)} module(s) analyzed, "
#             f"Overall: {collective_feedback.overall_performance.percentage:.1f}%"
#         )
        
#         return response
        
#     except ValueError as ve:
#         logger.error(f"Validation error: {ve}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(ve)
#         )
#     except Exception as e:
#         logger.error(f"Recommendation generation failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate recommendations: {str(e)}"
#         )


# @router.get("/health", summary="Check recommendation service health")
# async def health_check():
#     """Health check endpoint"""
#     if recommendation_service is None:
#         return {
#             "status": "unavailable",
#             "service": "module-recommendation",
#             "error": "Service not initialized"
#         }
    
#     return {
#         "status": "healthy",
#         "service": "module-recommendation",
#         "features": [
#             "individual_module_analysis",
#             "collective_performance_feedback",
#             "critical_gap_identification",
#             "question_type_analysis",
#             "ai_powered_feedback"
#         ]
#     }


# @router.get("/example", summary="Get example request format")
# async def get_example():
#     """Get example request showing the correct input format"""
#     return {
#         "description": "Module-based recommendation request format",
#         "input_structure": {
#             "student_id": "Unique student identifier",
#             "modules": [
#                 {
#                     "module_content": "Full text of learning material",
#                     "max_score": "Maximum quiz score (e.g., 50)",
#                     "question_results": [
#                         {
#                             "question_text": "The actual question",
#                             "student_answer": "What student answered",
#                             "correct_answer": "Correct answer",
#                             "awarded_marks": "Marks given",
#                             "max_marks": "Max marks for question",
#                             "question_type": "mcq/true_false/short_answer/essay",
#                             "is_correct": "true/false"
#                         }
#                     ]
#                 }
#             ]
#         },
#         "example": {
#             "student_id": "student_001",
#             "modules": [
#                 {
#                     "module_content": "Electrical Safety: Personal Protective Equipment (PPE) is essential when working with electrical systems. Required PPE includes insulated gloves rated for the voltage level, safety glasses with side shields, flame-resistant clothing, and insulated tools. Lockout/Tagout (LOTO) procedures must be followed to ensure equipment is de-energized before maintenance work begins.",
#                     "max_score": 20,
#                     "question_results": [
#                         {
#                             "question_text": "What does LOTO stand for in electrical safety?",
#                             "student_answer": "Lockout Tagout",
#                             "correct_answer": "Lockout/Tagout",
#                             "awarded_marks": 5,
#                             "max_marks": 5,
#                             "question_type": "short_answer",
#                             "is_correct": True
#                         },
#                         {
#                             "question_text": "Which PPE is required when working on live electrical circuits?",
#                             "student_answer": "Just gloves",
#                             "correct_answer": "Insulated gloves, safety glasses, flame-resistant clothing, and insulated tools",
#                             "awarded_marks": 2,
#                             "max_marks": 5,
#                             "question_type": "short_answer",
#                             "is_correct": False
#                         }
#                     ]
#                 },
#                 {
#                     "module_content": "Circuit Breakers: A circuit breaker is an automatic electrical switch designed to protect an electrical circuit from damage caused by excess current. There are two main types: thermal breakers use a bimetallic strip that bends when heated by excessive current, while magnetic breakers use an electromagnet that trips when current exceeds safe levels.",
#                     "max_score": 25,
#                     "question_results": [
#                         {
#                             "question_text": "What is the primary function of a circuit breaker?",
#                             "student_answer": "To break circuits",
#                             "correct_answer": "To protect electrical circuits from damage caused by excess current",
#                             "awarded_marks": 2,
#                             "max_marks": 5,
#                             "question_type": "short_answer",
#                             "is_correct": False
#                         },
#                         {
#                             "question_text": "How does a thermal circuit breaker detect overcurrent?",
#                             "student_answer": "Using heat",
#                             "correct_answer": "Through a bimetallic strip that bends when heated by excessive current",
#                             "awarded_marks": 3,
#                             "max_marks": 5,
#                             "question_type": "short_answer",
#                             "is_correct": False
#                         }
#                     ]
#                 }
#             ]
#         }
#     }




"""
Module-Based Recommendation Router - SIMPLIFIED
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