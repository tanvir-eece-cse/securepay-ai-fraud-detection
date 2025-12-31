"""ML API Router."""

from fastapi import APIRouter

from app.api.v1.endpoints import ml

router = APIRouter()

router.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])
