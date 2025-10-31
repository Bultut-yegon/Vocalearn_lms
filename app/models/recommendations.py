# from pydantic import BaseModel
# from typing import List, Optional

# class RecommendRequest(BaseModel):
#     user_id: int
#     context_text: Optional[str] = ""   # e.g., "interests: plumbing; weak: wiring"
#     top_k: Optional[int] = 5
#     alpha: Optional[float] = 0.6      # weight for CF vs content similarity

# class RecommendationItem(BaseModel):
#     content_id: int
#     title: str
#     score: float
#     reason: str

# class RecommendResponse(BaseModel):
#     user_id: int
#     recommendations: List[RecommendationItem]


from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base



class RecommendRequest(Base):
    __tablename__ = "recommend_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    context_text = Column(Text, default="")
    top_k = Column(Integer, default=5)
    alpha = Column(Float, default=0.6)

    # One request → many recommendation items
    recommendations = relationship("RecommendationItem", back_populates="request", cascade="all, delete-orphan")

class RecommendationItem(Base):
    __tablename__ = "recommendation_items"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(String(255), nullable=True)

    # Foreign key linking back to request
    request_id = Column(Integer, ForeignKey("recommend_requests.id"))
    request = relationship("RecommendRequest", back_populates="recommendations")

class RecommendResponse(Base):
    """
    Optional: If you want to persist responses (e.g. logs of recommendations).
    Could also be a view or computed dynamically from RecommendRequest + items.
    """
    __tablename__ = "recommend_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    request_id = Column(Integer, ForeignKey("recommend_requests.id"), nullable=False)
