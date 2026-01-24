# import os
# import json
# from typing import List, Dict, Optional, Literal
# from datetime import datetime
# from pydantic import BaseModel, Field
# from groq import Groq
# from app.core.logging_config import logger


# # Pydantic Models for Request/Response
# class SubTopic(BaseModel):
#     """Subtopic with its content"""
#     title: str
#     content: str


# class NotesInput(BaseModel):
#     """Input model for notes in JSON format"""
#     course: str
#     topic: str
#     subtopics: List[SubTopic]
#     metadata: Optional[Dict] = {}


# class QuizGenerationRequest(BaseModel):
#     """Request model for quiz generation"""
#     notes: NotesInput
#     num_questions: int = Field(ge=1, le=50, description="Number of questions to generate")
#     question_types: List[Literal["multiple_choice", "short_answer", "open_ended"]] = Field(
#         default=["multiple_choice"],
#         description="Types of questions to generate"
#     )
#     difficulty: Optional[Literal["easy", "medium", "hard"]] = "medium"


# class MultipleChoiceQuestion(BaseModel):
#     """Multiple choice question model"""
#     question: str
#     options: List[str] = Field(min_items=4, max_items=4)
#     correct_answer: str
#     explanation: Optional[str] = None


# class ShortAnswerQuestion(BaseModel):
#     """Short answer question model"""
#     question: str
#     expected_answer: str
#     keywords: List[str]
#     explanation: Optional[str] = None


# class OpenEndedQuestion(BaseModel):
#     """Open-ended question model"""
#     question: str
#     guidance: str
#     key_points: List[str]


# class Quiz(BaseModel):
#     """Quiz response model"""
#     quiz_id: str
#     course: str
#     topic: str
#     multiple_choice: Optional[List[MultipleChoiceQuestion]] = []
#     short_answer: Optional[List[ShortAnswerQuestion]] = []
#     open_ended: Optional[List[OpenEndedQuestion]] = []
#     total_questions: int
#     difficulty: str
#     generated_at: str


# class QuizGenerationService:
#     """
#     Service for generating quizzes from JSON notes using Groq LLM.
#     Supports multiple question types: multiple choice, short answer, and open-ended.
#     """
    
#     def __init__(self, groq_api_key: Optional[str] = None):
#         """Initialize Groq client"""
#         api_key = groq_api_key or os.getenv("GROQ_API_KEY")
#         if not api_key:
#             raise ValueError("GROQ_API_KEY must be provided or set in environment")
        
#         self.client = Groq(api_key=api_key)
#         self.model = "llama-3.3-70b-versatile"  # Using Groq's best model
        
#         logger.info("QuizGenerationService initialized with Groq")
    
#     async def generate_quiz(self, request: QuizGenerationRequest) -> Quiz:
#         """
#         Generate a quiz from JSON notes based on specified parameters.
        
#         Args:
#             request: QuizGenerationRequest containing notes and generation parameters
            
#         Returns:
#             Quiz object with generated questions
#         """
#         try:
#             logger.info(f"Generating quiz for topic: {request.notes.topic}")
            
#             # Prepare the content from notes
#             content = self._prepare_content_from_notes(request.notes)
            
#             # Calculate distribution of question types
#             questions_per_type = self._calculate_question_distribution(
#                 request.num_questions,
#                 request.question_types
#             )
            
#             # Generate questions for each type
#             quiz_data = {
#                 "quiz_id": self._generate_quiz_id(),
#                 "course": request.notes.course,
#                 "topic": request.notes.topic,
#                 "multiple_choice": [],
#                 "short_answer": [],
#                 "open_ended": [],
#                 "difficulty": request.difficulty,
#                 "generated_at": datetime.now().isoformat()
#             }
            
#             # Generate multiple choice questions
#             if "multiple_choice" in request.question_types:
#                 mc_questions = await self._generate_multiple_choice(
#                     content,
#                     questions_per_type["multiple_choice"],
#                     request.difficulty
#                 )
#                 quiz_data["multiple_choice"] = mc_questions
            
#             # Generate short answer questions
#             if "short_answer" in request.question_types:
#                 sa_questions = await self._generate_short_answer(
#                     content,
#                     questions_per_type["short_answer"],
#                     request.difficulty
#                 )
#                 quiz_data["short_answer"] = sa_questions
            
#             # Generate open-ended questions
#             if "open_ended" in request.question_types:
#                 oe_questions = await self._generate_open_ended(
#                     content,
#                     questions_per_type["open_ended"],
#                     request.difficulty
#                 )
#                 quiz_data["open_ended"] = oe_questions
            
#             # Calculate total questions
#             quiz_data["total_questions"] = (
#                 len(quiz_data["multiple_choice"]) +
#                 len(quiz_data["short_answer"]) +
#                 len(quiz_data["open_ended"])
#             )
            
#             logger.info(f"Successfully generated {quiz_data['total_questions']} questions")
            
#             return Quiz(**quiz_data)
            
#         except Exception as e:
#             logger.error(f"Quiz generation failed: {e}")
#             raise
    
#     def _prepare_content_from_notes(self, notes: NotesInput) -> str:
#         """Convert JSON notes into formatted text for LLM processing"""
#         content_parts = [
#             f"Course: {notes.course}",
#             f"Topic: {notes.topic}",
#             "\nContent:\n"
#         ]
        
#         for subtopic in notes.subtopics:
#             content_parts.append(f"\n### {subtopic.title}")
#             content_parts.append(subtopic.content)
        
#         return "\n".join(content_parts)
    
#     def _calculate_question_distribution(
#         self,
#         total_questions: int,
#         question_types: List[str]
#     ) -> Dict[str, int]:
#         """Distribute questions evenly across requested types"""
#         distribution = {
#             "multiple_choice": 0,
#             "short_answer": 0,
#             "open_ended": 0
#         }
        
