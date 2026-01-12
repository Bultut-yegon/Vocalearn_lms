# from fastapi import APIRouter, HTTPException, status
# from fastapi.responses import JSONResponse
# from typing import Dict, List
# from app.services.quiz_generation_service import (
#     QuizGenerationService,
#     QuizGenerationRequest,
#     NotesInput,
#     SubTopic,
#     Quiz
# )
# from app.core.logging_config import logger

# router = APIRouter(
#     prefix="/api/quiz",
#     tags=["Quiz Generation"]
# )

# # Initialize quiz service
# quiz_service = QuizGenerationService()


# @router.post("/generate", response_model=Quiz, status_code=status.HTTP_201_CREATED)
# async def generate_quiz(request: QuizGenerationRequest):
#     """
#     Generate a quiz from JSON notes.
    
#     **Request Body Example:**
#     ```json
#     {
#       "notes": {
#         "course": "Electrical Installation",
#         "topic": "Circuit Protection",
#         "subtopics": [
#           {
#             "title": "Circuit Breakers",
#             "content": "Circuit breakers are automatic electrical switches..."
#           },
#           {
#             "title": "Fuses",
#             "content": "A fuse is a safety device consisting of a strip of wire..."
#           }
#         ],
#         "metadata": {
#           "level": "intermediate",
#           "week": 3
#         }
#       },
#       "num_questions": 10,
#       "question_types": ["multiple_choice", "short_answer", "open_ended"],
#       "difficulty": "medium"
#     }
#     ```
    
#     **Response:** Quiz object with generated questions
#     """
#     try:
#         logger.info(f"Received quiz generation request for: {request.notes.topic}")
        
#         # Validate input
#         if not request.notes.subtopics:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Notes must contain at least one subtopic"
#             )
        
#         if request.num_questions < 1 or request.num_questions > 50:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Number of questions must be between 1 and 50"
#             )
        
#         # Generate quiz
#         quiz = await quiz_service.generate_quiz(request)
        
#         logger.info(f"Quiz generated successfully: {quiz.quiz_id}")
        
#         return quiz
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Quiz generation error: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate quiz: {str(e)}"
#         )


# @router.post("/generate-simple")
# async def generate_quiz_simple(
#     course: str,
#     topic: str,
#     content: str,
#     num_questions: int = 5,
#     question_type: str = "multiple_choice"
# ):
#     """
#     Simplified endpoint for quick quiz generation with single content block.
    
#     **Query Parameters:**
#     - course: Course name
#     - topic: Topic name
#     - content: The learning content (text)
#     - num_questions: Number of questions (default: 5)
#     - question_type: Type of questions (default: "multiple_choice")
    
#     **Example:**
#     ```
#     POST /api/quiz/generate-simple
#     {
#       "course": "Carpentry",
#       "topic": "Wood Joints",
#       "content": "A mortise and tenon joint is one of the strongest...",
#       "num_questions": 3,
#       "question_type": "multiple_choice"
#     }
#     ```
#     """
#     try:
#         # Create notes structure
#         notes = NotesInput(
#             course=course,
#             topic=topic,
#             subtopics=[
#                 SubTopic(title=topic, content=content)
#             ]
#         )
        
#         # Create request
#         request = QuizGenerationRequest(
#             notes=notes,
#             num_questions=num_questions,
#             question_types=[question_type]
#         )
        
#         # Generate quiz
#         quiz = await quiz_service.generate_quiz(request)
        
#         return quiz
        
#     except Exception as e:
#         logger.error(f"Simple quiz generation error: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate quiz: {str(e)}"
#         )


# @router.post("/preview")
# async def preview_quiz_format(num_questions: int, question_types: List[str]):
#     """
#     Preview how questions will be distributed across types.
    
#     **Example:**
#     ```json
#     {
#       "num_questions": 10,
#       "question_types": ["multiple_choice", "short_answer", "open_ended"]
#     }
#     ```
    
#     **Response:**
#     ```json
#     {
#       "total_questions": 10,
#       "distribution": {
#         "multiple_choice": 4,
#         "short_answer": 3,
#         "open_ended": 3
#       }
#     }
#     ```
#     """
#     distribution = quiz_service._calculate_question_distribution(
#         num_questions,
#         question_types
#     )
    
#     return {
#         "total_questions": num_questions,
#         "distribution": distribution,
#         "question_types": question_types
#     }


# @router.get("/health")
# async def health_check():
#     """Check if quiz generation service is running"""
#     return {
#         "status": "healthy",
#         "service": "quiz_generation",
#         "model": quiz_service.model,
#         "available_question_types": [
#             "multiple_choice",
#             "short_answer", 
#             "open_ended"
#         ]
#     }


# @router.post("/export/{quiz_id}")
# async def export_quiz(quiz_id: str, format: str = "json"):
#     """
#     Export a generated quiz in different formats.
    
#     **Note:** This is a placeholder. In production, you'd store generated quizzes
#     and retrieve them by quiz_id.
#     """
#     # This would typically retrieve from database
#     return {
#         "message": "Export functionality - integrate with your database",
#         "quiz_id": quiz_id,
#         "format": format
#     }