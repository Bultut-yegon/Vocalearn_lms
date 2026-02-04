"""
Grading Service
Works with the questions of : multiple_choice, true_false, short_answer
Location: app/services/grading_service.py
"""

import os
import httpx
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from app.core.logging_config import logger

load_dotenv()


class GradingService:
    """Auto-grading service compatible with legacy quiz format."""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQAPI_KEY")
        if not self.groq_api_key:
            logger.warning(" GROQAPI_KEY not found. LLM grading unavailable.")
        
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
        self.grade_scale = {
            90: "A", 80: "B", 70: "C", 60: "D", 0: "F"
        }
        
        logger.info("GradingService initialized (Legacy Format Compatible)")
    
    def grade_closed_ended(self, question: Dict) -> Dict:
        """Grade MCQ and True/False questions."""
        correct = str(question["correct_answer"]).strip().lower()
        student = str(question["student_answer"]).strip().lower()
        
        is_correct = correct == student
        awarded_points = question["points"] if is_correct else 0
        
        question_text = question.get("question_text", "Question")
        
        feedback = (
            "Correct! Well done." if is_correct 
            else f"Incorrect. The correct answer is: {question['correct_answer']}"
        )
        
        return {
            "question_id": question["question_id"],
            "question_type": question["question_type"],
            "max_points": question["points"],
            "awarded_points": awarded_points,
            "is_correct": is_correct,
            "feedback": feedback,
            "strengths": ["Accurate response"] if is_correct else None,
            "improvements": [f"Review: {question_text}"] if not is_correct else None
        }
    
    async def grade_open_ended_with_llm(self, question: Dict) -> Dict:
        """Grade open-ended questions using LLM."""
        
        if not self.groq_api_key:
            logger.warning(" GROQ_API_KEY not available, using fallback")
            return self._fallback_keyword_grading(question)
        
        system_prompt = """You are a TVET instructor grading student responses.
Evaluate fairly and provide constructive feedback.

OUTPUT FORMAT (JSON only, no markdown):
{
  "score_percentage": <0-100>,
  "strengths": ["strength1", "strength2"],
  "improvements": ["improvement1", "improvement2"],
  "feedback": "detailed feedback text"
}"""

        keywords_hint = ""
        if question.get("keywords"):
            keywords_hint = f"\n\nKey concepts: {', '.join(question['keywords'])}"
        
        user_prompt = f"""Grade this response:

QUESTION: {question['question_text']}

RUBRIC: {question['rubric']}{keywords_hint}

STUDENT ANSWER: {question['student_answer']}

Return ONLY JSON with score_percentage (0-100), strengths, improvements, and feedback."""

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    self.groq_url,
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    llm_output = result["choices"][0]["message"]["content"]
                    
                    grading_data = self._parse_llm_grading(llm_output)
                    
                    score_percentage = grading_data["score_percentage"]
                    awarded_points = (score_percentage / 100) * question["points"]
                    
                    return {
                        "question_id": question["question_id"],
                        "question_type": question["question_type"],
                        "max_points": question["points"],
                        "awarded_points": round(awarded_points, 2),
                        "is_correct": None,
                        "feedback": grading_data["feedback"],
                        "strengths": grading_data["strengths"],
                        "improvements": grading_data["improvements"]
                    }
                else:
                    logger.error(f"Groq API error: {response.status_code}")
                    raise Exception(f"LLM grading failed: {response.status_code}")
        
        except Exception as e:
            logger.error(f" Open-ended grading failed: {e}")
            return self._fallback_keyword_grading(question)
    
    def _parse_llm_grading(self, llm_output: str) -> Dict:
        """Parse LLM grading output."""
        try:
            llm_output = re.sub(r'```json\n?', '', llm_output)
            llm_output = re.sub(r'```\n?', '', llm_output)
            llm_output = llm_output.strip()
            
            grading_data = json.loads(llm_output)
            
            if "score_percentage" not in grading_data:
                raise ValueError("Missing score_percentage")
            
            grading_data["score_percentage"] = max(0, min(100, grading_data["score_percentage"]))
            grading_data.setdefault("strengths", [])
            grading_data.setdefault("improvements", [])
            grading_data.setdefault("feedback", "Response evaluated.")
            
            return grading_data
            
        except Exception as e:
            logger.error(f"Failed to parse LLM output: {e}")
            return {
                "score_percentage": 50,
                "strengths": ["Attempted the question"],
                "improvements": ["Provide more detail"],
                "feedback": "Answer needs more detail."
            }
    
    def _fallback_keyword_grading(self, question: Dict) -> Dict:
        """Fallback grading using keyword matching."""
        student_answer = question["student_answer"].lower()
        keywords = question.get("keywords", [])
        
        if not keywords:
            score_percentage = 60
            feedback = "Answer received but couldn't be fully evaluated."
        else:
            matches = sum(1 for kw in keywords if kw.lower() in student_answer)
            score_percentage = min(100, (matches / len(keywords)) * 100)
            feedback = f"Found {matches}/{len(keywords)} key concepts."
        
        awarded_points = (score_percentage / 100) * question["points"]
        
        return {
            "question_id": question["question_id"],
            "question_type": question["question_type"],
            "max_points": question["points"],
            "awarded_points": round(awarded_points, 2),
            "is_correct": None,
            "feedback": feedback,
            "strengths": ["Answered"] if score_percentage > 50 else None,
            "improvements": ["Include more key concepts"]
        }
    
    def calculate_letter_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade."""
        for threshold, grade in sorted(self.grade_scale.items(), reverse=True):
            if percentage >= threshold:
                return grade
        return "F"
    
    async def grade_quiz_from_generation_service(
        self,
        submission_id: str,
        student_id: str,
        quiz_data: Dict,
        student_answers: Dict[str, str]
    ) -> Dict:
        """
        Grade a quiz in LEGACY format.
        
        Handles: multiple_choice, true_false, short_answer
        """
        
        closed_ended = []
        open_ended = []
        
        logger.info(f" Processing quiz with legacy format")
        logger.info(f"Keys in quiz_data: {quiz_data.keys()}")
        
        # Process MCQs ( "multiple_choice")
        mcq_questions = quiz_data.get("multiple_choice", [])
        logger.info(f"Found {len(mcq_questions)} MCQ questions")
        
        for idx, mcq in enumerate(mcq_questions):
            answer_key = f"mcq_{idx}"
            if answer_key in student_answers:
                closed_ended.append({
                    "question_id": answer_key,
                    "question_text": mcq.get("question", "Question"),
                    "question_type": "mcq",
                    "correct_answer": mcq["correct_answer"],
                    "student_answer": student_answers[answer_key],
                    "points": 1  # Default 1 point per MCQ
                })
        
        # Process True/False ( "true_false")
        tf_questions = quiz_data.get("true_false", [])
        logger.info(f"Found {len(tf_questions)} T/F questions")
        
        for idx, tf in enumerate(tf_questions):
            answer_key = f"tf_{idx}"
            if answer_key in student_answers:
                closed_ended.append({
                    "question_id": answer_key,
                    "question_text": tf.get("question", "Statement"),
                    "question_type": "true_false",
                    "correct_answer": str(tf["correct_answer"]).lower(),
                    "student_answer": str(student_answers[answer_key]).lower(),
                    "points": 1  # Default 1 point per T/F
                })
        
        # Process Short Answer (legacy format: "short_answer")
        sa_questions = quiz_data.get("short_answer", [])
        logger.info(f"Found {len(sa_questions)} short answer questions")
        
        for idx, sa in enumerate(sa_questions):
            answer_key = f"sa_{idx}"
            if answer_key in student_answers:
                open_ended.append({
                    "question_id": answer_key,
                    "question_text": sa.get("question", "Question"),
                    "question_type": "short_answer",
                    "rubric": sa.get("sample_answer", ""),
                    "keywords": sa.get("key_points", []),
                    "student_answer": student_answers[answer_key],
                    "points": 2  # Default 2 points per short answer
                })
        
        logger.info(
            f"Processing: {len(closed_ended)} closed-ended, "
            f"{len(open_ended)} open-ended questions"
        )
        
        # Grade all questions
        question_results = []
        
        # Grade closed-ended
        for q in closed_ended:
            result = self.grade_closed_ended(q)
            question_results.append(result)
            logger.info(f"Graded {result['question_id']}: {result['awarded_points']}/{result['max_points']}")
        
        # Grade open-ended
        for q in open_ended:
            result = await self.grade_open_ended_with_llm(q)
            question_results.append(result)
            logger.info(f"Graded {result['question_id']}: {result['awarded_points']}/{result['max_points']}")
        
        # Calculate totals
        total_awarded = sum(r["awarded_points"] for r in question_results)
        total_max = sum(r["max_points"] for r in question_results)
        percentage = (total_awarded / total_max * 100) if total_max > 0 else 0
        
        # Get topic
        topic = quiz_data.get("difficulty_level", "General Assessment")
        
        # Generate feedback
        overall_feedback = self._generate_simple_feedback(percentage)
        
        result = {
            "submission_id": submission_id,
            "student_id": student_id,
            "topic": topic,
            "total_points": round(total_awarded, 2),
            "max_points": total_max,
            "percentage": round(percentage, 2),
            "grade_letter": self.calculate_letter_grade(percentage),
            "question_results": question_results,
            "overall_feedback": overall_feedback,
            "topic_mastery": {topic: round(percentage, 2)},
            "graded_at": datetime.now().isoformat()
        }
        
        logger.info(
            f"Grading complete: {percentage:.1f}% "
            f"({total_awarded}/{total_max} points)"
        )
        
        return result
    
    def _generate_simple_feedback(self, percentage: float) -> str:
        """Generate simple feedback based on percentage."""
        if percentage >= 90:
            return "Excellent work! You've demonstrated strong mastery."
        elif percentage >= 80:
            return "Great job! You're showing good understanding."
        elif percentage >= 70:
            return "Good effort. Review the areas marked for improvement."
        elif percentage >= 60:
            return "Passing, but there's room to grow. Keep practicing!"
        else:
            return "Keep working on it. Review the material and try again."