#         num_types = len(question_types)
#         base_count = total_questions // num_types
#         remainder = total_questions % num_types
        
#         for i, q_type in enumerate(question_types):
#             distribution[q_type] = base_count + (1 if i < remainder else 0)
        
#         return distribution
    
#     async def _generate_multiple_choice(
#         self,
#         content: str,
#         num_questions: int,
#         difficulty: str
#     ) -> List[MultipleChoiceQuestion]:
#         """Generate multiple choice questions using Groq"""
#         if num_questions == 0:
#             return []
        
#         prompt = f"""Based on the following educational content, generate {num_questions} multiple-choice questions at {difficulty} difficulty level.

# Content:
# {content}

# Requirements:
# - Each question must have exactly 4 options (A, B, C, D)
# - Only one option should be correct
# - Questions should test understanding, not just memorization
# - Include explanations for correct answers
# - Make distractors plausible but clearly incorrect

# Return ONLY a valid JSON array with this exact structure:
# [
#   {{
#     "question": "question text here",
#     "options": ["option A", "option B", "option C", "option D"],
#     "correct_answer": "option X (the full text of correct option)",
#     "explanation": "why this is correct"
#   }}
# ]

# Generate exactly {num_questions} questions. Return only the JSON array, no additional text."""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are an expert TVET educator who creates high-quality assessment questions. Always return valid JSON only."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=0.7,
#                 max_tokens=2000
#             )
            
#             response_text = response.choices[0].message.content.strip()
            
#             # Clean the response to extract JSON
#             response_text = self._extract_json(response_text)
            
#             questions_data = json.loads(response_text)
            
#             # Validate and convert to Pydantic models
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 questions.append(MultipleChoiceQuestion(**q_data))
            
#             return questions
            
#         except Exception as e:
#             logger.error(f"Multiple choice generation failed: {e}")
#             raise
    
#     async def _generate_short_answer(
#         self,
#         content: str,
#         num_questions: int,
#         difficulty: str
#     ) -> List[ShortAnswerQuestion]:
#         """Generate short answer questions using Groq"""
#         if num_questions == 0:
#             return []
        
#         prompt = f"""Based on the following educational content, generate {num_questions} short-answer questions at {difficulty} difficulty level.

# Content:
# {content}

# Requirements:
# - Questions should require 1-3 sentence answers
# - Include expected answer
# - Provide keywords that should appear in correct answers
# - Include explanation of what makes a good answer

# Return ONLY a valid JSON array with this exact structure:
# [
#   {{
#     "question": "question text here",
#     "expected_answer": "model answer here",
#     "keywords": ["keyword1", "keyword2", "keyword3"],
#     "explanation": "what makes this a good answer"
#   }}
# ]

# Generate exactly {num_questions} questions. Return only the JSON array, no additional text."""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are an expert TVET educator who creates high-quality assessment questions. Always return valid JSON only."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=0.7,
#                 max_tokens=2000
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
            
#             questions_data = json.loads(response_text)
            
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 questions.append(ShortAnswerQuestion(**q_data))
            
#             return questions
            
#         except Exception as e:
#             logger.error(f"Short answer generation failed: {e}")
#             raise
    
#     async def _generate_open_ended(
#         self,
#         content: str,
#         num_questions: int,
#         difficulty: str
#     ) -> List[OpenEndedQuestion]:
#         """Generate open-ended questions using Groq"""
#         if num_questions == 0:
#             return []
        
#         prompt = f"""Based on the following educational content, generate {num_questions} open-ended questions at {difficulty} difficulty level.

# Content:
# {content}

# Requirements:
# - Questions should encourage critical thinking and detailed responses
# - Provide guidance on how to approach the question
# - List key points that should be covered in a comprehensive answer
# - Questions should require paragraph-length responses

# Return ONLY a valid JSON array with this exact structure:
# [
#   {{
#     "question": "question text here",
#     "guidance": "how students should approach this question",
#     "key_points": ["point 1", "point 2", "point 3"]
#   }}
# ]

# Generate exactly {num_questions} questions. Return only the JSON array, no additional text."""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are an expert TVET educator who creates high-quality assessment questions. Always return valid JSON only."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=0.7,
#                 max_tokens=2000
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
            
#             questions_data = json.loads(response_text)
            
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 questions.append(OpenEndedQuestion(**q_data))
            
#             return questions
            
#         except Exception as e:
#             logger.error(f"Open-ended generation failed: {e}")
#             raise
    
#     def _extract_json(self, text: str) -> str:
#         """Extract JSON from LLM response that might have extra text"""
#         # Remove markdown code blocks if present
#         text = text.strip()
#         if text.startswith("```json"):
#             text = text[7:]
#         elif text.startswith("```"):
#             text = text[3:]
        
#         if text.endswith("```"):
#             text = text[:-3]
        
#         # Find first [ and last ]
#         start = text.find('[')
#         end = text.rfind(']')
        
#         if start != -1 and end != -1:
#             return text[start:end+1]
        
#         return text.strip()
    
#     def _generate_quiz_id(self) -> str:
#         """Generate unique quiz ID"""
#         from uuid import uuid4
#         return f"quiz_{uuid4().hex[:12]}"
    
#     def export_quiz_to_json(self, quiz: Quiz) -> str:
#         """Export quiz to JSON string"""
#         return quiz.model_dump_json(indent=2)
    
#     def export_quiz_to_dict(self, quiz: Quiz) -> Dict:
#         """Export quiz to dictionary"""
#         return quiz.model_dump()



# VERSION 2





# """
# Quiz Generation Service - Production Ready
# Generates quizzes from content using Groq LLM with strict validation
# to prevent hallucinations and ensure all questions are grounded in provided content.
# """

