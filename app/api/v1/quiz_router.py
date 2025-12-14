from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from app.models.quiz_models import (
    QuizGenerationRequest,
    AdaptiveQuizRequest,
    QuizGenerationResult,
    BulkQuizRequest,
    DifficultyLevel
)
from app.services.quiz_service import QuizGeneratorService
from app.core.logging_config import logger
from typing import List

router = APIRouter()
quiz_service = QuizGeneratorService()

@router.post(
    "/generate",
    response_model=QuizGenerationResult,
    summary="Generate a complete quiz",
    description="AI-powered quiz generation with customizable parameters"
)
async def generate_quiz(request: QuizGenerationRequest):
    """
    Generate a comprehensive quiz with mixed question types.
    
    Features:
    - Multiple question types (MCQ, T/F, Short Answer, Essay)
    - Difficulty levels (Beginner, Intermediate, Advanced)
    - Topic and subtopic specification
    - Reference material integration
    - Avoidance of already covered topics
    
    Perfect for creating assessments on-demand!
    """
    try:
        logger.info(f"Generating quiz for topic: {request.topic}")
        
        result = await quiz_service.generate_quiz(
            topic=request.topic,
            difficulty=request.difficulty_level.value,
            num_mcq=request.num_mcq,
            num_true_false=request.num_true_false,
            num_short_answer=request.num_short_answer,
            num_essay=request.num_essay,
            subtopics=request.subtopics,
            avoid_topics=request.avoid_topics,
            reference_materials=request.reference_materials
        )
        
        logger.info(f"Successfully generated quiz: {result['quiz_id']} with {result['total_questions']} questions")
        return QuizGenerationResult(**result)
        
    except Exception as e:
        logger.error(f"Quiz generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )

@router.post(
    "/generate-adaptive",
    response_model=QuizGenerationResult,
    summary="Generate adaptive quiz based on student performance",
    description="Creates personalized quiz focusing on student's weak areas"
)
async def generate_adaptive_quiz(request: AdaptiveQuizRequest):
    """
    Generate an adaptive quiz tailored to individual student needs.
    
    Analyzes:
    - Recent performance data
    - Identified weak areas
    - Current mastery level
    
    Automatically adjusts:
    - Difficulty level
    - Topic focus
    - Question distribution
    """
    try:
        logger.info(f"Generating adaptive quiz for student: {request.student_id}")
        
        result = await quiz_service.generate_adaptive_quiz(
            student_id=request.student_id,
            topic=request.topic,
            total_questions=request.total_questions,
            recent_performance=request.recent_performance,
            weak_areas=request.weak_areas
        )
        
        logger.info(f"Generated adaptive quiz: {result['quiz_id']}")
        return QuizGenerationResult(**result)
        
    except Exception as e:
        logger.error(f"Adaptive quiz generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate adaptive quiz: {str(e)}"
        )

@router.post(
    "/generate-bulk",
    summary="Generate multiple quizzes in bulk",
    description="Batch generation for multiple topics"
)
async def generate_bulk_quizzes(request: BulkQuizRequest, background_tasks: BackgroundTasks):
    """
    Generate quizzes for multiple topics efficiently.
    Useful for curriculum-wide assessment preparation.
    """
    try:
        logger.info(f"Bulk generating quizzes for {len(request.topics)} topics")
        
        results = []
        
        for topic in request.topics:
            # Distribute questions based on difficulty if specified
            if request.difficulty_distribution:
                # This is simplified - in production you'd generate per difficulty
                difficulty = "intermediate"
            else:
                difficulty = "intermediate"
            
            # Calculate question distribution
            total = request.questions_per_topic
            num_mcq = int(total * 0.5)
            num_tf = int(total * 0.3)
            num_short = total - num_mcq - num_tf
            
            result = await quiz_service.generate_quiz(
                topic=topic,
                difficulty=difficulty,
                num_mcq=num_mcq,
                num_true_false=num_tf,
                num_short_answer=num_short,
                num_essay=0
            )
            
            results.append(result)
            logger.info(f"Generated bulk quiz for: {topic}")
        
        return {
            "total_quizzes_generated": len(results),
            "quizzes": results,
            "summary": {
                "topics_covered": request.topics,
                "total_questions": sum(q["total_questions"] for q in results),
                "total_points": sum(q["total_points"] for q in results)
            }
        }
        
    except Exception as e:
        logger.error(f"Bulk quiz generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk generation failed: {str(e)}"
        )

@router.post(
    "/quick-generate",
    summary="Quick quiz generation with defaults",
    description="Generate a standard 10-question quiz instantly"
)
async def quick_generate_quiz(topic: str, difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE):
    """
    One-click quiz generation with sensible defaults.
    Perfect for rapid assessment creation!
    
    Default: 5 MCQ + 3 T/F + 2 Short Answer
    """
    try:
        result = await quiz_service.generate_quiz(
            topic=topic,
            difficulty=difficulty.value,
            num_mcq=5,
            num_true_false=3,
            num_short_answer=2
        )
        
        logger.info(f"Quick generated quiz for: {topic}")
        return QuizGenerationResult(**result)
        
    except Exception as e:
        logger.error(f"Quick generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick generation failed: {str(e)}"
        )

@router.get(
    "/health",
    summary="Check quiz generation service health"
)
async def health_check():
    """Health check endpoint for quiz generation service."""
    return {
        "status": "healthy",
        "service": "quiz-generation",
        "features": [
            "standard_quiz_generation",
            "adaptive_quiz_generation",
            "bulk_generation",
            "quick_generation",
            "multi_question_types",
            "difficulty_levels",
            "subtopic_targeting",
            "reference_material_integration"
        ],
        "supported_question_types": [
            "mcq",
            "true_false",
            "short_answer",
            "essay",
            "practical"
        ],
        "difficulty_levels": [
            "beginner",
            "intermediate",
            "advanced"
        ]
    }