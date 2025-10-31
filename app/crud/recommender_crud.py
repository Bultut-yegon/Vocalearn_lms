from sqlalchemy.orm import Session
from app.models.recommender import RecommendRequest, RecommendResponse, RecommendationItem

def create_recommend_request(db: Session, user_id: int, context_text: str, top_k: int = 5, alpha: float = 0.6):
    request = RecommendRequest(
        user_id=user_id, context_text=context_text, top_k=top_k, alpha=alpha
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

def create_recommend_response(db: Session, user_id: int, request_id: int):
    response = RecommendResponse(user_id=user_id, request_id=request_id)
    db.add(response)
    db.commit()
    db.refresh(response)
    return response

def add_recommendation_item(db: Session, response_id: int, content_id: int, title: str, score: float, reason: str):
    item = RecommendationItem(
        response_id=response_id,
        content_id=content_id,
        title=title,
        score=score,
        reason=reason,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
