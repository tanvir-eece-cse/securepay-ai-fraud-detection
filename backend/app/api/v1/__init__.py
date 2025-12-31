"""
API v1 Router
Main router for API version 1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, transactions, users, analytics, health

router = APIRouter()

# Include all endpoint routers
router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["Transactions"]
)

router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)
