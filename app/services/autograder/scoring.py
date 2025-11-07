# app/services/autograder/scoring.py
from typing import Dict, Any
from app.services.autograder.models import ShortAnswerGraderModel

grader_model = ShortAnswerGraderModel()

def grade_short_answer(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates rubric-based grading using a simple transformer inference.
    """
    answer = payload.get("answer_text", "")
    rubric = payload.get("rubric", [])
    context = payload.get("context", "")

    results = {}
    total = 0.0
    max_total = sum(r["max_score"] for r in rubric)

    for r in rubric:
        rubric_score = grader_model.predict(answer, context)
        # normalize score per rubric max
        normalized = min(rubric_score, r["max_score"])
        results[r["id"]] = normalized
        total += normalized

    # Generate feedback heuristically
    feedback = generate_feedback(answer, total, max_total)

    return {
        "scores": results,
        "total": round(total, 2),
        "max_total": round(max_total, 2),
        "feedback": feedback,
        "confidence": {r["id"]: 0.85 for r in rubric},  # mock confidence
    }


def generate_feedback(answer: str, total: float, max_total: float) -> str:
    ratio = total / max_total
    if ratio > 0.8:
        return "Excellent response! Well detailed and accurate."
    elif ratio > 0.5:
        return "Good effort, but expand on key concepts for full marks."
    else:
        return "Needs improvement — try to include more relevant details."
