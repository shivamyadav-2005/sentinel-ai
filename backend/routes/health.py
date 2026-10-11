
from backend.errors import resource_not_found

from fastapi import APIRouter

from backend.config import settings

router = APIRouter()


@router.get("/")
def root():
    return {
        "message": f"{settings.app_name} API is running!",
        "status": "online",
        "environment": settings.app_env,
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
    }

