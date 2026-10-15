
from fastapi import APIRouter

from backend.schemas import ScanRequest
from backend.services.s3_mock_data import (
    get_mock_bucket_name,
    get_mock_bucket_policy,
    get_mock_public_access_block,
)
from backend.services.s3_scanner import (
    analyze_bucket_policy,
    analyze_bucket_public_access,
)

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("/")
def create_scan(request: ScanRequest):
    # Local mock data only; no AWS API calls are made.
    bucket_name = get_mock_bucket_name()
    public_access_block = get_mock_public_access_block()
    bucket_policy = get_mock_bucket_policy()

    findings = [
        analyze_bucket_public_access(
            bucket_name,
            public_access_block,
        ),
        analyze_bucket_policy(
            bucket_name,
            bucket_policy,
        ),
    ]

    return {
        "message": "Scan analysis completed using mock data",
        "scan": request.model_dump(),
        "findings": findings,
        "source": "mock_data",
    }
