"""
SecurePay AI - ML Service
=========================
Machine Learning API for real-time fraud detection.

Author: Md. Tanvir Hossain
Project: M.Sc. CSE @ BRAC University

This service handles all ML predictions for fraud detection.
I used an ensemble approach combining XGBoost and Random Forest
because they complement each other well - XGBoost handles
non-linear patterns while RF provides stability.

TODO: Add model versioning with MLflow when time permits
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import time
from typing import AsyncGenerator

# Local imports
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1 import router as api_v1_router
from app.services.model_loader import model_manager

# Setup logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting SecurePay AI ML Service", version=settings.VERSION)
    
    # Load ML models
    await model_manager.load_models()
    logger.info("ML models loaded successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ML Service")


# Initialize FastAPI
app = FastAPI(
    title="SecurePay AI - ML Service",
    description="Machine Learning service for real-time fraud detection",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    """Add processing time header."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Include routers
app.include_router(api_v1_router, prefix="/api/v1", tags=["v1"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    models_loaded = model_manager.models_loaded()
    
    return {
        "status": "healthy" if models_loaded else "degraded",
        "service": "securepay-ml-service",
        "version": settings.VERSION,
        "models_loaded": models_loaded
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "SecurePay AI - ML Service",
        "version": settings.VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )
