
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


def analyze_bucket_policy(
    bucket_name: str,
    policy: dict[str, Any] | None,
) -> dict[str, Any]:
    """Identify potentially public access in an S3 bucket policy."""

    if policy is None:
        return {
            "bucket_name": bucket_name,
            "check": "s3_bucket_policy",
            "status": "WARNING",
            "severity": "MEDIUM",
            "message": (
                "Bucket policy was unavailable. "
                "Public exposure could not be assessed."
            ),
        }

    statements = policy.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]

    public_statements = []

    for statement in statements:
        if not isinstance(statement, dict):
            continue

        if statement.get("Effect") != "Allow":
            continue

        principal = statement.get("Principal")

        if principal == "*":
            public_statements.append(statement)

        elif isinstance(principal, dict):
            aws_principal = principal.get("AWS")

            if aws_principal == "*":
                public_statements.append(statement)

            elif (
                isinstance(aws_principal, list)
                and "*" in aws_principal
            ):
                public_statements.append(statement)

    if public_statements:
        return {
            "bucket_name": bucket_name,
            "check": "s3_bucket_policy",
            "status": "WARNING",
            "severity": "HIGH",
            "message": (
                "Policy contains an Allow statement with a wildcard "
                "principal. Review its effective access."
            ),
            "details": {
                "matching_statements": len(public_statements),
            },
        }

    return {
        "bucket_name": bucket_name,
        "check": "s3_bucket_policy",
        "status": "PASS",
        "severity": "INFO",
        "message": (
            "No Allow statement with a wildcard principal was found "
            "by this basic policy check."
        ),
    }
