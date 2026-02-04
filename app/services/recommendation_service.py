"""
Module-Based Recommendation Service 
Location: app/services/recommendation_service.py
"""

import os
import httpx
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from app.core.logging_config import logger
from collections import Counter
import re

load_dotenv()


class RecommendationService:
    """Module-focused recommendation system with specific, actionable feedback"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQAPI_KEY")
        if not self.groq_api_key:
            logger.warning(" GROQAPI_KEY not found. Will use fallback recommendations.")
        
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
        logger.info(" Module-Based RecommendationService initialized")
    
    def _clean_markdown(self, text: str) -> str:
        """Remove all markdown formatting from text"""
        text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def _remove_section_references(self, text: str) -> str:
        """Remove section references like 'section 3.2', 'sections 4.3 and 4.5'"""
        # Remove patterns like "section X.X", "sections X.X", "section X.X.X"
        text = re.sub(r'\(sections?\s+[\d\.,\s]+(?:and\s+[\d\.]+)?\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'sections?\s+[\d\.,\s]+(?:and\s+[\d\.]+)?', '', text, flags=re.IGNORECASE)
        # Remove patterns like "review section X.X in your material"
        text = re.sub(r',?\s*(?:review|see|refer to|check)\s+sections?\s+[\d\.,\s]+(?:and\s+[\d\.]+)?\s*(?:in your (?:learning )?material)?\.?', '', text, flags=re.IGNORECASE)
        # Clean up extra spaces and periods
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+\.', '.', text)
        text = re.sub(r'\.+', '.', text)
        return text.strip()
    
    def _remove_paragraph_labels(self, text: str) -> str:
        """Remove paragraph labels like 'Paragraph 1 - Critical Gaps:', 'Paragraph 2 -'"""
        text = re.sub(r'^Paragraph\s+\d+\s*[-:]\s*(?:Critical Gaps|Recommendations)?:?\s*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r'\n+Paragraph\s+\d+\s*[-:]\s*(?:Critical Gaps|Recommendations)?:?\s*\n?', '\n\n', text, flags=re.IGNORECASE)
        return text.strip()
    
    def analyze_module_performance(
        self,
        module_id: str,
        module_name: str,
        module_content: str,
        max_score: float,
        question_results: List[Dict]
    ) -> Dict:
        """Analyze performance on a single module"""
        
        total_awarded = sum(q.get("awarded_marks", 0) for q in question_results)
        percentage = (total_awarded / max_score * 100) if max_score > 0 else 0
        
        failed_questions = []
        concepts_to_review = []
        question_type_performance = {}
        
        for q in question_results:
            q_type = q.get("question_type", "unknown")
            awarded = q.get("awarded_marks", 0)
            max_marks = q.get("max_marks", 1)
            is_correct = q.get("is_correct", False)
            
            if q_type not in question_type_performance:
                question_type_performance[q_type] = {"correct": 0, "total": 0}
            
            question_type_performance[q_type]["total"] += 1
            if is_correct:
                question_type_performance[q_type]["correct"] += 1
            
            if not is_correct or awarded < max_marks * 0.7:
                failed_questions.append({
                    "question_text": q.get("question_text", ""),
                    "student_answer": q.get("student_answer", ""),
                    "correct_answer": q.get("correct_answer", ""),
                    "awarded_marks": awarded,
                    "max_marks": max_marks,
                    "question_type": q_type
                })
                
                # Store full question text for concepts_to_review
                question_text = q.get("question_text", "")
                if question_text:
                    concepts_to_review.append(question_text)
        
        if percentage >= 80:
            performance_level = "Excellent"
        elif percentage >= 70:
            performance_level = "Good"
        elif percentage >= 60:
            performance_level = "Satisfactory"
        else:
            performance_level = "Needs Improvement"
        
        return {
            "module_id": module_id,
            "module_name": module_name,
            "module_content": module_content,
            "total_score": total_awarded,
            "max_score": max_score,
            "percentage": round(percentage, 1),
            "performance_level": performance_level,
            "total_questions": len(question_results),
            "failed_questions": len(failed_questions),
            "failed_question_details": failed_questions,
            "question_type_performance": question_type_performance,
            "concepts_to_review": concepts_to_review  # Full questions now
        }
    
    def identify_critical_gaps(
        self,
        module_analyses: List[Dict]
    ) -> Dict:
        """Identify critical gaps across all modules"""
        
        all_failed_questions = []
        weak_modules = []
        strong_modules = []
        all_question_types = {}
        
        for analysis in module_analyses:
            percentage = analysis["percentage"]
            module_id = analysis["module_id"]
            module_name = analysis["module_name"]
            
            if percentage < 60:
                weak_modules.append({
                    "module_id": module_id,
                    "module_name": module_name,
                    "percentage": percentage,
                    "failed_count": analysis["failed_questions"],
                    "content": analysis["module_content"]
                })
            elif percentage >= 80:
                strong_modules.append({
                    "module_id": module_id,
                    "module_name": module_name,
                    "percentage": percentage,
                    "content": analysis["module_content"]
                })
            
            all_failed_questions.extend(analysis["failed_question_details"])
            
            for q_type, stats in analysis["question_type_performance"].items():
                if q_type not in all_question_types:
                    all_question_types[q_type] = {"correct": 0, "total": 0}
                all_question_types[q_type]["correct"] += stats["correct"]
                all_question_types[q_type]["total"] += stats["total"]
        
        weak_question_types = []
        for q_type, stats in all_question_types.items():
            percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            if percentage < 70:
                weak_question_types.append({
                    "type": q_type,
                    "percentage": round(percentage, 1),
                    "attempted": stats["total"]
                })
        
        return {
            "weak_modules": weak_modules,
            "strong_modules": strong_modules,
            "weak_question_types": weak_question_types,
            "total_failed_questions": len(all_failed_questions),
            "all_failed_questions": all_failed_questions,
            "overall_performance": self._calculate_overall_performance(module_analyses)
        }
    
    def _calculate_overall_performance(self, module_analyses: List[Dict]) -> Dict:
        """Calculate overall performance across all modules"""
        if not module_analyses:
            return {"percentage": 0, "level": "No Data"}
        
        total_score = sum(m["total_score"] for m in module_analyses)
        total_max = sum(m["max_score"] for m in module_analyses)
        percentage = (total_score / total_max * 100) if total_max > 0 else 0
        
        if percentage >= 80:
            level = "Excellent"
        elif percentage >= 70:
            level = "Good"
        elif percentage >= 60:
            level = "Satisfactory"
        else:
            level = "Needs Improvement"
        
        return {
            "total_score": total_score,
            "total_max": total_max,
            "percentage": round(percentage, 1),
            "level": level
        }
    
    async def generate_module_feedback(
        self,
        module_analysis: Dict
    ) -> str:
        """Generate AI feedback for individual module"""
        if not self.groq_api_key:
            return self._fallback_module_feedback(module_analysis)
        
        system_prompt = """You are a supportive TVET instructor providing feedback on module performance.
Be specific, constructive, and encouraging. Write in plain text without any markdown formatting.
Do NOT mention section numbers, chapter references, or page numbers.
Keep feedback concise (3-4 sentences) and actionable."""
        
        failed_details = "\n".join([
            f"Question: {q['question_text'][:100]} | Student: {q['student_answer']} | Correct: {q['correct_answer']}"
            for q in module_analysis["failed_question_details"][:3]
        ]) if module_analysis["failed_question_details"] else "None"
        
        user_prompt = f"""Module: {module_analysis['module_name']}
Score: {module_analysis['total_score']}/{module_analysis['max_score']} ({module_analysis['percentage']}%)
Performance Level: {module_analysis['performance_level']}
Questions Failed: {module_analysis['failed_questions']}/{module_analysis['total_questions']}

Failed Questions:
{failed_details}

Provide specific feedback (3-4 sentences) covering:
1. What they did well
2. What needs improvement
3. One concrete action to improve

Write in plain text without markdown, bullets, numbering, or section references."""

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
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 200
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    feedback = result["choices"][0]["message"]["content"].strip()
                    feedback = self._clean_markdown(feedback)
                    feedback = self._remove_section_references(feedback)
                    return feedback
                else:
                    return self._fallback_module_feedback(module_analysis)
            
        except Exception as e:
            logger.error(f" Module feedback generation failed: {e}")
            return self._fallback_module_feedback(module_analysis)
    
    def _fallback_module_feedback(self, module_analysis: Dict) -> str:
        """Fallback feedback when AI is unavailable"""
        percentage = module_analysis["percentage"]
        failed = module_analysis["failed_questions"]
        total = module_analysis["total_questions"]
        
        if percentage >= 80:
            return f"Excellent work on this module! You scored {percentage}% and demonstrated strong understanding of the concepts. Keep up this level of performance."
        elif percentage >= 70:
            return f"Good performance with {percentage}%. You missed {failed} out of {total} questions. Review the specific concepts from those questions to strengthen your understanding."
        elif percentage >= 60:
            return f"Satisfactory effort with {percentage}%. Focus on reviewing the {failed} questions you missed, particularly the core concepts. Additional practice will help solidify your knowledge."
        else:
            return f"This module needs more attention. You scored {percentage}%. Review the learning material carefully, especially the areas covered in the {failed} questions you missed. Consider revisiting the fundamental concepts before moving forward."
    
    async def generate_collective_feedback(
        self,
        critical_gaps: Dict,
        module_analyses: List[Dict]
    ) -> Tuple[str, str]:
        """Generate specific, actionable collective feedback"""
        if not self.groq_api_key:
            return self._fallback_collective_feedback(critical_gaps, module_analyses)
        
        system_prompt = """You are an experienced TVET instructor providing specific, actionable feedback.
