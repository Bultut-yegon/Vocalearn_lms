"""
Quiz Generation Service
Outputs simple dictionaries
Location: app/services/quiz_generation_service.py
"""

import os
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from app.core.logging_config import logger

load_dotenv()


class QuizGenerationService:
    """Quiz generation service outputting legacy format."""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        api_key = groq_api_key or os.getenv("GROQAPI_KEY")
        if not api_key:
            raise ValueError("GROQAPI_KEY must be provided")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.temperature = 0.3
        
        logger.info(" QuizGenerationService initialized (Legacy Format)")
    
    async def generate_weekly_quiz(self, request) -> Dict:
        """
        Generate weekly quiz in LEGACY format.
        
        Returns simple dict structure (not Pydantic models)
        """
        try:
            logger.info(
                f" Generating quiz (Legacy Format) | "
                f"MCQ={request.num_mcq}, T/F={request.num_true_false}, SA={request.num_short_answer}"
            )
            
            # Generate quiz data
            quiz_data = {
                "quiz_id": self._generate_quiz_id(),
                "generated_at": datetime.now().isoformat(),
                "difficulty_level": request.difficulty_level.value if hasattr(request.difficulty_level, 'value') else request.difficulty_level,
                "multiple_choice": [],
                "true_false": [],
                "short_answer": []
            }
            
            # Generate MCQs
            if request.num_mcq > 0:
                mcq = await self._generate_mcq(
                    request.combined_content,
                    request.num_mcq,
                    4,  # Always 4 options
                    quiz_data["difficulty_level"]
                )
                quiz_data["multiple_choice"] = mcq
            
            # Generate True/False
            if request.num_true_false > 0:
                tf = await self._generate_true_false(
                    request.combined_content,
                    request.num_true_false,
                    quiz_data["difficulty_level"]
                )
                quiz_data["true_false"] = tf
            
            # Generate Short Answer
            if request.num_short_answer > 0:
                sa = await self._generate_short_answer(
                    request.combined_content,
                    request.num_short_answer,
                    quiz_data["difficulty_level"]
                )
                quiz_data["short_answer"] = sa
            
            # Calculate total
            quiz_data["total_questions"] = (
                len(quiz_data["multiple_choice"]) +
                len(quiz_data["true_false"]) +
                len(quiz_data["short_answer"])
            )
            
            logger.info(f"Quiz generated: {quiz_data['quiz_id']} ({quiz_data['total_questions']} questions)")
            
            return quiz_data
            
        except Exception as e:
            logger.error(f" Quiz generation failed: {e}", exc_info=True)
            raise
    
    async def _generate_mcq(
        self,
        content: str,
        num_questions: int,
        num_options: int,
        difficulty: str
    ) -> List[Dict]:
        """Generate MCQ in legacy format."""
        
        prompt = f"""You are an expert TVET educator. Generate EXACTLY {num_questions} multiple-choice questions based ONLY on the content below.

CONTENT:
{content}

DIFFICULTY: {difficulty}

CRITICAL RULES:
1. ALL questions MUST come from the provided content
2. Create realistic distractors (plausible wrong answers)
3. Each question has EXACTLY 4 options (A, B, C, D)
4. Provide clear explanations

Return ONLY a JSON array with this EXACT structure:
[
  {{
    "question": "Question text here?",
    "options": {{
      "A": "First option text",
      "B": "Second option text",
      "C": "Third option text",
      "D": "Fourth option text"
    }},
    "correct_answer": "B",
    "explanation": "Why this answer is correct based on the content"
  }}
]

Generate EXACTLY {num_questions} questions. Return ONLY the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a TVET quiz creator. Generate questions ONLY from provided content. Return ONLY valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=3000
            )
            
            response_text = response.choices[0].message.content.strip()
            response_text = self._extract_json(response_text)
            questions = json.loads(response_text)
            
            logger.info(f" Generated {len(questions)} MCQ questions")
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f" MCQ generation failed: {e}")
            raise
    
    async def _generate_true_false(
        self,
        content: str,
        num_questions: int,
        difficulty: str
    ) -> List[Dict]:
        """Generate True/False in legacy format."""
        
        prompt = f"""You are an expert TVET educator. Generate EXACTLY {num_questions} True/False questions based ONLY on the content below.

CONTENT:
{content}

DIFFICULTY: {difficulty}

CRITICAL RULES:
1. ALL statements MUST come from the provided content
2. Create statements that are clearly true or clearly false
3. Provide explanations citing the content

Return ONLY a JSON array with this EXACT structure:
[
  {{
    "question": "Statement about the content.",
    "correct_answer": true,
    "explanation": "Why this is true/false based on the content"
  }}
]

IMPORTANT:
- Use boolean values: true or false (lowercase, no quotes)
- Generate EXACTLY {num_questions} questions
- Return ONLY the JSON array, no other text"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a TVET quiz creator. Return ONLY valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content.strip()
            response_text = self._extract_json(response_text)
            questions = json.loads(response_text)
            
            logger.info(f" Generated {len(questions)} T/F questions")
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f" T/F generation failed: {e}")
            raise
    
    async def _generate_short_answer(
        self,
        content: str,
        num_questions: int,
        difficulty: str
    ) -> List[Dict]:
        """Generate Short Answer in legacy format."""
        
        prompt = f"""You are an expert TVET educator. Generate EXACTLY {num_questions} open-ended short answer questions based ONLY on the content below.

CONTENT:
{content}

DIFFICULTY: {difficulty}

CRITICAL RULES:
1. ALL questions must be answerable using ONLY the provided content
2. Questions should require 2-4 sentence responses
3. Provide key points and sample answer

Return ONLY a JSON array with this EXACT structure:
[
  {{
    "question": "Open-ended question here?",
    "key_points": [
      "First key point",
      "Second key point",
      "Third key point"
    ],
    "sample_answer": "A complete sample answer that addresses all key points based on the content"
  }}
]

Generate EXACTLY {num_questions} questions. Return ONLY the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a TVET quiz creator. Return ONLY valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=2500
            )
            
            response_text = response.choices[0].message.content.strip()
            response_text = self._extract_json(response_text)
            questions = json.loads(response_text)
            
            logger.info(f"Generated {len(questions)} short answer questions")
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Short answer generation failed: {e}")
            raise
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response."""
        text = text.strip()
        
        # Remove markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        # Find JSON array
        start = text.find('[')
        end = text.rfind(']')
        
        if start != -1 and end != -1:
            return text[start:end+1]
        
        return text.strip()
    
    def _generate_quiz_id(self) -> str:
        """Generate unique quiz ID."""
        from uuid import uuid4
        return f"quiz_{uuid4().hex[:12]}"