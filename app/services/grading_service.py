import os
import httpx
import json
import re
from typing import List, Dict, Tuple
from datetime import datetime
from app.core.logging_config import logger

class GradingService:
    """
    Advanced auto-grading service for TVET assessments.
    Handles both closed-ended and open-ended questions with LLM-powered evaluation.
    """
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
        # Grading scale
        self.grade_scale = {
            90: "A", 80: "B", 70: "C", 60: "D", 0: "F"
        }
    
    def grade_closed_ended(self, question: Dict) -> Dict:
        """
        Grade closed-ended questions (MCQ, True/False).
        Fast, deterministic grading.
        """
        correct = question["correct_answer"].strip().lower()
        student = question["student_answer"].strip().lower()
        
        is_correct = correct == student
        awarded_points = question["points"] if is_correct else 0
        
        feedback = "Correct! Well done." if is_correct else f"Incorrect. The correct answer is: {question['correct_answer']}"
        
        return {
            "question_id": question["question_id"],
            "question_type": question["question_type"],
            "max_points": question["points"],
            "awarded_points": awarded_points,
            "is_correct": is_correct,
            "feedback": feedback,
            "strengths": ["Accurate response"] if is_correct else None,
            "improvements": ["Review this concept"] if not is_correct else None
        }
    
    async def grade_open_ended_with_llm(self, question: Dict) -> Dict:
        """
        Grade open-ended questions using LLM with rubric-based evaluation.
        Provides detailed feedback and partial credit.
        """
        
        # Prepare grading prompt
        system_prompt = """You are an experienced TVET instructor grading student responses for wiring and plumbing courses.
Your task is to evaluate student answers fairly and provide constructive feedback.

GRADING GUIDELINES:
- Be fair but strict in technical accuracy
- Award partial credit for partially correct answers
- Consider practical application knowledge
- Identify both strengths and areas for improvement
- Provide specific, actionable feedback

OUTPUT FORMAT (JSON only, no markdown):
{
  "score_percentage": <0-100>,
  "strengths": ["strength1", "strength2"],
  "improvements": ["improvement1", "improvement2"],
  "feedback": "detailed feedback text"
}"""

        keywords_hint = ""
        if question.get("keywords"):
            keywords_hint = f"\n\nKey concepts to look for: {', '.join(question['keywords'])}"
        
        context_hint = ""
        if question.get("context"):
            context_hint = f"\n\nTopic context: {question['context']}"
        
        user_prompt = f"""Grade this student response:

QUESTION: {question['question_text']}

RUBRIC/EXPECTED ANSWER: {question['rubric']}{keywords_hint}{context_hint}

STUDENT ANSWER: {question['student_answer']}

Evaluate the response and return ONLY a JSON object with score_percentage (0-100), strengths (list), improvements (list), and feedback (string)."""

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
                    
                    # Parse JSON from LLM response
                    grading_data = self._parse_llm_grading(llm_output)
                    
                    # Calculate awarded points
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
                    raise Exception(f"LLM grading failed with status {response.status_code}")
        
        except Exception as e:
            logger.error(f"Open-ended grading failed: {e}")
            return self._fallback_keyword_grading(question)
    
    def _parse_llm_grading(self, llm_output: str) -> Dict:
        """Parse and validate LLM grading output."""
        try:
            # Remove markdown code blocks if present
            llm_output = re.sub(r'```json\n?', '', llm_output)
            llm_output = re.sub(r'```\n?', '', llm_output)
            llm_output = llm_output.strip()
            
            grading_data = json.loads(llm_output)
            
            # Validate required fields
            if "score_percentage" not in grading_data:
                raise ValueError("Missing score_percentage")
            
            # Ensure score is within bounds
            grading_data["score_percentage"] = max(0, min(100, grading_data["score_percentage"]))
            
            # Provide defaults for optional fields
            grading_data.setdefault("strengths", [])
            grading_data.setdefault("improvements", [])
            grading_data.setdefault("feedback", "Response evaluated.")
            
            return grading_data
            
        except Exception as e:
            logger.error(f"Failed to parse LLM output: {e}")
            return {
                "score_percentage": 50,
                "strengths": ["Attempted the question"],
                "improvements": ["Provide more detail", "Include technical accuracy"],
                "feedback": "Answer needs more technical detail and accuracy."
            }
    
    def _fallback_keyword_grading(self, question: Dict) -> Dict:
        """
        Fallback grading using keyword matching when LLM fails.
        """
        student_answer = question["student_answer"].lower()
        keywords = question.get("keywords", [])
        
        if not keywords:
            score_percentage = 60
            feedback = "Answer received but couldn't be fully evaluated. Please review the rubric."
        else:
            matches = sum(1 for keyword in keywords if keyword.lower() in student_answer)
            score_percentage = min(100, (matches / len(keywords)) * 100)
            feedback = f"Found {matches}/{len(keywords)} key concepts in your answer."
        
        awarded_points = (score_percentage / 100) * question["points"]
        
        return {
            "question_id": question["question_id"],
            "question_type": question["question_type"],
            "max_points": question["points"],
            "awarded_points": round(awarded_points, 2),
            "is_correct": None,
            "feedback": feedback,
            "strengths": ["Answered the question"] if score_percentage > 50 else None,
            "improvements": ["Include more key concepts", "Add technical details"]
        }
    
    def calculate_letter_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade."""
        for threshold, grade in sorted(self.grade_scale.items(), reverse=True):
            if percentage >= threshold:
                return grade
        return "F"
    
    def analyze_topic_mastery(self, question_results: List[Dict], topic: str) -> Dict[str, float]:
        """Analyze mastery of different topic areas."""
        topic_scores = {}
        
        for result in question_results:
            percentage = (result["awarded_points"] / result["max_points"] * 100) if result["max_points"] > 0 else 0
            topic_key = topic
            topic_scores[topic_key] = topic_scores.get(topic_key, [])
            topic_scores[topic_key].append(percentage)
        
        topic_mastery = {
            topic_name: round(sum(scores) / len(scores), 2)
            for topic_name, scores in topic_scores.items()
        }
        
        return topic_mastery
    
    async def generate_overall_feedback(
        self,
        student_id: str,
        topic: str,
        percentage: float,
        question_results: List[Dict]
    ) -> str:
        """Generate personalized overall feedback using LLM."""
        
        total_questions = len(question_results)
        strengths = []
        improvements = []
        
        for result in question_results:
            if result.get("strengths"):
                strengths.extend(result["strengths"])
            if result.get("improvements"):
                improvements.extend(result["improvements"])
        
        strengths = list(set(strengths))[:5]
        improvements = list(set(improvements))[:5]
        
        prompt = f"""Generate brief, encouraging feedback for a TVET student:

