"""
Train pipeline:
- Load content items -> build embeddings
- Load interactions -> build implicit item-user matrix
- Train ALS model (implicit)
- Save models and artifacts to MODEL_DIR
"""
import os
import numpy as np
import pandas as pd
import joblib
from sentence_transformers import SentenceTransformer
from scipy import sparse
from implicit.als import AlternatingLeastSquares
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
from app.core.config import settings

DB_URL = settings.DATABASE_URL
MODEL_DIR = settings.MODEL_DIR
os.makedirs(MODEL_DIR, exist_ok=True)

engine = create_engine(DB_URL)

# 1) Load content items
content_df = pd.read_sql("SELECT id, external_id, title, description, tags FROM content_items", engine)
if content_df.empty:
    raise SystemExit("No content records found. Seed content_items table first.")

# 2) Build embeddings
embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
corpus = (content_df["title"].fillna("") + ". " + content_df["description"].fillna("") + ". " + content_df["tags"].fillna(""))
print("Encoding content embeddings...")
content_embeddings = embedder.encode(corpus.tolist(), convert_to_numpy=True, show_progress_bar=True, normalize_embeddings=True)
np.save(os.path.join(MODEL_DIR, "content_embeddings.npy"), content_embeddings)
joblib.dump(content_df.reset_index(drop=True), os.path.join(MODEL_DIR, "content_df.joblib"))

# 3) Load interactions & compute weights
inter_df = pd.read_sql("SELECT user_id, content_id, event_type, event_value FROM interactions", engine)
if inter_df.empty:
    print("Warning: interactions table empty. ALS training will be skipped but embeddings are saved.")
else:
    def event_weight(row):
        et = row['event_type']
        if et == "view": return 1.0 * (row.get('event_value') or 1.0)
        if et == "complete": return 5.0 * (row.get('event_value') or 1.0)
        if et == "like": return 3.0 * (row.get('event_value') or 1.0)
        if et == "quiz": return 2.0 * (row.get('event_value') or 1.0)
        return 1.0

    inter_df['weight'] = inter_df.apply(lambda r: event_weight(r), axis=1)

    # Map user_id and content_id to indices
    user_ids = inter_df['user_id'].unique().tolist()
    content_ids = inter_df['content_id'].unique().tolist()
    user_map = {u:i for i,u in enumerate(user_ids)}
    content_map = {c:i for i,c in enumerate(content_ids)}

    rows = inter_df['content_id'].map(content_map).to_numpy()
    cols = inter_df['user_id'].map(user_map).to_numpy()
    data = inter_df['weight'].to_numpy()

    # implicit expects item-user matrix (items x users)
    item_user = sparse.coo_matrix((data, (rows, cols)), shape=(len(content_map), len(user_map)))

    # train ALS
    print("Training ALS model (implicit)...")
    als = AlternatingLeastSquares(factors=64, regularization=0.01, iterations=20)
    als.fit(item_user)  # may use BLAS cores; tune iterations

    # persist
    joblib.dump(als, os.path.join(MODEL_DIR, "als_model.joblib"))
    joblib.dump(user_map, os.path.join(MODEL_DIR, "user_map.joblib"))
    joblib.dump(content_map, os.path.join(MODEL_DIR, "content_map.joblib"))
    print("ALS model and maps saved to", MODEL_DIR)

print("Training pipeline finished.")
