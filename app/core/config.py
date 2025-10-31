import os
# from pydantic import BaseSettings
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MODEL_DIR: str = "./models"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    TOP_K: int = 10
    OPENAI_API_KEY: str = ""
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    REDIS_URL: str = None

    class Config:
        env_file = ".env"

settings = Settings()
