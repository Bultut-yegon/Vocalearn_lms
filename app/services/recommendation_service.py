# from __future__ import annotations
# from dataclasses import dataclass, asdict
# from typing import List, Dict, Any, Optional, Callable
# from collections import defaultdict, deque
# import statistics
# import logging
# from datetime import datetime
# import math

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)


# @dataclass
# class TopicInfo:
#     topic: str
#     score: float
#     performance_level: str
#     priority: Optional[str] = None


# @dataclass
# class Recommendation:
#     topic: str
#     priority: str
#     current_score: float
#     target_score: float
#     action_items: List[str]
#     resources: List[Dict[str, str]]
#     estimated_study_hours: int


# @dataclass
# class StudySession:
#     topic: str
#     sessions_per_week: int
#     minutes_per_session: int
#     focus_areas: List[str]


# @dataclass
# class StrengthArea:
#     topic: str
#     score: float
#     performance_level: str
#     trend: str
#     recognition: str
#     next_steps: List[str]


# class RecommendationService:
#     """
#     Recommendation service for generating targeted study suggestions
#     from student performance history and topic scores.
#     """

#     def __init__(
#         self,
#         performance_threshold: float = 70.0,
#         strength_threshold: float = 85.0,
#         weakness_threshold: float = 60.0,
#         target_score: float = 75.0,
#         resource_provider: Optional[Callable[[str], List[Dict[str, str]]]] = None,
#     ):
#         """
#         resource_provider: optional callable(topic) -> list of resource dicts.
#         Allows injecting an external resource lookup (DB, search index, LLM).
#         """
#         self.performance_threshold = float(performance_threshold)
#         self.strength_threshold = float(strength_threshold)
#         self.weakness_threshold = float(weakness_threshold)
#         self.target_score = float(target_score)
#         self.resource_provider = resource_provider
#         # small cache to avoid repeated heavy operations (in-memory; replace with Redis if needed)
#         self._cache: Dict[str, Any] = {}

#     # Public API
#     def generate_recommendations(
#         self,
#         performance_history: List[Dict[str, Any]],
#         topic_scores: Dict[str, float],
#     ) -> Dict[str, Any]:
#         """
#         Return a structured recommendation payload.
#         """
#         logger.debug("Generating recommendations")

#         topic_analysis = self._analyze_topics(topic_scores)
#         performance_trends = self._analyze_performance_trends(performance_history)

#         weak_topics = topic_analysis["weak_topics"]
#         strong_topics = topic_analysis["strong_topics"]

#         recommendations = self._generate_topic_recommendations(
#             weak_topics, strong_topics, performance_trends
#         )

#         study_plan = self._generate_study_plan(weak_topics, performance_trends)

#         strengths = self._identify_strengths(strong_topics, performance_trends)

#         motivational_message = self._generate_motivational_message(
#             topic_analysis, performance_trends
#         )

#         return {
#             "summary": {
#                 "overall_performance": topic_analysis["average_score"],
#                 "performance_trend": performance_trends["trend"],
#                 "total_topics_assessed": len(topic_scores),
#                 "weak_areas_count": len(weak_topics),
#                 "strong_areas_count": len(strong_topics),
#                 "total_assessments": performance_trends.get("total_assessments", 0),
#             },
#             "weak_topics": [asdict(t) for t in weak_topics],
#             "strong_topics": [asdict(t) for t in strong_topics],
#             "recommendations": [asdict(r) for r in recommendations],
#             "study_plan": study_plan,
#             "strengths": {"message": strengths["message"], "areas": [asdict(a) for a in strengths["areas"]]},
#             "performance_trends": performance_trends,
#             "motivational_message": motivational_message,
#         }


#     # Topic analysis
#     def _analyze_topics(self, topic_scores: Dict[str, float]) -> Dict[str, Any]:
#         """
#         Produce weak/strong topic lists, sorted and enriched with levels/priorities.
#         """
#         logger.debug("Analyzing topics")
#         if not topic_scores:
#             return {"weak_topics": [], "strong_topics": [], "average_score": 0.0}

#         weak_topics: List[TopicInfo] = []
#         strong_topics: List[TopicInfo] = []

#         for topic, raw_score in topic_scores.items():
#             score = float(raw_score) if raw_score is not None else 0.0
#             perf_level = self._get_performance_level(score)

#             if score < self.weakness_threshold:
#                 weak_topics.append(
#                     TopicInfo(
#                         topic=topic,
#                         score=round(score, 2),
#                         performance_level=perf_level,
#                         priority=self._calculate_priority(score),
#                     )
#                 )
#             elif score >= self.strength_threshold:
#                 strong_topics.append(
#                     TopicInfo(
#                         topic=topic,
#                         score=round(score, 2),
#                         performance_level=perf_level,
#                     )
#                 )

#         weak_topics.sort(key=lambda x: x.score)  # ascending: worst first
#         strong_topics.sort(key=lambda x: x.score, reverse=True)  # best first

#         avg = 0.0
#         if topic_scores:
#             avg = sum(float(s or 0) for s in topic_scores.values()) / len(topic_scores)

#         return {"weak_topics": weak_topics, "strong_topics": strong_topics, "average_score": round(avg, 2)}


#     # Performance trends
#     def _analyze_performance_trends(self, performance_history: List[Dict[str, Any]]) -> Dict[str, Any]:
#         """
#         performance_history: list of dicts with keys: score, max_score (optional), topic (optional), timestamp (optional)
#         """
#         logger.debug("Analyzing performance trends")
#         if not performance_history:
#             return {
#                 "trend": "insufficient_data",
#                 "improvement_rate": 0.0,
#                 "consistency_score": 0.0,
#                 "recent_performance": 0.0,
#                 "total_assessments": 0,
#                 "topic_patterns": {},
#             }

