import os
import numpy as np
import joblib
from sentence_transformers import SentenceTransformer

from app.core.config import settings

MODEL_DIR = settings.MODEL_DIR
EMB_MODEL = settings.EMBEDDING_MODEL_NAME

# Lazy load artifacts
_content_df = None
_content_embeddings = None
_als = None
_user_map = None
_content_map = None
_embedder = None

def _load_artifacts():
    global _content_df, _content_embeddings, _als, _user_map, _content_map, _embedder
    if _content_df is None:
        _content_df = joblib.load(os.path.join(MODEL_DIR, "content_df.joblib"))
    if _content_embeddings is None:
        _content_embeddings = np.load(os.path.join(MODEL_DIR, "content_embeddings.npy"))
    if _embedder is None:
        _embedder = SentenceTransformer(EMB_MODEL)
    if _als is None:
        model_path = os.path.join(MODEL_DIR, "als_model.joblib")
        if os.path.exists(model_path):
            _als = joblib.load(model_path)
            _user_map = joblib.load(os.path.join(MODEL_DIR, "user_map.joblib"))
            _content_map = joblib.load(os.path.join(MODEL_DIR, "content_map.joblib"))
        else:
            _als = None

_load_artifacts()

def _emb_similarity_scores(user_text: str):
    # returns dict content_id -> similarity score
    if not user_text:
        user_text = "vocational training general"
    uemb = _embedder.encode(user_text, convert_to_numpy=True, normalize_embeddings=True)
    sims = np.dot(_content_embeddings, uemb)  # content_embeddings normalized -> cosine
    out = {}
    for i, s in enumerate(sims):
        cid = int(_content_df.iloc[i]["id"])
        out[cid] = float(s)
    return out

def _cf_scores_for_user(user_id: int, top_k=100):
    # returns dict content_id -> predicted score
    if _als is None:
        return {}
    if user_id not in _user_map:
        return {}
    uidx = _user_map[user_id]
    # use implicit ALS recommend (gives item indices and scores)
    recs = _als.recommend(userid=uidx, user_items=None, N=top_k)
    out = {}
    inv_map = {v:k for k,v in _content_map.items()}  # index -> content_id
    for idx, score in recs:
        cid = inv_map.get(int(idx))
        if cid is not None:
            out[int(cid)] = float(score)
    return out

def hybrid_recommend(user_id: int, user_text: str, top_k=10, alpha=0.6):
    emb_scores = _emb_similarity_scores(user_text)    # content_id -> sim
    cf_scores = _cf_scores_for_user(user_id, top_k=500)

    # normalize cf and emb
    cf_vals = np.array(list(cf_scores.values())) if cf_scores else np.array([0.0])
    if cf_vals.size>0:
        min_cf, max_cf = float(cf_vals.min()), float(cf_vals.max())
    else:
        min_cf, max_cf = 0.0, 1.0

    # combine candidate content_ids
    candidates = set(list(emb_scores.keys()) + list(cf_scores.keys()))
    combined = {}
    for cid in candidates:
        cf_raw = cf_scores.get(cid, 0.0)
        cf_norm = (cf_raw - min_cf)/(max_cf-min_cf) if max_cf>min_cf else 0.0
        emb_raw = emb_scores.get(cid, 0.0)
        emb_norm = (emb_raw + 1.0) / 2.0  # convert -1..1 to 0..1 (if normalized)
        score = alpha * cf_norm + (1-alpha) * emb_norm
        combined[cid] = score

    # sort and select top_k
    top = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_k]
    results = []
    for cid, sc in top:
        row = _content_df[_content_df["id"]==cid].iloc[0]
        results.append({
            "content_id": int(cid),
            "title": row["title"],
            "score": float(sc),
            "tags": row["tags"],
            "difficulty": row.get("difficulty","")
        })
    return results