Focus on WHAT CONTENT to study, not section numbers or chapter references.
Reference specific concepts, topics, and principles from the learning material.
Write in plain text without markdown formatting.
Do NOT mention section numbers, chapter numbers, or page numbers.
Be direct, specific, and actionable."""
        
        # Build detailed context about what they got wrong
        weak_content_details = ""
        for module in critical_gaps["weak_modules"]:
            weak_content_details += f"\n{module['module_name']} ({module['percentage']:.1f}%):\n"
            weak_content_details += f"Content covered: {module['content'][:300]}...\n"
        
        # Get specific failed questions
        failed_concepts = []
        for q in critical_gaps["all_failed_questions"][:8]:
            failed_concepts.append(f"- {q['question_text'][:100]}")
        failed_concepts_str = "\n".join(failed_concepts) if failed_concepts else "None"
        
        strong_content_details = ""
        for module in critical_gaps["strong_modules"]:
            strong_content_details += f"\n{module['module_name']} ({module['percentage']:.1f}%): Strong understanding\n"
        
        user_prompt = f"""Overall Performance: {critical_gaps['overall_performance']['percentage']:.1f}%

WEAK AREAS:
{weak_content_details}

SPECIFIC FAILED CONCEPTS:
{failed_concepts_str}

STRONG AREAS:
{strong_content_details}

Write TWO specific paragraphs (3-4 sentences each):

FIRST PARAGRAPH:
Identify the SPECIFIC TOPICS and CONCEPTS they need to study. Mention actual content areas and principles. Be precise about what they're missing. Do NOT mention section numbers.

SECOND PARAGRAPH:
Give CONCRETE study actions. Tell them exactly which topics to review, what to practice, and how to approach weak areas. Reference the actual content they need to master. Do NOT mention section numbers, chapter references, or page numbers.