#         # normalize input: compute percentage and sort by timestamp if available
#         processed = []
#         for rec in performance_history:
#             score = float(rec.get("score", 0) or 0)
#             max_score = float(rec.get("max_score", 1) or 1)
#             percentage = (score / max_score * 100) if max_score > 0 else 0.0
#             ts = rec.get("timestamp")
#             # try to accept common timestamp types
#             if isinstance(ts, (int, float)):
#                 ts_val = float(ts)
#             elif isinstance(ts, str):
#                 try:
#                     ts_val = float(datetime.fromisoformat(ts).timestamp())
#                 except Exception:
#                     ts_val = None
#             elif isinstance(ts, datetime):
#                 ts_val = ts.timestamp()
#             else:
#                 ts_val = None
#             processed.append({"percentage": percentage, "topic": rec.get("topic", "Unknown"), "ts": ts_val})

#         # sort by timestamp if present; otherwise keep existing order
#         processed.sort(key=lambda x: (x["ts"] is None, x["ts"] if x["ts"] is not None else 0))

#         scores = [p["percentage"] for p in processed]

#         trend = self._calculate_trend(scores)

#         improvement_rate = 0.0
#         if len(scores) >= 2:
#             # use moving-window averages: last 3 vs first 3 (robust even when shorter)
#             n = min(3, len(scores))
#             recent_avg = sum(scores[-n:]) / n
#             older_avg = sum(scores[:n]) / n
#             improvement_rate = round(recent_avg - older_avg, 2)

#         consistency_score = 0.0
#         if len(scores) >= 2:
#             try:
#                 std_dev = statistics.pstdev(scores)  # population stdev reduces sample noise for small n
#                 consistency_score = max(0.0, round(100.0 - std_dev, 2))
#             except statistics.StatisticsError:
#                 consistency_score = 0.0

#         recent_n = min(5, len(scores))
#         recent_performance = round(sum(scores[-recent_n:]) / recent_n, 2) if scores else 0.0

#         topic_patterns = self._analyze_topic_patterns(processed)

#         return {
#             "trend": trend,
#             "improvement_rate": improvement_rate,
#             "consistency_score": consistency_score,
#             "recent_performance": recent_performance,
#             "total_assessments": len(scores),
#             "topic_patterns": topic_patterns,
#         }

#     def _calculate_trend(self, scores: List[float]) -> str:
#         """
#         More robust trend calculation:
#           - if <3 samples => 'insufficient_data'
#           - compute linear slope via simple least-squares normalized by range to determine improving/declining/stable
#         """
#         if len(scores) < 3:
#             return "insufficient_data"

#         # Normalize x to [0,1]
#         n = len(scores)
#         xs = [i / (n - 1) for i in range(n)]
#         ys = scores
#         x_mean = sum(xs) / n
#         y_mean = sum(ys) / n
#         numer = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
#         denom = sum((xs[i] - x_mean) ** 2 for i in range(n)) or 1e-9
#         slope = numer / denom  # units: perc per normalized-step

#         # convert slope to percent-per-sample roughly
#         slope_scaled = slope * (n - 1)

#         # thresholds tuned for reasonable sensitivity
#         if slope_scaled > 5.0:
#             return "improving"
#         elif slope_scaled < -5.0:
#             return "declining"
#         else:
#             return "stable"

#     def _analyze_topic_patterns(self, processed_history: List[Dict[str, Any]]) -> Dict[str, Any]:
#         """
#         processed_history: list of dicts with keys "percentage", "topic", "ts"
#         returns a dict topic -> {average_score, trend, attempts}
#         """
#         topic_performances: Dict[str, List[float]] = defaultdict(list)
#         # collect in chronological order
#         for rec in processed_history:
#             topic_performances[rec["topic"]].append(rec["percentage"])

#         patterns: Dict[str, Any] = {}
#         for topic, scores in topic_performances.items():
#             avg = round(sum(scores) / len(scores), 2) if scores else 0.0
#             trend = self._calculate_trend(scores) if len(scores) >= 3 else "stable"
#             patterns[topic] = {"average_score": avg, "trend": trend, "attempts": len(scores)}

#         return patterns

#     # Recommendations generation
#     def _generate_topic_recommendations(
#         self,
#         weak_topics: List[TopicInfo],
#         strong_topics: List[TopicInfo],
#         performance_trends: Dict[str, Any],
#     ) -> List[Recommendation]:
#         recs: List[Recommendation] = []
#         # recommend up to N weak topics (configurable)
#         max_recs = 5
#         for t in weak_topics[:max_recs]:
#             est_hours = self._estimate_study_hours(t.score, self.target_score)
#             rec = Recommendation(
#                 topic=t.topic,
#                 priority=t.priority or self._calculate_priority(t.score),
#                 current_score=round(t.score, 2),
#                 target_score=self.target_score,
#                 action_items=self._get_action_items(t.topic, t.score),
#                 resources=self._get_learning_resources(t.topic),
#                 estimated_study_hours=est_hours,
#             )
#             recs.append(rec)
#         return recs

#     def _get_action_items(self, topic: str, score: float) -> List[str]:
#         items: List[str] = []
#         s = float(score)
#         if s < 40:
#             items = [
#                 f"Review fundamentals of {topic}",
#                 f"Follow a structured intro course on {topic}",
#                 "Practice basic exercises daily (20-30 min)",
#                 "Ask for targeted tutoring on core concepts",
#             ]
#         elif s < 60:
#             items = [
#                 f"Work on applied problems for {topic}",
#                 "Solve graded exercises and compare solutions",
#                 "Identify and correct common mistakes",
#                 "Form or join a short study group for peer review",
#             ]
#         else:
#             items = [
#                 f"Attempt advanced problem sets in {topic}",
#                 "Practice past exam-style questions under timed conditions",
#                 f"Explain core {topic} concepts to a peer (teaching is learning)",
#             ]

#         items.extend(self._get_topic_specific_actions(topic))
#         return items

