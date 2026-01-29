# from fastapi import APIRouter, HTTPException, status
# from app.models.grading_models import (
#     GradingRequest,
#     GradingResult,
#     QuestionGradeResult
# )
# from app.services.grading_service import GradingService
# from app.core.logging_config import logger

# router = APIRouter()
# grading_service = GradingService()

# @router.post(
#     "/grade",
#     response_model=GradingResult,
#     summary="Grade student submission",
#     description="Auto-grade both closed and open-ended questions with AI-powered evaluation"
# )
# async def grade_submission(request: GradingRequest):
#     """
#     Comprehensive auto-grading for student submissions.
    
#     Features:
#     - Fast deterministic grading for MCQs and True/False
#     - LLM-powered evaluation for open-ended questions
#     - Partial credit for open-ended responses
#     - Detailed feedback per question
#     - Overall performance analysis
#     - Topic mastery breakdown
    
#     Returns complete grading results with scores, feedback, and recommendations.
#     """
#     try:
#         logger.info(f"Grading submission {request.submission_id} for student {request.student_id}")
        
#         # Convert Pydantic models to dicts
#         closed_questions = [q.model_dump() for q in request.closed_ended_questions]
#         open_questions = [q.model_dump() for q in request.open_ended_questions]
        
#         # Grade the submission
#         result = await grading_service.grade_submission(
#             submission_id=request.submission_id,
#             student_id=request.student_id,
#             topic=request.topic,
#             closed_ended_questions=closed_questions,
#             open_ended_questions=open_questions
#         )
        
#         logger.info(f"Successfully graded submission {request.submission_id}: {result['percentage']:.1f}%")
#         return GradingResult(**result)
        
#     except Exception as e:
#         logger.error(f"Grading failed for submission {request.submission_id}: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to grade submission: {str(e)}"
#         )

# @router.post(
#     "/grade-batch",
#     summary="Grade multiple submissions in batch",
#     description="Process multiple student submissions efficiently"
# )
# async def grade_batch(requests: list[GradingRequest]):
#     """
#     Batch grading for multiple submissions.
#     Useful for grading entire class assessments.
#     """
#     try:
#         results = []
        
#         for request in requests:
#             closed_questions = [q.model_dump() for q in request.closed_ended_questions]
#             open_questions = [q.model_dump() for q in request.open_ended_questions]
            
#             result = await grading_service.grade_submission(
#                 submission_id=request.submission_id,
#                 student_id=request.student_id,
#                 topic=request.topic,
#                 closed_ended_questions=closed_questions,
#                 open_ended_questions=open_questions
#             )
            
#             results.append(result)
#             logger.info(f"Batch graded: {request.submission_id}")
        
#         return {
#             "total_graded": len(results),
#             "results": results,
#             "batch_summary": {
#                 "average_score": sum(r["percentage"] for r in results) / len(results) if results else 0,
#                 "highest_score": max((r["percentage"] for r in results), default=0),
#                 "lowest_score": min((r["percentage"] for r in results), default=0)
#             }
#         }
        
#     except Exception as e:
#         logger.error(f"Batch grading failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Batch grading failed: {str(e)}"
#         )

# @router.get(
#     "/health",
#     summary="Check grading service health"
# )
# async def health_check():
#     """Health check endpoint for grading service."""
#     return {
#         "status": "healthy",
#         "service": "auto-grading",
#         "features": [
#             "closed_ended_grading",
#             "open_ended_grading",
#             "llm_evaluation",
#             "partial_credit",
#             "detailed_feedback",
#             "topic_mastery_analysis",
#             "batch_processing"
#         ],
#         "supported_question_types": [
#             "mcq",
#             "true_false",
#             "short_answer",
#             "essay",
#             "practical"
#         ]
#     }










# VERSION 2






# """
# Grading Router - Auto-grade student quiz submissions
# Location: app/api/v1/grading_router.py
# """

# from fastapi import APIRouter, HTTPException, status
# from pydantic import BaseModel, Field
# from typing import List, Dict, Optional
# from app.models.grading_models import (
#     GradingRequest,
#     GradingResult,
#     QuestionGradeResult
# )
# from app.services.grading_service import GradingService
# from app.core.logging_config import logger
# import os

# router = APIRouter()

