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

# import numpy as np
# from typing import List, Dict, Tuple
# from sklearn.preprocessing import MinMaxScaler
# import os
# import httpx
# from app.core.logging_config import logger
# from datetime import datetime
# import json
# from typing import Optional
# from app.services.document_service import DocumentProcessingService


# class RecommendationService:
#     """
#     AI-powered recommendation system for TVET students.
#     Analyzes performance to suggest personalized learning paths.
#     """
    
#     def __init__(self):
#         self.groq_api_key = os.getenv("GROQ_API_KEY")
#         self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")  # Fast & free on Groq
#         self.weak_threshold = 0.6  # Below 60% = needs improvement
#         self.strong_threshold = 0.8  # Above 80% = strength
#         self.doc_service = DocumentProcessingService()
        
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
        
#         system_prompt = "You are a supportive TVET instructor. Be encouraging, specific, and practical. Focus on trades skills like wiring and plumbing."
        
#         user_prompt = f"""Student Performance Summary:
# - Strong Topics: {', '.join(strengths) if strengths else 'None yet'}
# - Topics Needing Work: {', '.join(weaknesses) if weaknesses else 'None'}
# - Performance Trends: {trends}
# - Topic Scores: {topic_averages}

# Study Plan:
# {study_plan}

# Generate two parts:
# 1. A brief explanation (2-3 sentences) of their learning pattern
# 2. An encouraging motivational message (2-3 sentences) specific to their situation

# Separate the two parts with a blank line."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 300
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     llm_output = result["choices"][0]["message"]["content"]
                    
#                     # Split into explanation and motivation
#                     parts = llm_output.split("\n\n")
#                     explanation = parts[0].strip() if len(parts) > 0 else llm_output
#                     motivation = parts[1].strip() if len(parts) > 1 else "Keep pushing forward! Every expert was once a beginner."
                    
#                     return explanation, motivation
#                 else:
#                     logger.error(f"Groq API error: {response.status_code} - {response.text}")
#                     raise Exception(f"Groq returned status {response.status_code}")
            
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

#     def track_improvement(self,student_id: str,current_metrics: Dict[str, float],previous_metrics: Optional[Dict[str, float]] = None) -> Dict[str, any]:

#         """
#         Track student improvement over time.
#         Compares current performance against previous assessment.
#         """
#         if not previous_metrics:
#             return {
#             "student_id": student_id,
#             "baseline_established": True,
#             "message": "Baseline performance recorded. Next assessment will show progress.",
#             "current_metrics": current_metrics,
#             "timestamp": datetime.now().isoformat()
#         }
    
#         improvements = {}
#         declines = {}
#         stable = {}
    
#         for topic, current_score in current_metrics.items():
#             if topic in previous_metrics:
#                 previous_score = previous_metrics[topic]
#                 change = current_score - previous_score
#                 change_percent = (change / previous_score * 100) if previous_score > 0 else 0
            
#             if change > 0.05:  # 5% improvement threshold
#                 improvements[topic] = {
#                     "previous": round(previous_score, 2),
#                     "current": round(current_score, 2),
#                     "change": round(change, 2),
#                     "change_percent": round(change_percent, 1)
#                 }
#             elif change < -0.05:  # 5% decline threshold
#                 declines[topic] = {
#                     "previous": round(previous_score, 2),
#                     "current": round(current_score, 2),
#                     "change": round(change, 2),
#                     "change_percent": round(change_percent, 1)
#                 }
#             else:
#                 stable[topic] = {
#                     "score": round(current_score, 2)
#                 }
    
#     # New topics that weren't in previous assessment
#         new_topics = {
#         topic: round(score, 2) 
#         for topic, score in current_metrics.items() 
#         if topic not in previous_metrics
#         }
    
#     # Overall progress indicator
#         if previous_metrics:
#             avg_previous = np.mean(list(previous_metrics.values()))
#             avg_current = np.mean(list(current_metrics.values()))
#             overall_change = avg_current - avg_previous
        
#             if overall_change > 0.05:
#                 progress_status = "improving"
#             elif overall_change < -0.05:
#                 progress_status = "declining"
#             else:
#                 progress_status = "stable"
#         else:
#             progress_status = "baseline"
    
#         return {
#         "student_id": student_id,
#         "timestamp": datetime.now().isoformat(),
#         "progress_status": progress_status,
#         "improvements": improvements,
#         "declines": declines,
#         "stable_topics": stable,
#         "new_topics": new_topics,
#         "summary": {
#             "topics_improved": len(improvements),
#             "topics_declined": len(declines),
#             "topics_stable": len(stable),
#             "new_topics_count": len(new_topics)
#         }
#     }


    
#     def generate_report_data(self,student_id: str,student_name: str,recommendations: Dict[str, any],improvement_tracking: Optional[Dict[str, any]] = None) -> Dict[str, any]:
            
#         """
#         Generate structured report data for export.
#         """
#         report = {
#         "report_metadata": {
#             "student_id": student_id,
#             "student_name": student_name,
#             "generated_at": datetime.now().isoformat(),
#             "report_type": "Performance Analysis & Recommendations"
#         },
#         "performance_summary": {
#             "strengths": recommendations.get("strengths", []),
#             "areas_for_improvement": recommendations["study_plan"]["skill_building"]["topics"],
#             "urgent_attention_needed": recommendations["study_plan"]["urgent_review"]["topics"],
#             "ready_for_advancement": recommendations["study_plan"]["advancement"]["topics"]
#         },
#         "detailed_analysis": {
#             "topic_trends": recommendations.get("trends", {}),
#             "llm_insights": {
#                 "explanation": recommendations.get("llm_explanation", ""),
#                 "motivation": recommendations.get("motivational_message", "")
#             }
#         },
#         "study_plan": recommendations.get("study_plan", {}),
#         "recommended_actions": recommendations.get("topic_recommendations", [])
#     }
    
#     # Add improvement tracking if available
#         if improvement_tracking:
#             report["progress_tracking"] = improvement_tracking
    
#         return report

#     async def generate_recommendations_with_documents(self,student_id: str,performance_history: List[Dict],topic_scores: Dict[str, float],course: str) -> Dict:
#         """
#         Generate recommendations with document-specific study suggestions.
#         """
    
#         # Generate base recommendations (existing logic)
#         base_recommendations = await self.generate_recommendations(performance_history, topic_scores)
    
#         # Identify weak topics
#         topic_averages = self.calculate_performance_metrics(performance_history)
#         weaknesses = [
#             topic for topic, score in topic_averages.items()
#             if score < self.weak_threshold
#         ]
    
#     # Get document references for weak topics
#         study_materials = []
#         for weak_topic in weaknesses[:3]:  # Top 3 weak areas
#             relevant_docs = self.doc_service.retrieve_relevant_content(
#                 query=weak_topic,
#                 filters={"course": course},
#                 top_k=2
#             )
        
#             for doc in relevant_docs:
#                 study_materials.append({
#                     "topic": weak_topic,
#                     "document_id": doc["metadata"]["document_id"],
#                     "week": doc["metadata"].get("week"),
#                     "section": doc["content"][:200] + "...",
#                     "relevance": f"Review this for {weak_topic}"
#                 })
    
#         # Enhance recommendations
#         base_recommendations["study_materials"] = study_materials
#         base_recommendations["document_references"] = len(study_materials)
    
#         return base_recommendations







# VERSION 2

# import numpy as np
# from typing import List, Dict, Tuple, Optional
# from sklearn.preprocessing import MinMaxScaler
# import os
# import httpx
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from datetime import datetime
# import json
# # from app.services.document_service import DocumentProcessingService

# # Load environment variables
# load_dotenv()


# class RecommendationService:
#     """
#     AI-powered recommendation system for TVET students.
#     Analyzes performance to suggest personalized learning paths.
#     """
    
#     def __init__(self):
#         # Load API key from environment
#         self.groq_api_key = os.getenv("GROQAPI_KEY")
#         if not self.groq_api_key:
#             logger.warning("GROQ_API_KEY not found. LLM-powered insights will not be available.")
        
#         self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")  # Fast & free on Groq
#         self.weak_threshold = 0.6  # Below 60% = needs improvement
#         self.strong_threshold = 0.8  # Above 80% = strength
        
#         # Initialize document service
#         try:
#             self.doc_service = DocumentProcessingService()
#         except Exception as e:
#             logger.warning(f"Document service initialization failed: {e}")
#             self.doc_service = None
        
#         logger.info("RecommendationService initialized")
        
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
        
#         # Check if API key is available
#         if not self.groq_api_key:
#             logger.warning("GROQ_API_KEY not available, using fallback messages")
#             explanation = "Your performance data shows areas of strength and opportunities for growth."
#             motivation = "Stay focused on your goals. Practical skills take time and consistent effort!"
#             return explanation, motivation
        
#         system_prompt = "You are a supportive TVET instructor. Be encouraging, specific, and practical. Focus on trades skills like wiring and plumbing."
        
#         user_prompt = f"""Student Performance Summary:
# - Strong Topics: {', '.join(strengths) if strengths else 'None yet'}
# - Topics Needing Work: {', '.join(weaknesses) if weaknesses else 'None'}
# - Performance Trends: {trends}
# - Topic Scores: {topic_averages}

# Study Plan:
# {study_plan}

# Generate two parts:
# 1. A brief explanation (2-3 sentences) of their learning pattern
# 2. An encouraging motivational message (2-3 sentences) specific to their situation

# Separate the two parts with a blank line."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 300
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     llm_output = result["choices"][0]["message"]["content"]
                    
#                     # Split into explanation and motivation
#                     parts = llm_output.split("\n\n")
#                     explanation = parts[0].strip() if len(parts) > 0 else llm_output
#                     motivation = parts[1].strip() if len(parts) > 1 else "Keep pushing forward! Every expert was once a beginner."
                    
#                     return explanation, motivation
#                 else:
#                     logger.error(f"Groq API error: {response.status_code} - {response.text}")
#                     raise Exception(f"Groq returned status {response.status_code}")
            
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

#     def track_improvement(
#         self,
#         student_id: str,
#         current_metrics: Dict[str, float],
#         previous_metrics: Optional[Dict[str, float]] = None
#     ) -> Dict[str, any]:
#         """
#         Track student improvement over time.
#         Compares current performance against previous assessment.
#         """
#         if not previous_metrics:
#             return {
#                 "student_id": student_id,
#                 "baseline_established": True,
#                 "message": "Baseline performance recorded. Next assessment will show progress.",
#                 "current_metrics": current_metrics,
#                 "timestamp": datetime.now().isoformat()
#             }
        
#         improvements = {}
#         declines = {}
#         stable = {}
        
#         for topic, current_score in current_metrics.items():
#             if topic in previous_metrics:
#                 previous_score = previous_metrics[topic]
#                 change = current_score - previous_score
#                 change_percent = (change / previous_score * 100) if previous_score > 0 else 0
                
#                 if change > 0.05:  # 5% improvement threshold
#                     improvements[topic] = {
#                         "previous": round(previous_score, 2),
#                         "current": round(current_score, 2),
#                         "change": round(change, 2),
#                         "change_percent": round(change_percent, 1)
#                     }
#                 elif change < -0.05:  # 5% decline threshold
#                     declines[topic] = {
#                         "previous": round(previous_score, 2),
#                         "current": round(current_score, 2),
#                         "change": round(change, 2),
#                         "change_percent": round(change_percent, 1)
#                     }
#                 else:
#                     stable[topic] = {
#                         "score": round(current_score, 2)
#                     }
        
#         # New topics that weren't in previous assessment
#         new_topics = {
#             topic: round(score, 2) 
#             for topic, score in current_metrics.items() 
#             if topic not in previous_metrics
#         }
        
#         # Overall progress indicator
#         if previous_metrics:
#             avg_previous = np.mean(list(previous_metrics.values()))
#             avg_current = np.mean(list(current_metrics.values()))
#             overall_change = avg_current - avg_previous
            
#             if overall_change > 0.05:
#                 progress_status = "improving"
#             elif overall_change < -0.05:
#                 progress_status = "declining"
#             else:
#                 progress_status = "stable"
#         else:
#             progress_status = "baseline"
        
#         return {
#             "student_id": student_id,
#             "timestamp": datetime.now().isoformat(),
#             "progress_status": progress_status,
#             "improvements": improvements,
#             "declines": declines,
#             "stable_topics": stable,
#             "new_topics": new_topics,
#             "summary": {
#                 "topics_improved": len(improvements),
#                 "topics_declined": len(declines),
#                 "topics_stable": len(stable),
#                 "new_topics_count": len(new_topics)
#             }
#         }

#     def generate_report_data(
#         self,
#         student_id: str,
#         student_name: str,
#         recommendations: Dict[str, any],
#         improvement_tracking: Optional[Dict[str, any]] = None
#     ) -> Dict[str, any]:
#         """
#         Generate structured report data for export.
#         """
#         report = {
#             "report_metadata": {
#                 "student_id": student_id,
#                 "student_name": student_name,
#                 "generated_at": datetime.now().isoformat(),
#                 "report_type": "Performance Analysis & Recommendations"
#             },
#             "performance_summary": {
#                 "strengths": recommendations.get("strengths", []),
#                 "areas_for_improvement": recommendations["study_plan"]["skill_building"]["topics"],
#                 "urgent_attention_needed": recommendations["study_plan"]["urgent_review"]["topics"],
#                 "ready_for_advancement": recommendations["study_plan"]["advancement"]["topics"]
#             },
#             "detailed_analysis": {
#                 "topic_trends": recommendations.get("trends", {}),
#                 "llm_insights": {
#                     "explanation": recommendations.get("llm_explanation", ""),
#                     "motivation": recommendations.get("motivational_message", "")
#                 }
#             },
#             "study_plan": recommendations.get("study_plan", {}),
#             "recommended_actions": recommendations.get("topic_recommendations", [])
#         }
        
#         # Add improvement tracking if available
#         if improvement_tracking:
#             report["progress_tracking"] = improvement_tracking
        
#         return report

#     async def generate_recommendations_with_documents(
#         self,
#         student_id: str,
#         performance_history: List[Dict],
#         topic_scores: Dict[str, float],
#         course: str
#     ) -> Dict:
#         """
#         Generate recommendations with document-specific study suggestions.
#         """
        
#         # Generate base recommendations (existing logic)
#         base_recommendations = await self.generate_recommendations(performance_history, topic_scores)
        
#         # Check if document service is available
#         if not self.doc_service:
#             logger.warning("Document service not available, skipping document references")
#             base_recommendations["study_materials"] = []
#             base_recommendations["document_references"] = 0
#             return base_recommendations
        
#         # Identify weak topics
#         topic_averages = self.calculate_performance_metrics(performance_history)
#         weaknesses = [
#             topic for topic, score in topic_averages.items()
#             if score < self.weak_threshold
#         ]
        
#         # Get document references for weak topics
#         study_materials = []
#         for weak_topic in weaknesses[:3]:  # Top 3 weak areas
#             try:
#                 relevant_docs = self.doc_service.retrieve_relevant_content(
#                     query=weak_topic,
#                     filters={"course": course},
#                     top_k=2
#                 )
                
