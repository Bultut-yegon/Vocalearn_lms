# app/schemas/recommendations.py
from pydantic import BaseModel
from typing import List, Optional

class RecommendRequest(BaseModel):
    user_id: str
    context_text: Optional[str] = None
    top_k: Optional[int] = 10
    alpha: Optional[float] = 0.6

class RecommendationItem(BaseModel):
    content_id: int
    title: str
    score: float
    reason: Optional[str] = None

class RecommendResponse(BaseModel):
    user_id: str
    recommendations: List[RecommendationItem]