# import os
# import json
# import re
# from typing import List, Dict, Optional, Literal
# from datetime import datetime
# from pydantic import BaseModel, Field, validator
# from groq import Groq
# from app.core.logging_config import logger
# from dotenv import load_dotenv
# load_dotenv


# # ============================================================================
# # REQUEST/RESPONSE MODELS
# # ============================================================================

# class QuizGenerationRequest(BaseModel):
#     """Request model matching your exact JSON format"""
#     content: str = Field(
#         ...,
#         min_length=100,
#         description="The learning content from database"
#     )
#     difficulty_level: Literal["beginner", "intermediate", "advanced"] = Field(
#         default="intermediate",
#         description="Difficulty level: beginner, intermediate, or advanced"
#     )
#     num_mcq: int = Field(
#         default=5,
#         ge=0,
#         le=20,
#         description="Number of multiple choice questions"
#     )
#     num_true_false: int = Field(
#         default=5,
#         ge=0,
#         le=20,
#         description="Number of true/false questions"
#     )
#     num_short_answer: int = Field(
#         default=2,
#         ge=0,
#         le=10,
#         description="Number of short answer (open-ended) questions"
#     )
#     num_of_options: int = Field(
#         default=4,
#         ge=2,
#         le=6,
#         description="Number of options for MCQ (e.g., 4 = A,B,C,D)"
#     )
    
#     @validator('content')
#     def validate_content(cls, v):
#         if len(v.strip()) < 100:
#             raise ValueError("Content must be at least 100 characters")
#         return v.strip()


# class MultipleChoiceQuestion(BaseModel):
#     """Multiple choice question"""
#     question: str
#     options: Dict[str, str]  # {"A": "option text", "B": "option text", ...}
#     correct_answer: str  # Just the letter (e.g., "B")
#     explanation: str


# class TrueFalseQuestion(BaseModel):
#     """True/False question"""
#     question: str
#     correct_answer: bool
#     explanation: str


# class ShortAnswerQuestion(BaseModel):
#     """Open-ended short answer question"""
#     question: str
#     key_points: List[str]
#     sample_answer: str


# class QuizResponse(BaseModel):
#     """Complete quiz response"""
#     quiz_id: str
#     generated_at: str
#     difficulty_level: str
#     total_questions: int
#     multiple_choice: List[MultipleChoiceQuestion] = []
#     true_false: List[TrueFalseQuestion] = []
#     short_answer: List[ShortAnswerQuestion] = []



# # QUIZ GENERATION SERVICE


# class QuizGenerationService:
#     """
#     Production-ready quiz generation service.
#     Prevents hallucinations by strictly grounding questions in provided content.
#     """
    
#     def __init__(self, groq_api_key: Optional[str] = None):
#         api_key = groq_api_key or os.getenv("GROQ_API_KEY")
#         if not api_key:
#             raise ValueError("GROQ_API_KEY must be provided")
        
#         self.client = Groq(api_key=api_key)
#         self.model = "llama-3.3-70b-versatile"
#         self.temperature = 0.3  # Lower temp for factual accuracy
        
#         logger.info("QuizGenerationService initialized")
    
#     async def generate_quiz(self, request: QuizGenerationRequest) -> QuizResponse:
#         """
#         Generate quiz from content based on request parameters.
#         All questions are strictly grounded in the provided content.
#         """
#         try:
#             logger.info(f"Generating quiz: MCQ={request.num_mcq}, T/F={request.num_true_false}, SA={request.num_short_answer}")
            
#             quiz_data = {
#                 "quiz_id": self._generate_quiz_id(),
#                 "generated_at": datetime.now().isoformat(),
#                 "difficulty_level": request.difficulty_level,
#                 "multiple_choice": [],
#                 "true_false": [],
#                 "short_answer": []
#             }
            
#             # Generate each question type
#             if request.num_mcq > 0:
#                 mcq = await self._generate_mcq(
#                     request.content, 
#                     request.num_mcq, 
#                     request.num_of_options,
#                     request.difficulty_level
#                 )
#                 quiz_data["multiple_choice"] = mcq
            
#             if request.num_true_false > 0:
#                 tf = await self._generate_true_false(
#                     request.content,
#                     request.num_true_false,
#                     request.difficulty_level
#                 )
#                 quiz_data["true_false"] = tf
            
#             if request.num_short_answer > 0:
#                 sa = await self._generate_short_answer(
#                     request.content,
#                     request.num_short_answer,
#                     request.difficulty_level
#                 )
#                 quiz_data["short_answer"] = sa
            
#             quiz_data["total_questions"] = (
#                 len(quiz_data["multiple_choice"]) +
#                 len(quiz_data["true_false"]) +
#                 len(quiz_data["short_answer"])
#             )
            
#             logger.info(f"Quiz generated successfully: {quiz_data['quiz_id']}")
#             return QuizResponse(**quiz_data)
            
#         except Exception as e:
#             logger.error(f"Quiz generation failed: {e}", exc_info=True)
#             raise
    
#     async def _generate_mcq(
#         self, 
#         content: str, 
#         num_questions: int,
#         num_options: int,
#         difficulty: str
#     ) -> List[MultipleChoiceQuestion]:
#         """Generate multiple choice questions"""
        
#         # Create option labels (A, B, C, D, E, F)
#         option_labels = [chr(65 + i) for i in range(num_options)]  # ['A', 'B', 'C', ...]
        
#         prompt = f"""You are an expert TVET educator creating a quiz. Generate EXACTLY {num_questions} multiple-choice questions based ONLY on the content provided below.

# CRITICAL RULES:
# 1. ALL questions and answers MUST come directly from the provided content
# 2. DO NOT add information not present in the content
# 3. Create realistic distractors (wrong answers) that are plausible but clearly incorrect
# 4. Each question must have EXACTLY {num_options} options
# 5. Mark the correct answer and provide explanation

# CONTENT:
# {content}

# DIFFICULTY LEVEL: {difficulty}