#                 for doc in relevant_docs:
#                     study_materials.append({
#                         "topic": weak_topic,
#                         "document_id": doc["metadata"]["document_id"],
#                         "week": doc["metadata"].get("week"),
#                         "section": doc["content"][:200] + "...",
#                         "relevance": f"Review this for {weak_topic}"
#                     })
#             except Exception as e:
#                 logger.error(f"Failed to retrieve documents for {weak_topic}: {e}")
#                 continue
        
#         # Enhance recommendations
#         base_recommendations["study_materials"] = study_materials
#         base_recommendations["document_references"] = len(study_materials)
        
#         return base_recommendations







# VERSION 3




# """recommendation service"""


# import numpy as np
# from typing import List, Dict, Tuple, Optional
# from sklearn.preprocessing import MinMaxScaler
# import os
# import httpx
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from datetime import datetime
# import json


# # Load environment variables
# load_dotenv()


# class RecommendationService:
#     """
#     AI-powered recommendation system for TVET students.
#     Analyzes performance to suggest personalized learning paths.
#     """
    
#     def __init__(self):
#         # Load API key from environment
#         self.groq_api_key = os.getenv("GROQ_API_KEY")
#         if not self.groq_api_key:
#             logger.warning("GROQ_API_KEY not found. LLM-powered insights will not be available.")
        
#         self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")  # Fast & free on Groq
#         self.weak_threshold = 0.6  # Below 60% = needs improvement
#         self.strong_threshold = 0.8  # Above 80% = strength
        
#         # Initialize document service
#         try:
#             self.doc_service = DocumentProcessingService()
#         except Exception as e:
#             logger.warning(f"Document service initialization failed: {e}")
#             self.doc_service = None
        
#         logger.info("RecommendationService initialized")
        
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
        
#         # Check if API key is available
#         if not self.groq_api_key:
#             logger.warning("GROQ_API_KEY not available, using fallback messages")
#             explanation = "Your performance data shows areas of strength and opportunities for growth."
#             motivation = "Stay focused on your goals. Practical skills take time and consistent effort!"
#             return explanation, motivation
        
#         system_prompt = "You are a supportive TVET instructor. Be encouraging, specific, and practical. Focus on trades skills like wiring and plumbing."
        
#         user_prompt = f"""Student Performance Summary:
# - Strong Topics: {', '.join(strengths) if strengths else 'None yet'}
# - Topics Needing Work: {', '.join(weaknesses) if weaknesses else 'None'}
# - Performance Trends: {trends}
# - Topic Scores: {topic_averages}

# Study Plan:
# {study_plan}

# Generate two parts:
# 1. A brief explanation (2-3 sentences) of their learning pattern
# 2. An encouraging motivational message (2-3 sentences) specific to their situation

# Separate the two parts with a blank line."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 300
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     llm_output = result["choices"][0]["message"]["content"]
                    
#                     # Split into explanation and motivation
#                     parts = llm_output.split("\n\n")
#                     explanation = parts[0].strip() if len(parts) > 0 else llm_output
#                     motivation = parts[1].strip() if len(parts) > 1 else "Keep pushing forward! Every expert was once a beginner."
                    
#                     return explanation, motivation
#                 else:
#                     logger.error(f"Groq API error: {response.status_code} - {response.text}")
#                     raise Exception(f"Groq returned status {response.status_code}")
            
#         except Exception as e:
#             logger.error(f"LLM generation failed: {e}")
#             # Fallback messages
#             explanation = "Your performance data shows areas of strength and opportunities for growth."
#             motivation = "Stay focused on your goals. Practical skills take time and consistent effort!"
#             return explanation, motivation
    

#     async def generate_recommendations(self,performance_history: List[Dict],topic_scores: Dict[str, float]) -> Dict[str, any]:
#         """
#         Generate recommendations per module and an overall summary.
#         """

#         module_recommendations = await self.generate_module_recommendations(
#         performance_history,
#         topic_scores
#     )

#         all_strengths = []
#         all_weaknesses = []

#         for module in module_recommendations.values():
#             all_strengths.extend(module["strengths"])
#             all_weaknesses.extend(module["weaknesses"])

#         return {
#         "module_recommendations": module_recommendations,
#         "overall_summary": {
#             "total_modules": len(module_recommendations),
#             "common_strengths": list(set(all_strengths)),
#             "common_weaknesses": list(set(all_weaknesses))
#         }
#     }


#     def track_improvement(self,student_id: str,current_metrics: Dict[str, float],previous_metrics: Optional[Dict[str, float]] = None) -> Dict[str, any]:
#         """
#         Track student improvement over time.
#         Compares current performance against previous assessment.
#         """
#         if not previous_metrics:
#             return {
#                 "student_id": student_id,
#                 "baseline_established": True,
#                 "message": "Baseline performance recorded. Next assessment will show progress.",
#                 "current_metrics": current_metrics,
#                 "timestamp": datetime.now().isoformat()
#             }
        
#         improvements = {}
#         declines = {}
#         stable = {}
        
#         for topic, current_score in current_metrics.items():
#             if topic in previous_metrics:
#                 previous_score = previous_metrics[topic]
#                 change = current_score - previous_score
#                 change_percent = (change / previous_score * 100) if previous_score > 0 else 0
                
#                 if change > 0.05:  # 5% improvement threshold
#                     improvements[topic] = {
#                         "previous": round(previous_score, 2),
#                         "current": round(current_score, 2),
#                         "change": round(change, 2),
#                         "change_percent": round(change_percent, 1)
#                     }
#                 elif change < -0.05:  # 5% decline threshold
#                     declines[topic] = {
#                         "previous": round(previous_score, 2),
#                         "current": round(current_score, 2),
#                         "change": round(change, 2),
#                         "change_percent": round(change_percent, 1)
#                     }
#                 else:
#                     stable[topic] = {
#                         "score": round(current_score, 2)
#                     }
        
#         # New topics that weren't in previous assessment
#         new_topics = {
#             topic: round(score, 2) 
#             for topic, score in current_metrics.items() 
#             if topic not in previous_metrics
#         }
        
#         # Overall progress indicator
#         if previous_metrics:
#             avg_previous = np.mean(list(previous_metrics.values()))
#             avg_current = np.mean(list(current_metrics.values()))
#             overall_change = avg_current - avg_previous
            
#             if overall_change > 0.05:
#                 progress_status = "improving"
#             elif overall_change < -0.05:
#                 progress_status = "declining"
#             else:
#                 progress_status = "stable"
#         else:
#             progress_status = "baseline"
        
#         return {
#             "student_id": student_id,
#             "timestamp": datetime.now().isoformat(),
#             "progress_status": progress_status,
#             "improvements": improvements,
#             "declines": declines,
#             "stable_topics": stable,
#             "new_topics": new_topics,
#             "summary": {
#                 "topics_improved": len(improvements),
#                 "topics_declined": len(declines),
#                 "topics_stable": len(stable),
#                 "new_topics_count": len(new_topics)
#             }
#         }

#     def group_performance_by_module(self,performance_history: List[Dict]) -> Dict[str, List[Dict]]:
#         """
#         Group performance records by module.
#         """
#         modules = {}

#         for record in performance_history:
#             module_id = record.get("module_id")
#             if not module_id:
#                 continue

#             modules.setdefault(module_id, []).append(record)

#         return modules

#     async def generate_module_recommendations(self,performance_history: List[Dict],topic_scores: Optional[Dict[str, float]] = None) -> Dict[str, Dict]:
#         """
#         Generate recommendations per module taken by the student.
#         """
#         module_groups = self.group_performance_by_module(performance_history)
#         module_results = {}

#         for module_id, records in module_groups.items():
#         # Ensure chronological order for trend detection
#             records = sorted(
#             records,
#             key=lambda r: r.get("timestamp", "")
#             )

#             topic_averages = self.calculate_performance_metrics(records)

#             if topic_scores:
#                 normalized_scores = {
#                 k: min(v, 1.0) for k, v in topic_scores.items()
#             }
#             topic_averages.update(normalized_scores)

#             strengths, weaknesses = self.identify_strengths_weaknesses(topic_averages)
#             trends = self.detect_trends(records)

#             study_plan = self.generate_study_plan(
#             weaknesses,
#             strengths,
#             trends,
#             topic_averages
#         )

#             explanation, motivation = await self.generate_llm_insights(
#             strengths,
#             weaknesses,
#             trends,
#             topic_averages,
#             study_plan
#         )

#             module_results[module_id] = {
#             "module_id": module_id,
#             "strengths": strengths,
#             "weaknesses": weaknesses,
#             "trends": trends,
#             "study_plan": study_plan,
#             "topic_recommendations": (
#                 study_plan["urgent_review"]["topics"]
#                 + study_plan["skill_building"]["topics"]
#                 + study_plan["advancement"]["topics"]
#             ),
#             "llm_explanation": explanation,
#             "motivational_message": motivation
#         }

#         return module_results



#     def generate_report_data(
#         self,
#         student_id: str,
#         student_name: str,
#         recommendations: Dict[str, any],
#         improvement_tracking: Optional[Dict[str, any]] = None
#     ) -> Dict[str, any]:
#         """
#         Generate structured report data for export.
#         """
#         report = {
#             "report_metadata": {
#                 "student_id": student_id,
#                 "student_name": student_name,
#                 "generated_at": datetime.now().isoformat(),
#                 "report_type": "Performance Analysis & Recommendations"
#             },
#             "performance_summary": {
#                 "strengths": recommendations.get("strengths", []),
#                 "areas_for_improvement": recommendations["study_plan"]["skill_building"]["topics"],
#                 "urgent_attention_needed": recommendations["study_plan"]["urgent_review"]["topics"],
#                 "ready_for_advancement": recommendations["study_plan"]["advancement"]["topics"]
#             },
#             "detailed_analysis": {
#                 "topic_trends": recommendations.get("trends", {}),
#                 "llm_insights": {
#                     "explanation": recommendations.get("llm_explanation", ""),
#                     "motivation": recommendations.get("motivational_message", "")
#                 }
#             },
#             "study_plan": recommendations.get("study_plan", {}),
#             "recommended_actions": recommendations.get("topic_recommendations", [])
#         }
        
#         # Add improvement tracking if available
#         if improvement_tracking:
#             report["progress_tracking"] = improvement_tracking
        
#         return report
    




# VERSION 4







# """
# Recommendation Service - FIXED VERSION
# AI-powered personalized learning recommendations
# """

# import numpy as np
# from typing import List, Dict, Tuple, Optional
# import os
# import httpx
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from datetime import datetime

# load_dotenv()


# class RecommendationService:
#     """AI-powered recommendation system for TVET students."""
    
#     def __init__(self):
#         self.groq_api_key = os.getenv("GROQAPI_KEY")
#         if not self.groq_api_key:
#             logger.warning("⚠️ GROQAPI_KEY not found. LLM insights unavailable.")
        
#         self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
#         self.weak_threshold = 0.6
#         self.strong_threshold = 0.8
        
#         logger.info("✅ RecommendationService initialized")
    
#     def calculate_performance_metrics(
#         self,
#         performance_history: List[Dict]
#     ) -> Dict[str, float]:
#         """Calculate normalized scores per topic."""
#         topic_performance = {}
        
#         for record in performance_history:
#             topic = record["topic"]
#             normalized_score = record["score"] / record["max_score"]
            
#             if topic not in topic_performance:
#                 topic_performance[topic] = []
#             topic_performance[topic].append(normalized_score)
        
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
        
#         for record in performance_history:
#             topic = record["topic"]
#             normalized_score = record["score"] / record["max_score"]
            
#             if topic not in topic_scores_timeline:
#                 topic_scores_timeline[topic] = []
#             topic_scores_timeline[topic].append(normalized_score)
        
#         for topic, scores in topic_scores_timeline.items():
#             if len(scores) < 2:
#                 topic_trends[topic] = "insufficient_data"
#                 continue
            
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
#     ) -> Dict:
#         """Create prioritized study plan."""
#         declining_topics = [
#             topic for topic, trend in trends.items()
#             if trend == "declining"
#         ]
        
#         improvement_topics = [
#             topic for topic in weaknesses
#             if topic not in declining_topics
#         ]
        
#         advancement_topics = [
#             topic for topic in strengths
#             if trends.get(topic) == "improving"
#         ]
        
#         return {
#             "urgent_review": {
#                 "topics": declining_topics,
#                 "reason": "Performance is declining - immediate attention needed",
#                 "suggested_hours": len(declining_topics) * 3
#             },
#             "skill_building": {
#                 "topics": improvement_topics,
#                 "reason": "Below mastery - foundational work needed",
#                 "suggested_hours": len(improvement_topics) * 2
#             },
#             "advancement": {
#                 "topics": advancement_topics,
#                 "reason": "Strong foundation - ready for advanced concepts",
#                 "suggested_hours": len(advancement_topics) * 1.5
#             }
#         }
    
#     async def generate_llm_insights(
#         self,
#         strengths: List[str],
#         weaknesses: List[str],
#         trends: Dict[str, str],
#         topic_averages: Dict[str, float],
#         study_plan: Dict
#     ) -> Tuple[str, str]:
#         """Generate personalized explanation and motivation using LLM."""
        
#         if not self.groq_api_key:
#             logger.warning("⚠️ API key unavailable, using fallback")
#             return self._fallback_insights(strengths, weaknesses)
        
#         system_prompt = "You are a supportive TVET instructor. Be encouraging and specific."
        
#         user_prompt = f"""Student Performance Summary:
# - Strong Topics: {', '.join(strengths) if strengths else 'None yet'}
# - Topics Needing Work: {', '.join(weaknesses) if weaknesses else 'None'}
# - Trends: {trends}
# - Scores: {topic_averages}

# Study Plan: {study_plan}

# Generate:
# 1. Brief explanation (2-3 sentences) of their learning pattern
# 2. Encouraging motivational message (2-3 sentences)

# Separate with a blank line."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 300
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     llm_output = result["choices"][0]["message"]["content"]
                    
#                     parts = llm_output.split("\n\n")
#                     explanation = parts[0].strip() if len(parts) > 0 else llm_output
#                     motivation = parts[1].strip() if len(parts) > 1 else "Keep pushing forward!"
                    
#                     return explanation, motivation
#                 else:
#                     logger.error(f"❌ Groq API error: {response.status_code}")
#                     return self._fallback_insights(strengths, weaknesses)
            
#         except Exception as e:
#             logger.error(f"❌ LLM generation failed: {e}")
#             return self._fallback_insights(strengths, weaknesses)
    
#     def _fallback_insights(
#         self,
#         strengths: List[str],
#         weaknesses: List[str]
#     ) -> Tuple[str, str]:
#         """Fallback insights when LLM unavailable."""
#         if strengths and weaknesses:
#             explanation = f"You're showing strength in {len(strengths)} areas while working on {len(weaknesses)} topics."
#             motivation = "Balance your practice between reinforcing strengths and improving weak areas!"
#         elif strengths:
#             explanation = f"Great progress! You're performing well across {len(strengths)} topics."
#             motivation = "Keep up the excellent work and challenge yourself with advanced material!"
#         elif weaknesses:
#             explanation = f"You're working on {len(weaknesses)} challenging topics."
#             motivation = "Stay focused! Consistent practice will lead to improvement."
#         else:
#             explanation = "Building your foundation in new topics."
#             motivation = "Every expert was once a beginner. Keep learning!"
        
