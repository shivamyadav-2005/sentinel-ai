
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.errors import APIError
from backend.routes.health import router as health_router

app = FastAPI(
    title=settings.app_name,
    description="AI assistant and cloud security platform",
    version=settings.app_version,
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
