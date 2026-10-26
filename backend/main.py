
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.errors import APIError
from backend.routes.health import router as health_router
from backend.routes.scans import router as scans_router

app = FastAPI(
    title=settings.app_name,
    description="AI assistant and cloud security platform",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


@app.exception_handler(APIError)
async def api_error_handler(
    request: Request,
    exc: APIError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        },
    )


app.include_router(health_router)
app.include_router(scans_router)
