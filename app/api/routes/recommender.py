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
    # model_path = os.path.join(settings.MODEL_DIR, "content_embeddings.npy")
    # df_path = os.path.join(settings.MODEL_DIR, "content_df.joblib")
    # if not os.path.exists(model_path) or not os.path.exists(df_path):
    #     return {"error": "Model artifacts missing. Train recommender first."}

    # content_embeddings = np.load(model_path)
    # content_df = joblib.load(df_path)
    # -----------------------------
#  Dummy model data (temporary)
# -----------------------------
import pandas as pd

# 10 sample contents for the TVET LMS
content_titles = [
    "Automotive Systems Fundamentals",
    "Basic Electrical Installation",
    "Plumbing and Pipe Maintenance",
    "Introduction to Welding Techniques",
    "Principles of Mechatronics",
    "Food Processing and Preservation",
    "Computer Hardware Maintenance",
    "Construction and Masonry Basics",
    "Refrigeration and Air Conditioning",
    "Safety in the Workshop",
]

# Fake embeddings (10 x 384)
content_embeddings = np.random.rand(10, 384)
content_df = pd.DataFrame({
    "id": range(1, 11),
    "title": content_titles
})


    # model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    model = SentenceTransformer('all-MiniLM-L6-v2')

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
