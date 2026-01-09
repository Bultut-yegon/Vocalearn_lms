"""
Enhanced Quiz Service with Document-Aware Generation
Generates quizzes based on uploaded PDFs/notes
"""

import os
import httpx
import json
import re
import uuid
from typing import List, Dict, Optional
from datetime import datetime
from app.core.logging_config import logger
from app.services.document_service import DocumentProcessingService

class DocumentAwareQuizService:
    """
    Enhanced quiz generation that reads from uploaded documents.
    Creates contextual quizzes based on actual course materials.
    """  
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
        # Initialize document service
        self.doc_service = DocumentProcessingService()
    
    async def generate_quiz_from_documents(self,course: str,topic: str,
        timeframe: str = "weekly",  # "daily", "weekly", "custom"
        difficulty: str = "intermediate",
        num_mcq: int = 5,
        num_true_false: int = 3,
        num_short_answer: int = 2,
        document_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate quiz from uploaded course documents.
        
        Args:
            course: Course name
            topic: Specific topic to focus on
            timeframe: "daily" (last 24h), "weekly" (last 7 days)
            difficulty: beginner/intermediate/advanced
            num_mcq: Number of MCQ questions
            num_true_false: Number of T/F questions
            num_short_answer: Number of short answer questions
            document_ids: Specific documents to use (optional)
        """
        
        logger.info(f"Generating document-aware quiz for {course} - {topic}")
        
        # Step 1: Retrieve relevant document content
        if document_ids:
            # Use specific documents
            relevant_content = self._get_content_from_documents(document_ids, topic)
        else:
            # Get documents from timeframe
            relevant_content = self._get_content_from_timeframe(
                course, topic, timeframe
            )
        
        if not relevant_content:
            raise Exception(f"No documents found for {course} in {timeframe} timeframe")
        
        # Step 2: Extract key concepts and context
        context = self._build_quiz_context(relevant_content)
        
        # Step 3: Generate questions using document context
        quiz_id = str(uuid.uuid4())
        
        mcq_questions = []
        tf_questions = []
        short_questions = []
        
        if num_mcq > 0:
            mcq_questions = await self._generate_context_mcq(
                topic, context, num_mcq, difficulty
            )
        
        if num_true_false > 0:
            tf_questions = await self._generate_context_tf(
                topic, context, num_true_false, difficulty
            )
        
        if num_short_answer > 0:
            short_questions = await self._generate_context_short_answer(
                topic, context, num_short_answer, difficulty
            )
        
        # Calculate totals
        total_questions = len(mcq_questions) + len(tf_questions) + len(short_questions)
        total_points = (
            sum(q["points"] for q in mcq_questions) +
            sum(q["points"] for q in tf_questions) +
            sum(q["points"] for q in short_questions)
        )
        
        estimated_duration = (
            len(mcq_questions) * 1.5 +
            len(tf_questions) * 1.5 +
            len(short_questions) * 5
        )
        
        return {
            "quiz_id": quiz_id,
            "course": course,
            "topic": topic,
            "difficulty_level": difficulty,
            "source_documents": [chunk["metadata"]["document_id"] for chunk in relevant_content[:5]],
            "document_references": self._extract_references(relevant_content),
            "mcq_questions": mcq_questions,
            "true_false_questions": tf_questions,
            "open_ended_questions": short_questions,
            "total_questions": total_questions,
            "total_points": round(total_points, 2),
            "estimated_duration_minutes": int(estimated_duration),
            "generated_at": datetime.now().isoformat(),
            "generation_metadata": {
                "source": "document-aware",
                "timeframe": timeframe,
                "documents_used": len(set(chunk["metadata"]["document_id"] for chunk in relevant_content)),
                "context_chunks": len(relevant_content)
            }
        }
    
    def _get_content_from_timeframe(self,course: str,topic: str,timeframe: str) -> List[Dict]:
        """Retrieve document content from timeframe."""
        
        # Get documents from specified timeframe
        documents = self.doc_service.get_documents_by_timeframe(course, timeframe)
        
        # Retrieve most relevant chunks for the topic
        relevant_content = self.doc_service.retrieve_relevant_content(
            query=topic,
            filters={"course": course},
            top_k=10  # Get top 10 most relevant chunks
        )
        
        return relevant_content
    
    def _get_content_from_documents(self,document_ids: List[str],topic: str) -> List[Dict]:
        """Get content from specific documents."""
        
        all_content = []
        for doc_id in document_ids:
            content = self.doc_service.retrieve_relevant_content(
                query=topic,
                filters={"document_id": doc_id},
                top_k=5
            )
            all_content.extend(content)
        
        return all_content
    
    def _build_quiz_context(self, relevant_content: List[Dict]) -> str:
        """Build context string from document chunks."""
        
        context_parts = []
        seen_content = set()
        
        for chunk in relevant_content[:8]:  # Use top 8 chunks
            content = chunk["content"]
            
            # Avoid duplicates
            if content[:100] not in seen_content:
                context_parts.append(content)
                seen_content.add(content[:100])
        
        full_context = "\n\n---\n\n".join(context_parts)
        
        # Truncate if too long (keep under 3000 tokens for LLM)
        if len(full_context) > 10000:
            full_context = full_context[:10000] + "..."
        
        return full_context
    
    def _extract_references(self, relevant_content: List[Dict]) -> List[Dict]:
        """Extract document references for citations."""
        
        references = []
        seen_docs = set()
        
        for chunk in relevant_content:
            doc_id = chunk["metadata"]["document_id"]
            if doc_id not in seen_docs:
                references.append({
                    "document_id": doc_id,
                    "topic": chunk["metadata"].get("topic", "Unknown"),
                    "week": chunk["metadata"].get("week"),
                    "upload_date": chunk["metadata"].get("upload_date")
                })
                seen_docs.add(doc_id)
        
        return references
    
    async def _generate_context_mcq(self,topic: str,context: str,count: int,difficulty: str) -> List[Dict]:
        """Generate MCQ questions based on document content."""
        
        system_prompt = """You are a TVET instructor creating quiz questions based on course materials.
Generate questions that directly test understanding of the provided content.

CRITICAL REQUIREMENTS:
- Questions MUST be based on the provided document content
- Do NOT make up information not in the documents
- Reference specific concepts, procedures, or facts from the materials
- Options should include plausible distractors based on the content

OUTPUT FORMAT (JSON array, no markdown):
[
  {
    "question_text": "question based on document content",
    "options": [
      {"option_id": "A", "text": "option A"},
      {"option_id": "B", "text": "option B"},
      {"option_id": "C", "text": "option C"},
      {"option_id": "D", "text": "option D"}
    ],
    "correct_answer": "A",
    "explanation": "why A is correct with document reference",
    "document_reference": "specific section or page if available"
  }
]"""

        user_prompt = f"""Based on this course material about {topic}:

COURSE CONTENT:
{context}

Generate {count} multiple choice questions that test understanding of this specific content.
Difficulty: {difficulty}

Return JSON array of {count} questions. Each question must be directly answerable from the provided content."""

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
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    llm_output = result["choices"][0]["message"]["content"]
                    
                    # Parse and validate
                    questions = self._parse_mcq_response(llm_output, topic, difficulty)
                    logger.info(f"Generated {len(questions)} context-aware MCQ questions")
                    return questions[:count]
                else:
                    logger.error(f"LLM error: {response.status_code}")
                    raise Exception(f"LLM returned status {response.status_code}")
        
        except Exception as e:
            logger.error(f"Context MCQ generation failed: {e}")
            return []
    
    async def _generate_context_tf(self,topic: str,context: str,count: int,difficulty: str) -> List[Dict]:
        """Generate T/F questions from document content."""
        
        system_prompt = """Create true/false questions based strictly on the provided course material.
        Each statement should be verifiable from the document content."""

        user_prompt = f"""Based on this content about {topic}:

{context}

Generate {count} true/false questions that can be verified from this content.
Difficulty: {difficulty}

Return JSON: [{{"question_text": "...", "correct_answer": true/false, "explanation": "..."}}]"""

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
                    return questions[:count]
        
        except Exception as e:
            logger.error(f"Context T/F generation failed: {e}")
            return []
    
    async def _generate_context_short_answer(self,topic: str,context: str,count: int,difficulty: str) -> List[Dict]:
        """Generate short answer questions from documents."""
        
        system_prompt = """Create short answer questions that require students to explain concepts from the course material.
        Include detailed rubrics based on the document content."""

        user_prompt = f"""Based on this material about {topic}:

{context}

Generate {count} short answer questions that test comprehension of this content.
Include rubrics with specific points from the material.

Return JSON: [{{"question_text": "...", "rubric": "...", "sample_answer": "...", "keywords": [...]}}]"""

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
                    questions = self._parse_open_ended_response(llm_output, topic, "short_answer", difficulty)
                    return questions[:count]
        
        except Exception as e:
            logger.error(f"Context short answer generation failed: {e}")
            return []
    
    def _parse_mcq_response(self, llm_output: str, topic: str, difficulty: str) -> List[Dict]:
        """Parse MCQ response from LLM."""
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
                        "document_reference": q.get("document_reference"),
                        "difficulty": difficulty,
                        "topic": topic,
                        "subtopic": q.get("subtopic"),
                        "points": 5.0
                    })
            
            return validated
        except Exception as e:
            logger.error(f"Failed to parse MCQ: {e}")
            return []
    
    def _validate_mcq_question(self, question: Dict) -> bool:
        """Validate MCQ structure."""
        required_fields = ["question_text", "options", "correct_answer"]
        if not all(field in question for field in required_fields):
            return False
        if len(question["options"]) != 4:
            return False
        if question["correct_answer"] not in {"A", "B", "C", "D"}:
            return False
        return True
    
    def _parse_true_false_response(self, llm_output: str, topic: str, difficulty: str) -> List[Dict]:
        """Parse T/F response."""
        try:
            llm_output = re.sub(r'```json\n?', '', llm_output)
            llm_output = re.sub(r'```\n?', '', llm_output)
            questions = json.loads(llm_output.strip())
            
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
            logger.error(f"Failed to parse T/F: {e}")
            return []
    
    def _parse_open_ended_response(self, llm_output: str, topic: str, question_type: str, difficulty: str) -> List[Dict]:
        """Parse open-ended response."""
        try:
            llm_output = re.sub(r'```json\n?', '', llm_output)
            llm_output = re.sub(r'```\n?', '', llm_output)
            questions = json.loads(llm_output.strip())
            
            points_map = {"short_answer": 10.0, "essay": 20.0, "practical": 15.0}
            
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
            logger.error(f"Failed to parse open-ended: {e}")
            return []