#     def _get_topic_specific_actions(self, topic: str) -> List[str]:
#         t = topic.lower()
#         if "plumb" in t:
#             return [
#                 "Practice hands-on pipe-fitting tasks in a workshop environment",
#                 "Study plumbing codes and standards",
#                 "Follow guided installation walkthroughs",
#             ]
#         elif "wir" in t or "electric" in t or "electr" in t:
#             return [
#                 "Work through circuit calculations and simulations",
#                 "Study relevant electrical code and safety rules",
#                 "Practice troubleshooting on sample circuits",
#             ]
#         elif "safety" in t:
#             return [
#                 "Review safety protocols and standard operating procedures",
#                 "Practice emergency response drills",
#                 "Read local regulatory guidelines and OSH summaries",
#             ]
#         else:
#             return ["Practice targeted problem-solving and review official docs"]

#     def _get_learning_resources(self, topic: str) -> List[Dict[str, str]]:
#         """
#         Return resources. If resource_provider is set, use it and fall back to defaults.
#         Each resource dict: {"type": "...", "title": "...", "description": "...", "url": "..."}
#         """
#         if self.resource_provider:
#             try:
#                 resources = self.resource_provider(topic)
#                 if resources:
#                     return resources
#             except Exception as exc:
#                 logger.exception("resource_provider failed: %s", exc)

#         # fallback defaults
#         t = topic.lower()
#         resources: List[Dict[str, str]] = []
#         if "plumb" in t:
#             resources.extend(
#                 [
#                     {"type": "Video", "title": "Plumbing Fundamentals", "description": "Intro to plumbing", "url": ""},
#                     {"type": "Manual", "title": "IPC - Plumbing Code", "description": "Reference manual", "url": ""},
#                 ]
#             )
#         elif "wir" in t or "electric" in t or "electr" in t:
#             resources.extend(
#                 [
#                     {"type": "Video", "title": "Electrical Wiring Basics", "description": "Circuit fundamentals", "url": ""},
#                     {"type": "Manual", "title": "NEC - Electrical Code", "description": "Standard reference", "url": ""},
#                 ]
#             )
#         else:
#             resources.extend(
#                 [
#                     {"type": "Video", "title": f"{topic} Tutorial Series", "description": f"Comprehensive {topic}", "url": ""},
#                     {"type": "Practice", "title": "Practice Exercises", "description": f"Hands-on exercises for {topic}", "url": ""},
#                 ]
#             )

#         resources.append({"type": "Assessment", "title": "Practice Quizzes", "description": f"Short quizzes for {topic}", "url": ""})
#         return resources

#     def _estimate_study_hours(self, current_score: float, target_score: float) -> int:
#         gap = max(0.0, float(target_score) - float(current_score))
#         # calibrated piecewise function
#         if gap <= 0:
#             return 2
#         if gap <= 10:
#             return 4
#         if gap <= 25:
#             return 8
#         if gap <= 40:
#             return 15
#         return 25

#     # Study plan & strengths
#     def _generate_study_plan(self, weak_topics: List[TopicInfo], performance_trends: Dict[str, Any]) -> Dict[str, Any]:
#         if not weak_topics:
#             return {"message": "No weak topics detected. Keep practicing to maintain performance.", "weekly_schedule": [], "goals": []}

#         weekly_schedule: List[Dict[str, Any]] = []
#         for topic in weak_topics[:3]:
#             hours = self._estimate_study_hours(topic.score, self.target_score)
#             # sessions roughly: 45-min sessions = hours/0.75 approx
#             sessions_per_week = min(4, max(1, math.ceil(hours / 3)))
#             minutes_per_session = 45
#             focus = self._get_action_items(topic.topic, topic.score)[:2]
#             weekly_schedule.append(StudySession(topic=topic.topic, sessions_per_week=sessions_per_week, minutes_per_session=minutes_per_session, focus_areas=focus))

#         goals = []
#         for t in weak_topics[:3]:
#             goals.append(
#                 {
#                     "topic": t.topic,
#                     "current_score": t.score,
#                     "target_score": self.target_score,
#                     "timeline_weeks": max(1, math.ceil(self._estimate_study_hours(t.score, self.target_score) / 3)),
#                 }
#             )

#         total_hours_per_week = sum((s.sessions_per_week * s.minutes_per_session) / 60.0 for s in weekly_schedule)
#         return {
#             "message": "Follow this weekly plan to systematically close skill gaps.",
#             "weekly_schedule": [asdict(s) for s in weekly_schedule],
#             "goals": goals,
#             "total_study_hours_per_week": round(total_hours_per_week, 2),
#         }

#     def _identify_strengths(self, strong_topics: List[TopicInfo], performance_trends: Dict[str, Any]) -> Dict[str, Any]:
#         if not strong_topics:
#             return {"message": "No strong topics identified yet.", "areas": []}

#         areas: List[StrengthArea] = []
#         for t in strong_topics:
#             topic_pattern = performance_trends.get("topic_patterns", {}).get(t.topic, {})
#             areas.append(
#                 StrengthArea(
#                     topic=t.topic,
#                     score=round(t.score, 2),
#                     performance_level=t.performance_level,
#                     trend=topic_pattern.get("trend", "stable"),
#                     recognition=self._get_strength_recognition(t.score),
#                     next_steps=self._get_advancement_suggestions(t.topic),
#                 )
#             )

#         return {"message": "These are your strong areas. Consider leveling up with advanced tasks.", "areas": areas}

#     def _get_strength_recognition(self, score: float) -> str:
#         s = float(score)
#         if s >= 95:
#             return "Outstanding mastery"
#         if s >= 90:
#             return "Excellent performance"
#         if s >= 85:
#             return "Very good"
#         return "Good"

#     def _get_advancement_suggestions(self, topic: str) -> List[str]:
#         base = [
#             f"Take on advanced projects in {topic}",
#             f"Mentor peers on {topic}",
#             f"Explore specialized applications of {topic}",
#         ]
#         t = topic.lower()
#         if "plumb" in t:
#             base.append("Consider advanced plumbing certifications")
#         if "wir" in t or "electr" in t:
#             base.append("Study industrial control / automation systems")
#         return base

