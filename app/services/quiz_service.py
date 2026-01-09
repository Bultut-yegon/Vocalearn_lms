import os
import httpx
import json
import re
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from app.core.logging_config import logger

class QuizGeneratorService:
    """
    Advanced AI-powered quiz generation service for TVET education.
    Generates adaptive, diverse questions using LLM and curriculum context.
    """
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        self.mcq_options_count = 4
        self.max_retries = 2
        
    async def generate_mcq_questions(
        self,
        topic: str,
        count: int,
        difficulty: str,
        subtopics: Optional[List[str]] = None,
        avoid_topics: Optional[List[str]] = None,
        reference_materials: Optional[str] = None
    ) -> List[Dict]:
        """Generate multiple choice questions using LLM."""
        
        subtopic_context = ""
        if subtopics:
            subtopic_context = f"\nFocus on these subtopics: {', '.join(subtopics)}"
        
        avoid_context = ""
        if avoid_topics:
            avoid_context = f"\nAvoid these already covered topics: {', '.join(avoid_topics)}"
        
        reference_context = ""
        if reference_materials:
            reference_context = f"\n\nReference materials/curriculum:\n{reference_materials[:1000]}"
        
        system_prompt = """You are an expert TVET instructor creating assessment questions for wiring and plumbing courses.
Generate high-quality, practical multiple choice questions that test real-world understanding.

REQUIREMENTS:
- Questions should test practical application, not just theory
- Options should be plausible and well-distributed
- Include clear explanations for correct answers
- Ensure technical accuracy
- Make questions relevant to trade skills

OUTPUT FORMAT (JSON array, no markdown):
[
  {
    "question_text": "question here",
    "options": [
      {"option_id": "A", "text": "option A text"},
      {"option_id": "B", "text": "option B text"},
      {"option_id": "C", "text": "option C text"},
      {"option_id": "D", "text": "option D text"}
    ],
    "correct_answer": "A",
    "explanation": "why A is correct",
    "subtopic": "specific subtopic"
  }
]"""

        difficulty_guide = {
            "beginner": "Basic concepts and definitions. Simple scenarios.",
            "intermediate": "Application of concepts. Problem-solving scenarios.",
            "advanced": "Complex scenarios. Integration of multiple concepts. Troubleshooting."
        }

        user_prompt = f"""Generate {count} multiple choice questions on: {topic}

Difficulty: {difficulty} - {difficulty_guide.get(difficulty, '')}
{subtopic_context}{avoid_context}{reference_context}

Return a JSON array of {count} questions following the format specified. Each question must have exactly 4 options (A, B, C, D)."""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
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
                        "temperature": 0.8,
                        "max_tokens": 2000
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    llm_output = result["choices"][0]["message"]["content"]
                    
                    questions = self._parse_mcq_response(llm_output, topic, difficulty)
                    logger.info(f"Generated {len(questions)} MCQ questions for {topic}")
                    return questions[:count]
                else:
                    logger.error(f"MCQ generation API error: {response.status_code}")
                    raise Exception(f"LLM returned status {response.status_code}")
        
        except Exception as e:
            logger.error(f"MCQ generation failed: {e}")
            return self._generate_fallback_mcq(topic, count, difficulty)
    
    async def generate_true_false_questions(
        self,
        topic: str,
        count: int,
        difficulty: str,
        subtopics: Optional[List[str]] = None
    ) -> List[Dict]:
        """Generate true/false questions using LLM."""
        
        subtopic_context = ""
        if subtopics:
            subtopic_context = f"\nFocus on: {', '.join(subtopics)}"
        
        system_prompt = """You are a TVET instructor creating true/false questions.
Create statements that test understanding of key concepts and common misconceptions.

OUTPUT FORMAT (JSON array):
[
  {
    "question_text": "statement here",
    "correct_answer": true,
    "explanation": "why true/false with context",
    "subtopic": "specific subtopic"
  }
]"""

        user_prompt = f"""Generate {count} true/false questions on: {topic}
Difficulty: {difficulty}
{subtopic_context}

Return a JSON array of {count} questions. Mix of true and false answers."""

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
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    llm_output = result["choices"][0]["message"]["content"]
                    
                    questions = self._parse_true_false_response(llm_output, topic, difficulty)
                    logger.info(f"Generated {len(questions)} T/F questions for {topic}")
                    return questions[:count]
                else:
                    raise Exception(f"LLM returned status {response.status_code}")
        
        except Exception as e:
            logger.error(f"T/F generation failed: {e}")
            return []
    
    async def generate_open_ended_questions(
        self,
        topic: str,
        count: int,
        question_type: str,
        difficulty: str,
        subtopics: Optional[List[str]] = None
    ) -> List[Dict]:
        """Generate open-ended questions (short answer or essay) using LLM."""
        
        subtopic_context = ""
        if subtopics:
            subtopic_context = f"\nFocus on: {', '.join(subtopics)}"
        
        type_guidance = {
            "short_answer": "Require 2-3 sentence responses. Test specific concepts.",
            "essay": "Require detailed explanations. Test comprehensive understanding and analysis.",
            "practical": "Describe practical scenarios requiring step-by-step solutions."
        }
        
        system_prompt = f"""You are a TVET instructor creating open-ended questions.
Create questions that test deep understanding and practical application.

Question type: {question_type} - {type_guidance.get(question_type, '')}

OUTPUT FORMAT (JSON array):
[
  {{
    "question_text": "question here",
    "rubric": "grading criteria and key points",
    "sample_answer": "exemplary answer",
    "keywords": ["key1", "key2", "key3"]
  }}
]"""

        user_prompt = f"""Generate {count} {question_type} questions on: {topic}
Difficulty: {difficulty}
{subtopic_context}

Return a JSON array of {count} questions with rubrics, sample answers, and keywords."""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
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
                        "temperature": 0.8,
                        "max_tokens": 2000
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    llm_output = result["choices"][0]["message"]["content"]
                    
                    questions = self._parse_open_ended_response(
                        llm_output, topic, question_type, difficulty
                    )
                    logger.info(f"Generated {len(questions)} open-ended questions for {topic}")
                    return questions[:count]
                else:
                    raise Exception(f"LLM returned status {response.status_code}")
        
        except Exception as e:
            logger.error(f"Open-ended generation failed: {e}")
            return []
    
    def _parse_mcq_response(self, llm_output: str, topic: str, difficulty: str) -> List[Dict]:
        """Parse and validate MCQ response from LLM."""
        try:
            llm_output = re.sub(r'```json\n?', '', llm_output)
            llm_output = re.sub(r'```\n?', '', llm_output)
            llm_output = llm_output.strip()
            
            questions = json.loads(llm_output)
            
            validated = []
            for q in questions:
                if self._validate_mcq_question(q):
                    validated.append({
                        "question_text": q["question_text"],
                        "options": q["options"],
                        "correct_answer": q["correct_answer"],
                        "explanation": q.get("explanation", ""),
                        "difficulty": difficulty,
                        "topic": topic,
                        "subtopic": q.get("subtopic"),
                        "points": 5.0
                    })
            
            return validated
            
        except Exception as e:
            logger.error(f"Failed to parse MCQ response: {e}")
            return []
    
    def _validate_mcq_question(self, question: Dict) -> bool:
        """Validate MCQ question structure."""
        required_fields = ["question_text", "options", "correct_answer"]
        
        if not all(field in question for field in required_fields):
            return False
        
        if len(question["options"]) != 4:
            return False
        
        valid_answers = {"A", "B", "C", "D"}
        if question["correct_answer"] not in valid_answers:
            return False
        
        return True
    
    def _parse_true_false_response(self, llm_output: str, topic: str, difficulty: str) -> List[Dict]:
        """Parse and validate True/False response from LLM."""
        try:
            llm_output = re.sub(r'```json\n?', '', llm_output)
            llm_output = re.sub(r'```\n?', '', llm_output)
            llm_output = llm_output.strip()
            
            questions = json.loads(llm_output)
            
            validated = []
            for q in questions:
                if "question_text" in q and "correct_answer" in q:
                    validated.append({
                        "question_text": q["question_text"],
                        "correct_answer": bool(q["correct_answer"]),
                        "explanation": q.get("explanation", ""),
                        "difficulty": difficulty,
                        "topic": topic,
                        "subtopic": q.get("subtopic"),
                        "points": 3.0
                    })
            
            return validated
            
        except Exception as e:
            logger.error(f"Failed to parse T/F response: {e}")
            return []
    
    def _parse_open_ended_response(
        self, 
        llm_output: str, 
        topic: str, 
        question_type: str, 
        difficulty: str
    ) -> List[Dict]:
        """Parse and validate open-ended response from LLM."""
        try:
            llm_output = re.sub(r'```json\n?', '', llm_output)
            llm_output = re.sub(r'```\n?', '', llm_output)
            llm_output = llm_output.strip()
            
            questions = json.loads(llm_output)
            
            points_map = {
                "short_answer": 10.0,
                "essay": 20.0,
                "practical": 15.0
            }
            
            validated = []
            for q in questions:
                if all(k in q for k in ["question_text", "rubric", "keywords"]):
                    validated.append({
                        "question_text": q["question_text"],
                        "rubric": q["rubric"],
                        "sample_answer": q.get("sample_answer", ""),
                        "keywords": q.get("keywords", []),
                        "difficulty": difficulty,
                        "topic": topic,
                        "subtopic": q.get("subtopic"),
                        "points": points_map.get(question_type, 10.0)
                    })
            
            return validated
            
        except Exception as e:
            logger.error(f"Failed to parse open-ended response: {e}")
            return []
    
    def _generate_fallback_mcq(self, topic: str, count: int, difficulty: str) -> List[Dict]:
        """Fallback MCQ generation when LLM fails."""
        logger.warning(f"Using fallback MCQ generation for {topic}")
        
        fallback = {
            "question_text": f"Question about {topic} (LLM generation failed - please regenerate)",
            "options": [
                {"option_id": "A", "text": "Option A"},
                {"option_id": "B", "text": "Option B"},
                {"option_id": "C", "text": "Option C"},
                {"option_id": "D", "text": "Option D"}
            ],
            "correct_answer": "A",
            "explanation": "Explanation pending - regenerate quiz",
            "difficulty": difficulty,
            "topic": topic,
            "subtopic": None,
            "points": 5.0
        }
        
        return [fallback] * min(count, 1)
    
    async def generate_adaptive_quiz(
        self,
        student_id: str,
        topic: str,
        total_questions: int,
        recent_performance: Optional[Dict[str, float]] = None,
        weak_areas: Optional[List[str]] = None
    ) -> Dict:
        """Generate adaptive quiz based on student performance."""
        
        if recent_performance:
            avg_score = sum(recent_performance.values()) / len(recent_performance)
            if avg_score >= 80:
                difficulty = "advanced"
            elif avg_score >= 60:
                difficulty = "intermediate"
            else:
                difficulty = "beginner"
        else:
            difficulty = "intermediate"
        
        subtopics = weak_areas if weak_areas else None
        
        num_mcq = int(total_questions * 0.5)
        num_tf = int(total_questions * 0.3)
        num_short = total_questions - num_mcq - num_tf
        
        logger.info(f"Generating adaptive quiz for student {student_id}: {difficulty} level")
        
        return await self.generate_quiz(
            topic=topic,
            difficulty=difficulty,
            num_mcq=num_mcq,
            num_true_false=num_tf,
            num_short_answer=num_short,
            subtopics=subtopics,
            avoid_topics=None,
            reference_materials=None
        )
    
    async def generate_quiz(
        self,
        topic: str,
        difficulty: str,
        num_mcq: int = 5,
        num_true_false: int = 3,
        num_short_answer: int = 2,
        num_essay: int = 0,
        subtopics: Optional[List[str]] = None,
        avoid_topics: Optional[List[str]] = None,
        reference_materials: Optional[str] = None
    ) -> Dict:
        """Main method to generate a complete quiz."""
        
        quiz_id = str(uuid.uuid4())
        
        mcq_questions = []
        tf_questions = []
        short_questions = []
        essay_questions = []
        
        if num_mcq > 0:
            mcq_questions = await self.generate_mcq_questions(
                topic, num_mcq, difficulty, subtopics, avoid_topics, reference_materials
            )
        
        if num_true_false > 0:
            tf_questions = await self.generate_true_false_questions(
                topic, num_true_false, difficulty, subtopics
            )
        
        if num_short_answer > 0:
            short_questions = await self.generate_open_ended_questions(
                topic, num_short_answer, "short_answer", difficulty, subtopics
            )
        
        if num_essay > 0:
            essay_questions = await self.generate_open_ended_questions(
                topic, num_essay, "essay", difficulty, subtopics
            )
        
        open_ended_questions = short_questions + essay_questions
        
        total_questions = len(mcq_questions) + len(tf_questions) + len(open_ended_questions)
        total_points = (
            sum(q["points"] for q in mcq_questions) +
            sum(q["points"] for q in tf_questions) +
            sum(q["points"] for q in open_ended_questions)
        )
        
        estimated_duration = (
            len(mcq_questions) * 1.5 +
            len(tf_questions) * 1.5 +
            len(short_questions) * 5 +
            len(essay_questions) * 15
        )
        
        return {
            "quiz_id": quiz_id,
            "topic": topic,
            "difficulty_level": difficulty,
            "mcq_questions": mcq_questions,
            "true_false_questions": tf_questions,
            "open_ended_questions": open_ended_questions,
            "total_questions": total_questions,
            "total_points": round(total_points, 2),
            "estimated_duration_minutes": int(estimated_duration),
            "generated_at": datetime.now().isoformat(),
            "generation_metadata": {
                "requested_mcq": num_mcq,
                "requested_tf": num_true_false,
                "requested_short_answer": num_short_answer,
                "requested_essay": num_essay,
                "generated_mcq": len(mcq_questions),
                "generated_tf": len(tf_questions),
                "generated_open_ended": len(open_ended_questions),
                "subtopics_covered": subtopics,
                "avoided_topics": avoid_topics
            }
        }
        