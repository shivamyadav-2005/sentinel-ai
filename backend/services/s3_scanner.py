
from typing import Any


def analyze_bucket_public_access(
    bucket_name: str,
    public_access_block: dict[str, Any] | None,
) -> dict[str, Any]:
    """Analyze an S3 bucket's public-access block configuration."""

    check = "s3_public_access_block"

    if not isinstance(public_access_block, dict):
        return {
            "bucket_name": bucket_name,
            "check": check,
            "status": "WARNING",
            "severity": "HIGH",
            "message": (
                "Public access block configuration is missing or invalid. "
                "The bucket's public exposure is not confirmed."
            ),
        }

    settings = public_access_block.get(
        "PublicAccessBlockConfiguration"
    )

    if not isinstance(settings, dict):
        return {
            "bucket_name": bucket_name,
            "check": check,
            "status": "WARNING",
            "severity": "HIGH",
            "message": (
                "Public access block settings are missing or invalid. "
                "The bucket's public exposure is not confirmed."
            ),
        }

    protection_keys = [
        "BlockPublicAcls",
        "IgnorePublicAcls",
        "BlockPublicPolicy",
        "RestrictPublicBuckets",
    ]

    disabled_settings = [
        key
        for key in protection_keys
        if settings.get(key) is not True
    ]

    if disabled_settings:
        return {
            "bucket_name": bucket_name,
            "check": check,
            "status": "WARNING",
            "severity": "HIGH",
            "message": (
                "One or more public-access protections are disabled "
                "or have invalid values."
            ),
            "details": {
                "disabled_settings": disabled_settings,
            },
        }

    return {
        "bucket_name": bucket_name,
        "check": check,
        "status": "PASS",
        "severity": "INFO",
        "message": "All four public-access block settings are enabled.",
    }


def analyze_bucket_policy(
    bucket_name: str,
    policy: dict[str, Any] | None,
) -> dict[str, Any]:
    """Identify potentially public access in an S3 bucket policy."""

    check = "s3_bucket_policy"

    if not isinstance(policy, dict):
        return {
            "bucket_name": bucket_name,
            "check": check,
            "status": "WARNING",
            "severity": "MEDIUM",
            "message": (
                "Bucket policy is missing or invalid. "
                "Public exposure could not be assessed."
            ),
        }

    if "Statement" not in policy:
        return {
            "bucket_name": bucket_name,
            "check": check,
            "status": "WARNING",
            "severity": "MEDIUM",
            "message": "Bucket policy does not contain a Statement field.",
        }

    statements = policy["Statement"]

    if isinstance(statements, dict):
        statements = [statements]
    elif not isinstance(statements, list):
        return {
            "bucket_name": bucket_name,
            "check": check,
            "status": "WARNING",
            "severity": "MEDIUM",
            "message": "Bucket policy Statement must be a list or object.",
        }

    public_statements = []
    invalid_statements = []

    for statement in statements:
        if not isinstance(statement, dict):
            invalid_statements.append(statement)
            continue

        effect = statement.get("Effect")

        if effect not in ("Allow", "Deny"):
            invalid_statements.append(statement)
            continue

        if effect == "Deny":
            continue

        principal = statement.get("Principal")

        is_wildcard = principal == "*"

        if isinstance(principal, dict):
            aws_principal = principal.get("AWS")

            is_wildcard = (
                aws_principal == "*"
                or (
                    isinstance(aws_principal, list)
                    and "*" in aws_principal
                )
            )

        if is_wildcard:
            public_statements.append(statement)

    if public_statements:
        return {
            "bucket_name": bucket_name,
            "check": check,
            "status": "WARNING",
            "severity": "HIGH",
            "message": (
                "Policy contains an Allow statement with a wildcard "
                "principal. Review its effective access."
            ),
            "details": {
                "matching_statements": len(public_statements),
                "invalid_statements": len(invalid_statements),
            },
        }

    if invalid_statements:
        return {
            "bucket_name": bucket_name,
            "check": check,
            "status": "WARNING",
            "severity": "MEDIUM",
            "message": (
                "Some policy statements are invalid or incomplete. "
                "The policy could not be fully assessed."
            ),
            "details": {
                "invalid_statements": len(invalid_statements),
            },
        }

    return {
        "bucket_name": bucket_name,
        "check": check,
        "status": "PASS",
        "severity": "INFO",
        "message": (
            "No Allow statement with a wildcard principal was found "
            "by this basic policy check."
        ),
    }
