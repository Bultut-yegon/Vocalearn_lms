# from fastapi import APIRouter, HTTPException, status, BackgroundTasks
# from app.models.quiz_models import (
#     QuizGenerationRequest,
#     AdaptiveQuizRequest,
#     QuizGenerationResult,
#     BulkQuizRequest,
#     DifficultyLevel
# )
# from app.services.quiz_service import QuizGeneratorService
# from app.core.logging_config import logger
# from typing import List

# router = APIRouter()
# quiz_service = QuizGeneratorService()

# @router.post(
#     "/generate",
#     response_model=QuizGenerationResult,
#     summary="Generate a complete quiz",
#     description="AI-powered quiz generation with customizable parameters"
# )
# async def generate_quiz(request: QuizGenerationRequest):
#     """
#     Generate a comprehensive quiz with mixed question types.
    
#     Features:
#     - Multiple question types (MCQ, T/F, Short Answer, Essay)
#     - Difficulty levels (Beginner, Intermediate, Advanced)
#     - Topic and subtopic specification
#     - Reference material integration
#     - Avoidance of already covered topics
    
#     Perfect for creating assessments on-demand!
#     """
#     try:
#         logger.info(f"Generating quiz for topic: {request.topic}")
        
#         result = await quiz_service.generate_quiz(
#             topic=request.topic,
#             difficulty=request.difficulty_level.value,
#             num_mcq=request.num_mcq,
#             num_true_false=request.num_true_false,
#             num_short_answer=request.num_short_answer,
#             num_essay=request.num_essay,
#             subtopics=request.subtopics,
#             avoid_topics=request.avoid_topics,
#             reference_materials=request.reference_materials
#         )
        
#         logger.info(f"Successfully generated quiz: {result['quiz_id']} with {result['total_questions']} questions")
#         return QuizGenerationResult(**result)
        
#     except Exception as e:
#         logger.error(f"Quiz generation failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate quiz: {str(e)}"
#         )

# @router.post(
#     "/generate-adaptive",
#     response_model=QuizGenerationResult,
#     summary="Generate adaptive quiz based on student performance",
#     description="Creates personalized quiz focusing on student's weak areas"
# )
# async def generate_adaptive_quiz(request: AdaptiveQuizRequest):
#     """
#     Generate an adaptive quiz tailored to individual student needs.
    
#     Analyzes:
#     - Recent performance data
#     - Identified weak areas
#     - Current mastery level
    
#     Automatically adjusts:
#     - Difficulty level
#     - Topic focus
#     - Question distribution
#     """
#     try:
#         logger.info(f"Generating adaptive quiz for student: {request.student_id}")
        
#         result = await quiz_service.generate_adaptive_quiz(
#             student_id=request.student_id,
#             topic=request.topic,
#             total_questions=request.total_questions,
#             recent_performance=request.recent_performance,
#             weak_areas=request.weak_areas
#         )
        
#         logger.info(f"Generated adaptive quiz: {result['quiz_id']}")
#         return QuizGenerationResult(**result)
        
#     except Exception as e:
#         logger.error(f"Adaptive quiz generation failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate adaptive quiz: {str(e)}"
#         )

# @router.post(
#     "/generate-bulk",
#     summary="Generate multiple quizzes in bulk",
#     description="Batch generation for multiple topics"
# )
# async def generate_bulk_quizzes(request: BulkQuizRequest, background_tasks: BackgroundTasks):
#     """
#     Generate quizzes for multiple topics efficiently.
#     Useful for curriculum-wide assessment preparation.
#     """
#     try:
#         logger.info(f"Bulk generating quizzes for {len(request.topics)} topics")
        
#         results = []
        
#         for topic in request.topics:
#             # Distribute questions based on difficulty if specified
#             if request.difficulty_distribution:
#                 # This is simplified - in production you'd generate per difficulty
#                 difficulty = "intermediate"
#             else:
#                 difficulty = "intermediate"
            
#             # Calculate question distribution
#             total = request.questions_per_topic
#             num_mcq = int(total * 0.5)
#             num_tf = int(total * 0.3)
#             num_short = total - num_mcq - num_tf
            
