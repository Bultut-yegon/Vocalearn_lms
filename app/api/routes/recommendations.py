from fastapi import APIRouter, HTTPException
# from app.models.recommendations import RecommendRequest, RecommendResponse, RecommendationItem
# from app.models.recommendations import RecommendRequest, RecommendResponse, RecommendationItem
from app.schemas.recommendations import RecommendRequest, RecommendResponse, RecommendationItem
from app.core.config import settings
import joblib
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

router = APIRouter()

MODEL_DIR = settings.MODEL_DIR
EMBEDDING_MODEL_NAME = settings.EMBEDDING_MODEL_NAME

# Load models and data
# try:
#     content_df = joblib.load(os.path.join(MODEL_DIR, "content_df.joblib"))
#     content_embeddings = np.load(os.path.join(MODEL_DIR, "content_embeddings.npy"))
#     als = joblib.load(os.path.join(MODEL_DIR, "als_model.joblib"))
#     user_map = joblib.load(os.path.join(MODEL_DIR, "user_map.joblib"))
#     content_map = joblib.load(os.path.join(MODEL_DIR, "content_map.joblib"))
#     embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
# except Exception as e:
#     raise RuntimeError(f"Error loading model assets: {e}")

# Load models and data (or create dummy data if missing)
import pandas as pd

try:
    content_df = joblib.load(os.path.join(MODEL_DIR, "content_df.joblib"))
    content_embeddings = np.load(os.path.join(MODEL_DIR, "content_embeddings.npy"))
    als = joblib.load(os.path.join(MODEL_DIR, "als_model.joblib"))
    user_map = joblib.load(os.path.join(MODEL_DIR, "user_map.joblib"))
    content_map = joblib.load(os.path.join(MODEL_DIR, "content_map.joblib"))
    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
except Exception as e:
    print(f"Warning: Could not load model assets ({e}). Using dummy data for testing.")

    # Dummy content titles
    titles = [
        "Basic Electrical Installation",
        "Welding Techniques",
        "Motor Vehicle Mechanics",
        "Computer Maintenance",
        "Plumbing and Pipe Fitting",
        "Food Processing and Preservation",
        "Construction and Masonry",
        "Refrigeration and Air Conditioning",
        "Safety in Engineering Workshops",
        "Introduction to Mechatronics"
    ]

    content_df = pd.DataFrame({
        "id": range(1, len(titles) + 1),
        "title": titles
    })

    # Create fake embeddings (10 x 384)
    content_embeddings = np.random.rand(len(titles), 384)

    # Dummy ALS and mappings
    class DummyALS:
        def recommend(self, user_idx, item_factors, N=10):
            scores = np.random.rand(N)
            ids = np.arange(N)
            return scores, ids
        item_factors = np.random.rand(10, 384)

    als = DummyALS()
    user_map = {"test_user": 0}
    content_map = {i: t for i, t in enumerate(titles)}

    embedder = SentenceTransformer('all-MiniLM-L6-v2')



@router.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """
    Generate hybrid recommendations using:
    - ALS collaborative filtering
    - Content similarity (context_text)
    """

    user_id = req.user_id
    top_k = req.top_k or 10
    alpha = req.alpha or 0.6  # weight between CF and content similarity

    # Collaborative filtering (ALS)
    if user_id not in user_map:
        raise HTTPException(status_code=404, detail="User not found in trained model")

    user_idx = user_map[user_id]
    cf_scores, cf_ids = als.recommend(user_idx, als.item_factors, N=top_k * 3)
    cf_items = [(list(content_map.keys())[i], score) for i, score in zip(cf_ids, cf_scores)]

    # Content-based recommendations using context text
    if req.context_text:
        context_vec = embedder.encode(req.context_text, convert_to_numpy=True, normalize_embeddings=True)
        similarities = np.dot(content_embeddings, context_vec)
        content_ranks = np.argsort(similarities)[::-1][:top_k * 3]
        cb_items = [(content_df.iloc[i]["id"], similarities[i]) for i in content_ranks]
    else:
        cb_items = []

    #  Combine (hybrid)
    combined_scores = {}
    for cid, score in cf_items:
        combined_scores[cid] = combined_scores.get(cid, 0) + alpha * score
    for cid, score in cb_items:
        combined_scores[cid] = combined_scores.get(cid, 0) + (1 - alpha) * score

    # Sort and format
    top_items = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    recommendations = []
    for cid, score in top_items:
        row = content_df[content_df["id"] == cid].iloc[0]
        recommendations.append(
            RecommendationItem(
                content_id=int(cid),
                title=row["title"],
                score=float(score),
                reason="Hybrid CF+Content recommendation"
            )
        )

    return RecommendResponse(user_id=user_id, recommendations=recommendations)


    