#         return explanation, motivation
    
#     async def generate_recommendations(self,performance_history: List[Dict],topic_scores: Optional[Dict[str, float]] = None) -> Dict:
#         """
#         Generate comprehensive recommendations.
        
#         Args:
#             performance_history: List of {topic, score, max_score} records
#             topic_scores: Optional dict of topic -> normalized score (0-1)
        
#         Returns:
#             Complete recommendation result
#         """
#         try:
#             # Calculate metrics
#             topic_averages = self.calculate_performance_metrics(performance_history)
            
#             # Merge with provided topic_scores if available
#             if topic_scores:
#                 normalized_scores = {k: min(v, 1.0) for k, v in topic_scores.items()}
#                 topic_averages.update(normalized_scores)
            
#             # Identify strengths/weaknesses
#             strengths, weaknesses = self.identify_strengths_weaknesses(topic_averages)
            
#             # Detect trends
#             trends = self.detect_trends(performance_history)
            
#             # Generate study plan
#             study_plan = self.generate_study_plan(
#                 weaknesses, strengths, trends, topic_averages
#             )
            
#             # Get LLM insights
#             explanation, motivation = await self.generate_llm_insights(
#                 strengths, weaknesses, trends, topic_averages, study_plan
#             )
            
#             # Compile recommendations
#             topic_recommendations = (
#                 study_plan["urgent_review"]["topics"] +
#                 study_plan["skill_building"]["topics"] +
#                 study_plan["advancement"]["topics"]
#             )
            
#             return {
#                 "topic_recommendations": topic_recommendations,
#                 "study_plan": study_plan,
#                 "strengths": strengths,
#                 "trends": trends,
#                 "motivational_message": motivation,
#                 "llm_explanation": explanation
#             }
            
#         except Exception as e:
#             logger.error(f" Recommendation generation failed: {e}", exc_info=True)
#             raise








# VERSION 5







# """
# Recommendation Service - PRODUCTION READY
# AI-powered personalized learning recommendations for TVET students
# Location: app/services/recommendation_service.py
# """

# import numpy as np
# from typing import List, Dict, Tuple, Optional
# import os
# import httpx
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from datetime import datetime

# load_dotenv()


# class RecommendationService:
#     """
#     AI-powered recommendation system that analyzes student performance
#     and generates personalized learning paths.
#     """
    
#     def __init__(self):
#         self.groq_api_key = os.getenv("GROQAPI_KEY")
#         if not self.groq_api_key:
#             logger.warning("GROQAPI_KEY not found. Will use fallback recommendations.")
        
#         self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
#         # Performance thresholds
#         self.weak_threshold = 0.60      # Below 60% = needs work
#         self.strong_threshold = 0.80    # Above 80% = strength
        
#         logger.info("RecommendationService initialized")
    
#     def calculate_performance_metrics(
#         self,
#         performance_history: List[Dict]
#     ) -> Dict[str, float]:
#         """
#         Calculate normalized performance scores per topic.
        
#         Args:
#             performance_history: List of {topic, score, max_score} records
            
#         Returns:
#             Dict mapping topic -> average normalized score (0-1)
#         """
#         topic_performance = {}
        
#         for record in performance_history:
#             topic = record["topic"]
#             normalized_score = record["score"] / record["max_score"] if record["max_score"] > 0 else 0
            
#             if topic not in topic_performance:
#                 topic_performance[topic] = []
#             topic_performance[topic].append(normalized_score)
        
#         # Calculate average per topic
#         topic_averages = {
#             topic: np.mean(scores)
#             for topic, scores in topic_performance.items()
#         }
        
#         return topic_averages
    
#     def identify_strengths_weaknesses(
#         self,
#         topic_averages: Dict[str, float]
#     ) -> Tuple[List[str], List[str]]:
#         """
#         Classify topics into strengths and weaknesses.
        
#         Args:
#             topic_averages: Dict of topic -> normalized score
            
#         Returns:
#             (strengths, weaknesses) tuple of topic lists
#         """
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
#         """
#         Detect performance trends: improving, declining, or stable.
        
#         Args:
#             performance_history: Chronologically ordered performance records
            
#         Returns:
#             Dict mapping topic -> trend ("improving"|"declining"|"stable"|"insufficient_data")
#         """
#         topic_trends = {}
#         topic_scores_timeline = {}
        
#         # Group scores by topic chronologically
#         for record in performance_history:
#             topic = record["topic"]
#             normalized_score = record["score"] / record["max_score"] if record["max_score"] > 0 else 0
            
#             if topic not in topic_scores_timeline:
#                 topic_scores_timeline[topic] = []
#             topic_scores_timeline[topic].append(normalized_score)
        
#         # Analyze trend for each topic
#         for topic, scores in topic_scores_timeline.items():
#             if len(scores) < 2:
#                 topic_trends[topic] = "insufficient_data"
#                 continue
            
#             # Compare recent performance vs early performance
#             recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else np.mean(scores)
#             early_avg = np.mean(scores[:3]) if len(scores) >= 3 else scores[0]
            
#             # 10% threshold for significant change
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
#     ) -> Dict:
#         """
#         Create a prioritized study plan.
        
#         Returns:
#             Study plan with urgent_review, skill_building, and advancement sections
#         """
#         # Priority 1: Declining topics (highest urgency)
#         declining_topics = [
#             topic for topic, trend in trends.items()
#             if trend == "declining"
#         ]
        
#         # Priority 2: Weak topics not yet declining
#         improvement_topics = [
#             topic for topic in weaknesses
#             if topic not in declining_topics
#         ]
        
#         # Priority 3: Strong topics showing improvement
#         advancement_topics = [
#             topic for topic in strengths
#             if trends.get(topic) == "improving"
#         ]
        
#         return {
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
    
#     async def generate_llm_insights(
#         self,
#         strengths: List[str],
#         weaknesses: List[str],
#         trends: Dict[str, str],
#         topic_averages: Dict[str, float],
#         study_plan: Dict
#     ) -> Tuple[str, str]:
#         """
#         Generate personalized explanation and motivation using LLM.
        
#         Returns:
#             (explanation, motivational_message) tuple
#         """
#         if not self.groq_api_key:
#             logger.warning(" GROQ_API_KEY unavailable, using fallback")
#             return self._fallback_insights(strengths, weaknesses)
        
#         system_prompt = """You are a supportive TVET instructor providing personalized feedback.
# Be encouraging, specific, and practical. Focus on technical/vocational skills."""
        
#         user_prompt = f"""Student Performance Analysis:
# - Strong Topics: {', '.join(strengths) if strengths else 'Still building foundation'}
# - Topics Needing Work: {', '.join(weaknesses) if weaknesses else 'Good progress across topics'}
# - Performance Trends: {trends}
# - Topic Scores: {topic_averages}

# Study Plan Summary:
# - Urgent Review: {', '.join(study_plan['urgent_review']['topics']) if study_plan['urgent_review']['topics'] else 'None'}
# - Skill Building: {', '.join(study_plan['skill_building']['topics']) if study_plan['skill_building']['topics'] else 'None'}
# - Ready to Advance: {', '.join(study_plan['advancement']['topics']) if study_plan['advancement']['topics'] else 'None'}

# Generate TWO short paragraphs (2-3 sentences each):
# 1. EXPLANATION: Analyze their learning pattern and what it means
# 2. MOTIVATION: Encouraging message specific to their situation

# Separate the paragraphs with a blank line."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 300
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     llm_output = result["choices"][0]["message"]["content"].strip()
                    
#                     # Split into explanation and motivation
#                     parts = llm_output.split("\n\n")
#                     explanation = parts[0].strip() if len(parts) > 0 else llm_output
#                     motivation = parts[1].strip() if len(parts) > 1 else "Keep up the great work!"
                    
#                     return explanation, motivation
#                 else:
#                     logger.error(f"Groq API error: {response.status_code}")
#                     return self._fallback_insights(strengths, weaknesses)
            
#         except Exception as e:
#             logger.error(f"LLM insights generation failed: {e}")
#             return self._fallback_insights(strengths, weaknesses)
    
#     def _fallback_insights(
#         self,
#         strengths: List[str],
#         weaknesses: List[str]
#     ) -> Tuple[str, str]:
#         """Fallback insights when LLM is unavailable."""
#         if strengths and weaknesses:
#             explanation = (
#                 f"You're showing strong performance in {len(strengths)} areas "
#                 f"while working to improve {len(weaknesses)} topics. "
#                 "This balanced progress shows you're engaging with the material effectively."
#             )
#             motivation = (
#                 "Keep balancing your study time between reinforcing your strengths "
#                 "and building skills in challenging areas. Consistent practice is key!"
#             )
#         elif strengths and not weaknesses:
#             explanation = (
#                 f"Excellent work! You're performing well across {len(strengths)} topics, "
#                 "demonstrating strong mastery of the fundamentals."
#             )
#             motivation = (
#                 "You're ready to challenge yourself with more advanced material. "
#                 "Keep up this outstanding momentum!"
#             )
#         elif weaknesses and not strengths:
#             explanation = (
#                 f"You're currently working on {len(weaknesses)} challenging topics. "
#                 "Building these foundational skills takes focused practice and patience."
#             )
#             motivation = (
#                 "Stay committed to your learning plan. Every expert started where you are now. "
#                 "Consistent effort will lead to improvement!"
#             )
#         else:
#             explanation = (
#                 "You're building your foundation in these technical topics. "
#                 "Early stages of learning require time and repetition."
#             )
#             motivation = (
#                 "Keep practicing! Each quiz helps build your skills. "
#                 "Progress comes with consistent effort."
#             )
        
#         return explanation, motivation
    
#     async def generate_recommendations(
#         self,
#         performance_history: List[Dict],
#         topic_scores: Optional[Dict[str, float]] = None
#     ) -> Dict:
#         """
#         Generate comprehensive personalized recommendations.
        
#         Args:
#             performance_history: List of performance records with topic, score, max_score
#             topic_scores: Optional dict of topic -> normalized score (0-1)
            
#         Returns:
#             Complete recommendation package with study plan, insights, and trends
#         """
#         try:
#             logger.info(f"Generating recommendations from {len(performance_history)} records")
            
#             # Calculate performance metrics
#             topic_averages = self.calculate_performance_metrics(performance_history)
            
#             # Merge with provided topic scores if available
#             if topic_scores:
#                 normalized_scores = {
#                     k: min(max(v, 0.0), 1.0)  # Clamp to 0-1
#                     for k, v in topic_scores.items()
#                 }
#                 topic_averages.update(normalized_scores)
            
#             # Identify strengths and weaknesses
#             strengths, weaknesses = self.identify_strengths_weaknesses(topic_averages)
            
#             # Detect performance trends
#             trends = self.detect_trends(performance_history)
            
#             # Generate study plan
#             study_plan = self.generate_study_plan(
#                 weaknesses, strengths, trends, topic_averages
#             )
            
#             # Generate AI insights
#             explanation, motivation = await self.generate_llm_insights(
#                 strengths, weaknesses, trends, topic_averages, study_plan
#             )
            
#             # Compile all recommendations
#             topic_recommendations = (
#                 study_plan["urgent_review"]["topics"] +
#                 study_plan["skill_building"]["topics"] +
#                 study_plan["advancement"]["topics"]
#             )
            
#             result = {
#                 "topic_recommendations": topic_recommendations,
#                 "study_plan": study_plan,
#                 "strengths": strengths,
#                 "trends": trends,
#                 "motivational_message": motivation,
#                 "llm_explanation": explanation
#             }
            
#             logger.info(
#                 f"Recommendations generated: {len(topic_recommendations)} topics, "
#                 f"{len(strengths)} strengths, {len(weaknesses)} areas to improve"
#             )
            
#             return result
            
#         except Exception as e:
#             logger.error(f" Recommendation generation failed: {e}", exc_info=True)
#             raise










# VERSION 6








"""
Enhanced Recommendation Service 
Analyzes actual student mistakes and provides specific, actionable recommendations
Location: app/services/recommendation_service.py
"""

# import numpy as np
# from typing import List, Dict, Tuple, Optional
# import os
# import httpx
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from datetime import datetime
# from collections import Counter

# load_dotenv()


# class RecommendationService:
#     """
#     Advanced recommendation system that analyzes:
#     1. Overall performance trends
#     2. Specific question failures
#     3. Concept-level weaknesses
#     4. Learning patterns
#     """
    
#     def __init__(self):
#         self.groq_api_key = os.getenv("GROQAPI_KEY")
#         if not self.groq_api_key:
#             logger.warning(" GROQAPI_KEY not found. Will use fallback recommendations.")
        
#         self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
#         # Performance thresholds
#         self.weak_threshold = 0.60
#         self.strong_threshold = 0.80
        
#         logger.info("Enhanced RecommendationService initialized")
    
#     def analyze_question_failures(
#         self,
#         question_results: List[Dict]
#     ) -> Dict:
#         """
#         Analyze specific questions that were answered incorrectly.
        
#         Args:
#             question_results: List of graded question results
            
#         Returns:
#             Detailed failure analysis with specific recommendations
#         """
#         failures = {
#             "failed_questions": [],
#             "weak_question_types": [],
#             "concepts_to_review": [],
#             "specific_improvements": []
#         }
        
#         # Track performance by question type
#         type_performance = {}
        
#         for result in question_results:
#             q_type = result["question_type"]
#             is_correct = result.get("is_correct")
#             awarded = result["awarded_points"]
#             max_points = result["max_points"]
            
#             # Track by type
#             if q_type not in type_performance:
#                 type_performance[q_type] = {"correct": 0, "total": 0, "points": 0, "max": 0}
            
#             type_performance[q_type]["total"] += 1
#             type_performance[q_type]["points"] += awarded
#             type_performance[q_type]["max"] += max_points
            
#             # Identify failures
#             if is_correct is False or (is_correct is None and awarded < max_points * 0.7):
#                 failures["failed_questions"].append({
#                     "question_id": result["question_id"],
#                     "type": q_type,
#                     "points_lost": max_points - awarded,
#                     "feedback": result.get("feedback", ""),
#                     "improvements": result.get("improvements", [])
#                 })
                
#                 # Extract specific concepts from improvements
#                 if result.get("improvements"):
#                     failures["concepts_to_review"].extend(result["improvements"])
        
#         # Identify weak question types
#         for q_type, stats in type_performance.items():
#             percentage = (stats["points"] / stats["max"] * 100) if stats["max"] > 0 else 0
#             if percentage < 70:
#                 failures["weak_question_types"].append({
#                     "type": q_type,
#                     "percentage": round(percentage, 1),
#                     "questions_attempted": stats["total"]
#                 })
        
#         # Generate specific improvements
#         failures["specific_improvements"] = self._generate_specific_improvements(
#             failures["failed_questions"],
#             failures["weak_question_types"]
#         )
        