#             result = await quiz_service.generate_quiz(
#                 topic=topic,
#                 difficulty=difficulty,
#                 num_mcq=num_mcq,
#                 num_true_false=num_tf,
#                 num_short_answer=num_short,
#                 num_essay=0
#             )
            
#             results.append(result)
#             logger.info(f"Generated bulk quiz for: {topic}")
        
#         return {
#             "total_quizzes_generated": len(results),
#             "quizzes": results,
#             "summary": {
#                 "topics_covered": request.topics,
#                 "total_questions": sum(q["total_questions"] for q in results),
#                 "total_points": sum(q["total_points"] for q in results)
#             }
#         }
        
#     except Exception as e:
#         logger.error(f"Bulk quiz generation failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Bulk generation failed: {str(e)}"
#         )

# @router.post(
#     "/quick-generate",
#     summary="Quick quiz generation with defaults",
#     description="Generate a standard 10-question quiz instantly"
# )
# async def quick_generate_quiz(topic: str, difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE):
#     """
#     One-click quiz generation with sensible defaults.
#     Perfect for rapid assessment creation!
    
#     Default: 5 MCQ + 3 T/F + 2 Short Answer
#     """
#     try:
#         result = await quiz_service.generate_quiz(
#             topic=topic,
#             difficulty=difficulty.value,
#             num_mcq=5,
#             num_true_false=3,
#             num_short_answer=2
#         )
        
#         logger.info(f"Quick generated quiz for: {topic}")
#         return QuizGenerationResult(**result)
        
#     except Exception as e:
#         logger.error(f"Quick generation failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Quick generation failed: {str(e)}"
#         )

# @router.get(
#     "/health",
#     summary="Check quiz generation service health"
# )
# async def health_check():
#     """Health check endpoint for quiz generation service."""
#     return {
#         "status": "healthy",
#         "service": "quiz-generation",
#         "features": [
#             "standard_quiz_generation",
#             "adaptive_quiz_generation",
#             "bulk_generation",
#             "quick_generation",
#             "multi_question_types",
#             "difficulty_levels",
#             "subtopic_targeting",
#             "reference_material_integration"
#         ],
#         "supported_question_types": [
#             "mcq",
#             "true_false",
#             "short_answer",
#             "essay",
#             "practical"
#         ],
#         "difficulty_levels": [
#             "beginner",
#             "intermediate",
#             "advanced"
#         ]
#     }


# VERSION 2






# """
# Quiz Router - Matches your exact JSON format
# Location: app/api/v1/quiz_router.py
# """

# from fastapi import APIRouter, HTTPException, status
# from fastapi.responses import JSONResponse
# from typing import Dict
# from app.services.quiz_generation_service import (
#     QuizGenerationService,
#     QuizGenerationRequest,
#     QuizResponse
# )
# from app.core.logging_config import logger

# from app.models.quiz_models import (
#     QuizGenerationRequest,
#     QuizGenerationResult,
#     WeeklyQuizGenerationRequest
# )

# import os

# router = APIRouter()

# # Initialize quiz service
# try:
#     groq_api_key = os.getenv("GROQAPI_KEY")
#     if not groq_api_key:
#         logger.error("GROQAPI_KEY not found in environment")
#         quiz_service = None
#     else:
#         quiz_service = QuizGenerationService(groq_api_key=groq_api_key)
#         logger.info("Quiz Generation Service initialized")
# except Exception as e:
#     logger.error(f" Failed to initialize Quiz Service: {e}")
#     quiz_service = None


# def check_service():
#     """Verify service is available"""
#     if quiz_service is None:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="Quiz generation service unavailable. Check GROQAPI_KEY configuration."
#         )


# @router.post(
#     "/generate-weekly",
#     response_model=QuizGenerationResult,
#     status_code=status.HTTP_201_CREATED
# )
# async def generate_weekly_quiz(request: WeeklyQuizGenerationRequest):
#     check_service()

#     try:
#         logger.info(
#             f"Generating weekly quiz | Course={request.course_id}, Week={request.week_number}"
#         )

#         return await quiz_service.generate_weekly_quiz(request)

#     except Exception as e:
#         logger.error(f"Weekly quiz generation failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to generate weekly quizzes"
#         )