Topic: {topic}
Overall Score: {percentage:.1f}%
Questions: {total_questions}
Key Strengths: {', '.join(strengths) if strengths else 'Basic understanding shown'}
Areas to Improve: {', '.join(improvements) if improvements else 'Continue practicing'}

Provide 2-3 sentences of constructive feedback that's specific and encouraging."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.groq_url,
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are an encouraging TVET instructor providing constructive feedback."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 200
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
        
        except Exception as e:
            logger.error(f"Overall feedback generation failed: {e}")
        
        if percentage >= 80:
            return f"Excellent work on {topic}! You've demonstrated strong understanding. Keep up the great effort!"
        elif percentage >= 60:
            return f"Good effort on {topic}. You're on the right track. Focus on the areas marked for improvement to reach mastery."
        else:
            return f"You're making progress on {topic}. Review the feedback carefully and practice the concepts that need work."
    
    async def grade_submission(
        self,
        submission_id: str,
        student_id: str,
        topic: str,
        closed_ended_questions: List[Dict],
        open_ended_questions: List[Dict]
    ) -> Dict:
        """Main method to grade a complete submission."""
        
        question_results = []
        
        for question in closed_ended_questions:
            result = self.grade_closed_ended(question)
            question_results.append(result)
            logger.info(f"Graded closed-ended question {question['question_id']}")
        
        for question in open_ended_questions:
            result = await self.grade_open_ended_with_llm(question)
            question_results.append(result)
            logger.info(f"Graded open-ended question {question['question_id']}")
        
        total_awarded = sum(r["awarded_points"] for r in question_results)
        total_max = sum(r["max_points"] for r in question_results)
        percentage = (total_awarded / total_max * 100) if total_max > 0 else 0
        
        overall_feedback = await self.generate_overall_feedback(
            student_id, topic, percentage, question_results
        )
        
        topic_mastery = self.analyze_topic_mastery(question_results, topic)
        
        return {
            "submission_id": submission_id,
            "student_id": student_id,
            "topic": topic,
            "total_points": round(total_awarded, 2),
            "max_points": total_max,
            "percentage": round(percentage, 2),
            "grade_letter": self.calculate_letter_grade(percentage),
            "question_results": question_results,
            "overall_feedback": overall_feedback,
            "topic_mastery": topic_mastery,
            "graded_at": datetime.now().isoformat()
        }