# # Initialize grading service
# try:
#     grading_service = GradingService()
#     logger.info("✅ Grading Service initialized")
# except Exception as e:
#     logger.error(f"❌ Failed to initialize Grading Service: {e}")
#     grading_service = None


# # ============================================================================
# # ADDITIONAL MODELS (for quiz integration)
# # ============================================================================

# class QuizSubmission(BaseModel):
#     """Submission for a quiz generated by quiz service"""
#     submission_id: str
#     student_id: str
#     quiz_id: str
#     quiz_data: Dict  # The original quiz from quiz generation service
#     student_answers: Dict[str, str]  # {"mcq_0": "B", "tf_1": "true", "sa_2": "answer text"}


# # ============================================================================
# # ENDPOINTS
# # ============================================================================

# def check_service():
#     """Verify grading service is available"""
#     if grading_service is None:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="Grading service unavailable. Check configuration."
#         )


# @router.post(
#     "/grade",
#     response_model=GradingResult,
#     summary="Grade student submission",
#     description="Auto-grade both closed and open-ended questions with AI-powered evaluation"
# )
# async def grade_submission(request: GradingRequest):
#     """
#     Comprehensive auto-grading for student submissions.
    
#     Features:
#     - Fast deterministic grading for MCQs and True/False
#     - LLM-powered evaluation for open-ended questions
#     - Partial credit for open-ended responses
#     - Detailed feedback per question
#     - Overall performance analysis
#     - Topic mastery breakdown
    
#     Returns complete grading results with scores, feedback, and recommendations.
#     """
#     check_service()
    
#     try:
#         logger.info(f"Grading submission {request.submission_id} for student {request.student_id}")
        
#         # Convert Pydantic models to dicts
#         closed_questions = [q.model_dump() for q in request.closed_ended_questions]
#         open_questions = [q.model_dump() for q in request.open_ended_questions]
        
#         # Grade the submission
#         result = await grading_service.grade_submission(
#             submission_id=request.submission_id,
#             student_id=request.student_id,
#             topic=request.topic,
#             closed_ended_questions=closed_questions,
#             open_ended_questions=open_questions
#         )
        
#         logger.info(f"✅ Successfully graded submission {request.submission_id}: {result['percentage']:.1f}%")
#         return GradingResult(**result)
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"❌ Grading failed for submission {request.submission_id}: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to grade submission: {str(e)}"
#         )


# @router.post(
#     "/grade-quiz",
#     summary="Grade quiz generated by quiz service",
#     description="Grade a quiz that was generated by the quiz generation service - easiest method!"
# )
# async def grade_quiz_submission(request: QuizSubmission):
#     """
#     Grade a quiz that was generated by the quiz generation service.
    
#     This is the easiest way to grade - just pass the quiz and student answers!
    
#     **Features:**
#     - Automatically extracts questions from quiz_data
#     - Grades MCQ, True/False, and Short Answer
#     - Returns detailed feedback
#     - Calculates overall score and letter grade
    
#     **Request Example:**
#     ```json
#     {
#       "submission_id": "sub_789",
#       "student_id": "student_456",
#       "quiz_id": "quiz_abc123",
#       "quiz_data": {
#         "quiz_id": "quiz_abc123",
#         "difficulty_level": "intermediate",
#         "multiple_choice": [...],
#         "true_false": [...],
#         "short_answer": [...]
#       },
#       "student_answers": {
#         "mcq_0": "B",
#         "tf_0": "false",
#         "sa_0": "answer text"
#       }
#     }
#     ```
#     """
#     check_service()
    
#     try:
#         logger.info(f"Grading quiz submission {request.submission_id} for quiz {request.quiz_id}")
        
#         # Grade using the quiz service integration
#         result = await grading_service.grade_quiz_generated_by_service(
#             submission_id=request.submission_id,
#             student_id=request.student_id,
#             quiz_data=request.quiz_data,
#             student_answers=request.student_answers
#         )
        
#         logger.info(f"✅ Graded quiz {request.quiz_id}: {result['percentage']:.1f}%")
        
#         return result
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"❌ Quiz grading failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Quiz grading failed: {str(e)}"
#         )


# @router.post(
#     "/grade-batch",
#     summary="Grade multiple submissions in batch",
#     description="Process multiple student submissions efficiently"
# )
# async def grade_batch(requests: List[GradingRequest]):
#     """
#     Batch grading for multiple submissions.
#     Useful for grading entire class assessments.
    
