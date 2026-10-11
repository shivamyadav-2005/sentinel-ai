
from fastapi import APIRouter

from backend.schemas import ScanRequest

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("/")
def create_scan(request: ScanRequest):
    return {
        "message": "Scan request validated successfully",
        "scan": request.model_dump(),
    }
