
from fastapi import FastAPI

app = FastAPI(
    title="SentinelAI",
    description="AI assistant and cloud security platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "SentinelAI API is running!",
        "status": "online",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SentinelAI",
    }
