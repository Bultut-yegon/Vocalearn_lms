from fastapi import FastAPI
from app.api.routes import recommendations, autograde, quizgen
# from app.api.recommend import router as rec_router
from app.core.config import settings

app = FastAPI(title="VocaLearn AI Service", version="0.1")
# app.include_router(rec_router, prefix="/api", tags=["recommend"])
app.include_router(recommender.router, prefix="/api", tags=["Recommender"])
app.include_router(autograde.router)
app.include(quizgen.router)

@app.get("/")
def health():
    return {"status": "ok"}








