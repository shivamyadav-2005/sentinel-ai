
def get_mock_bucket_name() -> str:
    """Return a fictional S3 bucket name for local testing."""
    return "sentinelai-demo-bucket"


def get_mock_public_access_block() -> dict:
    """Return sample S3 public-access-block settings."""
    return {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        }
    }


def get_mock_bucket_policy() -> dict:
    """Return a sample policy containing a wildcard principal."""
    bucket_name = get_mock_bucket_name()

    return {
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            }
        ]
    }
