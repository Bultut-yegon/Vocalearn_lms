from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.logging_config import logger

async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )
