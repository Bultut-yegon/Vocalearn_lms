# from fastapi import FastAPI
# from app.core.logging_config import setup_logging
# from app.api.v1.recommendation_router import router as recommendation_router

# setup_logging()

# app = FastAPI(
#     title="AI Learning Services",
#     version="1.0.0"
# )

# app.include_router(recommendation_router)

# @app.get("/")
# def root():
#     return {"status": "AI services running successfully"}


from dotenv import load_dotenv
load_dotenv() 
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.logging_config import logger
from app.core.error_handler import unhandled_exception_handler
from app.api.v1.recommendation_router import router as recommendation_router
from app.api.v1.grading_router import router as grading_router
from app.api.v1.quiz_router import router as quiz_router

# from app.api.v1.quiz_router import router as quiz_router
# from app.api.v1.grading_router import router as autograde_router

import time
import os

def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Learning Services",
        description="AI-driven recommendation, auto-grading, and adaptive quiz generation",
        version="1.0.0",
        docs_url="/docs" if os.getenv("ENV", "dev") == "dev" else None,
        redoc_url="/redoc" if os.getenv("ENV", "dev") == "dev" else None,
    )


    # CORS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["ALLOWED_ORIGINS","*"],  # restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    


    # Logging middleware
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        logger.info(f"Incoming request: {request.method} {request.url}")

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Error while processing request: {e}")
            raise

        process_time = round(time.time() - start_time, 3)
        logger.info(
            f"Completed {request.method} {request.url} in {process_time}s (status: {response.status_code})"
        )
        return response


    # Exception Handler
 
    app.add_exception_handler(Exception, unhandled_exception_handler)


    # Routers

    app.include_router(recommendation_router, prefix="/api/recommendation", tags=["Recommendation"])
    app.include_router(grading_router, prefix="/api/autograde", tags=["Auto-Grading"])
    app.include_router(quiz_router, prefix="/api/quiz", tags=["Quiz Generator"])
    # app.include_router(quiz_router, prefix="/api/quiz", tags=["Quiz Generator"])
    # app.include_router(autograde_router, prefix="/api/autograde", tags=["Auto-Grading"])


    # Health Check
 
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "AI Learning Services"}

    return app


app = create_app()