#     except Exception as e:
#         logger.error(f"Weekly quiz generation failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to generate weekly quizzes"
#         )



# @router.post("/generate", response_model=QuizGenerationResult, status_code=status.HTTP_201_CREATED)
# async def generate_quiz(request: QuizGenerationRequest):
#     """
#     Generate quiz from content using your exact JSON format.
    
#     **Request Example:**
#     ```json
#     {
#       "content": "Circuit breakers are automatic electrical switches designed to protect electrical circuits from damage caused by overcurrent. They work by detecting when current exceeds safe levels and automatically interrupting the circuit...",
#       "difficulty_level": "intermediate",
#       "num_mcq": 5,
#       "num_true_false": 5,
#       "num_short_answer": 2,
#       "num_of_options": 4
#     }
#     ```
    
#     **Parameters:**
#     - **content**: The learning content from your database (min 100 chars)
#     - **difficulty_level**: "beginner", "intermediate", or "advanced"
#     - **num_mcq**: Number of multiple choice questions (0-20)
#     - **num_true_false**: Number of true/false questions (0-20)
#     - **num_short_answer**: Number of open-ended questions (0-10)
#     - **num_of_options**: Number of MCQ options (2-6, typically 4 for A,B,C,D)
    
#     **Response:** Complete quiz with all question types
#     """
#     check_service()
    
#     try:
#         # Validate content length
#         if len(request.content.strip()) < 100:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Content must be at least 100 characters to generate meaningful questions"
#             )
        
#         # Validate at least one question type is requested
#         total_questions = request.num_mcq + request.num_true_false + request.num_short_answer
#         if total_questions == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Must request at least one question (num_mcq, num_true_false, or num_short_answer must be > 0)"
#             )
        
#         if total_questions > 50:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Total questions cannot exceed 50"
#             )
        
#         logger.info(f"Generating quiz: MCQ={request.num_mcq}, T/F={request.num_true_false}, SA={request.num_short_answer}")
        
#         # Generate quiz
#         quiz = await quiz_service.generate_quiz(request)
        
#         logger.info(f"Quiz generated: {quiz.quiz_id} with {quiz.total_questions} questions")
        
#         return quiz
        
#     except HTTPException:
#         raise
#     except ValueError as ve:
#         logger.error(f"Validation error: {ve}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(ve)
#         )
#     except Exception as e:
#         logger.error(f"Quiz generation failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Quiz generation failed: {str(e)}"
#         )


# @router.post("/generate-batch")
# async def generate_quiz_batch(requests: list[QuizGenerationRequest]):
#     """
#     Generate multiple quizzes in one request (for batch processing).
    
#     **Use case:** Generate quizzes for multiple topics/students at once
    
#     **Request Example:**
#     ```json
#     [
#       {
#         "content": "Content 1...",
#         "difficulty_level": "beginner",
#         "num_mcq": 5,
#         "num_true_false": 5,
#         "num_short_answer": 2,
#         "num_of_options": 4
#       },
#       {
#         "content": "Content 2...",
#         "difficulty_level": "advanced",
#         "num_mcq": 10,
#         "num_true_false": 0,
#         "num_short_answer": 5,
#         "num_of_options": 4
#       }
#     ]
#     ```
#     """
#     check_service()
    
#     if len(requests) > 10:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Maximum 10 quizzes per batch request"
#         )
    
#     try:
#         quizzes = []
#         errors = []
        
#         for idx, req in enumerate(requests):
#             try:
#                 quiz = await quiz_service.generate_quiz(req)
#                 quizzes.append(quiz)
#             except Exception as e:
#                 logger.error(f"Failed to generate quiz {idx}: {e}")
#                 errors.append({
#                     "index": idx,
#                     "error": str(e)
#                 })
        
#         return {
#             "success": len(quizzes),
#             "failed": len(errors),
#             "quizzes": quizzes,
#             "errors": errors
#         }
        
#     except Exception as e:
#         logger.error(f"Batch generation failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )


# @router.get("/health")
# async def health_check():
#     """Check quiz service health"""
#     if quiz_service is None:
#         return {
#             "status": "unavailable",
#             "service": "quiz_generation",
#             "error": "GROQAPI_KEY not configured"
#         }
    
#     return {
#         "status": "healthy",
#         "service": "quiz_generation",
#         "model": quiz_service.model,
#         "supported_question_types": [
#             "multiple_choice",
#             "true_false",
#             "short_answer"
#         ],
#         "max_questions_per_type": {
#             "mcq": 20,
#             "true_false": 20,
#             "short_answer": 10
#         },
#         "max_total_questions": 50
#     }


# @router.get("/format-example")
# async def get_format_example():
#     """
#     Get example of the expected request format.
#     Useful for Java developers integrating with this API.
#     """
#     return {
#         "description": "Quiz generation request format",
#         "example_request": {
#             "content": "Your learning content from database goes here. It should be at least 100 characters long. For example: Circuit breakers are automatic electrical switches designed to protect electrical circuits from damage caused by overcurrent. When excessive current flows through the circuit, the circuit breaker trips and interrupts the flow of electricity.",
#             "difficulty_level": "intermediate",
#             "num_mcq": 5,
#             "num_true_false": 5,
#             "num_short_answer": 2,
#             "num_of_options": 4
#         },
#         "field_descriptions": {
#             "content": "Learning content from your database (min 100 characters)",
#             "difficulty_level": "beginner | intermediate | advanced",
#             "num_mcq": "Number of multiple choice questions (0-20)",
#             "num_true_false": "Number of true/false questions (0-20)",
#             "num_short_answer": "Number of open-ended questions (0-10)",
#             "num_of_options": "Number of options per MCQ (2-6, typically 4)"
#         },
#         "response_structure": {
#             "quiz_id": "unique identifier",
#             "generated_at": "ISO timestamp",
#             "difficulty_level": "requested difficulty",
#             "total_questions": "total count",
#             "multiple_choice": [
#                 {
#                     "question": "Question text?",
#                     "options": {
#                         "A": "Option A",
#                         "B": "Option B",
#                         "C": "Option C",
#                         "D": "Option D"
#                     },
#                     "correct_answer": "B",
#                     "explanation": "Why B is correct"
#                 }
#             ],
#             "true_false": [
#                 {
#                     "question": "Statement here.",
#                     "correct_answer": True,
#                     "explanation": "Why this is true/false"
#                 }
#             ],
#             "short_answer": [
#                 {
#                     "question": "Open-ended question?",
#                     "key_points": ["Point 1", "Point 2"],
#                     "sample_answer": "Example answer"
#                 }
#             ]
#         }
#     }


# @router.get("/difficulty-levels")
# async def get_difficulty_info():
#     """Get information about difficulty levels"""
#     return {
#         "difficulty_levels": {
#             "beginner": {
#                 "description": "Basic recall and simple understanding",
#                 "characteristics": [
#                     "Straightforward questions",
#                     "Clear, unambiguous answers",
#                     "Tests basic knowledge"
#                 ]
#             },
#             "intermediate": {
#                 "description": "Application and analysis",
#                 "characteristics": [
#                     "Requires understanding of concepts",
#                     "May involve application to scenarios",
#                     "Tests comprehension and reasoning"
#                 ]
#             },
#             "advanced": {
#                 "description": "Complex analysis and synthesis",
#                 "characteristics": [
#                     "Requires deep understanding",
#                     "May involve multiple concepts",
#                     "Tests critical thinking"
#                 ]
#             }
#         }
#     }


# @router.post("/validate-request")
# async def validate_request(request: QuizGenerationRequest):
#     """
#     Validate a quiz generation request without actually generating.
#     Useful for frontend validation before submission.
#     """
#     try:
#         total = request.num_mcq + request.num_true_false + request.num_short_answer
        
#         return {
#             "valid": True,
#             "summary": {
#                 "content_length": len(request.content),
#                 "difficulty_level": request.difficulty_level,
#                 "total_questions": total,
#                 "breakdown": {
#                     "multiple_choice": request.num_mcq,
#                     "true_false": request.num_true_false,
#                     "short_answer": request.num_short_answer
#                 },
#                 "estimated_generation_time": f"{total * 2}-{total * 3} seconds"
#             }
#         }
#     except Exception as e:
#         return {
#             "valid": False,
#             "error": str(e)
#         }