Write in plain text. No markdown. No section references. Be specific and actionable."""

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
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 400
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    output = result["choices"][0]["message"]["content"].strip()
                    output = self._clean_markdown(output)
                    output = self._remove_section_references(output)
                    output = self._remove_paragraph_labels(output)
                    
                    parts = output.split("\n\n")
                    critical_gaps_text = parts[0].strip() if len(parts) > 0 else output
                    recommendations = parts[1].strip() if len(parts) > 1 else "Keep practicing and reviewing the material."
                    
                    return critical_gaps_text, recommendations
                else:
                    return self._fallback_collective_feedback(critical_gaps, module_analyses)
            
        except Exception as e:
            logger.error(f" Collective feedback generation failed: {e}")
            return self._fallback_collective_feedback(critical_gaps, module_analyses)
    
    def _fallback_collective_feedback(
        self,
        critical_gaps: Dict,
        module_analyses: List[Dict]
    ) -> Tuple[str, str]:
        """Specific fallback collective feedback"""
        overall = critical_gaps["overall_performance"]
        weak_modules = critical_gaps["weak_modules"]
        
        if weak_modules:
            # Extract specific content topics from failed questions
            failed_topics = set()
            for q in critical_gaps["all_failed_questions"][:5]:
                question = q["question_text"]
                # Extract key phrases
                if "PPE" in question or "Personal Protective" in question:
                    failed_topics.add("Personal Protective Equipment requirements")
                if "LOTO" in question or "Lockout" in question:
                    failed_topics.add("Lockout/Tagout procedures")
                if "RMS" in question:
                    failed_topics.add("RMS voltage calculations and meaning")
                if "AC" in question and "DC" in question:
                    failed_topics.add("AC versus DC current characteristics")
                if "transformer" in question.lower():
                    failed_topics.add("transformer operation and power transmission")
                if "hierarchy" in question.lower():
                    failed_topics.add("hierarchy of electrical safety controls")
                if "AWG" in question:
                    failed_topics.add("AWG wire sizing system")
                if "ampacity" in question.lower():
                    failed_topics.add("wire ampacity ratings")
                if "grounding" in question.lower() and "bonding" in question.lower():
                    failed_topics.add("difference between grounding and bonding")
                if "GFCI" in question:
                    failed_topics.add("GFCI operation and specifications")
            
            if not failed_topics:
                failed_topics = {f"{m['module_name']} fundamentals" for m in weak_modules[:2]}
            
            topics_list = ", ".join(list(failed_topics)[:4])
            
            gaps = f"You need to strengthen your understanding of several critical concepts: {topics_list}. Your performance shows gaps in these foundational topics that are essential for safe and effective electrical work. These aren't just theoretical - they're practical skills you'll use daily in the field."
            
            # Build specific recommendations
            study_items = []
            for module in weak_modules[:2]:
                content = module["content"]
                sentences = content.split(". ")
                if sentences:
                    key_concept = sentences[0].strip()
                    study_items.append(f"review {key_concept.lower()}")
            
            if not study_items:
                study_items = ["review the fundamental concepts", "practice the question types you missed"]
            
            recommendations = f"Start by focusing on your weakest areas: {' and '.join(study_items[:2])}. Don't just read - actively practice applying these concepts. Work through similar questions, draw diagrams to visualize the processes, and explain the concepts out loud to reinforce your understanding. Spend extra time on {list(failed_topics)[0] if failed_topics else 'core concepts'} since this appeared in multiple questions you missed."
        else:
            gaps = f"Your overall performance of {overall['percentage']:.1f}% shows {overall['level'].lower()} understanding across all topics. You're demonstrating consistent comprehension of the material."
            recommendations = "Continue reinforcing your knowledge through practice. Challenge yourself with more complex scenarios and real-world applications to deepen your expertise."
        
        return gaps, recommendations
    
    async def generate_recommendations(
        self,
        modules: List[Dict]
    ) -> Dict:
        """Generate comprehensive recommendations for all modules"""
        try:
            logger.info(f" Analyzing {len(modules)} module(s)")
            
            module_analyses = []
            module_feedbacks = []
            
            for idx, module in enumerate(modules):
                logger.info(f" Analyzing module {idx + 1}/{len(modules)}")
                
                analysis = self.analyze_module_performance(
                    module_id=module.get("module_id", f"module_{idx+1}"),
                    module_name=module.get("module_name", f"Module {idx+1}"),
                    module_content=module.get("module_content", ""),
                    max_score=module.get("max_score", 0),
                    question_results=module.get("question_results", [])
                )
                
                feedback = await self.generate_module_feedback(analysis)
                
                module_analyses.append(analysis)
                module_feedbacks.append({
                    "module_id": analysis["module_id"],
                    "module_name": analysis["module_name"],
                    "score": f"{analysis['total_score']}/{analysis['max_score']}",
                    "percentage": analysis["percentage"],
                    "performance_level": analysis["performance_level"],
                    "feedback": feedback,
                    "concepts_to_review": analysis["concepts_to_review"]  # Full questions
                })
            
            critical_gaps = self.identify_critical_gaps(module_analyses)
            
            gaps_analysis, recommendations = await self.generate_collective_feedback(
                critical_gaps, module_analyses
            )
            
            result = {
                "individual_module_reviews": module_feedbacks,
                "collective_feedback": {
                    "overall_performance": critical_gaps["overall_performance"],
                    "critical_gaps": gaps_analysis,
                    "recommendations": recommendations,
                    "weak_question_types": critical_gaps["weak_question_types"],
                    "total_failed_questions": critical_gaps["total_failed_questions"]
                }
            }
            
            logger.info(f"Recommendations generated successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}", exc_info=True)
            raise