#     **Features:**
#     - Grades multiple submissions in one request
#     - Returns individual results plus batch summary
#     - Calculates class statistics (avg, high, low)
    
#     **Use Case:** Grade all students' submissions after a quiz
#     """
#     check_service()
    
#     try:
#         results = []
        
#         for request in requests:
#             closed_questions = [q.model_dump() for q in request.closed_ended_questions]
#             open_questions = [q.model_dump() for q in request.open_ended_questions]
            
#             result = await grading_service.grade_submission(
#                 submission_id=request.submission_id,
#                 student_id=request.student_id,
#                 topic=request.topic,
#                 closed_ended_questions=closed_questions,
#                 open_ended_questions=open_questions
#             )
            
#             results.append(result)
#             logger.info(f"Batch graded: {request.submission_id}")
        
#         batch_summary = {
#             "total_graded": len(results),
#             "average_score": round(sum(r["percentage"] for r in results) / len(results), 2) if results else 0,
#             "highest_score": max((r["percentage"] for r in results), default=0),
#             "lowest_score": min((r["percentage"] for r in results), default=0),
#             "grade_distribution": {
#                 "A": sum(1 for r in results if r["percentage"] >= 90),
#                 "B": sum(1 for r in results if 80 <= r["percentage"] < 90),
#                 "C": sum(1 for r in results if 70 <= r["percentage"] < 80),
#                 "D": sum(1 for r in results if 60 <= r["percentage"] < 70),
#                 "F": sum(1 for r in results if r["percentage"] < 60)
#             }
#         }
        
#         logger.info(f"✅ Batch graded {len(results)} submissions. Avg: {batch_summary['average_score']}%")
        
#         return {
#             "results": results,
#             "batch_summary": batch_summary
#         }
        
#     except Exception as e:
#         logger.error(f"❌ Batch grading failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Batch grading failed: {str(e)}"
#         )


# @router.post(
#     "/grade-sample",
#     summary="Grade a sample submission (for testing)",
#     description="Test the grading service with built-in sample data"
# )
# async def grade_sample():
#     """
#     Grade a sample submission for testing.
#     No request body needed - uses built-in test data.
    
#     **Use Case:** Quick test to verify grading service is working
#     """
#     check_service()
    
#     # Sample test data
#     from app.models.grading_models import ClosedEndedQuestion, OpenEndedQuestion
    
#     sample_request = GradingRequest(
#         submission_id="test_sub_001",
#         student_id="test_student_001",
#         topic="Circuit Breakers",
#         closed_ended_questions=[
#             ClosedEndedQuestion(
#                 question_id="q1",
#                 question_type="multiple_choice",
#                 correct_answer="B",
#                 student_answer="B",
#                 points=1
#             ),
#             ClosedEndedQuestion(
#                 question_id="q2",
#                 question_type="true_false",
#                 correct_answer="false",
#                 student_answer="false",
#                 points=1
#             )
#         ],
#         open_ended_questions=[
#             OpenEndedQuestion(
#                 question_id="q3",
#                 question_type="short_answer",
#                 question_text="Explain how a thermal circuit breaker works.",
#                 rubric="Should mention: bimetallic strip that bends when heated by excessive current, triggering the breaker to trip",
#                 student_answer="A thermal circuit breaker uses a bimetallic strip. When too much current flows, the strip heats up and bends. This bending motion triggers the breaker to trip and stop the current.",
#                 keywords=["bimetallic strip", "heat", "current", "trip"],
#                 points=2
#             )
#         ]
#     )
    
#     closed_questions = [q.model_dump() for q in sample_request.closed_ended_questions]
#     open_questions = [q.model_dump() for q in sample_request.open_ended_questions]
    
#     result = await grading_service.grade_submission(
#         submission_id=sample_request.submission_id,
#         student_id=sample_request.student_id,
#         topic=sample_request.topic,
#         closed_ended_questions=closed_questions,
#         open_ended_questions=open_questions
#     )
    
#     return {
#         "message": "Sample grading completed",
#         "request": sample_request.model_dump(),
#         "result": result
#     }


# @router.get(
#     "/health",
#     summary="Check grading service health"
# )
# async def health_check():
#     """
#     Health check endpoint for grading service.
    
#     Returns service status and available features.
#     """
#     if grading_service is None:
#         return {
#             "status": "unavailable",
#             "service": "auto-grading",
#             "error": "Service not initialized"
#         }
    
#     groq_available = bool(os.getenv("GROQ_API_KEY"))
    
#     return {
#         "status": "healthy",
#         "service": "auto-grading",
#         "llm_grading_available": groq_available,
#         "features": [
#             "closed_ended_grading",
#             "open_ended_grading",
#             "llm_evaluation",
#             "partial_credit",
#             "detailed_feedback",
#             "topic_mastery_analysis",
#             "batch_processing",
#             "quiz_integration"
#         ],
#         "supported_question_types": [
#             "multiple_choice",
#             "true_false",
#             "short_answer",
#             "essay"
#         ],
#         "endpoints": {
#             "basic_grading": "/grade",
#             "quiz_grading": "/grade-quiz",
#             "batch_grading": "/grade-batch",
#             "sample_test": "/grade-sample"
#         }
#     }


# @router.get(
#     "/statistics",
#     summary="Get grading statistics",
#     description="Get overview of grading service usage and performance"
# )
# async def get_statistics():
#     """
#     Get grading service statistics.
    
#     **Note:** This is a placeholder. In production, you'd track:
#     - Total submissions graded
#     - Average scores by topic
#     - Most common mistakes
#     - Grading performance metrics
#     """
#     return {
#         "message": "Statistics endpoint - integrate with your database",
#         "suggested_metrics": {
#             "total_submissions_graded": "Track in database",
#             "average_score_by_topic": "Aggregate from grading results",
#             "grade_distribution": "Calculate from all submissions",
#             "common_mistakes": "Analyze incorrect answers",
#             "grading_performance": "Track API response times"
#         }
#     }






# VERSION 3







# """
# Grading Router - Auto-grade student quiz submissions
# Location: app/api/v1/grading_router.py
# """

# from fastapi import APIRouter, HTTPException, status
# from pydantic import BaseModel, Field
# from typing import List, Dict, Optional
# from app.models.grading_models import (
#     GradingRequest,
#     GradingResult,
#     QuestionGradeResult
# )
# from app.services.grading_service import GradingService
# from app.core.logging_config import logger
# import os

# router = APIRouter()

# # Initialize grading service
# try:
#     grading_service = GradingService()
#     logger.info(" Grading Service initialized")
# except Exception as e:
#     logger.error(f" Failed to initialize Grading Service: {e}")
#     grading_service = None


# # ============================================================================
# # ADDITIONAL MODELS (for quiz integration)
# # ============================================================================

# class QuizSubmission(BaseModel):
#     """Submission for a quiz generated by quiz service"""
#     submission_id: str
#     student_id: str
#     quiz_id: str
#     topic: Optional[str] = "General Assessment"  # Added with default
#     quiz_data: Dict  # The original quiz from quiz generation service
#     student_answers: Dict[str, str]  # {"mcq_0": "B", "tf_1": "true", "sa_2": "answer text"}



# # ENDPOINTS


# def check_service():
#     """Verify grading service is available"""
#     if grading_service is None:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="Grading service unavailable. Check configuration."
#         )


# @router.post(
#     "/grade",
#     response_model=GradingResult,
#     summary="Grade student submission",
#     description="Auto-grade both closed and open-ended questions with AI-powered evaluation"
# )
# async def grade_submission(request: GradingRequest):
#     """
#     Comprehensive auto-grading for student submissions.
    
#     Features:
#     - Fast deterministic grading for MCQs and True/False
#     - LLM-powered evaluation for open-ended questions
#     - Partial credit for open-ended responses
#     - Detailed feedback per question
#     - Overall performance analysis
#     - Topic mastery breakdown
    
#     Returns complete grading results with scores, feedback, and recommendations.
#     """
#     check_service()
    
#     try:
#         logger.info(f"Grading submission {request.submission_id} for student {request.student_id}")
        
#         # Convert Pydantic models to dicts
#         closed_questions = [q.model_dump() for q in request.closed_ended_questions]
#         open_questions = [q.model_dump() for q in request.open_ended_questions]
        