#     # Messaging & labels
#     def _generate_motivational_message(self, topic_analysis: Dict[str, Any], performance_trends: Dict[str, Any]) -> str:
#         trend = performance_trends.get("trend", "insufficient_data")
#         avg_score = topic_analysis.get("average_score", 0.0)
#         parts = []
#         if trend == "improving":
#             parts.append("Great progress — your performance is improving.")
#         elif trend == "declining":
#             parts.append("Don't be discouraged — there are actionable steps to recover.")
#         elif trend == "stable":
#             parts.append("Performance is stable — focus on targeted improvement.")
#         else:
#             parts.append("Insufficient data to determine a trend — keep practicing and logging results.")

#         if avg_score >= 85:
#             parts.append("You're performing exceptionally well overall.")
#         elif avg_score >= 70:
#             parts.append("Good overall performance — focus on weak areas to improve further.")
#         elif avg_score >= 50:
#             parts.append("You're making progress; stay consistent and follow the study plan.")
#         else:
#             parts.append("This is a critical time; use focused practice and ask for help if needed.")

#         parts.append("Consistent practice and hands-on exercises will accelerate learning.")
#         return " ".join(parts)

#     # Utility helpers
#     def _get_performance_level(self, score: float) -> str:
#         s = float(score)
#         if s >= 90:
#             return "Excellent"
#         if s >= 80:
#             return "Very Good"
#         if s >= 70:
#             return "Good"
#         if s >= 60:
#             return "Satisfactory"
#         if s >= 50:
#             return "Needs Improvement"
#         return "Requires Significant Improvement"

#     def _calculate_priority(self, score: float) -> str:
#         s = float(score)
#         if s < 40:
#             return "Critical"
#         if s < 50:
#             return "High"
#         if s < 60:
#             return "Medium"
#         return "Low"

#     # Small util for clearing cache (in long-run app)
#     def clear_cache(self) -> None:
#         self._cache.clear()

# import logging
# from typing import Dict, List

# from app.models.recommendation_models import (
#     RecommendationRequest,
#     RecommendationResult
# )
# from app.services.llm_service import LLMService

# logger = logging.getLogger(__name__)


# class RecommendationService:

#     def __init__(self):
#         self.llm = LLMService()

#     async def generate_recommendations(self, data: RecommendationRequest) -> RecommendationResult:
#         try:
#             logger.info("Processing recommendation request...")

#             topic_scores = data.topic_scores
#             history = data.performance_history

#             # Trend Analysis 
#             trends = self._analyze_trends(history)

#             #Identify Weak & Strong Topics 
#             topic_recommendations = [
#                 t for t, score in topic_scores.items() if score < 60
#             ]

#             strengths = [
#                 t for t, score in topic_scores.items() if score > 80
#             ]

#             # Study Plan 
#             study_plan = {}
#             for t in topic_recommendations:
#                 study_plan[t] = {
#                     "priority_level": "high",
#                     "recommended_hours": 4,
#                     "actions": [
#                         "Review topic notes",
#                         "Solve practice problems",
#                         "Watch related tutorials",
#                         "Attempt previous quizzes"
#                     ]
#                 }

#             motivational_message = (
#                 "You're progressing well! Stay consistent and focus on improving the selected key areas."
#             )

#             #   LLM Explanation 
#             llm_text = await self.llm.generate_explanation(
#                 topic_recommendations, study_plan, strengths
#             )

#             result = RecommendationResult(
#                 topic_recommendations=topic_recommendations,
#                 study_plan=study_plan,
#                 strengths=strengths,
#                 trends=trends,
#                 motivational_message=motivational_message,
#                 llm_explanation=llm_text
#             )

#             logger.info("Recommendation generation completed successfully.")
#             return result

#         except Exception as e:
#             logger.error(f"Recommendation service failed: {e}")
#             raise e  # Handled in router

#     def _analyze_trends(self, history):
#         trends = {}
#         for record in history:
#             percentage = (record.score / record.max_score) * 100
#             trends.setdefault(record.topic, []).append(percentage)
#         return trends


# import numpy as np
# from typing import List, Dict, Tuple
# from sklearn.preprocessing import MinMaxScaler
# import os
# from openai import AsyncOpenAI
# from app.core.logging_config import logger

# class RecommendationService:
#     """
#     AI-powered recommendation system for TVET students.
#     Analyzes performance to suggest personalized learning paths.
#     """
    
#     def __init__(self):
#         self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#         self.weak_threshold = 0.6  # Below 60% = needs improvement
#         self.strong_threshold = 0.8  # Above 80% = strength
        
#     def calculate_performance_metrics(
#         self, 
#         performance_history: List[Dict]
#     ) -> Dict[str, float]:
#         """Calculate normalized scores and identify patterns."""
#         topic_performance = {}
        
#         for record in performance_history:
#             topic = record["topic"]
#             normalized_score = record["score"] / record["max_score"]
            
#             if topic not in topic_performance:
#                 topic_performance[topic] = []
#             topic_performance[topic].append(normalized_score)
        
#         # Average performance per topic
#         topic_averages = {
#             topic: np.mean(scores) 
#             for topic, scores in topic_performance.items()
#         }
        
#         return topic_averages
    
#     def identify_strengths_weaknesses(
#         self, 
#         topic_averages: Dict[str, float]
#     ) -> Tuple[List[str], List[str]]:
#         """Classify topics into strengths and weaknesses."""
#         strengths = [
#             topic for topic, score in topic_averages.items() 
#             if score >= self.strong_threshold
#         ]
        
#         weaknesses = [
#             topic for topic, score in topic_averages.items() 
#             if score < self.weak_threshold
#         ]
        
#         return strengths, weaknesses
    
#     def detect_trends(
#         self, 
#         performance_history: List[Dict]
#     ) -> Dict[str, str]:
#         """Detect if student is improving, declining, or stable."""
#         topic_trends = {}
#         topic_scores_timeline = {}
        
#         # Group scores by topic in chronological order
#         for record in performance_history:
#             topic = record["topic"]
#             normalized_score = record["score"] / record["max_score"]
            