# VERSION 3

















"""
Quiz Router - FIXED VERSION
"""

from fastapi import APIRouter, HTTPException, status
from app.services.quiz_generation_service import QuizGenerationService
from app.models.quiz_models import (
    WeeklyQuizGenerationRequest,
    QuizGenerationResult
)
from app.core.logging_config import logger
import os

router = APIRouter()

# Initialize quiz service
try:
    groq_api_key = os.getenv("GROQAPI_KEY")
    if not groq_api_key:
        logger.error("❌ GROQAPI_KEY not found in environment")
        quiz_service = None
    else:
        quiz_service = QuizGenerationService(groq_api_key=groq_api_key)
        logger.info("✅ Quiz Generation Service initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize Quiz Service: {e}")
    quiz_service = None


def check_service():
    """Verify service is available"""
    if quiz_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Quiz generation service unavailable. Check GROQAPI_KEY configuration."
        )


@router.post(
    "/generate-weekly",
    response_model=QuizGenerationResult,
    status_code=status.HTTP_201_CREATED,
    summary="Generate weekly quiz",
    description="Generate a Canvas-style quiz for one week of content"
)
async def generate_weekly_quiz(request: WeeklyQuizGenerationRequest):
    """
    Generate weekly quiz from combined content.
    
    **Request Example:**
    ```json
    {
      "course_id": "CS101",
      "week_number": 3,
      "modules": ["Module 1", "Module 2"],
      "combined_content": "Your week's learning content here (min 100 chars)...",
      "difficulty_level": "intermediate",
      "num_mcq": 5,
      "num_true_false": 5,
      "num_short_answer": 2,
      "student_id": "optional_student_id"
    }
    ```
    
    **Returns:** Complete quiz with MCQ, T/F, and short answer questions
    """
    check_service()

    try:
        logger.info(
            f"📝 Generating weekly quiz | Course={request.course_id}, "
            f"Week={request.week_number}"
        )

        # Generate the quiz
        result = await quiz_service.generate_weekly_quiz(request)
        
        logger.info(
            f"✅ Weekly quiz generated: {result.quiz_id} | "
            f"{result.total_questions} questions"
        )
        
        return result

    except ValueError as ve:
        logger.error(f"❌ Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"❌ Weekly quiz generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weekly quiz: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check quiz service health"""
    if quiz_service is None:
        return {
            "status": "unavailable",
            "service": "quiz_generation",
            "error": "GROQAPI_KEY not configured"
        }
    
    return {
        "status": "healthy",
        "service": "quiz_generation",
        "model": quiz_service.model,
        "supported_question_types": [
            "multiple_choice",
            "true_false",
            "short_answer"
        ],
        "endpoints": {
            "weekly_quiz": "/generate-weekly",
            "health": "/health"
        }
    }


@router.get("/example-request")
async def get_example_request():
    """
    Get example request format for weekly quiz generation.
    """
    return {
        "description": "Weekly quiz generation request format",
        "example": {
            "course_id": "TVET-101",
            "week_number": 1,
            "modules": [
                "Introduction to Circuit Breakers",
                "Safety Procedures"
            ],
            "combined_content": "Circuit breakers are automatic electrical switches designed to protect electrical circuits from damage caused by overcurrent. They detect when current exceeds safe levels and automatically interrupt the circuit. Modern circuit breakers use thermal or magnetic mechanisms. Thermal breakers use a bimetallic strip that bends when heated, while magnetic breakers use an electromagnet. Safety procedures require proper PPE and lockout/tagout protocols.",
            "difficulty_level": "intermediate",
            "num_mcq": 5,
            "num_true_false": 3,
            "num_short_answer": 2,
            "student_id": None
        },
        "required_fields": [
            "course_id",
            "week_number",
            "modules",
            "combined_content"
        ],
        "optional_fields": {
            "difficulty_level": "beginner | intermediate | advanced (default: intermediate)",
            "num_mcq": "0-20 (default: 5)",
            "num_true_false": "0-20 (default: 5)",
            "num_short_answer": "0-10 (default: 2)",
            "student_id": "Optional for adaptive quizzes"
        }
    }