# Generate EXACTLY {num_questions} multiple-choice questions as a JSON array with this EXACT structure:
# [
#   {{
#     "question": "Question text here?",
#     "options": {{
#       "A": "First option",
#       "B": "Second option",
#       "C": "Third option",
#       "D": "Fourth option"
#     }},
#     "correct_answer": "B",
#     "explanation": "Why this answer is correct based on the content"
#   }}
# ]

# IMPORTANT: 
# - Return ONLY the JSON array, no other text
# - Use exactly these option labels: {', '.join(option_labels)}
# - All information must be from the provided content
# - Generate EXACTLY {num_questions} questions"""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a TVET quiz creator. Generate questions ONLY from provided content. Never add external information. Return ONLY valid JSON."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=self.temperature,
#                 max_tokens=3000
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
#             questions_data = json.loads(response_text)
            
#             # Validate and convert
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 # Ensure correct number of options
#                 if len(q_data.get("options", {})) != num_options:
#                     logger.warning(f"Question has wrong number of options, skipping")
#                     continue
                
#                 questions.append(MultipleChoiceQuestion(**q_data))
            
#             logger.info(f"Generated {len(questions)} MCQ questions")
#             return questions
            
#         except Exception as e:
#             logger.error(f"MCQ generation failed: {e}")
#             raise
    
#     async def _generate_true_false(
#         self,
#         content: str,
#         num_questions: int,
#         difficulty: str
#     ) -> List[TrueFalseQuestion]:
#         """Generate true/false questions"""
        
#         prompt = f"""You are an expert TVET educator. Generate EXACTLY {num_questions} True/False questions based ONLY on the content provided below.

# CRITICAL RULES:
# 1. ALL statements MUST come directly from the provided content
# 2. DO NOT add information not present in the content
# 3. Create statements that are clearly true or clearly false based on the content
# 4. Provide explanations citing the content

# CONTENT:
# {content}

# DIFFICULTY LEVEL: {difficulty}

# Generate EXACTLY {num_questions} True/False questions as a JSON array with this EXACT structure:
# [
#   {{
#     "question": "Statement about the content here.",
#     "correct_answer": true,
#     "explanation": "Why this is true/false based on the content"
#   }}
# ]

# IMPORTANT:
# - Return ONLY the JSON array, no other text
# - Use boolean values: true or false (lowercase, no quotes)
# - All statements must be verifiable from the provided content
# - Generate EXACTLY {num_questions} questions"""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a TVET quiz creator. Generate questions ONLY from provided content. Return ONLY valid JSON."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=self.temperature,
#                 max_tokens=2000
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
#             questions_data = json.loads(response_text)
            
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 questions.append(TrueFalseQuestion(**q_data))
            
#             logger.info(f"Generated {len(questions)} T/F questions")
#             return questions
            
#         except Exception as e:
#             logger.error(f"True/False generation failed: {e}")
#             raise
    
#     async def _generate_short_answer(
#         self,
#         content: str,
#         num_questions: int,
#         difficulty: str
#     ) -> List[ShortAnswerQuestion]:
#         """Generate short answer (open-ended) questions"""
        
#         prompt = f"""You are an expert TVET educator. Generate EXACTLY {num_questions} open-ended short answer questions based ONLY on the content provided below.

# CRITICAL RULES:
# 1. ALL questions must be answerable using ONLY the provided content
# 2. DO NOT ask about information not present in the content
# 3. Questions should require 2-4 sentence responses
# 4. Provide key points that should be covered and a sample answer

# CONTENT:
# {content}

# DIFFICULTY LEVEL: {difficulty}

# Generate EXACTLY {num_questions} short answer questions as a JSON array with this EXACT structure:
# [
#   {{
#     "question": "Open-ended question here?",
#     "key_points": [
#       "First key point to cover",
#       "Second key point to cover",
#       "Third key point to cover"
#     ],
#     "sample_answer": "A complete sample answer that addresses all key points based on the content"
#   }}
# ]

# IMPORTANT:
# - Return ONLY the JSON array, no other text
# - All questions must be answerable from the provided content
# - Provide 3-5 key points per question
# - Sample answer should be 2-4 sentences
# - Generate EXACTLY {num_questions} questions"""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a TVET quiz creator. Generate questions ONLY from provided content. Return ONLY valid JSON."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=self.temperature,
#                 max_tokens=2500
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
#             questions_data = json.loads(response_text)
            
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 questions.append(ShortAnswerQuestion(**q_data))
            
#             logger.info(f"Generated {len(questions)} short answer questions")
#             return questions
            
#         except Exception as e:
#             logger.error(f"Short answer generation failed: {e}")
#             raise
    
#     def _extract_json(self, text: str) -> str:
#         """Extract JSON from LLM response"""
#         text = text.strip()
        
#         # Remove markdown code blocks
#         if text.startswith("```json"):
#             text = text[7:]
#         elif text.startswith("```"):
#             text = text[3:]
        
#         if text.endswith("```"):
#             text = text[:-3]
        
#         # Find JSON array
#         start = text.find('[')
#         end = text.rfind(']')
        
#         if start != -1 and end != -1:
#             return text[start:end+1]
        
#         return text.strip()
    
#     def _generate_quiz_id(self) -> str:
#         """Generate unique quiz ID"""
#         from uuid import uuid4
#         return f"quiz_{uuid4().hex[:12]}"
    
#     def export_to_json(self, quiz: QuizResponse) -> str:
#         """Export quiz to JSON string"""
#         return quiz.model_dump_json(indent=2)
    
#     def export_to_dict(self, quiz: QuizResponse) -> Dict:
#         """Export quiz to dictionary"""
#         return quiz.model_dump() 




# VERSION 3








# """
# Quiz Generation Service - Production Ready
# Generates quizzes from content using Groq LLM with strict validation
# to prevent hallucinations and ensure all questions are grounded in provided content.
# """

