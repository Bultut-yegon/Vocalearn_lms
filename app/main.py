"""
Main Application Entry Point
AI Learning Services 
"""

from dotenv import load_dotenv

# Load environment variables FIRST before importing anything else
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.logging_config import logger
from app.core.error_handler import unhandled_exception_handler

# Import routers
from app.api.v1.recommendation_router import router as recommendation_router
from app.api.v1.grading_router import router as grading_router
from app.api.v1.quiz_router import router as quiz_router
# from app.api.v1.document_router import router as document_router

# NEW: Import submission router for complete flow
try:
    from app.api.v1.quiz_submission_router import router as submission_router
    SUBMISSION_ROUTER_AVAILABLE = True
except ImportError:
    logger.warning(" Submission router not found - integrated flow unavailable")
    SUBMISSION_ROUTER_AVAILABLE = False

import time
import os


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI app instance
    """
    
    # Environment
    env = os.getenv("ENV", "dev")
    is_production = env == "production"
    
    # App initialization
    app = FastAPI(
        title="AI Learning Services",
        description="""
        ##  AI-Powered TVET Learning Platform
        
        Complete suite of AI services for technical and vocational education:
        
        ###  Core Services
        - **Quiz Generation**: AI-generated quizzes from course content
        - **Auto-Grading**: Instant grading with AI-powered feedback
        - **Recommendations**: Personalized learning paths based on performance
        - **Integrated Submission**: Complete flow (submit → grade → recommend)
        
        ### Features
        - LLM-powered question generation
        - Automated grading for MCQ, T/F, and open-ended questions
        - Performance trend analysis
        - Personalized study plans
        - Real-time feedback
        
        ###  Quick Start
        1. Generate a quiz: `POST /api/quiz/generate-weekly`
        2. Submit answers: `POST /api/submissions/submit-quiz`
        3. Get instant grading + recommendations!
        """,
        version="1.0.0",
        docs_url="/docs" if not is_production else None,
        redoc_url="/redoc" if not is_production else None,
        contact={
            "name": "AI Learning Services Team",
            "email": "bultutyegonn@gmail.com"
        },
        license_info={
            "name": "MIT License",
        }
    )
    
    
    # CORS Configuration
   
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
    
    if allowed_origins == "*":
        logger.warning(" CORS allowing all origins - restrict in production!")
        origins = ["*"]
    else:
        origins = [origin.strip() for origin in allowed_origins.split(",")]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
        max_age=3600  # Cache preflight requests for 1 hour
    )
    
    
    # Request Logging Middleware
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests and responses with timing."""
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
        
        logger.info(
            f"[{request_id}]   {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            
            process_time = round(time.time() - start_time, 3)
            
            # Log level based on status code
            if response.status_code < 400:
                logger.info(
                    f"[{request_id}]  {request.method} {request.url.path} "
                    f"→ {response.status_code} ({process_time}s)"
                )
            elif response.status_code < 500:
                logger.warning(
                    f"[{request_id}]   {request.method} {request.url.path} "
                    f"→ {response.status_code} ({process_time}s)"
                )
            else:
                logger.error(
                    f"[{request_id}]  {request.method} {request.url.path} "
                    f"→ {response.status_code} ({process_time}s)"
                )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = round(time.time() - start_time, 3)
            logger.error(
                f"[{request_id}]  Error processing request: {e} ({process_time}s)",
                exc_info=True
            )
            raise
    
    
    # Exception Handlers
   
    app.add_exception_handler(Exception, unhandled_exception_handler)
    
    
    # API Routers
    
    
    # V1 API Routes
    API_V1_PREFIX = "/api/v1"
    
    # Core services
    app.include_router(
        quiz_router,
        prefix=f"{API_V1_PREFIX}/quiz",
        tags=[" Quiz Generation"]
    )
    
    app.include_router(
        grading_router,
        prefix=f"{API_V1_PREFIX}/grading",
        tags=[" Auto-Grading"]
    )
    
    app.include_router(
        recommendation_router,
        prefix=f"{API_V1_PREFIX}/recommendations",
        tags=[" Recommendations"]
    )
    
    # Integrated submission flow (if available)
    if SUBMISSION_ROUTER_AVAILABLE:
        app.include_router(
            submission_router,
            prefix=f"{API_V1_PREFIX}/submissions",
            tags=[" Complete Submission Flow"]
        )
        logger.info(" Integrated submission router registered")
    
    # Document processing (when ready)
    # app.include_router(
    #     document_router,
    #     prefix=f"{API_V1_PREFIX}/documents",
    #     tags=[" Document Processing"]
    # )
    
    # Legacy routes (maintain backwards compatibility)
    app.include_router(
        recommendation_router,
        prefix="/api/recommendation",
        tags=["Recommendation (Legacy)"],
        include_in_schema=False  # Hide from docs
    )
    
    app.include_router(
        grading_router,
        prefix="/api/autograde",
        tags=["Auto-Grading (Legacy)"],
        include_in_schema=False
    )
    
    
    # Health & Status Endpoints
    
    
    @app.get("/health", tags=[" Health"])
    async def health_check():
        """
        Comprehensive health check endpoint.
        Returns status of all services and dependencies.
        """
        # Check GROQ API key
        groq_configured = bool(os.getenv("GROQAPI_KEY"))
        
        # Build service status
        services_status = {
            "quiz_generation": {
                "status": "operational" if groq_configured else "degraded",
                "llm_available": groq_configured
            },
            "auto_grading": {
                "status": "operational" if groq_configured else "degraded",
                "llm_grading": groq_configured,
                "fallback_available": True
            },
            "recommendations": {
                "status": "operational" if groq_configured else "degraded",
                "ai_insights": groq_configured,
                "fallback_available": True
            }
        }
        
        if SUBMISSION_ROUTER_AVAILABLE:
            services_status["integrated_submission"] = {
                "status": "operational",
                "complete_flow": True
            }
        
        # Overall status
        overall_status = "healthy" if groq_configured else "degraded"
        
        return {
            "status": overall_status,
            "service": "AI Learning Services",
            "version": "1.0.0",
            "environment": os.getenv("ENV", "dev"),
            "timestamp": time.time(),
            "services": services_status,
            "warnings": [] if groq_configured else [
                "GROQAPI_KEY not configured - using fallback methods"
            ]
        }
    
    @app.get("/", tags=[" Info"])
    async def root():
        """
        Root endpoint - API information and available services.
        """
        return {
            "service": "AI Learning Services",
            "version": "1.0.0",
            "status": "running",
            "description": "AI-powered platform for TVET education",
            "features": [
                " Adaptive Quiz Generation",
                " Automated Grading (MCQ, T/F, Open-ended)",
                " Performance Analytics",
                " Personalized Recommendations",
                " Integrated Submission Flow"
            ],
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc"
            },
            "api": {
                "version": "v1",
                "base_path": "/api/v1",
                "endpoints": {
                    "quiz_generation": "/api/v1/quiz",
                    "grading": "/api/v1/grading",
                    "recommendations": "/api/v1/recommendations",
                    "submissions": "/api/v1/submissions" if SUBMISSION_ROUTER_AVAILABLE else None,
                    "health": "/health"
                }
            },
            "quick_start": {
                "1": "Generate quiz: POST /api/v1/quiz/generate-weekly",
                "2": "Submit answers: POST /api/v1/submissions/submit-quiz",
                "3": "Get instant feedback + personalized recommendations!"
            }
        }
    
    @app.get("/api/v1/status", tags=["Info"])
    async def api_status():
        """Detailed API status and configuration."""
        return {
            "api_version": "1.0.0",
            "environment": os.getenv("ENV", "dev"),
            "available_routers": {
                "quiz_generation": True,
                "grading": True,
                "recommendations": True,
                "integrated_submission": SUBMISSION_ROUTER_AVAILABLE
            },
            "features": {
                "llm_powered": bool(os.getenv("GROQAPI_KEY")),
                "fallback_grading": True,
                "performance_tracking": True,
                "ai_insights": bool(os.getenv("GROQAPI_KEY"))
            },
            "configuration": {
                "cors_enabled": True,
                "request_logging": True,
                "error_handling": True
            }
        }
    
    
    # Startup/Shutdown Events
    
    
    @app.on_event("startup")
    async def startup_event():
        """Execute on application startup."""
        logger.info("=" * 80)
        logger.info("AI Learning Services Starting...")
        logger.info("=" * 80)
        logger.info(f"Environment: {os.getenv('ENV', 'dev')}")
        logger.info(f"Version: 1.0.0")
        logger.info(f"GROQ API configured: {bool(os.getenv('GROQAPI_KEY'))}")
        logger.info(f"Integrated submission flow: {SUBMISSION_ROUTER_AVAILABLE}")
        logger.info("=" * 80)
        logger.info("AI Learning Services ready to serve!")
        logger.info("=" * 80)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Execute on application shutdown."""
        logger.info("=" * 80)
        logger.info(" AI Learning Services shutting down...")
        logger.info("=" * 80)
    
    return app



# Application Instance


app = create_app()



# Development Server

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    env = os.getenv("ENV", "dev")
    reload = env == "dev"
    
    logger.info("=" * 80)
    logger.info(f"Starting AI Learning Services")
    logger.info(f"Host: {host}:{port}")
    logger.info(f"Environment: {env}")
    logger.info(f"Hot reload: {reload}")
    logger.info(f"Docs: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    logger.info("=" * 80)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )