
from backend.services.s3_scanner import analyze_bucket_public_access


def test_all_public_access_protections_enabled():
    config = {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        }
    }

    result = analyze_bucket_public_access(
        "test-bucket",
        config,
    )

    assert result["status"] == "PASS"
    assert result["severity"] == "INFO"


def test_disabled_protection_returns_warning():
    config = {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": False,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        }
    }

    result = analyze_bucket_public_access(
        "test-bucket",
        config,
    )

    assert result["status"] == "WARNING"
    assert result["severity"] == "HIGH"
    assert "BlockPublicAcls" in result["details"]["disabled_settings"]


def test_missing_configuration_returns_warning():
    result = analyze_bucket_public_access(
        "test-bucket",
        None,
    )

    assert result["status"] == "WARNING"
    assert "not yet confirmed" in result["message"]