#         # Grade the submission
#         result = await grading_service.grade_submission(
#             submission_id=request.submission_id,
#             student_id=request.student_id,
#             topic=request.topic,
#             closed_ended_questions=closed_questions,
#             open_ended_questions=open_questions
#         )
        
#         logger.info(f"Successfully graded submission {request.submission_id}: {result['percentage']:.1f}%")
#         return GradingResult(**result)
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Grading failed for submission {request.submission_id}: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to grade submission: {str(e)}"
#         )


# @router.post(
#     "/grade-quiz",
#     summary="Grade quiz generated by quiz service",
#     description="Grade a quiz that was generated by the quiz generation service - easiest method!"
# )
# async def grade_quiz_submission(request: QuizSubmission):
#     """
#     Grade a quiz that was generated by the quiz generation service.
    
#     This is the easiest way to grade - just pass the quiz and student answers!
    
#     **Features:**
#     - Automatically extracts questions from quiz_data
#     - Grades MCQ, True/False, and Short Answer
#     - Returns detailed feedback
#     - Calculates overall score and letter grade
    
#     **Request Example:**
#     ```json
#     {
#       "submission_id": "sub_789",
#       "student_id": "student_456",
#       "quiz_id": "quiz_abc123",
#       "quiz_data": {
#         "quiz_id": "quiz_abc123",
#         "difficulty_level": "intermediate",
#         "multiple_choice": [...],
#         "true_false": [...],
#         "short_answer": [...]
#       },
#       "student_answers": {
#         "mcq_0": "B",
#         "tf_0": "false",
#         "sa_0": "answer text"
#       }
#     }
#     ```
#     """
#     check_service()
    
#     try:
#         logger.info(f"Grading quiz submission {request.submission_id} for quiz {request.quiz_id}")
        
#         # Grade using the quiz service integration
#         result = await grading_service.grade_quiz_generated_by_service(
#             submission_id=request.submission_id,
#             student_id=request.student_id,
#             quiz_data=request.quiz_data,
#             student_answers=request.student_answers
#         )
        
#         logger.info(f" Graded quiz {request.quiz_id}: {result['percentage']:.1f}%")
        
#         return result
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Quiz grading failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Quiz grading failed: {str(e)}"
#         )


# @router.post(
#     "/grade-batch",
#     summary="Grade multiple submissions in batch",
#     description="Process multiple student submissions efficiently"
# )
# async def grade_batch(requests: List[GradingRequest]):
#     """
#     Batch grading for multiple submissions.
#     Useful for grading entire class assessments.
    
#     **Features:**
#     - Grades multiple submissions in one request
#     - Returns individual results plus batch summary
#     - Calculates class statistics (avg, high, low)
    
#     **Use Case:** Grade all students' submissions after a quiz
#     """
#     check_service()
    
#     try:
#         results = []
        
#         for request in requests:
#             closed_questions = [q.model_dump() for q in request.closed_ended_questions]
#             open_questions = [q.model_dump() for q in request.open_ended_questions]
            
#             result = await grading_service.grade_submission(
#                 submission_id=request.submission_id,
#                 student_id=request.student_id,
#                 topic=request.topic,
#                 closed_ended_questions=closed_questions,
#                 open_ended_questions=open_questions
#             )
            
#             results.append(result)
#             logger.info(f"Batch graded: {request.submission_id}")
        
#         batch_summary = {
#             "total_graded": len(results),
#             "average_score": round(sum(r["percentage"] for r in results) / len(results), 2) if results else 0,
#             "highest_score": max((r["percentage"] for r in results), default=0),
#             "lowest_score": min((r["percentage"] for r in results), default=0),
#             "grade_distribution": {
#                 "A": sum(1 for r in results if r["percentage"] >= 90),
#                 "B": sum(1 for r in results if 80 <= r["percentage"] < 90),
#                 "C": sum(1 for r in results if 70 <= r["percentage"] < 80),
#                 "D": sum(1 for r in results if 60 <= r["percentage"] < 70),
#                 "F": sum(1 for r in results if r["percentage"] < 60)
#             }
#         }
        
#         logger.info(f"Batch graded {len(results)} submissions. Avg: {batch_summary['average_score']}%")
        
#         return {
#             "results": results,
#             "batch_summary": batch_summary
#         }
        
#     except Exception as e:
#         logger.error(f" Batch grading failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Batch grading failed: {str(e)}"
#         )


# @router.post(
#     "/grade-sample",
#     summary="Grade a sample submission (for testing)",
#     description="Test the grading service with built-in sample data"
# )
# async def grade_sample():
#     """
#     Grade a sample submission for testing.
#     No request body needed - uses built-in test data.
    
#     **Use Case:** Quick test to verify grading service is working
#     """
#     check_service()
    
#     # Sample test data
#     from app.models.grading_models import ClosedEndedQuestion, OpenEndedQuestion
    
#     sample_request = GradingRequest(
#         submission_id="test_sub_001",
#         student_id="test_student_001",
#         topic="Circuit Breakers",
#         closed_ended_questions=[
#             ClosedEndedQuestion(
#                 question_id="q1",
#                 question_type="multiple_choice",
#                 correct_answer="B",
#                 student_answer="B",
#                 points=1
#             ),
#             ClosedEndedQuestion(
#                 question_id="q2",
#                 question_type="true_false",
#                 correct_answer="false",
#                 student_answer="false",
#                 points=1
#             )
#         ],
#         open_ended_questions=[
#             OpenEndedQuestion(
#                 question_id="q3",
#                 question_type="short_answer",
#                 question_text="Explain how a thermal circuit breaker works.",
#                 rubric="Should mention: bimetallic strip that bends when heated by excessive current, triggering the breaker to trip",
#                 student_answer="A thermal circuit breaker uses a bimetallic strip. When too much current flows, the strip heats up and bends. This bending motion triggers the breaker to trip and stop the current.",
#                 keywords=["bimetallic strip", "heat", "current", "trip"],
#                 points=2
#             )
#         ]
#     )
    
#     closed_questions = [q.model_dump() for q in sample_request.closed_ended_questions]
#     open_questions = [q.model_dump() for q in sample_request.open_ended_questions]
    
#     result = await grading_service.grade_submission(
#         submission_id=sample_request.submission_id,
#         student_id=sample_request.student_id,
#         topic=sample_request.topic,
#         closed_ended_questions=closed_questions,
#         open_ended_questions=open_questions
#     )
    
#     return {
#         "message": "Sample grading completed",
#         "request": sample_request.model_dump(),
#         "result": result
#     }


# @router.get(
#     "/health",
#     summary="Check grading service health"
# )
# async def health_check():
#     """
#     Health check endpoint for grading service.
    
#     Returns service status and available features.
#     """
#     if grading_service is None:
#         return {
#             "status": "unavailable",
#             "service": "auto-grading",
#             "error": "Service not initialized"
#         }
    
#     groq_available = bool(os.getenv("GROQAPI_KEY"))
    
#     return {
#         "status": "healthy",
#         "service": "auto-grading",
#         "llm_grading_available": groq_available,
#         "features": [
#             "closed_ended_grading",
#             "open_ended_grading",
#             "llm_evaluation",
#             "partial_credit",
#             "detailed_feedback",
#             "topic_mastery_analysis",
#             "batch_processing",
#             "quiz_integration"
#         ],
#         "supported_question_types": [
#             "multiple_choice",
#             "true_false",
#             "short_answer",
#             "essay"
#         ],
#         "endpoints": {
#             "basic_grading": "/grade",
#             "quiz_grading": "/grade-quiz",
#             "batch_grading": "/grade-batch",
#             "sample_test": "/grade-sample"
#         }
#     }


# @router.get(
#     "/statistics",
#     summary="Get grading statistics",
#     description="Get overview of grading service usage and performance"
# )
# async def get_statistics():
#     """
#     Get grading service statistics.
    
#     **Note:** This is a placeholder. In production, you'd track:
#     - Total submissions graded
#     - Average scores by topic
#     - Most common mistakes
#     - Grading performance metrics
#     """
#     return {
#         "message": "Statistics endpoint - integrate with your database",
#         "suggested_metrics": {
#             "total_submissions_graded": "Track in database",
#             "average_score_by_topic": "Aggregate from grading results",
#             "grade_distribution": "Calculate from all submissions",
#             "common_mistakes": "Analyze incorrect answers",
#             "grading_performance": "Track API response times"
#         }
#     }






# VERSION 4











"""
Simple Grading Router - Clean Output (No Recommendations)
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