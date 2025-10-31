# app/api/routes/quizgen.py
from fastapi import APIRouter, HTTPException
from app.services.quizgen.models import GenerateQuizRequest, GenerateQuizResponse, MCQItem, ShortQItem, TrueFalseItem
from app.services.quizgen.generator import QuizGenerator

router = APIRouter(prefix="/api/quizgen", tags=["QuizGen"])

gen = QuizGenerator()

@router.post("/generate", response_model=dict)
def generate_quiz(req: GenerateQuizRequest):
    """
    Generate an adaptive quiz. The backend can send 'content_candidates' as part
    of seed_text or call a separate endpoint to provide course snippets.
    """
    try:
        # We accept GenerateQuizRequest; the Java backend may pass extra fields via raw dict.
        payload = req.dict()
        seed = payload.get("seed_text") or ""
        num = payload.get("num_questions", req.num_questions)
        difficulty = payload.get("difficulty", "medium")
        qtypes = payload.get("question_types", None)
        # Optionally, the backend may include 'content_candidates' in the request body
        content_candidates = payload.get("content_candidates", None)

        quiz = gen.generate(seed_text=seed, num_questions=num, difficulty=difficulty,
                            question_types=qtypes, content_candidates=content_candidates)
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
