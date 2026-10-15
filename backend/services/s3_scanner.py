
from typing import Any


def analyze_bucket_public_access(
    bucket_name: str,
    public_access_block: dict[str, Any] | None,
) -> dict[str, Any]:
    """Analyze an S3 bucket's public-access block configuration."""

    if public_access_block is None:
        return {
            "bucket_name": bucket_name,
            "check": "s3_public_access_block",
            "status": "WARNING",
            "severity": "HIGH",
            "message": (
                "Public access block configuration was not available. "
                "The bucket's public exposure is not yet confirmed."
            ),
        }

    settings = public_access_block.get(
        "PublicAccessBlockConfiguration",
        {},
    )

    protection_keys = [
        "BlockPublicAcls",
        "IgnorePublicAcls",
        "BlockPublicPolicy",
        "RestrictPublicBuckets",
    ]

    disabled_settings = [
        key for key in protection_keys
        if settings.get(key) is not True
    ]

    if disabled_settings:
        return {
            "bucket_name": bucket_name,
            "check": "s3_public_access_block",
            "status": "WARNING",
            "severity": "HIGH",
            "message": "One or more public-access protections are disabled.",
            "details": {
                "disabled_settings": disabled_settings,
            },
        }

    return {
        "bucket_name": bucket_name,
        "check": "s3_public_access_block",
        "status": "PASS",
        "severity": "INFO",
        "message": "All four public-access block settings are enabled.",
    }
