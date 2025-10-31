# from fastapi import APIRouter, HTTPException
# from app.models.schema import RecommendRequest, RecommendResponse, RecommendationItem
# from app.services.hybrid_recommender import hybrid_recommend
# from app.services.gpt_re_ranker import re_rank_with_gpt
# from app.core.db import SessionLocal
# from sqlalchemy import text

# router = APIRouter()

# @router.post("/recommend", response_model=RecommendResponse)
# def recommend_endpoint(req: RecommendRequest):
#     # Validate user existence
#     with SessionLocal() as db:
#         r = db.execute(text("SELECT 1 FROM users WHERE id=:uid"), {"uid": req.user_id}).fetchone()
#         if r is None:
#             raise HTTPException(status_code=404, detail="User not found")

#     # Step 1: hybrid baseline
#     baseline = hybrid_recommend(req.user_id, req.context_text or "", top_k= max(req.top_k, 10), alpha=req.alpha)

#     # Step 2: call GPT to re-rank & explain (best-effort)
#     # Build user profile summary for GPT
#     user_profile = req.context_text or "No profile provided; learner is a vocational student."
#     enhanced = re_rank_with_gpt(user_profile, baseline, max_recs=req.top_k)

#     # convert to schema
#     recs = []
#     for item in enhanced:
#         recs.append(RecommendationItem(
#             content_id = int(item.get("content_id")),
#             title = item.get("title", ""),
#             score = float(item.get("score", 0.0)) if item.get("score") else 0.0,
#             reason = item.get("reason", "")[:250]
#         ))
#     return RecommendResponse(user_id=req.user_id, recommendations=recs)



from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud import recommender_crud
from app.models.recommender import RecommendRequest
from app.core.config import settings
from sentence_transformers import SentenceTransformer, util
import joblib
import numpy as np
import os

router = APIRouter()

@router.post("/recommend")
def recommend(user_id: int, context_text: str, top_k: int = 5, db: Session = Depends(get_db)):
    # Load saved artifacts
    model_path = os.path.join(settings.MODEL_DIR, "content_embeddings.npy")
    df_path = os.path.join(settings.MODEL_DIR, "content_df.joblib")
    if not os.path.exists(model_path) or not os.path.exists(df_path):
        return {"error": "Model artifacts missing. Train recommender first."}

    content_embeddings = np.load(model_path)
    content_df = joblib.load(df_path)

    model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    query_emb = model.encode(context_text, convert_to_tensor=True, normalize_embeddings=True)
    scores = util.cos_sim(query_emb, content_embeddings)[0]
    top_results = np.argsort(-scores)[:top_k]

    # Store request
    req = recommender_crud.create_recommend_request(db, user_id, context_text, top_k)
    res = recommender_crud.create_recommend_response(db, user_id, req.id)

    recommendations = []
    for idx in top_results:
        row = content_df.iloc[idx]
        item = recommender_crud.add_recommendation_item(
            db,
            response_id=res.id,
            content_id=int(row["id"]),
            title=row["title"],
            score=float(scores[idx]),
            reason="Semantic similarity",
        )
        recommendations.append({
            "title": row["title"],
            "score": float(scores[idx]),
            "reason": item.reason,
        })

    return {"user_id": user_id, "recommendations": recommendations}

