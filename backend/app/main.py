"""
SecurePay AI - Backend API Server
================================
Main FastAPI application entry point.

Author: Md. Tanvir Hossain
Project: M.Sc. CSE @ BRAC University

This module sets up the FastAPI server with all the necessary middleware,
routes, and configurations for the fraud detection system.

Note: I spent a lot of time getting the middleware order right - 
      the order matters for security headers and rate limiting!
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog
import time
from typing import AsyncGenerator

# Local imports
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.logging import setup_logging
from app.core.security import SecurityHeadersMiddleware
from app.api.v1 import router as api_v1_router
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.audit import AuditMiddleware

# Initialize structured logging first
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting SecurePay AI Backend Service", version=settings.VERSION)
    await init_db()
    logger.info("Database connection established")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SecurePay AI Backend Service")
    await close_db()
    logger.info("Database connection closed")


# Initialize FastAPI application
app = FastAPI(
    title="SecurePay AI - Fraud Detection API",
    description="""
    ## 🛡️ Intelligent Financial Fraud Detection Platform
    
    A production-ready API for real-time fraud detection in Bangladesh's 
    digital payment ecosystem.
    
    ### Features
    - **Real-time Fraud Detection** - Sub-100ms response time
    - **ML-Powered Analysis** - Ensemble model predictions
    - **Comprehensive Security** - OAuth2 + JWT authentication
    - **Audit Logging** - Complete transaction trail
    
    ### Authentication
    All endpoints require Bearer token authentication unless specified otherwise.
    """,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining"]
)

# Trusted Host Middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# Audit Logging Middleware
app.add_middleware(AuditMiddleware)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed response."""
    logger.warning(
        "Validation error",
        path=request.url.path,
        errors=exc.errors()
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Error",
            "errors": exc.errors(),
            "body": exc.body if hasattr(exc, 'body') else None
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Include API routers
app.include_router(
    api_v1_router,
    prefix="/api/v1",
    tags=["v1"]
)


# Health Check Endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    Returns service status and version information.
    """
    return {
        "status": "healthy",
        "service": "securepay-ai-backend",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness probe for Kubernetes.
    Checks database and Redis connectivity.
    """
    from app.core.database import check_db_connection
    from app.core.redis import check_redis_connection
    
    db_status = await check_db_connection()
    redis_status = await check_redis_connection()
    
    is_ready = db_status and redis_status
    
    return JSONResponse(
        status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": {
                "database": "connected" if db_status else "disconnected",
                "redis": "connected" if redis_status else "disconnected"
            }
        }
    )


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """
    Liveness probe for Kubernetes.
    Simple check to verify the application is running.
    """
    return {"status": "alive"}


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "service": "SecurePay AI - Fraud Detection API",
        "version": settings.VERSION,
        "documentation": "/docs" if settings.DEBUG else "Contact admin for API access",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=settings.WORKERS
    )