# import os
# import json
# import re
# from typing import List, Dict, Optional, Literal
# from datetime import datetime
# from pydantic import BaseModel, Field, validator
# from groq import Groq
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from typing import List
# from datetime import datetime
# from app.models.quiz_models import (
#     WeeklyQuizGenerationRequest,
#     QuizGenerationRequest,
#     QuizGenerationResult
# )

# # Load environment variables
# load_dotenv()



# # REQUEST/RESPONSE MODELS


# class QuizGenerationRequest(BaseModel):
#     """Request model matching your exact JSON format"""
#     content: str = Field(
#         ...,
#         min_length=100,
#         description="The learning content from database"
#     )
#     difficulty_level: Literal["beginner", "intermediate", "advanced"] = Field(
#         default="intermediate",
#         description="Difficulty level: beginner, intermediate, or advanced"
#     )
#     num_mcq: int = Field(
#         default=5,
#         ge=0,
#         le=20,
#         description="Number of multiple choice questions"
#     )
#     num_true_false: int = Field(
#         default=5,
#         ge=0,
#         le=20,
#         description="Number of true/false questions"
#     )

#     num_short_answer: int = Field(
#         default=2,
#         ge=0,
#         le=10,
#         description="Number of short answer (open-ended) questions"
#     )
#     num_of_options: int = Field(
#         default=4,
#         ge=2,
#         le=6,
#         description="Number of options for MCQ (e.g., 4 = A,B,C,D)"
#     )
    
#     @validator('content')
#     def validate_content(cls, v):
#         if len(v.strip()) < 100:
#             raise ValueError("Content must be at least 100 characters")
#         return v.strip()


# class MultipleChoiceQuestion(BaseModel):
#     """Multiple choice question"""
#     question: str
#     options: Dict[str, str]  # {"A": "option text", "B": "option text", ...}
#     correct_answer: str  # Just the letter (e.g., "B")
#     explanation: str


# class TrueFalseQuestion(BaseModel):
#     """True/False question"""
#     question: str
#     correct_answer: bool
#     explanation: str


# class ShortAnswerQuestion(BaseModel):
#     """Open-ended short answer question"""
#     question: str
#     key_points: List[str]
#     sample_answer: str


# class QuizResponse(BaseModel):
#     """Complete quiz response"""
#     quiz_id: str
#     generated_at: str
#     difficulty_level: str
#     total_questions: int
#     multiple_choice: List[MultipleChoiceQuestion] = []
#     true_false: List[TrueFalseQuestion] = []
#     short_answer: List[ShortAnswerQuestion] = []

# class WeeklyContent(BaseModel):
#     week: int
#     contents: List[Dict[str, str]]  # { "type": "...", "text": "..." }


# class WeeklyQuizGenerationRequest(BaseModel):
#     weeks: List[WeeklyContent]
#     difficulty_level: Literal["beginner", "intermediate", "advanced"] = "intermediate"
#     num_mcq: int = 5
#     num_true_false: int = 5
#     num_short_answer: int = 2
#     num_of_options: int = 4



# # QUIZ GENERATION SERVICE


# class QuizGenerationService:
#     """
#     Production-ready quiz generation service.
#     Prevents hallucinations by strictly grounding questions in provided content.
#     """
    
#     def __init__(self, groq_api_key: Optional[str] = None):
#         api_key = groq_api_key or os.getenv("GROQAPI_KEY")
#         if not api_key:
#             raise ValueError("GROQAPI_KEY must be provided")
        
#         self.client = Groq(api_key=api_key)
#         self.model = "llama-3.3-70b-versatile"
#         self.temperature = 0.3  # Lower temp for factual accuracy
        
#         logger.info("QuizGenerationService initialized")
    
#     async def generate_quiz(self, request: QuizGenerationRequest) -> QuizResponse:
#         """
#         Generate quiz from content based on request parameters.
#         All questions are strictly grounded in the provided content.
#         """
#         try:
#             logger.info(f"Generating quiz: MCQ={request.num_mcq}, T/F={request.num_true_false}, SA={request.num_short_answer}")
            
#             quiz_data = {
#                 "quiz_id": self._generate_quiz_id(),
#                 "generated_at": datetime.now().isoformat(),
#                 "difficulty_level": request.difficulty_level,
#                 "multiple_choice": [],
#                 "true_false": [],
#                 "short_answer": []
#             }
            
#             # Generate each question type
#             if request.num_mcq > 0:
#                 mcq = await self._generate_mcq(
#                     request.content, 
#                     request.num_mcq, 
#                     request.num_of_options,
#                     request.difficulty_level
#                 )
#                 quiz_data["multiple_choice"] = mcq
            
#             if request.num_true_false > 0:
#                 tf = await self._generate_true_false(
#                     request.content,
#                     request.num_true_false,
#                     request.difficulty_level
#                 )
#                 quiz_data["true_false"] = tf
            
#             if request.num_short_answer > 0:
#                 sa = await self._generate_short_answer(
#                     request.content,
#                     request.num_short_answer,
#                     request.difficulty_level
#                 )
#                 quiz_data["short_answer"] = sa
            
#             quiz_data["total_questions"] = (
#                 len(quiz_data["multiple_choice"]) +
#                 len(quiz_data["true_false"]) +
#                 len(quiz_data["short_answer"])
#             )
            
#             logger.info(f"Quiz generated successfully: {quiz_data['quiz_id']}")
#             return QuizResponse(**quiz_data)
            
#         except Exception as e:
#             logger.error(f"Quiz generation failed: {e}", exc_info=True)
#             raise
    
#     async def _generate_mcq(
#         self, 
#         content: str, 
#         num_questions: int,
#         num_options: int,
#         difficulty: str
#     ) -> List[MultipleChoiceQuestion]:
#         """Generate multiple choice questions"""
        