#             if topic not in topic_scores_timeline:
#                 topic_scores_timeline[topic] = []
#             topic_scores_timeline[topic].append(normalized_score)
        
#         # Analyze trend for each topic
#         for topic, scores in topic_scores_timeline.items():
#             if len(scores) < 2:
#                 topic_trends[topic] = "insufficient_data"
#                 continue
                
#             # Simple linear trend detection
#             recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else np.mean(scores)
#             early_avg = np.mean(scores[:3]) if len(scores) >= 3 else scores[0]
            
#             if recent_avg > early_avg + 0.1:
#                 topic_trends[topic] = "improving"
#             elif recent_avg < early_avg - 0.1:
#                 topic_trends[topic] = "declining"
#             else:
#                 topic_trends[topic] = "stable"
        
#         return topic_trends
    
#     def generate_study_plan(
#         self,
#         weaknesses: List[str],
#         strengths: List[str],
#         trends: Dict[str, str],
#         topic_averages: Dict[str, float]
#     ) -> Dict[str, any]:
#         """Create a prioritized study plan."""
#         # Priority 1: Declining topics (urgent)
#         declining_topics = [
#             topic for topic, trend in trends.items() 
#             if trend == "declining"
#         ]
        
#         # Priority 2: Weak topics (needs improvement)
#         improvement_topics = [
#             topic for topic in weaknesses 
#             if topic not in declining_topics
#         ]
        
#         # Priority 3: Build on strengths (next level)
#         advancement_topics = [
#             topic for topic in strengths
#             if trends.get(topic) == "improving"
#         ]
        
#         study_plan = {
#             "urgent_review": {
#                 "topics": declining_topics,
#                 "reason": "Performance is declining - immediate attention needed",
#                 "suggested_hours": len(declining_topics) * 3
#             },
#             "skill_building": {
#                 "topics": improvement_topics,
#                 "reason": "Below mastery threshold - foundational work needed",
#                 "suggested_hours": len(improvement_topics) * 2
#             },
#             "advancement": {
#                 "topics": advancement_topics,
#                 "reason": "Strong foundation - ready for advanced concepts",
#                 "suggested_hours": len(advancement_topics) * 1.5
#             }
#         }
        
#         return study_plan
    
#     async def generate_llm_insights(
#         self,
#         strengths: List[str],
#         weaknesses: List[str],
#         trends: Dict[str, str],
#         topic_averages: Dict[str, float],
#         study_plan: Dict[str, any]
#     ) -> Tuple[str, str]:
#         """Use LLM to generate personalized explanation and motivation."""
        
#         # Prepare context for LLM
#         context = f"""
# You are an encouraging TVET (Technical and Vocational Education) instructor helping a student in wiring and plumbing trades.

# Student Performance Summary:
# - Strong Topics: {', '.join(strengths) if strengths else 'None yet'}
# - Topics Needing Work: {', '.join(weaknesses) if weaknesses else 'None'}
# - Performance Trends: {trends}
# - Topic Scores: {topic_averages}

# Study Plan:
# {study_plan}

# Generate:
# 1. A brief explanation (2-3 sentences) of their learning pattern
# 2. An encouraging motivational message (2-3 sentences) that's specific to their situation
# """

#         try:
#             response = await self.client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[
#                     {
#                         "role": "system", 
#                         "content": "You are a supportive TVET instructor. Be encouraging, specific, and practical. Focus on trades skills like wiring and plumbing."
#                     },
#                     {"role": "user", "content": context}
#                 ],
#                 temperature=0.7,
#                 max_tokens=300
#             )
            
#             llm_output = response.choices[0].message.content
            
#             # Split into explanation and motivation
#             parts = llm_output.split("\n\n")
#             explanation = parts[0] if len(parts) > 0 else llm_output
#             motivation = parts[1] if len(parts) > 1 else "Keep pushing forward! Every expert was once a beginner."
            
#             return explanation, motivation
            
#         except Exception as e:
#             logger.error(f"LLM generation failed: {e}")
#             # Fallback messages
#             explanation = "Your performance data shows areas of strength and opportunities for growth."
#             motivation = "Stay focused on your goals. Practical skills take time and consistent effort!"
#             return explanation, motivation
    
#     async def generate_recommendations(
#         self,
#         performance_history: List[Dict],
#         topic_scores: Dict[str, float]
#     ) -> Dict[str, any]:
#         """Main method to generate comprehensive recommendations."""
        
#         # Calculate metrics
#         topic_averages = self.calculate_performance_metrics(performance_history)
        
#         # Merge with provided topic_scores if available
#         if topic_scores:
#             topic_averages.update(topic_scores)
        
#         # Identify strengths and weaknesses
#         strengths, weaknesses = self.identify_strengths_weaknesses(topic_averages)
        
#         # Detect trends
#         trends = self.detect_trends(performance_history)
        
#         # Generate study plan
#         study_plan = self.generate_study_plan(
#             weaknesses, strengths, trends, topic_averages
#         )
        
#         # Get LLM insights
#         explanation, motivation = await self.generate_llm_insights(
#             strengths, weaknesses, trends, topic_averages, study_plan
#         )
        
#         # Compile topic recommendations (prioritized list)
#         topic_recommendations = (
#             study_plan["urgent_review"]["topics"] +
#             study_plan["skill_building"]["topics"] +
#             study_plan["advancement"]["topics"]
#         )
        
#         return {
#             "topic_recommendations": topic_recommendations,
#             "study_plan": study_plan,
#             "strengths": strengths,
#             "trends": trends,
#             "motivational_message": motivation,
#             "llm_explanation": explanation
#         }





# import numpy as np
# from typing import List, Dict, Tuple
# from sklearn.preprocessing import MinMaxScaler
# import os
# import httpx
# from app.core.logging_config import logger

# class RecommendationService:
#     """
#     AI-powered recommendation system for TVET students.
#     Analyzes performance to suggest personalized learning paths.
#     """
    