#         # Deduplicate concepts
#         failures["concepts_to_review"] = list(set(failures["concepts_to_review"]))
        
#         return failures
    
#     def _generate_specific_improvements(
#         self,
#         failed_questions: List[Dict],
#         weak_types: List[Dict]
#     ) -> List[str]:
#         """Generate actionable improvement recommendations."""
#         improvements = []
        
#         # Recommendations based on failed questions
#         if failed_questions:
#             improvements.append(
#                 f"Review the {len(failed_questions)} questions you missed - "
#                 "understanding your mistakes is key to improvement"
#             )
            
#             # Group by type
#             type_counts = Counter(q["type"] for q in failed_questions)
#             for q_type, count in type_counts.most_common(2):
#                 type_name = self._humanize_question_type(q_type)
#                 improvements.append(
#                     f"Practice more {type_name} questions - "
#                     f"you missed {count} in this area"
#                 )
        
#         # Recommendations based on weak types
#         for weak in weak_types:
#             type_name = self._humanize_question_type(weak["type"])
#             improvements.append(
#                 f"Strengthen your {type_name} skills - "
#                 f"currently at {weak['percentage']:.0f}%"
#             )
        
#         return improvements
    
#     def _humanize_question_type(self, q_type: str) -> str:
#         """Convert question type codes to readable names."""
#         type_map = {
#             "mcq": "multiple choice",
#             "multiple_choice": "multiple choice",
#             "true_false": "true/false",
#             "short_answer": "short answer",
#             "essay": "essay",
#             "practical": "practical"
#         }
#         return type_map.get(q_type.lower(), q_type)
    
#     def calculate_performance_metrics(
#         self,
#         performance_history: List[Dict]
#     ) -> Dict[str, float]:
#         """Calculate normalized performance scores per topic."""
#         topic_performance = {}
        
#         for record in performance_history:
#             topic = record["topic"]
#             normalized_score = record["score"] / record["max_score"] if record["max_score"] > 0 else 0
            
#             if topic not in topic_performance:
#                 topic_performance[topic] = []
#             topic_performance[topic].append(normalized_score)
        
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
#         """Detect performance trends: improving, declining, or stable."""
#         topic_trends = {}
#         topic_scores_timeline = {}
        
#         for record in performance_history:
#             topic = record["topic"]
#             normalized_score = record["score"] / record["max_score"] if record["max_score"] > 0 else 0
            
#             if topic not in topic_scores_timeline:
#                 topic_scores_timeline[topic] = []
#             topic_scores_timeline[topic].append(normalized_score)
        
#         for topic, scores in topic_scores_timeline.items():
#             if len(scores) < 2:
#                 topic_trends[topic] = "insufficient_data"
#                 continue
            
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
#         topic_averages: Dict[str, float],
#         failure_analysis: Optional[Dict] = None
#     ) -> Dict:
#         """
#         Create a prioritized study plan based on:
#         1. Performance trends
#         2. Weak topics
#         3. Specific question failures
#         """
#         # Priority 1: Declining topics + failed concepts
#         declining_topics = [
#             topic for topic, trend in trends.items()
#             if trend == "declining"
#         ]
        
#         # Priority 2: Weak topics
#         improvement_topics = [
#             topic for topic in weaknesses
#             if topic not in declining_topics
#         ]
        
#         # Priority 3: Strong topics showing improvement
#         advancement_topics = [
#             topic for topic in strengths
#             if trends.get(topic) == "improving"
#         ]
        
#         # Build study plan
#         study_plan = {
#             "urgent_review": {
#                 "topics": declining_topics,
#                 "reason": "Performance is declining - immediate attention needed",
#                 "suggested_hours": len(declining_topics) * 3,
#                 "specific_actions": []
#             },
#             "skill_building": {
#                 "topics": improvement_topics,
#                 "reason": "Below mastery threshold - foundational work needed",
#                 "suggested_hours": len(improvement_topics) * 2,
#                 "specific_actions": []
#             },
#             "advancement": {
#                 "topics": advancement_topics,
#                 "reason": "Strong foundation - ready for advanced concepts",
#                 "suggested_hours": len(advancement_topics) * 1.5,
#                 "specific_actions": []
#             }
#         }
        
#         # Add specific actions from failure analysis
#         if failure_analysis:
#             # Add concept reviews to urgent/skill-building
#             concepts = failure_analysis.get("concepts_to_review", [])
#             if concepts:
#                 if declining_topics:
#                     study_plan["urgent_review"]["specific_actions"].extend([
#                         f"Review: {concept}" for concept in concepts[:3]
#                     ])
#                 else:
#                     study_plan["skill_building"]["specific_actions"].extend([
#                         f"Review: {concept}" for concept in concepts[:3]
#                     ])
            
#             # Add question type practice
#             weak_types = failure_analysis.get("weak_question_types", [])
#             for weak in weak_types:
#                 action = f"Practice {self._humanize_question_type(weak['type'])} questions"
#                 study_plan["skill_building"]["specific_actions"].append(action)
        
#         return study_plan
    
#     async def generate_llm_insights(
#         self,
#         strengths: List[str],
#         weaknesses: List[str],
#         trends: Dict[str, str],
#         topic_averages: Dict[str, float],
#         study_plan: Dict,
#         failure_analysis: Optional[Dict] = None
#     ) -> Tuple[str, str]:
#         """Generate personalized insights based on actual performance."""
#         if not self.groq_api_key:
#             return self._fallback_insights(strengths, weaknesses, failure_analysis)
        
#         # Build context from failure analysis
#         failure_context = ""
#         if failure_analysis:
#             failed_count = len(failure_analysis.get("failed_questions", []))
#             concepts = failure_analysis.get("concepts_to_review", [])
#             weak_types = failure_analysis.get("weak_question_types", [])
            
#             if failed_count > 0:
#                 failure_context = f"""
# Recent Quiz Performance:
# - Questions missed: {failed_count}
# - Concepts needing review: {', '.join(concepts[:5]) if concepts else 'N/A'}
# - Question types to practice: {', '.join([t['type'] for t in weak_types]) if weak_types else 'N/A'}
# """
        
#         system_prompt = """You are a supportive TVET instructor providing personalized feedback.
# Be specific about what the student needs to work on based on their actual mistakes.
# Reference specific concepts they struggled with."""
        
#         user_prompt = f"""Student Performance Analysis:
# - Strong Topics: {', '.join(strengths) if strengths else 'Still building foundation'}
# - Topics Needing Work: {', '.join(weaknesses) if weaknesses else 'Good progress'}
# - Trends: {trends}
# {failure_context}

# Study Plan:
# - Urgent: {', '.join(study_plan['urgent_review']['topics']) if study_plan['urgent_review']['topics'] else 'None'}
# - Build Skills: {', '.join(study_plan['skill_building']['topics']) if study_plan['skill_building']['topics'] else 'None'}
# - Advance: {', '.join(study_plan['advancement']['topics']) if study_plan['advancement']['topics'] else 'None'}

# Generate TWO paragraphs (2-3 sentences each):
# 1. EXPLANATION: What patterns you see in their learning, specifically addressing their recent mistakes
# 2. MOTIVATION: Encouraging message that acknowledges their challenges and provides hope

# Be specific - mention actual concepts they struggled with if available."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 350
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     llm_output = result["choices"][0]["message"]["content"].strip()
                    
#                     parts = llm_output.split("\n\n")
#                     explanation = parts[0].strip() if len(parts) > 0 else llm_output
#                     motivation = parts[1].strip() if len(parts) > 1 else "Keep working hard!"
                    
#                     return explanation, motivation
#                 else:
#                     return self._fallback_insights(strengths, weaknesses, failure_analysis)
            
#         except Exception as e:
#             logger.error(f"LLM insights failed: {e}")
#             return self._fallback_insights(strengths, weaknesses, failure_analysis)
    
#     def _fallback_insights(
#         self,
#         strengths: List[str],
#         weaknesses: List[str],
#         failure_analysis: Optional[Dict] = None
#     ) -> Tuple[str, str]:
#         """Enhanced fallback with failure analysis."""
#         concepts_str = ""
#         if failure_analysis:
#             concepts = failure_analysis.get("concepts_to_review", [])
#             if concepts:
#                 concepts_str = f" Pay special attention to: {', '.join(concepts[:3])}."
        
#         if weaknesses:
#             explanation = (
#                 f"Your recent quiz shows you need to strengthen your understanding in "
#                 f"{len(weaknesses)} areas: {', '.join(weaknesses[:2])}."
#                 f"{concepts_str} Focused practice on these concepts will help you improve."
#             )
#             motivation = (
#                 "Every expert struggled with difficult concepts at first. "
#                 "The fact that you're identifying where you need help shows you're on the right path. "
#                 "Keep practicing these specific areas!"
#             )
#         elif strengths:
#             explanation = (
#                 f"Excellent work! You're showing strong mastery in {len(strengths)} topics. "
#                 "Your consistent performance demonstrates solid understanding."
#             )
#             motivation = (
#                 "You're ready to tackle more advanced material. "
#                 "Keep up this outstanding work!"
#             )
#         else:
#             explanation = "You're building your foundation in these topics."
#             motivation = "Stay consistent with your practice. Progress takes time!"
        
#         return explanation, motivation
    
#     async def generate_recommendations(
#         self,
#         performance_history: List[Dict],
#         topic_scores: Optional[Dict[str, float]] = None,
#         question_results: Optional[List[Dict]] = None
#     ) -> Dict:
#         """
#         Generate comprehensive recommendations with question-level analysis.
        
#         Args:
#             performance_history: Historical performance records
#             topic_scores: Optional topic scores
#             question_results: NEW - Actual question results from latest quiz
            
#         Returns:
#             Complete recommendation with specific, actionable feedback
#         """
#         try:
#             logger.info(f"Generating enhanced recommendations")
            
#             # STEP 1: Analyze specific question failures (NEW!)
#             failure_analysis = None
#             if question_results:
#                 failure_analysis = self.analyze_question_failures(question_results)
#                 logger.info(
#                     f"Analyzed {len(question_results)} questions, "
#                     f"found {len(failure_analysis['failed_questions'])} failures"
#                 )
            
#             # STEP 2: Calculate overall performance metrics
#             topic_averages = self.calculate_performance_metrics(performance_history)
            
#             if topic_scores:
#                 normalized_scores = {
#                     k: min(max(v, 0.0), 1.0)
#                     for k, v in topic_scores.items()
#                 }
#                 topic_averages.update(normalized_scores)
            
#             # STEP 3: Identify strengths and weaknesses
#             strengths, weaknesses = self.identify_strengths_weaknesses(topic_averages)
            
#             # STEP 4: Detect trends
#             trends = self.detect_trends(performance_history)
            
#             # STEP 5: Generate study plan with specific actions
#             study_plan = self.generate_study_plan(
#                 weaknesses, strengths, trends, topic_averages, failure_analysis
#             )
            
#             # STEP 6: Generate AI insights
#             explanation, motivation = await self.generate_llm_insights(
#                 strengths, weaknesses, trends, topic_averages, study_plan, failure_analysis
#             )
            
#             # STEP 7: Compile recommendations
#             topic_recommendations = (
#                 study_plan["urgent_review"]["topics"] +
#                 study_plan["skill_building"]["topics"] +
#                 study_plan["advancement"]["topics"]
#             )
            
#             result = {
#                 "topic_recommendations": topic_recommendations,
#                 "study_plan": study_plan,
#                 "strengths": strengths,
#                 "weaknesses": weaknesses,
#                 "trends": trends,
#                 "motivational_message": motivation,
#                 "llm_explanation": explanation,
#                 # NEW: Include failure analysis
#                 "failure_analysis": failure_analysis
#             }
            
#             logger.info(
#                 f"Enhanced recommendations: {len(topic_recommendations)} topics, "
#                 f"{len(failure_analysis.get('specific_improvements', []) if failure_analysis else [])} specific improvements"
#             )
            
#             return result
            
#         except Exception as e:
#             logger.error(f" Recommendation generation failed: {e}", exc_info=True)
#             raise














"""
Content-Aware Recommendation Service
Location: app/services/recommendation_service.py
"""

# import numpy as np
# from typing import List, Dict, Tuple, Optional
# import os
# import httpx
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from datetime import datetime
# from collections import Counter

# load_dotenv()


# class RecommendationService:
#     """
#     Content-aware recommendation system that analyzes actual learning materials
#     """
    
#     def __init__(self):
#         self.groq_api_key = os.getenv("GROQAPI_KEY")
#         if not self.groq_api_key:
#             logger.warning(" GROQAPI_KEY not found. Will use fallback recommendations.")
        
#         self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
#         # Performance thresholds
#         self.weak_threshold = 0.60
#         self.strong_threshold = 0.80
        
#         logger.info("Content-Aware RecommendationService initialized")
    
#     def analyze_question_failures(
#         self,
#         question_results: List[Dict]
#     ) -> Dict:
#         """Analyze specific questions that were answered incorrectly"""
#         failures = {
#             "failed_questions": [],
#             "weak_question_types": [],
#             "concepts_to_review": [],
#             "specific_improvements": []
#         }
        
#         if not question_results:
#             logger.info("No question results provided for failure analysis")
#             return failures
        
#         # Track performance by question type
#         type_performance = {}
        
#         for result in question_results:
#             q_type = result.get("question_type", "unknown")
#             is_correct = result.get("is_correct")
#             awarded = result.get("awarded_points", 0)
#             max_points = result.get("max_points", 1)
            
#             # Track by type
#             if q_type not in type_performance:
#                 type_performance[q_type] = {"correct": 0, "total": 0, "points": 0, "max": 0}
            
#             type_performance[q_type]["total"] += 1
#             type_performance[q_type]["points"] += awarded
#             type_performance[q_type]["max"] += max_points
            
#             # Identify failures (is_correct=False OR scored less than 70%)
#             score_percentage = (awarded / max_points) if max_points > 0 else 0
#             if is_correct is False or score_percentage < 0.7:
#                 failures["failed_questions"].append({
#                     "question_id": result.get("question_id", "unknown"),
#                     "type": q_type,
#                     "points_lost": max_points - awarded,
#                     "feedback": result.get("feedback", ""),
#                     "improvements": result.get("improvements", [])
#                 })
                
#                 # Extract specific concepts from improvements
#                 if result.get("improvements"):
#                     failures["concepts_to_review"].extend(result["improvements"])
        
#         # Identify weak question types (below 70%)
#         for q_type, stats in type_performance.items():
#             percentage = (stats["points"] / stats["max"] * 100) if stats["max"] > 0 else 0
#             if percentage < 70:
#                 failures["weak_question_types"].append({
#                     "type": q_type,
#                     "percentage": round(percentage, 1),
#                     "questions_attempted": stats["total"]
#                 })
        
#         # Generate specific improvements
#         failures["specific_improvements"] = self._generate_specific_improvements(
#             failures["failed_questions"],
#             failures["weak_question_types"]
#         )
        
#         # Deduplicate concepts
#         failures["concepts_to_review"] = list(set(failures["concepts_to_review"]))
        
