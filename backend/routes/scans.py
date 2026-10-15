
from fastapi import APIRouter

from backend.schemas import ScanRequest
from backend.services.s3_scanner import (
    analyze_bucket_policy,
    analyze_bucket_public_access,
)

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("/")
def create_scan(request: ScanRequest):
    # Mocked data for local development.
    # This does not connect to AWS.
    mock_bucket_name = "sentinelai-demo-bucket"

    mock_public_access_block = {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        }
    }

    mock_bucket_policy = {
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": (
                    "arn:aws:s3:::sentinelai-demo-bucket/*"
                ),
            }
        ]
    }

    findings = [
        analyze_bucket_public_access(
            mock_bucket_name,
            mock_public_access_block,
        ),
        analyze_bucket_policy(
            mock_bucket_name,
            mock_bucket_policy,
        ),
    ]

    return {
        "message": "Scan analysis completed using mock data",
        "scan": request.model_dump(),
        "findings": findings,
        "source": "mock_data",
    }