#     def __init__(self):
#         self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
#         self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
#         self.weak_threshold = 0.6  # Below 60% = needs improvement
#         self.strong_threshold = 0.8  # Above 80% = strength
        
#     def calculate_performance_metrics(
#         self, 
#         performance_history: List[Dict]
#     ) -> Dict[str, float]:
#         """Calculate normalized scores and identify patterns."""
#         topic_performance = {}
        
#         for record in performance_history:
#             topic = record["topic"]
#             normalized_score = record["score"] / record["max_score"]
            
#             if topic not in topic_performance:
#                 topic_performance[topic] = []
#             topic_performance[topic].append(normalized_score)
        
#         # Average performance per topic
#         topic_averages = {
#             topic: np.mean(scores) 
#             for topic, scores in topic_performance.items()
#         }
        
#         return topic_averages
    
#     def identify_strengths_weaknesses(
#         self, 
#         topic_averages: Dict[str, float]
#     ) -> Tuple[List[str], List[str]]:
#         """Classify topics into strengths and weaknesses."""
#         strengths = [
#             topic for topic, score in topic_averages.items() 
#             if score >= self.strong_threshold
#         ]
        
#         weaknesses = [
#             topic for topic, score in topic_averages.items() 
#             if score < self.weak_threshold
#         ]
        
#         return strengths, weaknesses
    
#     def detect_trends(
#         self, 
#         performance_history: List[Dict]
#     ) -> Dict[str, str]:
#         """Detect if student is improving, declining, or stable."""
#         topic_trends = {}
#         topic_scores_timeline = {}
        
#         # Group scores by topic in chronological order
#         for record in performance_history:
#             topic = record["topic"]
#             normalized_score = record["score"] / record["max_score"]
            
#             if topic not in topic_scores_timeline:
#                 topic_scores_timeline[topic] = []
#             topic_scores_timeline[topic].append(normalized_score)
        
#         # Analyze trend for each topic
#         for topic, scores in topic_scores_timeline.items():
#             if len(scores) < 2:
#                 topic_trends[topic] = "insufficient_data"
#                 continue
                
#             # Simple linear trend detection
#             recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else np.mean(scores)
#             early_avg = np.mean(scores[:3]) if len(scores) >= 3 else scores[0]
            
#             if recent_avg > early_avg + 0.1:
#                 topic_trends[topic] = "improving"
#             elif recent_avg < early_avg - 0.1:
#                 topic_trends[topic] = "declining"
#             else:
#                 topic_trends[topic] = "stable"
        
#         return topic_trends
    
#     def generate_study_plan(
#         self,
#         weaknesses: List[str],
#         strengths: List[str],
#         trends: Dict[str, str],
#         topic_averages: Dict[str, float]
#     ) -> Dict[str, any]:
#         """Create a prioritized study plan."""
#         # Priority 1: Declining topics (urgent)
#         declining_topics = [
#             topic for topic, trend in trends.items() 
#             if trend == "declining"
#         ]
        
#         # Priority 2: Weak topics (needs improvement)
#         improvement_topics = [
#             topic for topic in weaknesses 
#             if topic not in declining_topics
#         ]
        
#         # Priority 3: Build on strengths (next level)
#         advancement_topics = [
#             topic for topic in strengths
#             if trends.get(topic) == "improving"
#         ]
        
#         study_plan = {
#             "urgent_review": {
#                 "topics": declining_topics,
#                 "reason": "Performance is declining - immediate attention needed",
#                 "suggested_hours": len(declining_topics) * 3
#             },
#             "skill_building": {
#                 "topics": improvement_topics,
#                 "reason": "Below mastery threshold - foundational work needed",
#                 "suggested_hours": len(improvement_topics) * 2
#             },
#             "advancement": {
#                 "topics": advancement_topics,
#                 "reason": "Strong foundation - ready for advanced concepts",
#                 "suggested_hours": len(advancement_topics) * 1.5
#             }
#         }
        
#         return study_plan
    
#     async def generate_llm_insights(
#         self,
#         strengths: List[str],
#         weaknesses: List[str],
#         trends: Dict[str, str],
#         topic_averages: Dict[str, float],
#         study_plan: Dict[str, any]
#     ) -> Tuple[str, str]:
#         """Use LLM to generate personalized explanation and motivation."""
        
#         # Prepare context for LLM
#         system_prompt = "You are a supportive TVET instructor. Be encouraging, specific, and practical. Focus on trades skills like wiring and plumbing."
        
#         user_prompt = f"""Student Performance Summary:
# - Strong Topics: {', '.join(strengths) if strengths else 'None yet'}
# - Topics Needing Work: {', '.join(weaknesses) if weaknesses else 'None'}
# - Performance Trends: {trends}
# - Topic Scores: {topic_averages}

# Study Plan:
# {study_plan}

# Generate:
# 1. A brief explanation (2-3 sentences) of their learning pattern
# 2. An encouraging motivational message (2-3 sentences) that's specific to their situation

# Format your response with the explanation first, then a blank line, then the motivational message."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     f"{self.ollama_url}/api/generate",
#                     json={
#                         "model": self.model,
#                         "prompt": f"{system_prompt}\n\n{user_prompt}",
#                         "stream": False,
#                         "options": {
#                             "temperature": 0.7,
#                             "num_predict": 300
#                         }
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     llm_output = result.get("response", "")
                    
#                     # Split into explanation and motivation
#                     parts = llm_output.split("\n\n")
#                     explanation = parts[0].strip() if len(parts) > 0 else llm_output
#                     motivation = parts[1].strip() if len(parts) > 1 else "Keep pushing forward! Every expert was once a beginner."
                    
#                     return explanation, motivation
#                 else:
#                     logger.error(f"Ollama API error: {response.status_code}")
#                     raise Exception(f"Ollama returned status {response.status_code}")
            
#         except Exception as e:
#             logger.error(f"LLM generation failed: {e}")
#             # Fallback messages
#             explanation = "Your performance data shows areas of strength and opportunities for growth."
#             motivation = "Stay focused on your goals. Practical skills take time and consistent effort!"
#             return explanation, motivation
    
#     async def generate_recommendations(
#         self,
#         performance_history: List[Dict],
#         topic_scores: Dict[str, float]
#     ) -> Dict[str, any]:
#         """Main method to generate comprehensive recommendations."""
        
#         # Calculate metrics
#         topic_averages = self.calculate_performance_metrics(performance_history)
        
#         # Merge with provided topic_scores if available
#         if topic_scores:
#             topic_averages.update(topic_scores)
        
#         # Identify strengths and weaknesses
#         strengths, weaknesses = self.identify_strengths_weaknesses(topic_averages)
        
#         # Detect trends
#         trends = self.detect_trends(performance_history)
        
#         # Generate study plan
#         study_plan = self.generate_study_plan(
#             weaknesses, strengths, trends, topic_averages
#         )
        
#         # Get LLM insights
#         explanation, motivation = await self.generate_llm_insights(
#             strengths, weaknesses, trends, topic_averages, study_plan
#         )
        
#         # Compile topic recommendations (prioritized list)
#         topic_recommendations = (
#             study_plan["urgent_review"]["topics"] +
#             study_plan["skill_building"]["topics"] +
#             study_plan["advancement"]["topics"]
#         )
        
#         return {
#             "topic_recommendations": topic_recommendations,
#             "study_plan": study_plan,
#             "strengths": strengths,
#             "trends": trends,
#             "motivational_message": motivation,
#             "llm_explanation": explanation
#         }



# Latest

import numpy as np
from typing import List, Dict, Tuple
from sklearn.preprocessing import MinMaxScaler
import os
import httpx
from app.core.logging_config import logger
from datetime import datetime
import json
from typing import Optional