#         logger.info(
#             f"Failure analysis: {len(failures['failed_questions'])} failed, "
#             f"{len(failures['concepts_to_review'])} concepts to review"
#         )
        
#         return failures
    
#     def _generate_specific_improvements(
#         self,
#         failed_questions: List[Dict],
#         weak_types: List[Dict]
#     ) -> List[str]:
#         """Generate actionable improvement recommendations"""
#         improvements = []
        
#         # Recommendations based on failed questions
#         if failed_questions:
#             improvements.append(
#                 f"Review the {len(failed_questions)} questions you missed - "
#                 "understanding your mistakes is key to improvement"
#             )
            
#             # Group by type
#             type_counts = Counter(q["type"] for q in failed_questions)
#             for q_type, count in type_counts.most_common(2):
#                 type_name = self._humanize_question_type(q_type)
#                 improvements.append(
#                     f"Practice more {type_name} questions - "
#                     f"you missed {count} in this area"
#                 )
        
#         # Recommendations based on weak types
#         for weak in weak_types:
#             type_name = self._humanize_question_type(weak["type"])
#             improvements.append(
#                 f"Strengthen your {type_name} skills - "
#                 f"currently at {weak['percentage']:.0f}%"
#             )
        
#         return improvements
    
#     def _humanize_question_type(self, q_type: str) -> str:
#         """Convert question type codes to readable names"""
#         type_map = {
#             "mcq": "multiple choice",
#             "multiple_choice": "multiple choice",
#             "true_false": "true/false",
#             "short_answer": "short answer",
#             "essay": "essay",
#             "practical": "practical"
#         }
#         return type_map.get(q_type.lower(), q_type)
    
#     def calculate_content_performance(
#         self,
#         performance_history: List[Dict]
#     ) -> Dict[str, Dict]:
#         """
#         Calculate performance metrics per content area
#         Returns: {content_id: {score: float, content: str, performance: float}}
#         """
#         content_performance = {}
        
#         for record in performance_history:
#             content_id = record.get("content_id", record.get("topic", "unknown"))
#             content_text = record.get("content", record.get("topic", ""))
#             score = record.get("score", 0)
#             max_score = record.get("max_score", 1)
#             normalized_score = score / max_score if max_score > 0 else 0
            
#             if content_id not in content_performance:
#                 content_performance[content_id] = {
#                     "content": content_text,
#                     "scores": [],
#                     "total_score": 0,
#                     "total_max": 0
#                 }
            
#             content_performance[content_id]["scores"].append(normalized_score)
#             content_performance[content_id]["total_score"] += score
#             content_performance[content_id]["total_max"] += max_score
        
#         # Calculate averages
#         for content_id, data in content_performance.items():
#             data["average_performance"] = np.mean(data["scores"])
#             data["overall_percentage"] = (data["total_score"] / data["total_max"] * 100) if data["total_max"] > 0 else 0
        
#         return content_performance
    
#     def identify_content_gaps(
#         self,
#         content_performance: Dict[str, Dict]
#     ) -> Tuple[List[Dict], List[Dict]]:
#         """
#         Identify strong and weak content areas
#         Returns: (strengths, weaknesses) with content details
#         """
#         strengths = []
#         weaknesses = []
        
#         for content_id, data in content_performance.items():
#             performance = data["average_performance"]
#             content_info = {
#                 "content_id": content_id,
#                 "content": data["content"],
#                 "performance": round(performance * 100, 1),
#                 "score": data["total_score"],
#                 "max_score": data["total_max"]
#             }
            
#             if performance >= self.strong_threshold:
#                 strengths.append(content_info)
#             elif performance < self.weak_threshold:
#                 weaknesses.append(content_info)
        
#         # Sort by performance
#         strengths.sort(key=lambda x: x["performance"], reverse=True)
#         weaknesses.sort(key=lambda x: x["performance"])
        
#         return strengths, weaknesses
    
#     def generate_study_plan(
#         self,
#         weaknesses: List[Dict],
#         strengths: List[Dict],
#         content_performance: Dict[str, Dict],
#         failure_analysis: Optional[Dict] = None
#     ) -> Dict:
#         """Create content-focused study plan"""
        
#         # Priority 1: Failed content (below 60%)
#         urgent_content = [w for w in weaknesses if w["performance"] < 50]
        
#         # Priority 2: Weak content (60-79%)
#         improvement_content = [w for w in weaknesses if w["performance"] >= 50]
        
#         # Priority 3: Strong content (80%+)
#         advancement_content = strengths[:3]  # Top 3 strengths
        
#         # Calculate suggested hours based on performance gap
#         urgent_hours = sum(3 * (60 - c["performance"]) / 60 for c in urgent_content) if urgent_content else 0
#         skill_hours = sum(2 * (80 - c["performance"]) / 80 for c in improvement_content) if improvement_content else 0
#         advance_hours = len(advancement_content) * 1.5 if advancement_content else 0
        
#         # Ensure minimums
#         urgent_hours = max(urgent_hours, 2.0) if urgent_content else 0
#         skill_hours = max(skill_hours, 2.0) if improvement_content else 0
#         advance_hours = max(advance_hours, 1.5) if advancement_content else 0
        
#         # Build study plan
#         study_plan = {
#             "urgent_review": {
#                 "content_areas": [
#                     {
#                         "content": c["content"][:200] + "..." if len(c["content"]) > 200 else c["content"],
#                         "current_performance": f"{c['performance']:.1f}%",
#                         "score": f"{c['score']}/{c['max_score']}"
#                     }
#                     for c in urgent_content
#                 ],
#                 "reason": "Critical gaps - immediate attention needed to build foundation",
#                 "suggested_hours": round(urgent_hours, 1),
#                 "specific_actions": []
#             },
#             "skill_building": {
#                 "content_areas": [
#                     {
#                         "content": c["content"][:200] + "..." if len(c["content"]) > 200 else c["content"],
#                         "current_performance": f"{c['performance']:.1f}%",
#                         "score": f"{c['score']}/{c['max_score']}"
#                     }
#                     for c in improvement_content
#                 ],
#                 "reason": "Below mastery - focused practice needed",
#                 "suggested_hours": round(skill_hours, 1),
#                 "specific_actions": []
#             },
#             "advancement": {
#                 "content_areas": [
#                     {
#                         "content": c["content"][:200] + "..." if len(c["content"]) > 200 else c["content"],
#                         "current_performance": f"{c['performance']:.1f}%",
#                         "score": f"{c['score']}/{c['max_score']}"
#                     }
#                     for c in advancement_content
#                 ],
#                 "reason": "Strong foundation - ready for advanced topics",
#                 "suggested_hours": round(advance_hours, 1),
#                 "specific_actions": []
#             }
#         }
        
#         # Add specific actions from failure analysis
#         if failure_analysis:
#             concepts = failure_analysis.get("concepts_to_review", [])
#             weak_types = failure_analysis.get("weak_question_types", [])
            
#             # Add to appropriate section
#             target = "urgent_review" if urgent_content else "skill_building"
            
#             if concepts:
#                 study_plan[target]["specific_actions"].extend([
#                     f"Review and practice: {concept}" for concept in concepts[:5]
#                 ])
            
#             for weak in weak_types[:3]:
#                 action = f"Practice {self._humanize_question_type(weak['type'])} questions (currently {weak['percentage']:.0f}%)"
#                 study_plan[target]["specific_actions"].append(action)
            
#             # Add general improvements
#             improvements = failure_analysis.get("specific_improvements", [])
#             if improvements:
#                 study_plan[target]["specific_actions"].extend(improvements[:2])
        
#         return study_plan
    
#     async def generate_content_insights(
#         self,
#         strengths: List[Dict],
#         weaknesses: List[Dict],
#         content_performance: Dict[str, Dict],
#         failure_analysis: Optional[Dict] = None
#     ) -> Tuple[str, str]:
#         """Generate AI insights based on actual content"""
#         if not self.groq_api_key:
#             return self._fallback_insights(strengths, weaknesses, failure_analysis)
        
#         # Build content summary
#         weak_content_summary = "\n".join([
#             f"- {w['content'][:150]}... (Performance: {w['performance']:.1f}%)"
#             for w in weaknesses[:3]
#         ]) if weaknesses else "None"
        
#         strong_content_summary = "\n".join([
#             f"- {s['content'][:150]}... (Performance: {s['performance']:.1f}%)"
#             for s in strengths[:3]
#         ]) if strengths else "None"
        
#         # Failure context
#         failure_context = ""
#         if failure_analysis:
#             failed_count = len(failure_analysis.get("failed_questions", []))
#             concepts = failure_analysis.get("concepts_to_review", [])
            
#             if concepts:
#                 failure_context = f"""
# Specific Concepts Needing Review:
# {chr(10).join([f"- {c}" for c in concepts[:5]])}

# Questions Missed: {failed_count}
# """
        
#         system_prompt = """You are an expert TVET instructor analyzing student performance on specific learning content.
# Provide concrete, actionable feedback focused on the actual content they studied.
# Be encouraging but specific about what needs improvement."""
        
#         user_prompt = f"""Analyze this student's performance on learning content:

# WEAK AREAS (Need immediate attention):
# {weak_content_summary}

# STRONG AREAS (Well understood):
# {strong_content_summary}

# {failure_context}

# Generate TWO concise paragraphs (2-3 sentences each):
# 1. ANALYSIS: What specific content areas they're struggling with and why
# 2. ENCOURAGEMENT: Motivating message with actionable next steps

# Focus on the actual content, not generic advice."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 300
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     llm_output = result["choices"][0]["message"]["content"].strip()
                    
#                     parts = llm_output.split("\n\n")
#                     analysis = parts[0].strip() if len(parts) > 0 else llm_output
#                     encouragement = parts[1].strip() if len(parts) > 1 else "Keep practicing!"
                    
#                     # Clean markdown
#                     analysis = analysis.replace("**ANALYSIS:**", "").replace("**Analysis:**", "").strip()
#                     encouragement = encouragement.replace("**ENCOURAGEMENT:**", "").replace("**Encouragement:**", "").strip()
                    
#                     return analysis, encouragement
#                 else:
#                     logger.warning(f"LLM API returned status {response.status_code}")
#                     return self._fallback_insights(strengths, weaknesses, failure_analysis)
            
#         except Exception as e:
#             logger.error(f" LLM insights failed: {e}")
#             return self._fallback_insights(strengths, weaknesses, failure_analysis)
    
#     def _fallback_insights(
#         self,
#         strengths: List[Dict],
#         weaknesses: List[Dict],
#         failure_analysis: Optional[Dict] = None
#     ) -> Tuple[str, str]:
#         """Fallback insights with content focus"""
        
#         specific_concepts = ""
#         if failure_analysis:
#             concepts = failure_analysis.get("concepts_to_review", [])
#             if concepts:
#                 specific_concepts = f" Specifically, focus on: {', '.join(concepts[:3])}."
        
#         if weaknesses:
#             weak_summary = ", ".join([w["content"][:50] + "..." for w in weaknesses[:2]])
#             analysis = (
#                 f"Your assessment shows gaps in understanding of {len(weaknesses)} content areas. "
#                 f"The material on {weak_summary} needs more attention.{specific_concepts} "
#                 "Targeted review of these specific topics will strengthen your foundation."
#             )
#             encouragement = (
#                 "Learning technical content takes time and repetition. Focus on understanding "
#                 "the core concepts in your weak areas, and don't hesitate to revisit the material. "
#                 "Each review session builds stronger understanding!"
#             )
#         elif strengths:
#             strong_summary = strengths[0]["content"][:80] + "..."
#             analysis = (
#                 f"Excellent grasp of the material! Your performance on '{strong_summary}' "
#                 f"and {len(strengths)-1} other areas shows solid understanding."
#             )
#             encouragement = (
#                 "You're demonstrating strong comprehension. Keep up this momentum and "
#                 "challenge yourself with more complex problems in these areas!"
#             )
#         else:
#             analysis = "You're building your understanding of these technical concepts."
#             encouragement = (
#                 "Stay consistent with your studies. Technical mastery comes from "
#                 "repeated practice and application of concepts!"
#             )
        
#         return analysis, encouragement
    
#     async def generate_recommendations(
#         self,
#         performance_history: List[Dict],
#         question_results: Optional[List[Dict]] = None
#     ) -> Dict:
#         """Generate content-aware recommendations"""
#         try:
#             logger.info(f"🔍 Generating content-aware recommendations for {len(performance_history)} records")
            
#             if not performance_history:
#                 raise ValueError("Performance history cannot be empty")
            
#             # STEP 1: Analyze question failures
#             failure_analysis = None
#             if question_results:
#                 failure_analysis = self.analyze_question_failures(question_results)
#                 logger.info(f"Analyzed {len(question_results)} questions")
            
#             # STEP 2: Calculate content-based performance
#             content_performance = self.calculate_content_performance(performance_history)
            
#             # STEP 3: Identify content gaps
#             strengths, weaknesses = self.identify_content_gaps(content_performance)
            
#             # STEP 4: Generate study plan
#             study_plan = self.generate_study_plan(
#                 weaknesses, strengths, content_performance, failure_analysis
#             )
            
#             # STEP 5: Generate AI insights
#             analysis, encouragement = await self.generate_content_insights(
#                 strengths, weaknesses, content_performance, failure_analysis
#             )
            
#             # STEP 6: Compile recommendations
#             content_recommendations = [
#                 {"content": w["content"], "performance": w["performance"]}
#                 for w in weaknesses
#             ]
            
#             result = {
#                 "content_recommendations": content_recommendations,
#                 "study_plan": study_plan,
#                 "strengths": [{"content": s["content"], "performance": s["performance"]} for s in strengths],
#                 "weaknesses": [{"content": w["content"], "performance": w["performance"]} for w in weaknesses],
#                 "analysis": analysis,
#                 "encouragement": encouragement,
#                 "failure_analysis": failure_analysis
#             }
            
#             logger.info(
#                 f" Recommendations generated: {len(weaknesses)} weak areas, "
#                 f"{len(strengths)} strong areas"
#             )
            
#             return result
            
#         except Exception as e:
#             logger.error(f"Recommendation generation failed: {e}", exc_info=True)
#             raise










# """
# Module-Based Recommendation Service
# Analyzes individual module performance and provides targeted feedback
# Location: app/services/recommendation_service.py
# """

# import os
# import httpx
# from typing import List, Dict, Optional, Tuple
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from collections import Counter

# load_dotenv()


# class RecommendationService:
#     """
#     Module-focused recommendation system that analyzes:
#     1. Individual module performance
#     2. Question-level failures
#     3. Critical gaps in understanding
#     4. Collective performance feedback
#     """
    
#     def __init__(self):
#         self.groq_api_key = os.getenv("GROQAPI_KEY")
#         if not self.groq_api_key:
#             logger.warning(" GROQAPI_KEY not found. Will use fallback recommendations.")
        
#         self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
#         logger.info("Module-Based RecommendationService initialized")
    
#     def analyze_module_performance(
#         self,
#         module_content: str,
#         max_score: float,
#         question_results: List[Dict]
#     ) -> Dict:
#         """
#         Analyze performance on a single module
        
#         Args:
#             module_content: The actual learning content of the module
#             max_score: Maximum possible score for the module
#             question_results: List of question results with student answers
            
#         Returns:
#             Individual module analysis with feedback
#         """
#         # Calculate module score
#         total_awarded = sum(q.get("awarded_marks", 0) for q in question_results)
#         percentage = (total_awarded / max_score * 100) if max_score > 0 else 0
        
#         # Analyze question failures
#         failed_questions = []
#         concepts_to_review = []
#         question_type_performance = {}
        
#         for q in question_results:
#             q_type = q.get("question_type", "unknown")
#             awarded = q.get("awarded_marks", 0)
#             max_marks = q.get("max_marks", 1)
#             is_correct = q.get("is_correct", False)
            
#             # Track by type
#             if q_type not in question_type_performance:
#                 question_type_performance[q_type] = {"correct": 0, "total": 0}
            
#             question_type_performance[q_type]["total"] += 1
#             if is_correct:
#                 question_type_performance[q_type]["correct"] += 1
            
#             # Identify failures
#             if not is_correct or awarded < max_marks * 0.7:
#                 failed_questions.append({
#                     "question_text": q.get("question_text", ""),
#                     "student_answer": q.get("student_answer", ""),
#                     "correct_answer": q.get("correct_answer", ""),
#                     "awarded_marks": awarded,
#                     "max_marks": max_marks,
#                     "question_type": q_type
#                 })
                
#                 # Extract concepts from question content
#                 concepts_to_review.append(q.get("question_text", "")[:100])
        
#         # Performance level
#         if percentage >= 80:
#             performance_level = "Excellent"
#         elif percentage >= 70:
#             performance_level = "Good"
#         elif percentage >= 60:
#             performance_level = "Satisfactory"
#         else:
#             performance_level = "Needs Improvement"
        
#         return {
#             "module_content": module_content[:300] + "..." if len(module_content) > 300 else module_content,
#             "total_score": total_awarded,
#             "max_score": max_score,
#             "percentage": round(percentage, 1),
#             "performance_level": performance_level,
#             "total_questions": len(question_results),
#             "failed_questions": len(failed_questions),
#             "failed_question_details": failed_questions,
#             "question_type_performance": question_type_performance,
#             "concepts_to_review": concepts_to_review[:5]
#         }
    
#     def identify_critical_gaps(
#         self,
#         module_analyses: List[Dict]
#     ) -> Dict:
#         """
#         Identify critical gaps across all modules
        
#         Args:
#             module_analyses: List of individual module analyses
            
#         Returns:
#             Critical gaps and patterns
#         """
#         all_failed_questions = []
#         weak_modules = []
#         strong_modules = []
#         all_question_types = {}
        
#         for analysis in module_analyses:
#             percentage = analysis["percentage"]
            
#             # Categorize modules
#             if percentage < 60:
#                 weak_modules.append({
#                     "content": analysis["module_content"],
#                     "percentage": percentage,
#                     "failed_count": analysis["failed_questions"]
#                 })
#             elif percentage >= 80:
#                 strong_modules.append({
#                     "content": analysis["module_content"],
#                     "percentage": percentage
#                 })
            
#             # Collect failed questions
#             all_failed_questions.extend(analysis["failed_question_details"])
            
#             # Aggregate question type performance
#             for q_type, stats in analysis["question_type_performance"].items():
#                 if q_type not in all_question_types:
#                     all_question_types[q_type] = {"correct": 0, "total": 0}
#                 all_question_types[q_type]["correct"] += stats["correct"]
#                 all_question_types[q_type]["total"] += stats["total"]
        
#         # Identify weak question types
#         weak_question_types = []
#         for q_type, stats in all_question_types.items():
#             percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
#             if percentage < 70:
#                 weak_question_types.append({
#                     "type": q_type,
#                     "percentage": round(percentage, 1),
#                     "attempted": stats["total"]
#                 })
        
#         # Most common mistakes
#         mistake_patterns = []
#         if all_failed_questions:
#             # Group by similar patterns (simplified - could use more advanced analysis)
#             mistake_patterns = [
#                 f"Struggled with {q['question_type']} questions"
#                 for q in all_failed_questions[:3]
#             ]
        
#         return {
#             "weak_modules": weak_modules,
#             "strong_modules": strong_modules,
#             "weak_question_types": weak_question_types,
#             "total_failed_questions": len(all_failed_questions),
#             "critical_gaps": mistake_patterns,
#             "overall_performance": self._calculate_overall_performance(module_analyses)
#         }
    
#     def _calculate_overall_performance(self, module_analyses: List[Dict]) -> Dict:
#         """Calculate overall performance across all modules"""
#         if not module_analyses:
#             return {"percentage": 0, "level": "No Data"}
        
#         total_score = sum(m["total_score"] for m in module_analyses)
#         total_max = sum(m["max_score"] for m in module_analyses)
#         percentage = (total_score / total_max * 100) if total_max > 0 else 0
        
#         if percentage >= 80:
#             level = "Excellent"
#         elif percentage >= 70:
#             level = "Good"
#         elif percentage >= 60:
#             level = "Satisfactory"
#         else:
#             level = "Needs Improvement"
        
#         return {
#             "total_score": total_score,
#             "total_max": total_max,
#             "percentage": round(percentage, 1),
#             "level": level
#         }
    
#     async def generate_module_feedback(
#         self,
#         module_analysis: Dict
#     ) -> str:
#         """Generate AI feedback for individual module"""
#         if not self.groq_api_key:
#             return self._fallback_module_feedback(module_analysis)
        
#         system_prompt = """You are a supportive TVET instructor providing feedback on module performance.
# Be specific about what the student did well and what needs improvement.
# Keep feedback concise (2-3 sentences) and actionable."""
        
#         failed_details = "\n".join([
#             f"- Question: {q['question_text'][:100]}... (Got: {q['student_answer']}, Correct: {q['correct_answer']})"
#             for q in module_analysis["failed_question_details"][:3]
#         ]) if module_analysis["failed_question_details"] else "None"
        
#         user_prompt = f"""Module Performance Analysis:
# Module Content: {module_analysis['module_content']}
# Score: {module_analysis['total_score']}/{module_analysis['max_score']} ({module_analysis['percentage']}%)
# Performance Level: {module_analysis['performance_level']}
# Questions Failed: {module_analysis['failed_questions']}/{module_analysis['total_questions']}

# Failed Questions:
# {failed_details}

# Generate specific feedback (2-3 sentences) on:
# 1. What the student understood well
# 2. What specific concepts need more work
# 3. One actionable recommendation"""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 200
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     return result["choices"][0]["message"]["content"].strip()
#                 else:
#                     return self._fallback_module_feedback(module_analysis)
            
#         except Exception as e:
#             logger.error(f" Module feedback generation failed: {e}")
#             return self._fallback_module_feedback(module_analysis)
    
#     def _fallback_module_feedback(self, module_analysis: Dict) -> str:
#         """Fallback feedback when AI is unavailable"""
#         percentage = module_analysis["percentage"]
#         failed = module_analysis["failed_questions"]
#         total = module_analysis["total_questions"]
        
#         if percentage >= 80:
#             return f"Excellent work on this module! You scored {percentage}% and demonstrated strong understanding of the concepts. Keep up this level of performance."
#         elif percentage >= 70:
#             return f"Good performance with {percentage}%. You missed {failed} out of {total} questions. Review the specific concepts from those questions to strengthen your understanding."
#         elif percentage >= 60:
#             return f"Satisfactory effort with {percentage}%. Focus on reviewing the {failed} questions you missed, particularly the core concepts. Additional practice will help solidify your knowledge."
#         else:
#             return f"This module needs more attention - you scored {percentage}%. Review the learning material carefully, especially the areas covered in the {failed} questions you missed. Consider revisiting the fundamental concepts before moving forward."
    
#     async def generate_collective_feedback(
#         self,
#         critical_gaps: Dict,
#         module_analyses: List[Dict]
#     ) -> Tuple[str, str]:
#         """Generate overall feedback and recommendations"""
#         if not self.groq_api_key:
#             return self._fallback_collective_feedback(critical_gaps, module_analyses)
        
#         system_prompt = """You are an experienced TVET instructor providing comprehensive performance feedback.
# Analyze patterns across multiple modules and provide actionable guidance.
# Be encouraging but honest about areas needing improvement."""
        
#         weak_modules_summary = "\n".join([
#             f"- {m['content'][:100]}... ({m['percentage']:.1f}%, {m['failed_count']} questions failed)"
#             for m in critical_gaps["weak_modules"]
#         ]) if critical_gaps["weak_modules"] else "None"
        
#         strong_modules_summary = "\n".join([
#             f"- {m['content'][:100]}... ({m['percentage']:.1f}%)"
#             for m in critical_gaps["strong_modules"]
#         ]) if critical_gaps["strong_modules"] else "None"
        
#         user_prompt = f"""Overall Performance Analysis:
# Overall Score: {critical_gaps['overall_performance']['total_score']}/{critical_gaps['overall_performance']['total_max']} ({critical_gaps['overall_performance']['percentage']:.1f}%)
# Performance Level: {critical_gaps['overall_performance']['level']}

# Weak Modules (Need Immediate Attention):
# {weak_modules_summary}

# Strong Modules (Well Understood):
# {strong_modules_summary}

# Weak Question Types:
# {', '.join([f"{qt['type']} ({qt['percentage']:.1f}%)" for qt in critical_gaps['weak_question_types']]) if critical_gaps['weak_question_types'] else 'None'}

# Total Failed Questions: {critical_gaps['total_failed_questions']}

# Generate TWO paragraphs (3-4 sentences each):
# 1. CRITICAL GAPS: Identify the most important areas the student needs to focus on
# 2. RECOMMENDATIONS: Specific, actionable steps to improve performance"""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 350
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     output = result["choices"][0]["message"]["content"].strip()
                    
#                     parts = output.split("\n\n")
#                     critical_gaps_text = parts[0].strip() if len(parts) > 0 else output
#                     recommendations = parts[1].strip() if len(parts) > 1 else "Keep practicing and reviewing the material."
                    
#                     # Clean markdown
#                     critical_gaps_text = critical_gaps_text.replace("**CRITICAL GAPS:**", "").replace("**Critical Gaps:**", "").strip()
#                     recommendations = recommendations.replace("**RECOMMENDATIONS:**", "").replace("**Recommendations:**", "").strip()
                    
#                     return critical_gaps_text, recommendations
#                 else:
#                     return self._fallback_collective_feedback(critical_gaps, module_analyses)
            
#         except Exception as e:
#             logger.error(f"Collective feedback generation failed: {e}")
#             return self._fallback_collective_feedback(critical_gaps, module_analyses)
    
#     def _fallback_collective_feedback(
#         self,
#         critical_gaps: Dict,
#         module_analyses: List[Dict]
#     ) -> Tuple[str, str]:
#         """Fallback collective feedback"""
#         overall = critical_gaps["overall_performance"]
#         weak_count = len(critical_gaps["weak_modules"])
        
#         if weak_count > 0:
#             weak_list = ", ".join([m["content"][:50] + "..." for m in critical_gaps["weak_modules"][:2]])
#             gaps = f"You have critical gaps in {weak_count} modules: {weak_list}. These areas scored below 60% and need immediate attention. Focus on understanding the core concepts before moving to advanced topics."
            
#             recommendations = f"Start by thoroughly reviewing the modules where you scored below 60%. Re-read the learning materials, practice the question types you struggled with, and seek help on concepts you don't understand. Dedicate at least 2-3 hours per weak module for review and practice."
#         else:
#             gaps = f"Your overall performance is {overall['level']} with {overall['percentage']:.1f}%. You're showing good understanding across most modules."
#             recommendations = "Continue your current study approach. Focus on maintaining consistency and challenging yourself with more advanced problems in your strong areas."
        
#         return gaps, recommendations
    
#     async def generate_recommendations(
#         self,
#         modules: List[Dict]
#     ) -> Dict:
#         """
#         Generate comprehensive recommendations for all modules
        
#         Args:
#             modules: List of modules, each containing:
#                 - module_content: str
#                 - max_score: float
#                 - question_results: List[Dict]
                
#         Returns:
#             Complete recommendation with individual and collective feedback
#         """
#         try:
#             logger.info(f"🔍 Analyzing {len(modules)} module(s)")
            
#             # Analyze each module individually
#             module_analyses = []
#             module_feedbacks = []
            
#             for idx, module in enumerate(modules):
#                 logger.info(f" Analyzing module {idx + 1}/{len(modules)}")
                
#                 analysis = self.analyze_module_performance(
#                     module_content=module.get("module_content", ""),
#                     max_score=module.get("max_score", 0),
#                     question_results=module.get("question_results", [])
#                 )
                
#                 # Generate AI feedback for this module
#                 feedback = await self.generate_module_feedback(analysis)
                
#                 module_analyses.append(analysis)
#                 module_feedbacks.append({
#                     "module_content": analysis["module_content"],
#                     "score": f"{analysis['total_score']}/{analysis['max_score']}",
#                     "percentage": analysis["percentage"],
#                     "performance_level": analysis["performance_level"],
#                     "feedback": feedback,
#                     "failed_questions": analysis["failed_questions"],
#                     "concepts_to_review": analysis["concepts_to_review"]
#                 })
            
#             # Identify critical gaps across all modules
#             critical_gaps = self.identify_critical_gaps(module_analyses)
            
#             # Generate collective feedback
#             gaps_analysis, recommendations = await self.generate_collective_feedback(
#                 critical_gaps, module_analyses
#             )
            
#             result = {
#                 "individual_module_reviews": module_feedbacks,
#                 "collective_feedback": {
#                     "overall_performance": critical_gaps["overall_performance"],
#                     "critical_gaps": gaps_analysis,
#                     "recommendations": recommendations,
#                     "weak_modules": critical_gaps["weak_modules"],
#                     "strong_modules": critical_gaps["strong_modules"],
#                     "weak_question_types": critical_gaps["weak_question_types"],
#                     "total_failed_questions": critical_gaps["total_failed_questions"]
#                 }
#             }
            
#             logger.info(f"Recommendations generated successfully")
            
#             return result
            
#         except Exception as e:
#             logger.error(f"Recommendation generation failed: {e}", exc_info=True)
#             raise









            # Version 5






"""
Module-Based Recommendation Service - FIXED
Location: app/services/recommendation_service.py
"""

# import os
# import httpx
# from typing import List, Dict, Optional, Tuple
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from collections import Counter
# import re

# load_dotenv()


# class RecommendationService:
#     """Module-focused recommendation system"""
    
#     def __init__(self):
#         self.groq_api_key = os.getenv("GROQAPI_KEY")
#         if not self.groq_api_key:
#             logger.warning(" GROQAPI_KEY not found. Will use fallback recommendations.")
        
#         self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
#         logger.info("Module-Based RecommendationService initialized")
    
#     def _clean_markdown(self, text: str) -> str:
#         """Remove all markdown formatting from text"""
#         # Remove bold/italic
#         text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)
#         # Remove headers
#         text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
#         # Remove numbered lists at start
#         text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
#         # Clean up extra whitespace
#         text = re.sub(r'\n\s*\n', '\n\n', text)
#         return text.strip()
    
#     def analyze_module_performance(
#         self,
#         module_id: str,
#         module_name: str,
#         module_content: str,
#         max_score: float,
#         question_results: List[Dict]
#     ) -> Dict:
#         """Analyze performance on a single module"""
        
#         # Calculate module score
#         total_awarded = sum(q.get("awarded_marks", 0) for q in question_results)
#         percentage = (total_awarded / max_score * 100) if max_score > 0 else 0
        
#         # Analyze question failures
#         failed_questions = []
#         concepts_to_review = []
#         question_type_performance = {}
        
#         for q in question_results:
#             q_type = q.get("question_type", "unknown")
#             awarded = q.get("awarded_marks", 0)
#             max_marks = q.get("max_marks", 1)
#             is_correct = q.get("is_correct", False)
            
#             # Track by type
#             if q_type not in question_type_performance:
#                 question_type_performance[q_type] = {"correct": 0, "total": 0}
            
#             question_type_performance[q_type]["total"] += 1
#             if is_correct:
#                 question_type_performance[q_type]["correct"] += 1
            
#             # Identify failures
#             if not is_correct or awarded < max_marks * 0.7:
#                 failed_questions.append({
#                     "question_text": q.get("question_text", ""),
#                     "student_answer": q.get("student_answer", ""),
#                     "correct_answer": q.get("correct_answer", ""),
#                     "awarded_marks": awarded,
#                     "max_marks": max_marks,
#                     "question_type": q_type
#                 })
                
#                 # Extract concepts (first 80 chars of question)
#                 question_text = q.get("question_text", "")
#                 if question_text:
#                     concepts_to_review.append(question_text[:80])
        
#         # Performance level
#         if percentage >= 80:
#             performance_level = "Excellent"
#         elif percentage >= 70:
#             performance_level = "Good"
#         elif percentage >= 60:
#             performance_level = "Satisfactory"
#         else:
#             performance_level = "Needs Improvement"
        
#         return {
#             "module_id": module_id,
#             "module_name": module_name,
#             "module_content": module_content,  # Keep for AI analysis
#             "total_score": total_awarded,
#             "max_score": max_score,
#             "percentage": round(percentage, 1),
#             "performance_level": performance_level,
#             "total_questions": len(question_results),
#             "failed_questions": len(failed_questions),
#             "failed_question_details": failed_questions,
#             "question_type_performance": question_type_performance,
#             "concepts_to_review": concepts_to_review[:5]
#         }
    
#     def identify_critical_gaps(
#         self,
#         module_analyses: List[Dict]
#     ) -> Dict:
#         """Identify critical gaps across all modules"""
        
#         all_failed_questions = []
#         weak_modules = []
#         strong_modules = []
#         all_question_types = {}
        
#         for analysis in module_analyses:
#             percentage = analysis["percentage"]
#             module_id = analysis["module_id"]
#             module_name = analysis["module_name"]
            
#             # Categorize modules
#             if percentage < 60:
#                 weak_modules.append({
#                     "module_id": module_id,
#                     "module_name": module_name,
#                     "percentage": percentage,
#                     "failed_count": analysis["failed_questions"]
#                 })
#             elif percentage >= 80:
#                 strong_modules.append({
#                     "module_id": module_id,
#                     "module_name": module_name,
#                     "percentage": percentage
#                 })
            
#             # Collect failed questions
#             all_failed_questions.extend(analysis["failed_question_details"])
            
#             # Aggregate question type performance
#             for q_type, stats in analysis["question_type_performance"].items():
#                 if q_type not in all_question_types:
#                     all_question_types[q_type] = {"correct": 0, "total": 0}
#                 all_question_types[q_type]["correct"] += stats["correct"]
#                 all_question_types[q_type]["total"] += stats["total"]
        
#         # Identify weak question types
#         weak_question_types = []
#         for q_type, stats in all_question_types.items():
#             percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
#             if percentage < 70:
#                 weak_question_types.append({
#                     "type": q_type,
#                     "percentage": round(percentage, 1),
#                     "attempted": stats["total"]
#                 })
        
#         return {
#             "weak_modules": weak_modules,
#             "strong_modules": strong_modules,
#             "weak_question_types": weak_question_types,
#             "total_failed_questions": len(all_failed_questions),
#             "overall_performance": self._calculate_overall_performance(module_analyses)
#         }
    
#     def _calculate_overall_performance(self, module_analyses: List[Dict]) -> Dict:
#         """Calculate overall performance across all modules"""
#         if not module_analyses:
#             return {"percentage": 0, "level": "No Data"}
        
#         total_score = sum(m["total_score"] for m in module_analyses)
#         total_max = sum(m["max_score"] for m in module_analyses)
#         percentage = (total_score / total_max * 100) if total_max > 0 else 0
        
#         if percentage >= 80:
#             level = "Excellent"
#         elif percentage >= 70:
#             level = "Good"
#         elif percentage >= 60:
#             level = "Satisfactory"
#         else:
#             level = "Needs Improvement"
        
#         return {
#             "total_score": total_score,
#             "total_max": total_max,
#             "percentage": round(percentage, 1),
#             "level": level
#         }
    
#     async def generate_module_feedback(
#         self,
#         module_analysis: Dict
#     ) -> str:
#         """Generate AI feedback for individual module"""
#         if not self.groq_api_key:
#             return self._fallback_module_feedback(module_analysis)
        
#         system_prompt = """You are a supportive TVET instructor providing feedback on module performance.
# Be specific, constructive, and encouraging. Write in plain text without any markdown formatting.
# Keep feedback concise (3-4 sentences) and actionable."""
        
#         failed_details = "\n".join([
#             f"Question: {q['question_text'][:100]} | Student: {q['student_answer']} | Correct: {q['correct_answer']}"
#             for q in module_analysis["failed_question_details"][:3]
#         ]) if module_analysis["failed_question_details"] else "None"
        
#         user_prompt = f"""Module: {module_analysis['module_name']}
# Score: {module_analysis['total_score']}/{module_analysis['max_score']} ({module_analysis['percentage']}%)
# Performance Level: {module_analysis['performance_level']}
# Questions Failed: {module_analysis['failed_questions']}/{module_analysis['total_questions']}

# Failed Questions:
# {failed_details}

# Provide specific feedback (3-4 sentences) covering:
# 1. What they did well
# 2. What needs improvement
# 3. One concrete action to improve

# Write in plain text without markdown, bullets, or numbering."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 200
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     feedback = result["choices"][0]["message"]["content"].strip()
#                     return self._clean_markdown(feedback)
#                 else:
#                     return self._fallback_module_feedback(module_analysis)
            
#         except Exception as e:
#             logger.error(f" Module feedback generation failed: {e}")
#             return self._fallback_module_feedback(module_analysis)
    
#     def _fallback_module_feedback(self, module_analysis: Dict) -> str:
#         """Fallback feedback when AI is unavailable"""
#         percentage = module_analysis["percentage"]
#         failed = module_analysis["failed_questions"]
#         total = module_analysis["total_questions"]
        
#         if percentage >= 80:
#             return f"Excellent work on this module! You scored {percentage}% and demonstrated strong understanding of the concepts. Keep up this level of performance."
#         elif percentage >= 70:
#             return f"Good performance with {percentage}%. You missed {failed} out of {total} questions. Review the specific concepts from those questions to strengthen your understanding."
#         elif percentage >= 60:
#             return f"Satisfactory effort with {percentage}%. Focus on reviewing the {failed} questions you missed, particularly the core concepts. Additional practice will help solidify your knowledge."
#         else:
#             return f"This module needs more attention. You scored {percentage}%. Review the learning material carefully, especially the areas covered in the {failed} questions you missed. Consider revisiting the fundamental concepts before moving forward."
    
#     async def generate_collective_feedback(
#         self,
#         critical_gaps: Dict,
#         module_analyses: List[Dict]
#     ) -> Tuple[str, str]:
#         """Generate overall feedback and recommendations"""
#         if not self.groq_api_key:
#             return self._fallback_collective_feedback(critical_gaps, module_analyses)
        
#         system_prompt = """You are an experienced TVET instructor providing comprehensive performance feedback.
# Analyze patterns across modules and provide actionable guidance.
# Write in plain text without markdown formatting, bullets, or numbering.
# Be encouraging but honest about areas needing improvement."""
        
#         weak_modules_summary = "\n".join([
#             f"{m['module_name']}: {m['percentage']:.1f}% ({m['failed_count']} questions failed)"
#             for m in critical_gaps["weak_modules"]
#         ]) if critical_gaps["weak_modules"] else "None"
        
#         strong_modules_summary = "\n".join([
#             f"{m['module_name']}: {m['percentage']:.1f}%"
#             for m in critical_gaps["strong_modules"]
#         ]) if critical_gaps["strong_modules"] else "None"
        
#         user_prompt = f"""Overall Performance: {critical_gaps['overall_performance']['total_score']}/{critical_gaps['overall_performance']['total_max']} ({critical_gaps['overall_performance']['percentage']:.1f}%)
# Level: {critical_gaps['overall_performance']['level']}

# Weak Modules:
# {weak_modules_summary}

# Strong Modules:
# {strong_modules_summary}

# Total Failed Questions: {critical_gaps['total_failed_questions']}

# Write TWO paragraphs (3-4 sentences each) in plain text:
# 1. Identify the most critical gaps and patterns
# 2. Provide specific, actionable steps to improve

# No markdown, no bullets, just clear prose."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 350
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     output = result["choices"][0]["message"]["content"].strip()
#                     output = self._clean_markdown(output)
                    
#                     parts = output.split("\n\n")
#                     critical_gaps_text = parts[0].strip() if len(parts) > 0 else output
#                     recommendations = parts[1].strip() if len(parts) > 1 else "Keep practicing and reviewing the material."
                    
#                     return critical_gaps_text, recommendations
#                 else:
#                     return self._fallback_collective_feedback(critical_gaps, module_analyses)
            
#         except Exception as e:
#             logger.error(f" Collective feedback generation failed: {e}")
#             return self._fallback_collective_feedback(critical_gaps, module_analyses)
    
#     def _fallback_collective_feedback(
#         self,
#         critical_gaps: Dict,
#         module_analyses: List[Dict]
#     ) -> Tuple[str, str]:
#         """Fallback collective feedback"""
#         overall = critical_gaps["overall_performance"]
#         weak_count = len(critical_gaps["weak_modules"])
        
#         if weak_count > 0:
#             weak_list = ", ".join([m["module_name"] for m in critical_gaps["weak_modules"][:2]])
#             gaps = f"You have critical gaps in {weak_count} modules: {weak_list}. These areas scored below 60% and need immediate attention. Focus on understanding the core concepts before moving to advanced topics."
            
#             recommendations = f"Start by thoroughly reviewing the modules where you scored below 60%. Re-read the learning materials, practice the question types you struggled with, and seek help on concepts you don't understand. Dedicate at least 2-3 hours per weak module for review and practice."
#         else:
#             gaps = f"Your overall performance is {overall['level']} with {overall['percentage']:.1f}%. You're showing good understanding across most modules."
#             recommendations = "Continue your current study approach. Focus on maintaining consistency and challenging yourself with more advanced problems in your strong areas."
        
#         return gaps, recommendations
    
#     async def generate_recommendations(
#         self,
#         modules: List[Dict]
#     ) -> Dict:
#         """Generate comprehensive recommendations for all modules"""
#         try:
#             logger.info(f" Analyzing {len(modules)} module(s)")
            
#             # Analyze each module individually
#             module_analyses = []
#             module_feedbacks = []
            
#             for idx, module in enumerate(modules):
#                 logger.info(f"Analyzing module {idx + 1}/{len(modules)}")
                
#                 analysis = self.analyze_module_performance(
#                     module_id=module.get("module_id", f"module_{idx+1}"),
#                     module_name=module.get("module_name", f"Module {idx+1}"),
#                     module_content=module.get("module_content", ""),
#                     max_score=module.get("max_score", 0),
#                     question_results=module.get("question_results", [])
#                 )
                
#                 # Generate AI feedback for this module
#                 feedback = await self.generate_module_feedback(analysis)
                
#                 module_analyses.append(analysis)
#                 module_feedbacks.append({
#                     "module_id": analysis["module_id"],
#                     "module_name": analysis["module_name"],
#                     "score": f"{analysis['total_score']}/{analysis['max_score']}",
#                     "percentage": analysis["percentage"],
#                     "performance_level": analysis["performance_level"],
#                     "feedback": feedback,
#                     "failed_questions": analysis["failed_questions"],
#                     "concepts_to_review": analysis["concepts_to_review"]
#                 })
            
#             # Identify critical gaps across all modules
#             critical_gaps = self.identify_critical_gaps(module_analyses)
            
#             # Generate collective feedback
#             gaps_analysis, recommendations = await self.generate_collective_feedback(
#                 critical_gaps, module_analyses
#             )
            
#             result = {
#                 "individual_module_reviews": module_feedbacks,
#                 "collective_feedback": {
#                     "overall_performance": critical_gaps["overall_performance"],
#                     "critical_gaps": gaps_analysis,
#                     "recommendations": recommendations,
#                     "weak_modules": critical_gaps["weak_modules"],
#                     "strong_modules": critical_gaps["strong_modules"],
#                     "weak_question_types": critical_gaps["weak_question_types"],
#                     "total_failed_questions": critical_gaps["total_failed_questions"]
#                 }
#             }
            
#             logger.info(f" Recommendations generated successfully")
            
#             return result
            
#         except Exception as e:
#             logger.error(f" Recommendation generation failed: {e}", exc_info=True)
#             raise











# VERSION 7









"""
Module-Based Recommendation Service - SPECIFIC FEEDBACK
Location: app/services/recommendation_service.py
"""

# import os
# import httpx
# from typing import List, Dict, Optional, Tuple
# from dotenv import load_dotenv
# from app.core.logging_config import logger
# from collections import Counter
# import re

# load_dotenv()


# class RecommendationService:
#     """Module-focused recommendation system with specific, actionable feedback"""
    
#     def __init__(self):
#         self.groq_api_key = os.getenv("GROQAPI_KEY")
#         if not self.groq_api_key:
#             logger.warning(" GROQAPI_KEY not found. Will use fallback recommendations.")
        
#         self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
#         logger.info(" Module-Based RecommendationService initialized")
    
#     def _clean_markdown(self, text: str) -> str:
#         """Remove all markdown formatting from text"""
#         text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)
#         text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
#         text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
#         text = re.sub(r'\n\s*\n', '\n\n', text)
#         return text.strip()
    
#     def analyze_module_performance(
#         self,
#         module_id: str,
#         module_name: str,
#         module_content: str,
#         max_score: float,
#         question_results: List[Dict]
#     ) -> Dict:
#         """Analyze performance on a single module"""
        
#         total_awarded = sum(q.get("awarded_marks", 0) for q in question_results)
#         percentage = (total_awarded / max_score * 100) if max_score > 0 else 0
        
#         failed_questions = []
#         concepts_to_review = []
#         question_type_performance = {}
        
#         for q in question_results:
#             q_type = q.get("question_type", "unknown")
#             awarded = q.get("awarded_marks", 0)
#             max_marks = q.get("max_marks", 1)
#             is_correct = q.get("is_correct", False)
            
#             if q_type not in question_type_performance:
#                 question_type_performance[q_type] = {"correct": 0, "total": 0}
            
#             question_type_performance[q_type]["total"] += 1
#             if is_correct:
#                 question_type_performance[q_type]["correct"] += 1
            
#             if not is_correct or awarded < max_marks * 0.7:
#                 failed_questions.append({
#                     "question_text": q.get("question_text", ""),
#                     "student_answer": q.get("student_answer", ""),
#                     "correct_answer": q.get("correct_answer", ""),
#                     "awarded_marks": awarded,
#                     "max_marks": max_marks,
#                     "question_type": q_type
#                 })
                
#                 question_text = q.get("question_text", "")
#                 if question_text:
#                     concepts_to_review.append(question_text[:80])
        
#         if percentage >= 80:
#             performance_level = "Excellent"
#         elif percentage >= 70:
#             performance_level = "Good"
#         elif percentage >= 60:
#             performance_level = "Satisfactory"
#         else:
#             performance_level = "Needs Improvement"
        
#         return {
#             "module_id": module_id,
#             "module_name": module_name,
#             "module_content": module_content,
#             "total_score": total_awarded,
#             "max_score": max_score,
#             "percentage": round(percentage, 1),
#             "performance_level": performance_level,
#             "total_questions": len(question_results),
#             "failed_questions": len(failed_questions),
#             "failed_question_details": failed_questions,
#             "question_type_performance": question_type_performance,
#             "concepts_to_review": concepts_to_review[:5]
#         }
    
#     def identify_critical_gaps(
#         self,
#         module_analyses: List[Dict]
#     ) -> Dict:
#         """Identify critical gaps across all modules"""
        
#         all_failed_questions = []
#         weak_modules = []
#         strong_modules = []
#         all_question_types = {}
        
#         for analysis in module_analyses:
#             percentage = analysis["percentage"]
#             module_id = analysis["module_id"]
#             module_name = analysis["module_name"]
            
#             if percentage < 60:
#                 weak_modules.append({
#                     "module_id": module_id,
#                     "module_name": module_name,
#                     "percentage": percentage,
#                     "failed_count": analysis["failed_questions"],
#                     "content": analysis["module_content"]  # Keep for AI analysis
#                 })
#             elif percentage >= 80:
#                 strong_modules.append({
#                     "module_id": module_id,
#                     "module_name": module_name,
#                     "percentage": percentage,
#                     "content": analysis["module_content"]
#                 })
            
#             all_failed_questions.extend(analysis["failed_question_details"])
            
#             for q_type, stats in analysis["question_type_performance"].items():
#                 if q_type not in all_question_types:
#                     all_question_types[q_type] = {"correct": 0, "total": 0}
#                 all_question_types[q_type]["correct"] += stats["correct"]
#                 all_question_types[q_type]["total"] += stats["total"]
        
#         weak_question_types = []
#         for q_type, stats in all_question_types.items():
#             percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
#             if percentage < 70:
#                 weak_question_types.append({
#                     "type": q_type,
#                     "percentage": round(percentage, 1),
#                     "attempted": stats["total"]
#                 })
        
#         return {
#             "weak_modules": weak_modules,
#             "strong_modules": strong_modules,
#             "weak_question_types": weak_question_types,
#             "total_failed_questions": len(all_failed_questions),
#             "all_failed_questions": all_failed_questions,
#             "overall_performance": self._calculate_overall_performance(module_analyses)
#         }
    
#     def _calculate_overall_performance(self, module_analyses: List[Dict]) -> Dict:
#         """Calculate overall performance across all modules"""
#         if not module_analyses:
#             return {"percentage": 0, "level": "No Data"}
        
#         total_score = sum(m["total_score"] for m in module_analyses)
#         total_max = sum(m["max_score"] for m in module_analyses)
#         percentage = (total_score / total_max * 100) if total_max > 0 else 0
        
#         if percentage >= 80:
#             level = "Excellent"
#         elif percentage >= 70:
#             level = "Good"
#         elif percentage >= 60:
#             level = "Satisfactory"
#         else:
#             level = "Needs Improvement"
        
#         return {
#             "total_score": total_score,
#             "total_max": total_max,
#             "percentage": round(percentage, 1),
#             "level": level
#         }
    
#     async def generate_module_feedback(
#         self,
#         module_analysis: Dict
#     ) -> str:
#         """Generate AI feedback for individual module"""
#         if not self.groq_api_key:
#             return self._fallback_module_feedback(module_analysis)
        
#         system_prompt = """You are a supportive TVET instructor providing feedback on module performance.
# Be specific, constructive, and encouraging. Write in plain text without any markdown formatting.
# Keep feedback concise (3-4 sentences) and actionable."""
        
#         failed_details = "\n".join([
#             f"Question: {q['question_text'][:100]} | Student: {q['student_answer']} | Correct: {q['correct_answer']}"
#             for q in module_analysis["failed_question_details"][:3]
#         ]) if module_analysis["failed_question_details"] else "None"
        
#         user_prompt = f"""Module: {module_analysis['module_name']}
# Score: {module_analysis['total_score']}/{module_analysis['max_score']} ({module_analysis['percentage']}%)
# Performance Level: {module_analysis['performance_level']}
# Questions Failed: {module_analysis['failed_questions']}/{module_analysis['total_questions']}

# Failed Questions:
# {failed_details}

# Provide specific feedback (3-4 sentences) covering:
# 1. What they did well
# 2. What needs improvement
# 3. One concrete action to improve

# Write in plain text without markdown, bullets, or numbering."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 200
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     feedback = result["choices"][0]["message"]["content"].strip()
#                     return self._clean_markdown(feedback)
#                 else:
#                     return self._fallback_module_feedback(module_analysis)
            
#         except Exception as e:
#             logger.error(f"Module feedback generation failed: {e}")
#             return self._fallback_module_feedback(module_analysis)
    
#     def _fallback_module_feedback(self, module_analysis: Dict) -> str:
#         """Fallback feedback when AI is unavailable"""
#         percentage = module_analysis["percentage"]
#         failed = module_analysis["failed_questions"]
#         total = module_analysis["total_questions"]
        
#         if percentage >= 80:
#             return f"Excellent work on this module! You scored {percentage}% and demonstrated strong understanding of the concepts. Keep up this level of performance."
#         elif percentage >= 70:
#             return f"Good performance with {percentage}%. You missed {failed} out of {total} questions. Review the specific concepts from those questions to strengthen your understanding."
#         elif percentage >= 60:
#             return f"Satisfactory effort with {percentage}%. Focus on reviewing the {failed} questions you missed, particularly the core concepts. Additional practice will help solidify your knowledge."
#         else:
#             return f"This module needs more attention. You scored {percentage}%. Review the learning material carefully, especially the areas covered in the {failed} questions you missed. Consider revisiting the fundamental concepts before moving forward."
    
#     async def generate_collective_feedback(
#         self,
#         critical_gaps: Dict,
#         module_analyses: List[Dict]
#     ) -> Tuple[str, str]:
#         """Generate specific, actionable collective feedback"""
#         if not self.groq_api_key:
#             return self._fallback_collective_feedback(critical_gaps, module_analyses)
        
#         system_prompt = """You are an experienced TVET instructor providing specific, actionable feedback.
# Focus on WHAT CONTENT to study, not which module numbers.
# Reference specific concepts, topics, and sections from the learning material.
# Write in plain text without markdown. Be direct and specific."""
        
#         # Build detailed context about what they got wrong
#         weak_content_details = ""
#         for module in critical_gaps["weak_modules"]:
#             weak_content_details += f"\n{module['module_name']} ({module['percentage']:.1f}%):\n"
#             weak_content_details += f"Content covered: {module['content'][:300]}...\n"
        
#         # Get specific failed questions
#         failed_concepts = []
#         for q in critical_gaps["all_failed_questions"][:8]:
#             failed_concepts.append(f"- {q['question_text'][:100]}")
#         failed_concepts_str = "\n".join(failed_concepts) if failed_concepts else "None"
        
#         strong_content_details = ""
#         for module in critical_gaps["strong_modules"]:
#             strong_content_details += f"\n{module['module_name']} ({module['percentage']:.1f}%): Strong understanding\n"
        
#         user_prompt = f"""Overall Performance: {critical_gaps['overall_performance']['percentage']:.1f}%

# WEAK AREAS:
# {weak_content_details}

# SPECIFIC FAILED CONCEPTS:
# {failed_concepts_str}

# STRONG AREAS:
# {strong_content_details}

# Write TWO specific paragraphs (3-4 sentences each):

# PARAGRAPH 1 - CRITICAL GAPS:
# Identify the SPECIFIC TOPICS and CONCEPTS they need to study. Mention actual content areas like "Lockout/Tagout procedures", "RMS voltage calculations", "the hierarchy of safety controls", etc. Be precise about what they're missing.

# PARAGRAPH 2 - RECOMMENDATIONS:
# Give CONCRETE study actions. Tell them exactly which topics to review, what to practice, and how to approach weak areas. Reference the actual content they need to master, not just module numbers.

# Write in plain text. No markdown. Be specific and actionable."""

#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.groq_url,
#                     headers={
#                         "Authorization": f"Bearer {self.groq_api_key}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": self.model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 400
#                     }
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     output = result["choices"][0]["message"]["content"].strip()
#                     output = self._clean_markdown(output)
                    
#                     parts = output.split("\n\n")
#                     critical_gaps_text = parts[0].strip() if len(parts) > 0 else output
#                     recommendations = parts[1].strip() if len(parts) > 1 else "Keep practicing and reviewing the material."
                    
#                     return critical_gaps_text, recommendations
#                 else:
#                     return self._fallback_collective_feedback(critical_gaps, module_analyses)
            
#         except Exception as e:
#             logger.error(f" Collective feedback generation failed: {e}")
#             return self._fallback_collective_feedback(critical_gaps, module_analyses)
    
#     def _fallback_collective_feedback(
#         self,
#         critical_gaps: Dict,
#         module_analyses: List[Dict]
#     ) -> Tuple[str, str]:
#         """Specific fallback collective feedback"""
#         overall = critical_gaps["overall_performance"]
#         weak_modules = critical_gaps["weak_modules"]
        
#         if weak_modules:
#             # Extract specific content topics from failed questions
#             failed_topics = set()
#             for q in critical_gaps["all_failed_questions"][:5]:
#                 question = q["question_text"]
#                 # Extract key phrases (simplified - could be more sophisticated)
#                 if "PPE" in question or "Personal Protective" in question:
#                     failed_topics.add("Personal Protective Equipment requirements")
#                 if "LOTO" in question or "Lockout" in question:
#                     failed_topics.add("Lockout/Tagout procedures")
#                 if "RMS" in question:
#                     failed_topics.add("RMS voltage calculations and meaning")
#                 if "AC" in question and "DC" in question:
#                     failed_topics.add("AC versus DC current characteristics")
#                 if "transformer" in question.lower():
#                     failed_topics.add("transformer operation and power transmission")
#                 if "hierarchy" in question.lower():
#                     failed_topics.add("hierarchy of electrical safety controls")
            
#             if not failed_topics:
#                 failed_topics = {f"{m['module_name']} fundamentals" for m in weak_modules[:2]}
            
#             topics_list = ", ".join(list(failed_topics)[:4])
            
#             gaps = f"You need to strengthen your understanding of several critical concepts: {topics_list}. Your performance shows gaps in these foundational topics that are essential for safe and effective electrical work. These aren't just theoretical - they're practical skills you'll use daily in the field."
            
#             # Build specific recommendations
#             study_items = []
#             for module in weak_modules[:2]:
#                 # Extract first major concept from module content
#                 content = module["content"]
#                 sentences = content.split(". ")
#                 if sentences:
#                     key_concept = sentences[0].strip()
#                     study_items.append(f"review {key_concept.lower()}")
            
#             if not study_items:
#                 study_items = ["review the fundamental concepts", "practice the question types you missed"]
            
#             recommendations = f"Start by focusing on your weakest areas: {' and '.join(study_items[:2])}. Don't just read - actively practice applying these concepts. Work through similar questions, draw diagrams to visualize the processes, and explain the concepts out loud to reinforce your understanding. Spend extra time on {list(failed_topics)[0] if failed_topics else 'core concepts'} since this appeared in multiple questions you missed."
#         else:
#             gaps = f"Your overall performance of {overall['percentage']:.1f}% shows {overall['level'].lower()} understanding across all topics. You're demonstrating consistent comprehension of the material."
#             recommendations = "Continue reinforcing your knowledge through practice. Challenge yourself with more complex scenarios and real-world applications to deepen your expertise."
        
#         return gaps, recommendations
    
#     async def generate_recommendations(
#         self,
#         modules: List[Dict]
#     ) -> Dict:
#         """Generate comprehensive recommendations for all modules"""
#         try:
#             logger.info(f" Analyzing {len(modules)} module(s)")
            
#             module_analyses = []
#             module_feedbacks = []
            
#             for idx, module in enumerate(modules):
#                 logger.info(f"📚 Analyzing module {idx + 1}/{len(modules)}")
                
#                 analysis = self.analyze_module_performance(
#                     module_id=module.get("module_id", f"module_{idx+1}"),
#                     module_name=module.get("module_name", f"Module {idx+1}"),
#                     module_content=module.get("module_content", ""),
#                     max_score=module.get("max_score", 0),
#                     question_results=module.get("question_results", [])
#                 )
                
#                 feedback = await self.generate_module_feedback(analysis)
                
#                 module_analyses.append(analysis)
#                 module_feedbacks.append({
#                     "module_id": analysis["module_id"],
#                     "module_name": analysis["module_name"],
#                     "score": f"{analysis['total_score']}/{analysis['max_score']}",
#                     "percentage": analysis["percentage"],
#                     "performance_level": analysis["performance_level"],
#                     "feedback": feedback,
#                     "failed_questions": analysis["failed_questions"],
#                     "concepts_to_review": analysis["concepts_to_review"]
#                 })
            
#             critical_gaps = self.identify_critical_gaps(module_analyses)
            
#             gaps_analysis, recommendations = await self.generate_collective_feedback(
#                 critical_gaps, module_analyses
#             )
            
#             result = {
#                 "individual_module_reviews": module_feedbacks,
#                 "collective_feedback": {
#                     "overall_performance": critical_gaps["overall_performance"],
#                     "critical_gaps": gaps_analysis,
#                     "recommendations": recommendations,
#                     "weak_question_types": critical_gaps["weak_question_types"],
#                     "total_failed_questions": critical_gaps["total_failed_questions"]
#                 }
#             }
            
#             logger.info(f" Recommendations generated successfully")
            
#             return result
            
#         except Exception as e:
#             logger.error(f" Recommendation generation failed: {e}", exc_info=True)
#             raise




"""
Module-Based Recommendation Service - FINAL VERSION
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