#         # Create option labels (A, B, C, D, E, F)
#         option_labels = [chr(65 + i) for i in range(num_options)]  # ['A', 'B', 'C', ...]
        
#         prompt = f"""You are an expert TVET educator creating a quiz. Generate EXACTLY {num_questions} multiple-choice questions based ONLY on the content provided below.

# CRITICAL RULES:
# 1. ALL questions and answers MUST come directly from the provided content
# 2. DO NOT add information not present in the content
# 3. Create realistic distractors (wrong answers) that are plausible but clearly incorrect
# 4. Each question must have EXACTLY {num_options} options
# 5. Mark the correct answer and provide explanation

# CONTENT:
# {content}

# DIFFICULTY LEVEL: {difficulty}

# Generate EXACTLY {num_questions} multiple-choice questions as a JSON array with this EXACT structure:
# [
#   {{
#     "question": "Question text here?",
#     "options": {{
#       "A": "First option",
#       "B": "Second option",
#       "C": "Third option",
#       "D": "Fourth option"
#     }},
#     "correct_answer": "B",
#     "explanation": "Why this answer is correct based on the content"
#   }}
# ]

# IMPORTANT: 
# - Return ONLY the JSON array, no other text
# - Use exactly these option labels: {', '.join(option_labels)}
# - All information must be from the provided content
# - Generate EXACTLY {num_questions} questions"""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a TVET quiz creator. Generate questions ONLY from provided content. Never add external information. Return ONLY valid JSON."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=self.temperature,
#                 max_tokens=3000
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
#             questions_data = json.loads(response_text)
            
#             # Validate and convert
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 # Ensure correct number of options
#                 if len(q_data.get("options", {})) != num_options:
#                     logger.warning(f"Question has wrong number of options, skipping")
#                     continue
                
#                 questions.append(MultipleChoiceQuestion(**q_data))
            
#             logger.info(f"Generated {len(questions)} MCQ questions")
#             return questions
            
#         except Exception as e:
#             logger.error(f"MCQ generation failed: {e}")
#             raise
    
#     async def _generate_true_false(
#         self,
#         content: str,
#         num_questions: int,
#         difficulty: str
#     ) -> List[TrueFalseQuestion]:
#         """Generate true/false questions"""
        
#         prompt = f"""You are an expert TVET educator. Generate EXACTLY {num_questions} True/False questions based ONLY on the content provided below.

# CRITICAL RULES:
# 1. ALL statements MUST come directly from the provided content
# 2. DO NOT add information not present in the content
# 3. Create statements that are clearly true or clearly false based on the content
# 4. Provide explanations citing the content

# CONTENT:
# {content}

# DIFFICULTY LEVEL: {difficulty}

# Generate EXACTLY {num_questions} True/False questions as a JSON array with this EXACT structure:
# [
#   {{
#     "question": "Statement about the content here.",
#     "correct_answer": true,
#     "explanation": "Why this is true/false based on the content"
#   }}
# ]

# IMPORTANT:
# - Return ONLY the JSON array, no other text
# - Use boolean values: true or false (lowercase, no quotes)
# - All statements must be verifiable from the provided content
# - Generate EXACTLY {num_questions} questions"""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a TVET quiz creator. Generate questions ONLY from provided content. Return ONLY valid JSON."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=self.temperature,
#                 max_tokens=2000
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
#             questions_data = json.loads(response_text)
            
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 questions.append(TrueFalseQuestion(**q_data))
            
#             logger.info(f"Generated {len(questions)} T/F questions")
#             return questions
            
#         except Exception as e:
#             logger.error(f"True/False generation failed: {e}")
#             raise
    
#     async def _generate_short_answer(
#         self,
#         content: str,
#         num_questions: int,
#         difficulty: str
#     ) -> List[ShortAnswerQuestion]:
#         """Generate short answer (open-ended) questions"""
        
#         prompt = f"""You are an expert TVET educator. Generate EXACTLY {num_questions} open-ended short answer questions based ONLY on the content provided below.

# CRITICAL RULES:
# 1. ALL questions must be answerable using ONLY the provided content
# 2. DO NOT ask about information not present in the content
# 3. Questions should require 2-4 sentence responses
# 4. Provide key points that should be covered and a sample answer

# CONTENT:
# {content}

# DIFFICULTY LEVEL: {difficulty}

# Generate EXACTLY {num_questions} short answer questions as a JSON array with this EXACT structure:
# [
#   {{
#     "question": "Open-ended question here?",
#     "key_points": [
#       "First key point to cover",
#       "Second key point to cover",
#       "Third key point to cover"
#     ],
#     "sample_answer": "A complete sample answer that addresses all key points based on the content"
#   }}
# ]

# IMPORTANT:
# - Return ONLY the JSON array, no other text
# - All questions must be answerable from the provided content
# - Provide 3-5 key points per question
# - Sample answer should be 2-4 sentences
# - Generate EXACTLY {num_questions} questions"""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a TVET quiz creator. Generate questions ONLY from provided content. Return ONLY valid JSON."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=self.temperature,
#                 max_tokens=2500
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
#             questions_data = json.loads(response_text)
            
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 questions.append(ShortAnswerQuestion(**q_data))
            
#             logger.info(f"Generated {len(questions)} short answer questions")
#             return questions
            
#         except Exception as e:
#             logger.error(f"Short answer generation failed: {e}")
#             raise
    


#     async def generate_weekly_quiz(self,request: WeeklyQuizGenerationRequest):
#         """
#         Generate exactly one Canvas-style quiz for a given week.
#         """

#         if len(request.combined_content.strip()) < 100:
#             raise ValueError("Weekly content is insufficient for quiz generation")

#         # USE CONTENT-BASED REQUEST
#         quiz_request = QuizGenerationRequest(
#         content=request.combined_content,
#         difficulty_level=request.difficulty_level.value,
#         num_mcq=request.num_mcq,
#         num_true_false=request.num_true_false,
#         num_short_answer=request.num_short_answer,
#         num_of_options=4
#     )

#         quiz = await self.generate_quiz(quiz_request)

#         # Attach metadata safely
#         quiz.generation_metadata = {
#         "course_id": request.course_id,
#         "week_number": request.week_number,
#         "modules": request.modules,
#         "quiz_type": "weekly"
#         }

#         return quiz


    
#     def _extract_json(self, text: str) -> str:
#         """Extract JSON from LLM response"""
#         text = text.strip()
        
#         # Remove markdown code blocks
#         if text.startswith("```json"):
#             text = text[7:]
#         elif text.startswith("```"):
#             text = text[3:]
        
#         if text.endswith("```"):
#             text = text[:-3]
        
#         # Find JSON array
#         start = text.find('[')
#         end = text.rfind(']')
        
#         if start != -1 and end != -1:
#             return text[start:end+1]
        
#         return text.strip()
    
#     def _generate_quiz_id(self) -> str:
#         """Generate unique quiz ID"""
#         from uuid import uuid4
#         return f"quiz_{uuid4().hex[:12]}"
    
#     def export_to_json(self, quiz: QuizResponse) -> str:
#         """Export quiz to JSON string"""
#         return quiz.model_dump_json(indent=2)
    
#     def export_to_dict(self, quiz: QuizResponse) -> Dict:
#         """Export quiz to dictionary"""
#         return quiz.model_dump()




# VERSION 4








"""
Quiz Generation Service - FIXED VERSION
Generates quizzes from content using Groq LLM
"""

# import os
# import json
# import re
# from typing import List, Dict, Optional
# from datetime import datetime
# from groq import Groq
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from app.models.quiz_models import (
#     WeeklyQuizGenerationRequest,
#     QuizGenerationResult,
#     GeneratedMCQ,
#     GeneratedTrueFalse,
#     GeneratedOpenEnded,
#     MCQOption,
#     DifficultyLevel
# )

# load_dotenv()


# class QuizGenerationService:
#     """Production-ready quiz generation service."""
    
#     def __init__(self, groq_api_key: Optional[str] = None):
#         api_key = groq_api_key or os.getenv("GROQAPI_KEY")
#         if not api_key:
#             raise ValueError("GROQAPI_KEY must be provided")
        
#         self.client = Groq(api_key=api_key)
#         self.model = "llama-3.3-70b-versatile"
#         self.temperature = 0.3
        
#         logger.info("QuizGenerationService initialized")
    
#     async def generate_weekly_quiz(self, request: WeeklyQuizGenerationRequest) -> QuizGenerationResult:
#         """
#         Generate exactly one Canvas-style quiz for a given week.
        
#         Args:
#             request: WeeklyQuizGenerationRequest with combined_content
            
#         Returns:
#             QuizGenerationResult with all questions
#         """
#         try:
#             if len(request.combined_content.strip()) < 100:
#                 raise ValueError("Weekly content is insufficient for quiz generation")

#             logger.info(
#                 f"Generating weekly quiz | Course={request.course_id}, "
#                 f"Week={request.week_number}, MCQ={request.num_mcq}, "
#                 f"T/F={request.num_true_false}, SA={request.num_short_answer}"
#             )
            
#             # Generate quiz ID
#             quiz_id = self._generate_quiz_id()
            
#             # Initialize result lists
#             mcq_questions = []
#             tf_questions = []
#             sa_questions = []
            
#             # Generate MCQs
#             if request.num_mcq > 0:
#                 mcq_questions = await self._generate_mcq(
#                     content=request.combined_content,
#                     num_questions=request.num_mcq,
#                     difficulty=request.difficulty_level,
#                     topic=f"Week {request.week_number}"
#                 )
            
#             # Generate True/False
#             if request.num_true_false > 0:
#                 tf_questions = await self._generate_true_false(
#                     content=request.combined_content,
#                     num_questions=request.num_true_false,
#                     difficulty=request.difficulty_level,
#                     topic=f"Week {request.week_number}"
#                 )
            
#             # Generate Short Answer
#             if request.num_short_answer > 0:
#                 sa_questions = await self._generate_short_answer(
#                     content=request.combined_content,
#                     num_questions=request.num_short_answer,
#                     difficulty=request.difficulty_level,
#                     topic=f"Week {request.week_number}"
#                 )
            
#             # Calculate totals
#             total_questions = len(mcq_questions) + len(tf_questions) + len(sa_questions)
#             total_points = (
#                 sum(q.points for q in mcq_questions) +
#                 sum(q.points for q in tf_questions) +
#                 sum(q.points for q in sa_questions)
#             )
            
#             # Estimate duration (2 min per MCQ/TF, 5 min per SA)
#             estimated_duration = (
#                 (len(mcq_questions) + len(tf_questions)) * 2 +
#                 len(sa_questions) * 5
#             )
            
#             # Build result
#             result = QuizGenerationResult(
#                 # quiz_id=quiz_id,
#                 # topic=f"Week {request.week_number} - {', '.join(request.modules[:2])}",
#                 difficulty_level=request.difficulty_level,
#                 mcq_questions=mcq_questions,
#                 true_false_questions=tf_questions,
#                 open_ended_questions=sa_questions,
#                 total_questions=total_questions,
#                 total_points=total_points,
#                 estimated_duration_minutes=estimated_duration,
#                 generated_at=datetime.now().isoformat(),
#                 generation_metadata={
#                     "course_id": request.course_id,
#                     # "week_number": request.week_number,
#                     # "modules": request.modules,
#                     "quiz_type": "weekly",
#                     "student_id": request.student_id
#                 }
#             )
            
#             logger.info(
#                 f" Weekly quiz generated: {quiz_id} | "
#                 f"{total_questions} questions, {total_points} points"
#             )
            
#             return result
            
#         except Exception as e:
#             logger.error(f" Weekly quiz generation failed: {e}", exc_info=True)
#             raise
    
#     async def _generate_mcq(self,content: str,num_questions: int,difficulty: DifficultyLevel,topic: str) -> List[GeneratedMCQ]:
#         """Generate multiple choice questions."""
        
#         prompt = f"""You are a TVET educator. Generate EXACTLY {num_questions} multiple-choice questions based ONLY on this content.

# CONTENT:
# {content}

# DIFFICULTY: {difficulty.value}

# RULES:
# 1. Questions MUST come from the content
# 2. Create 4 options (A, B, C, D) per question
# 3. Make distractors plausible but incorrect
# 4. Provide clear explanations

# Return ONLY a JSON array:
# [
#   {{
#     "question": "Question text?",
#     "options": [
#       {{"id": "A", "text": "Option A"}},
#       {{"id": "B", "text": "Option B"}},
#       {{"id": "C", "text": "Option C"}},
#       {{"id": "D", "text": "Option D"}}
#     ],
#     "correct_answer": "B",
#     "explanation": "Why B is correct"
#   }}
# ]

# Generate EXACTLY {num_questions} questions."""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a TVET quiz creator. Return ONLY valid JSON."
#                     },
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=self.temperature,
#                 max_tokens=3000
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
#             questions_data = json.loads(response_text)
            
#             # Convert to Pydantic models
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 # Convert options to MCQOption objects
#                 options = [
#                     MCQOption(option_id=opt["id"], text=opt["text"])
#                     for opt in q_data["options"]
#                 ]
                
#                 questions.append(GeneratedMCQ(
#                     question_text=q_data["question"],
#                     options=options,
#                     correct_answer=q_data["correct_answer"],
#                     explanation=q_data["explanation"],
#                     difficulty=difficulty,
#                     topic=topic,
#                     points=5.0
#                 ))
            
#             logger.info(f"Generated {len(questions)} MCQ questions")
#             return questions
            
#         except Exception as e:
#             logger.error(f" MCQ generation failed: {e}")
#             raise
    
#     async def _generate_true_false(
#         self,
#         content: str,
#         num_questions: int,
#         difficulty: DifficultyLevel,
#         topic: str
#     ) -> List[GeneratedTrueFalse]:
#         """Generate true/false questions."""
        
#         prompt = f"""Generate EXACTLY {num_questions} True/False questions based ONLY on this content.

# CONTENT:
# {content}

# DIFFICULTY: {difficulty.value}

# Return ONLY a JSON array:
# [
#   {{
#     "question": "Statement here.",
#     "correct_answer": true,
#     "explanation": "Why this is true/false"
#   }}
# ]

# Generate EXACTLY {num_questions} questions."""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a TVET quiz creator. Return ONLY valid JSON."
#                     },
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=self.temperature,
#                 max_tokens=2000
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
#             questions_data = json.loads(response_text)
            
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 questions.append(GeneratedTrueFalse(
#                     question_text=q_data["question"],
#                     correct_answer=q_data["correct_answer"],
#                     explanation=q_data["explanation"],
#                     difficulty=difficulty,
#                     topic=topic,
#                     points=3.0
#                 ))
            
#             logger.info(f" Generated {len(questions)} T/F questions")
#             return questions
            
#         except Exception as e:
#             logger.error(f" T/F generation failed: {e}")
#             raise
    
#     async def _generate_short_answer(self,content: str,num_questions: int,difficulty: DifficultyLevel,topic: str) -> List[GeneratedOpenEnded]:
#         """Generate short answer questions."""
        
#         prompt = f"""Generate EXACTLY {num_questions} short answer questions based ONLY on this content.

# CONTENT:
# {content}

# DIFFICULTY: {difficulty.value}

# Return ONLY a JSON array:
# [
#   {{
#     "question": "Question here?",
#     "rubric": "Grading criteria",
#     "sample_answer": "Complete answer",
#     "keywords": ["key1", "key2", "key3"]
#   }}
# ]

# Generate EXACTLY {num_questions} questions."""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a TVET quiz creator. Return ONLY valid JSON."
#                     },
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=self.temperature,
#                 max_tokens=2500
#             )
            
#             response_text = response.choices[0].message.content.strip()
#             response_text = self._extract_json(response_text)
#             questions_data = json.loads(response_text)
            
#             questions = []
#             for q_data in questions_data[:num_questions]:
#                 questions.append(GeneratedOpenEnded(
#                     question_text=q_data["question"],
#                     rubric=q_data["rubric"],
#                     sample_answer=q_data["sample_answer"],
#                     keywords=q_data.get("keywords", []),
#                     difficulty=difficulty,
#                     topic=topic,
#                     points=10.0
#                 ))
            
#             logger.info(f"Generated {len(questions)} short answer questions")
#             return questions
            
#         except Exception as e:
#             logger.error(f" Short answer generation failed: {e}")
#             raise
    
#     def _extract_json(self, text: str) -> str:
#         """Extract JSON from LLM response."""
#         text = text.strip()
        
#         # Remove markdown
#         if text.startswith("```json"):
#             text = text[7:]
#         elif text.startswith("```"):
#             text = text[3:]
        
#         if text.endswith("```"):
#             text = text[:-3]
        
#         # Find JSON array
#         start = text.find('[')
#         end = text.rfind(']')
        
#         if start != -1 and end != -1:
#             return text[start:end+1]
        
#         return text.strip()
    
#     def _generate_quiz_id(self) -> str:
#         """Generate unique quiz ID."""
#         from uuid import uuid4
#         return f"quiz_{uuid4().hex[:12]}"






# Legacy version










"""
Quiz Generation Service - Legacy Format
Outputs in your original format with simple dictionaries
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