class RecommendationService:
    """
    AI-powered recommendation system for TVET students.
    Analyzes performance to suggest personalized learning paths.
    """
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")  # Fast & free on Groq
        self.weak_threshold = 0.6  # Below 60% = needs improvement
        self.strong_threshold = 0.8  # Above 80% = strength
        
    def calculate_performance_metrics(
        self, 
        performance_history: List[Dict]
    ) -> Dict[str, float]:
        """Calculate normalized scores and identify patterns."""
        topic_performance = {}
        
        for record in performance_history:
            topic = record["topic"]
            normalized_score = record["score"] / record["max_score"]
            
            if topic not in topic_performance:
                topic_performance[topic] = []
            topic_performance[topic].append(normalized_score)
        
        # Average performance per topic
        topic_averages = {
            topic: np.mean(scores) 
            for topic, scores in topic_performance.items()
        }
        
        return topic_averages
    
    def identify_strengths_weaknesses(
        self, 
        topic_averages: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """Classify topics into strengths and weaknesses."""
        strengths = [
            topic for topic, score in topic_averages.items() 
            if score >= self.strong_threshold
        ]
        
        weaknesses = [
            topic for topic, score in topic_averages.items() 
            if score < self.weak_threshold
        ]
        
        return strengths, weaknesses
    
    def detect_trends(
        self, 
        performance_history: List[Dict]
    ) -> Dict[str, str]:
        """Detect if student is improving, declining, or stable."""
        topic_trends = {}
        topic_scores_timeline = {}
        
        # Group scores by topic in chronological order
        for record in performance_history:
            topic = record["topic"]
            normalized_score = record["score"] / record["max_score"]
            
            if topic not in topic_scores_timeline:
                topic_scores_timeline[topic] = []
            topic_scores_timeline[topic].append(normalized_score)
        
        # Analyze trend for each topic
        for topic, scores in topic_scores_timeline.items():
            if len(scores) < 2:
                topic_trends[topic] = "insufficient_data"
                continue
                
            # Simple linear trend detection
            recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else np.mean(scores)
            early_avg = np.mean(scores[:3]) if len(scores) >= 3 else scores[0]
            
            if recent_avg > early_avg + 0.1:
                topic_trends[topic] = "improving"
            elif recent_avg < early_avg - 0.1:
                topic_trends[topic] = "declining"
            else:
                topic_trends[topic] = "stable"
        
        return topic_trends
    
    def generate_study_plan(
        self,
        weaknesses: List[str],
        strengths: List[str],
        trends: Dict[str, str],
        topic_averages: Dict[str, float]
    ) -> Dict[str, any]:
        """Create a prioritized study plan."""
        # Priority 1: Declining topics (urgent)
        declining_topics = [
            topic for topic, trend in trends.items() 
            if trend == "declining"
        ]
        
        # Priority 2: Weak topics (needs improvement)
        improvement_topics = [
            topic for topic in weaknesses 
            if topic not in declining_topics
        ]
        
        # Priority 3: Build on strengths (next level)
        advancement_topics = [
            topic for topic in strengths
            if trends.get(topic) == "improving"
        ]
        
        study_plan = {
            "urgent_review": {
                "topics": declining_topics,
                "reason": "Performance is declining - immediate attention needed",
                "suggested_hours": len(declining_topics) * 3
            },
            "skill_building": {
                "topics": improvement_topics,
                "reason": "Below mastery threshold - foundational work needed",
                "suggested_hours": len(improvement_topics) * 2
            },
            "advancement": {
                "topics": advancement_topics,
                "reason": "Strong foundation - ready for advanced concepts",
                "suggested_hours": len(advancement_topics) * 1.5
            }
        }
        
        return study_plan
    
    async def generate_llm_insights(
        self,
        strengths: List[str],
        weaknesses: List[str],
        trends: Dict[str, str],
        topic_averages: Dict[str, float],
        study_plan: Dict[str, any]
    ) -> Tuple[str, str]:
        """Use LLM to generate personalized explanation and motivation."""
        
        system_prompt = "You are a supportive TVET instructor. Be encouraging, specific, and practical. Focus on trades skills like wiring and plumbing."
        
        user_prompt = f"""Student Performance Summary:
- Strong Topics: {', '.join(strengths) if strengths else 'None yet'}
- Topics Needing Work: {', '.join(weaknesses) if weaknesses else 'None'}
- Performance Trends: {trends}
- Topic Scores: {topic_averages}

Study Plan:
{study_plan}

Generate two parts:
1. A brief explanation (2-3 sentences) of their learning pattern
2. An encouraging motivational message (2-3 sentences) specific to their situation

Separate the two parts with a blank line."""

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
                        "max_tokens": 300
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    llm_output = result["choices"][0]["message"]["content"]
                    
                    # Split into explanation and motivation
                    parts = llm_output.split("\n\n")
                    explanation = parts[0].strip() if len(parts) > 0 else llm_output
                    motivation = parts[1].strip() if len(parts) > 1 else "Keep pushing forward! Every expert was once a beginner."
                    
                    return explanation, motivation
                else:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    raise Exception(f"Groq returned status {response.status_code}")
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Fallback messages
            explanation = "Your performance data shows areas of strength and opportunities for growth."
            motivation = "Stay focused on your goals. Practical skills take time and consistent effort!"
            return explanation, motivation
    
    async def generate_recommendations(
        self,
        performance_history: List[Dict],
        topic_scores: Dict[str, float]
    ) -> Dict[str, any]:
        """Main method to generate comprehensive recommendations."""
        
        # Calculate metrics
        topic_averages = self.calculate_performance_metrics(performance_history)
        
        # Merge with provided topic_scores if available
        if topic_scores:
            topic_averages.update(topic_scores)
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self.identify_strengths_weaknesses(topic_averages)
        
        # Detect trends
        trends = self.detect_trends(performance_history)
        
        # Generate study plan
        study_plan = self.generate_study_plan(
            weaknesses, strengths, trends, topic_averages
        )
        
        # Get LLM insights
        explanation, motivation = await self.generate_llm_insights(
            strengths, weaknesses, trends, topic_averages, study_plan
        )
        
        # Compile topic recommendations (prioritized list)
        topic_recommendations = (
            study_plan["urgent_review"]["topics"] +
            study_plan["skill_building"]["topics"] +
            study_plan["advancement"]["topics"]
        )
        
        return {
            "topic_recommendations": topic_recommendations,
            "study_plan": study_plan,
            "strengths": strengths,
            "trends": trends,
            "motivational_message": motivation,
            "llm_explanation": explanation
        }

    def track_improvement(self,student_id: str,current_metrics: Dict[str, float],previous_metrics: Optional[Dict[str, float]] = None) -> Dict[str, any]:

        """
        Track student improvement over time.
        Compares current performance against previous assessment.
        """
        if not previous_metrics:
            return {
            "student_id": student_id,
            "baseline_established": True,
            "message": "Baseline performance recorded. Next assessment will show progress.",
            "current_metrics": current_metrics,
            "timestamp": datetime.now().isoformat()
        }
    
        improvements = {}
        declines = {}
        stable = {}
    
        for topic, current_score in current_metrics.items():
            if topic in previous_metrics:
                previous_score = previous_metrics[topic]
                change = current_score - previous_score
                change_percent = (change / previous_score * 100) if previous_score > 0 else 0
            
            if change > 0.05:  # 5% improvement threshold
                improvements[topic] = {
                    "previous": round(previous_score, 2),
                    "current": round(current_score, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 1)
                }
            elif change < -0.05:  # 5% decline threshold
                declines[topic] = {
                    "previous": round(previous_score, 2),
                    "current": round(current_score, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 1)
                }
            else:
                stable[topic] = {
                    "score": round(current_score, 2)
                }
    
    # New topics that weren't in previous assessment
        new_topics = {
        topic: round(score, 2) 
        for topic, score in current_metrics.items() 
        if topic not in previous_metrics
        }
    
    # Overall progress indicator
        if previous_metrics:
            avg_previous = np.mean(list(previous_metrics.values()))
            avg_current = np.mean(list(current_metrics.values()))
            overall_change = avg_current - avg_previous
        
            if overall_change > 0.05:
                progress_status = "improving"
            elif overall_change < -0.05:
                progress_status = "declining"
            else:
                progress_status = "stable"
        else:
            progress_status = "baseline"
    
        return {
        "student_id": student_id,
        "timestamp": datetime.now().isoformat(),
        "progress_status": progress_status,
        "improvements": improvements,
        "declines": declines,
        "stable_topics": stable,
        "new_topics": new_topics,
        "summary": {
            "topics_improved": len(improvements),
            "topics_declined": len(declines),
            "topics_stable": len(stable),
            "new_topics_count": len(new_topics)
        }
    }


    
    def generate_report_data(self,student_id: str,student_name: str,recommendations: Dict[str, any],improvement_tracking: Optional[Dict[str, any]] = None) -> Dict[str, any]:
            
        """
        Generate structured report data for export.
        """
        report = {
        "report_metadata": {
            "student_id": student_id,
            "student_name": student_name,
            "generated_at": datetime.now().isoformat(),
            "report_type": "Performance Analysis & Recommendations"
        },
        "performance_summary": {
            "strengths": recommendations.get("strengths", []),
            "areas_for_improvement": recommendations["study_plan"]["skill_building"]["topics"],
            "urgent_attention_needed": recommendations["study_plan"]["urgent_review"]["topics"],
            "ready_for_advancement": recommendations["study_plan"]["advancement"]["topics"]
        },
        "detailed_analysis": {
            "topic_trends": recommendations.get("trends", {}),
            "llm_insights": {
                "explanation": recommendations.get("llm_explanation", ""),
                "motivation": recommendations.get("motivational_message", "")
            }
        },
        "study_plan": recommendations.get("study_plan", {}),
        "recommended_actions": recommendations.get("topic_recommendations", [])
    }
    
    # Add improvement tracking if available
        if improvement_tracking:
            report["progress_tracking"] = improvement_tracking
    
        return report


    # Add these methods to your RecommendationService class






    