
from fastapi import FastAPI

from backend.config import settings

app = FastAPI(
    title=settings.app_name,
    description="AI assistant and cloud security platform",
    version=settings.app_version,
)


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} API is running!",
        "status": "online",
        "environment": settings.app_env,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
    }
