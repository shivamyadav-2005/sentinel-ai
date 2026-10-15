
from backend.services.s3_scanner import (
    analyze_bucket_policy,
    analyze_bucket_public_access,
)


BUCKET_NAME = "sentinelai-demo-bucket"


def test_all_public_access_protections_enabled():
    result = analyze_bucket_public_access(
        BUCKET_NAME,
        {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            }
        },
    )

    assert result["status"] == "PASS"


def test_disabled_public_access_protection():
    result = analyze_bucket_public_access(
        BUCKET_NAME,
        {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": False,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            }
        },
    )

    assert result["status"] == "WARNING"
    assert result["severity"] == "HIGH"
    assert "BlockPublicAcls" in result["details"]["disabled_settings"]


def test_missing_public_access_block():
    result = analyze_bucket_public_access(BUCKET_NAME, None)

    assert result["status"] == "WARNING"
    assert result["severity"] == "HIGH"


def test_wildcard_principal_policy():
    result = analyze_bucket_policy(
        BUCKET_NAME,
        {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*",
                }
            ]
        },
    )

    assert result["status"] == "WARNING"
    assert result["severity"] == "HIGH"
    assert result["details"]["matching_statements"] == 1


def test_wildcard_aws_principal_in_dictionary():
    result = analyze_bucket_policy(
        BUCKET_NAME,
        {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                }
            ]
        },
    )

    assert result["status"] == "WARNING"


def test_wildcard_aws_principal_in_list():
    result = analyze_bucket_policy(
        BUCKET_NAME,
        {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["123456789012", "*"]},
                    "Action": "s3:GetObject",
                }
            ]
        },
    )

    assert result["status"] == "WARNING"


def test_non_wildcard_principal_policy():
    result = analyze_bucket_policy(
        BUCKET_NAME,
        {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "123456789012"},
                    "Action": "s3:GetObject",
                }
            ]
        },
    )

    assert result["status"] == "PASS"


def test_deny_statement_with_wildcard_is_not_flagged():
    result = analyze_bucket_policy(
        BUCKET_NAME,
        {
            "Statement": [
                {
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                }
            ]
        },
    )

    assert result["status"] == "PASS"


def test_policy_with_multiple_statements():
    result = analyze_bucket_policy(
        BUCKET_NAME,
        {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "123456789012"},
                    "Action": "s3:GetObject",
                },
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:PutObject",
                },
            ]
        },
    )

    assert result["status"] == "WARNING"
    assert result["details"]["matching_statements"] == 1


def test_missing_bucket_policy():
    result = analyze_bucket_policy(BUCKET_NAME, None)

    assert result["status"] == "WARNING"
    assert result["severity"] == "MEDIUM"
