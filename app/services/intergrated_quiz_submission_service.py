# """
# Integrated Quiz Submission Service
# Handles: Grading + Immediate Recommendations
# """

# from typing import Dict, List, Optional
# from datetime import datetime
# from app.services.grading_service import GradingService
# from app.services.recommendation_service import RecommendationService
# from app.core.logging_config import logger


# class QuizSubmissionService:
#     """
#     Orchestrates quiz grading and recommendation generation.
#     Provides complete feedback loop for students.
#     """
    
#     def __init__(self):
#         self.grading_service = GradingService()
#         self.recommendation_service = RecommendationService()
#         logger.info("QuizSubmissionService initialized")
    
#     async def process_quiz_submission(
#         self,
#         submission_id: str,
#         student_id: str,
#         quiz_data: Dict,
#         student_answers: Dict[str, str],
#         performance_history: Optional[List[Dict]] = None
#     ) -> Dict:
#         """
#         Complete quiz submission processing:
#         1. Grade the quiz
#         2. Generate personalized recommendations
#         3. Return comprehensive feedback
        
#         Args:
#             submission_id: Unique submission identifier
#             student_id: Student's ID
#             quiz_data: Quiz structure from generation service
#             student_answers: Student's answers {"mcq_0": "B", ...}
#             performance_history: Optional past performance for better recommendations
            
#         Returns:
#             Complete response with grading + recommendations
#         """
#         try:
#             logger.info(f" Processing submission {submission_id} for student {student_id}")
            
#             # STEP 1: Grade the quiz
#             grading_result = await self.grading_service.grade_quiz_from_generation_service(
#                 submission_id=submission_id,
#                 student_id=student_id,
#                 quiz_data=quiz_data,
#                 student_answers=student_answers
#             )
            
#             logger.info(
#                 f" Graded {submission_id}: {grading_result['percentage']:.1f}% "
#                 f"({grading_result['grade_letter']})"
#             )
            
#             # STEP 2: Build performance record from current submission
#             current_performance = {
#                 "topic": quiz_data.get("topic", "General Assessment"),
#                 "score": grading_result["total_points"],
#                 "max_score": grading_result["max_points"],
#                 "percentage": grading_result["percentage"],
#                 "timestamp": grading_result["graded_at"],
#                 "module_id": quiz_data.get("generation_metadata", {}).get("course_id"),
#                 "week_number": quiz_data.get("generation_metadata", {}).get("week_number")
#             }
            
#             # STEP 3: Combine with historical performance
#             if performance_history is None:
#                 performance_history = []
            
#             # Add current submission to history
#             full_history = performance_history + [current_performance]
            
#             # STEP 4: Extract topic-level scores from question results
#             topic_scores = self._extract_topic_scores(grading_result["question_results"])
            
#             # STEP 5: Generate personalized recommendations
#             recommendations = await self.recommendation_service.generate_recommendations(
#                 performance_history=full_history,
#                 topic_scores=topic_scores
#             )
            
#             logger.info(
#                 f" Recommendations generated for {student_id}: "
#                 f"{len(recommendations['topic_recommendations'])} topics"
#             )
            
#             # STEP 6: Build comprehensive response
#             return {
#                 "submission_id": submission_id,
#                 "student_id": student_id,
#                 "submitted_at": grading_result["graded_at"],
                
#                 # Grading Results
#                 "grading": {
#                     "total_points": grading_result["total_points"],
#                     "max_points": grading_result["max_points"],
#                     "percentage": grading_result["percentage"],
#                     "grade_letter": grading_result["grade_letter"],
#                     "overall_feedback": grading_result["overall_feedback"]
#                 },
                
#                 # Question-by-Question Results
#                 "question_results": grading_result["question_results"],
                
#                 # Performance Analysis
#                 "performance_analysis": {
#                     "current_score": grading_result["percentage"],
#                     "topic": current_performance["topic"],
#                     "strengths": recommendations["strengths"],
#                     "areas_for_improvement": recommendations["study_plan"]["skill_building"]["topics"],
#                     "urgent_review_needed": recommendations["study_plan"]["urgent_review"]["topics"]
#                 },
                
#                 # Personalized Recommendations
#                 "recommendations": {
#                     "priority_topics": recommendations["topic_recommendations"],
#                     "study_plan": recommendations["study_plan"],
#                     "trends": recommendations["trends"],
#                     "next_steps": self._generate_next_steps(recommendations, grading_result)
#                 },
                
#                 # AI Insights
#                 "ai_insights": {
#                     "explanation": recommendations["llm_explanation"],
#                     "motivational_message": recommendations["motivational_message"]
#                 },
                
#                 # Metadata
#                 "metadata": {
#                     "quiz_id": quiz_data.get("quiz_id"),
#                     "course_id": quiz_data.get("generation_metadata", {}).get("course_id"),
#                     "week_number": quiz_data.get("generation_metadata", {}).get("week_number"),
#                     "total_submissions": len(full_history)
#                 }
#             }
            
#         except Exception as e:
#             logger.error(f" Quiz submission processing failed: {e}", exc_info=True)
#             raise
    
#     def _extract_topic_scores(self, question_results: List[Dict]) -> Dict[str, float]:
#         """
#         Extract normalized topic scores from question results.
#         Groups by question type for topic mastery analysis.
#         """
#         topic_scores = {}
        
#         # Group by question type
#         for result in question_results:
#             q_type = result["question_type"]
#             if result["max_points"] > 0:
#                 score = result["awarded_points"] / result["max_points"]
#                 topic_scores[q_type] = topic_scores.get(q_type, [])
#                 topic_scores[q_type].append(score)
        
#         # Average scores per type
#         return {
#             topic: sum(scores) / len(scores)
#             for topic, scores in topic_scores.items()
#         }
    
#     def _generate_next_steps(
#         self,
#         recommendations: Dict,
#         grading_result: Dict
#     ) -> List[str]:
#         """Generate actionable next steps for the student."""
#         next_steps = []
        
#         percentage = grading_result["percentage"]
#         urgent_topics = recommendations["study_plan"]["urgent_review"]["topics"]
#         improvement_topics = recommendations["study_plan"]["skill_building"]["topics"]
        
#         # Based on performance level
#         if percentage >= 90:
#             next_steps.append(" Excellent work! Challenge yourself with advanced material.")
#             if recommendations["study_plan"]["advancement"]["topics"]:
#                 next_steps.append(
#                     f" Ready to advance in: {', '.join(recommendations['study_plan']['advancement']['topics'][:2])}"
#                 )
#         elif percentage >= 70:
#             next_steps.append("Good progress! Focus on consistency.")
#             if improvement_topics:
#                 next_steps.append(
#                     f" Strengthen your understanding of: {', '.join(improvement_topics[:2])}"
#                 )
#         else:
#             next_steps.append(" Review the fundamentals to build a stronger foundation.")
#             if urgent_topics:
#                 next_steps.append(
#                     f"Priority review needed for: {', '.join(urgent_topics[:2])}"
#                 )
        
#         # Study time recommendations
#         total_study_hours = (
#             recommendations["study_plan"]["urgent_review"].get("suggested_hours", 0) +
#             recommendations["study_plan"]["skill_building"].get("suggested_hours", 0)
#         )
        
#         if total_study_hours > 0:
#             next_steps.append(
#                 f"Recommended study time this week: {int(total_study_hours)} hours"
#             )
        
#         # Specific action items
#         if improvement_topics:
#             next_steps.append(
#                 f"Focus areas: Review course materials for {improvement_topics[0]}"
#             )
        
#         next_steps.append("Practice similar questions to reinforce your learning")
        
#         return next_steps
    
#     async def get_student_progress_summary(
#         self,
#         student_id: str,
#         performance_history: List[Dict]
#     ) -> Dict:
#         """
#         Generate overall progress summary for a student.
#         Useful for dashboards and progress tracking.
#         """
#         try:
#             if not performance_history:
#                 return {
#                     "student_id": student_id,
#                     "message": "No performance history available yet",
#                     "total_submissions": 0
#                 }
            
#             # Calculate overall metrics
#             total_submissions = len(performance_history)
#             average_score = sum(p["percentage"] for p in performance_history) / total_submissions
            
#             # Get latest performance
#             latest = performance_history[-1]
            
#             # Track improvement over time
#             if total_submissions >= 2:
#                 recent_avg = sum(p["percentage"] for p in performance_history[-3:]) / min(3, total_submissions)
#                 early_avg = sum(p["percentage"] for p in performance_history[:3]) / min(3, total_submissions)
#                 improvement = recent_avg - early_avg
#             else:
#                 improvement = 0
            
#             # Generate recommendations based on full history
#             topic_scores = {}
#             for record in performance_history:
#                 topic = record["topic"]
#                 score = record["percentage"] / 100  # Normalize to 0-1
#                 topic_scores[topic] = score
            
#             recommendations = await self.recommendation_service.generate_recommendations(
#                 performance_history=performance_history,
#                 topic_scores=topic_scores
#             )
            
#             return {
#                 "student_id": student_id,
#                 "summary": {
#                     "total_submissions": total_submissions,
#                     "average_score": round(average_score, 2),
#                     "latest_score": round(latest["percentage"], 2),
#                     "improvement_trend": "improving" if improvement > 5 else "stable" if improvement > -5 else "declining",
#                     "improvement_points": round(improvement, 2)
#                 },
#                 "strengths": recommendations["strengths"],
#                 "areas_for_improvement": recommendations["study_plan"]["skill_building"]["topics"],
#                 "study_plan": recommendations["study_plan"],
#                 "motivation": recommendations["motivational_message"],
#                 "timestamp": datetime.now().isoformat()
#             }
            
#         except Exception as e:
#             logger.error(f"Progress summary generation failed: {e}", exc_info=True)
#             raise










# VERSION 2









"""
Integrated Quiz Submission Service
Handles: Grading + Immediate Recommendations
"""

from typing import Dict, List, Optional
from datetime import datetime
from app.services.grading_service import GradingService
from app.services.recommendation_service import RecommendationService
from app.core.logging_config import logger


class QuizSubmissionService:
    """
    Orchestrates quiz grading and recommendation generation.
    Provides complete feedback loop for students.
    """
    
    def __init__(self):
        self.grading_service = GradingService()
        self.recommendation_service = RecommendationService()
        logger.info("QuizSubmissionService initialized")
    
    async def process_quiz_submission(
        self,
        submission_id: str,
        student_id: str,
        quiz_data: Dict,
        student_answers: Dict[str, str],
        performance_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Complete quiz submission processing:
        1. Grade the quiz
        2. Generate personalized recommendations
        3. Return comprehensive feedback
        
        Args:
            submission_id: Unique submission identifier
            student_id: Student's ID
            quiz_data: Quiz structure from generation service
            student_answers: Student's answers {"mcq_0": "B", ...}
            performance_history: Optional past performance for better recommendations
            
        Returns:
            Complete response with grading + recommendations
        """
        try:
            logger.info(f" Processing submission {submission_id} for student {student_id}")
            
            # STEP 1: Grade the quiz
            grading_result = await self.grading_service.grade_quiz_from_generation_service(
                submission_id=submission_id,
                student_id=student_id,
                quiz_data=quiz_data,
                student_answers=student_answers
            )
            
            logger.info(
                f" Graded {submission_id}: {grading_result['percentage']:.1f}% "
                f"({grading_result['grade_letter']})"
            )
            
            # STEP 2: Build performance record from current submission
            current_performance = {
                "topic": quiz_data.get("topic", "General Assessment"),
                "score": grading_result["total_points"],
                "max_score": grading_result["max_points"],
                "percentage": grading_result["percentage"],
                "timestamp": grading_result["graded_at"],
                "module_id": quiz_data.get("generation_metadata", {}).get("course_id"),
                "week_number": quiz_data.get("generation_metadata", {}).get("week_number")
            }
            
            # STEP 3: Combine with historical performance
            if performance_history is None:
                performance_history = []
            
            # Add current submission to history
            full_history = performance_history + [current_performance]
            
            # STEP 4: Extract topic-level scores from question results
            topic_scores = self._extract_topic_scores(grading_result["question_results"])
            
            # STEP 5: Generate personalized recommendations WITH question results
            recommendations = await self.recommendation_service.generate_recommendations(
                performance_history=full_history,
                topic_scores=topic_scores,
                question_results=grading_result["question_results"]  # NEW: Pass actual questions
            )
            
            logger.info(
                f"Recommendations generated for {student_id}: "
                f"{len(recommendations['topic_recommendations'])} topics"
            )
            
            # STEP 6: Build comprehensive response
            return {
                "submission_id": submission_id,
                "student_id": student_id,
                "submitted_at": grading_result["graded_at"],
                
                # Grading Results
                "grading": {
                    "total_points": grading_result["total_points"],
                    "max_points": grading_result["max_points"],
                    "percentage": grading_result["percentage"],
                    "grade_letter": grading_result["grade_letter"],
                    "overall_feedback": grading_result["overall_feedback"]
                },
                
                # Question-by-Question Results
                "question_results": grading_result["question_results"],
                
                # Performance Analysis
                "performance_analysis": {
                    "current_score": grading_result["percentage"],
                    "topic": current_performance["topic"],
                    "strengths": recommendations["strengths"],
                    "areas_for_improvement": recommendations["study_plan"]["skill_building"]["topics"],
                    "urgent_review_needed": recommendations["study_plan"]["urgent_review"]["topics"]
                },
                
                # Personalized Recommendations
                "recommendations": {
                    "priority_topics": recommendations["topic_recommendations"],
                    "study_plan": recommendations["study_plan"],
                    "trends": recommendations["trends"],
                    "next_steps": self._generate_next_steps(recommendations, grading_result)
                },
                
                # AI Insights
                "ai_insights": {
                    "explanation": recommendations["llm_explanation"],
                    "motivational_message": recommendations["motivational_message"]
                },
                
                # Metadata
                "metadata": {
                    "quiz_id": quiz_data.get("quiz_id"),
                    "course_id": quiz_data.get("generation_metadata", {}).get("course_id"),
                    "week_number": quiz_data.get("generation_metadata", {}).get("week_number"),
                    "total_submissions": len(full_history)
                }
            }
            
        except Exception as e:
            logger.error(f"Quiz submission processing failed: {e}", exc_info=True)
            raise
    
    def _extract_topic_scores(self, question_results: List[Dict]) -> Dict[str, float]:
        """
        Extract normalized topic scores from question results.
        Groups by question type for topic mastery analysis.
        """
        topic_scores = {}
        
        # Group by question type
        for result in question_results:
            q_type = result["question_type"]
            if result["max_points"] > 0:
                score = result["awarded_points"] / result["max_points"]
                topic_scores[q_type] = topic_scores.get(q_type, [])
                topic_scores[q_type].append(score)
        
        # Average scores per type
        return {
            topic: sum(scores) / len(scores)
            for topic, scores in topic_scores.items()
        }
    
    def _generate_next_steps(
        self,
        recommendations: Dict,
        grading_result: Dict
    ) -> List[str]:
        """Generate actionable next steps for the student."""
        next_steps = []
        
        percentage = grading_result["percentage"]
        urgent_topics = recommendations["study_plan"]["urgent_review"]["topics"]
        improvement_topics = recommendations["study_plan"]["skill_building"]["topics"]
        
        # Based on performance level
        if percentage >= 90:
            next_steps.append("Excellent work! Challenge yourself with advanced material.")
            if recommendations["study_plan"]["advancement"]["topics"]:
                next_steps.append(
                    f" Ready to advance in: {', '.join(recommendations['study_plan']['advancement']['topics'][:2])}"
                )
        elif percentage >= 70:
            next_steps.append(" Good progress! Focus on consistency.")
            if improvement_topics:
                next_steps.append(
                    f" Strengthen your understanding of: {', '.join(improvement_topics[:2])}"
                )
        else:
            next_steps.append(" Review the fundamentals to build a stronger foundation.")
            if urgent_topics:
                next_steps.append(
                    f" Priority review needed for: {', '.join(urgent_topics[:2])}"
                )
        
        # Study time recommendations
        total_study_hours = (
            recommendations["study_plan"]["urgent_review"].get("suggested_hours", 0) +
            recommendations["study_plan"]["skill_building"].get("suggested_hours", 0)
        )
        
        if total_study_hours > 0:
            next_steps.append(
                f" Recommended study time this week: {int(total_study_hours)} hours"
            )
        
        # Specific action items
        if improvement_topics:
            next_steps.append(
                f"Focus areas: Review course materials for {improvement_topics[0]}"
            )
        
        next_steps.append(" Practice similar questions to reinforce your learning")
        
        return next_steps
    
    async def get_student_progress_summary(
        self,
        student_id: str,
        performance_history: List[Dict]
    ) -> Dict:
        """
        Generate overall progress summary for a student.
        Useful for dashboards and progress tracking.
        """
        try:
            if not performance_history:
                return {
                    "student_id": student_id,
                    "message": "No performance history available yet",
                    "total_submissions": 0
                }
            
            # Calculate overall metrics
            total_submissions = len(performance_history)
            average_score = sum(p["percentage"] for p in performance_history) / total_submissions
            
            # Get latest performance
            latest = performance_history[-1]
            
            # Track improvement over time
            if total_submissions >= 2:
                recent_avg = sum(p["percentage"] for p in performance_history[-3:]) / min(3, total_submissions)
                early_avg = sum(p["percentage"] for p in performance_history[:3]) / min(3, total_submissions)
                improvement = recent_avg - early_avg
            else:
                improvement = 0
            
            # Generate recommendations based on full history
            topic_scores = {}
            for record in performance_history:
                topic = record["topic"]
                score = record["percentage"] / 100  # Normalize to 0-1
                topic_scores[topic] = score
            
            recommendations = await self.recommendation_service.generate_recommendations(
                performance_history=performance_history,
                topic_scores=topic_scores
            )
            
            return {
                "student_id": student_id,
                "summary": {
                    "total_submissions": total_submissions,
                    "average_score": round(average_score, 2),
                    "latest_score": round(latest["percentage"], 2),
                    "improvement_trend": "improving" if improvement > 5 else "stable" if improvement > -5 else "declining",
                    "improvement_points": round(improvement, 2)
                },
                "strengths": recommendations["strengths"],
                "areas_for_improvement": recommendations["study_plan"]["skill_building"]["topics"],
                "study_plan": recommendations["study_plan"],
                "motivation": recommendations["motivational_message"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Progress summary generation failed: {e}", exc_info=True)
            raise