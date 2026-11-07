
import pytest
from backend.services.analyst import (
    analyze_question,
    find_matching_finding,
)


@pytest.fixture
def multiple_findings():
    return [
        {
            "bucket_name": "sentinel-demo-bucket",
            "check": "s3_public_access_block",
            "status": "WARNING",
            "severity": "HIGH",
            "message": "Public access protections are disabled.",
            "explanation": "Some public access protections are disabled.",
            "potential_impact": "The bucket may be exposed.",
            "remediation": ["Enable all four public access block settings."],
        },
        {
            "bucket_name": "sentinel-demo-bucket",
            "check": "s3_bucket_policy",
            "status": "WARNING",
            "severity": "MEDIUM",
            "message": "Bucket policy requires review.",
            "explanation": "The bucket policy needs inspection.",
            "potential_impact": "Unintended access may be possible.",
            "remediation": ["Review the bucket policy."],
        },
        {
            "bucket_name": "another-demo-bucket",
            "check": "ec2_ssh_exposure",
            "status": "WARNING",
            "severity": "HIGH",
            "message": "SSH access is open to the internet.",
            "explanation": "The security group permits public SSH access.",
            "potential_impact": "The instance may face unauthorized login attempts.",
            "remediation": ["Restrict SSH access to trusted IP addresses."],
        },
    ]


def test_matches_s3_bucket_policy(multiple_findings):
    finding = find_matching_finding(
        "Explain the S3 bucket policy issue",
        multiple_findings,
    )

    assert finding is not None
    assert finding["check"] == "s3_bucket_policy"


def test_matches_s3_public_access_block(multiple_findings):
    finding = find_matching_finding(
        "Explain the S3 public access block issue",
        multiple_findings,
    )

    assert finding is not None
    assert finding["check"] == "s3_public_access_block"


def test_matches_ec2_ssh_finding(multiple_findings):
    finding = find_matching_finding(
        "Explain EC2 SSH exposure",
        multiple_findings,
    )

    assert finding is not None
    assert finding["check"] == "ec2_ssh_exposure"


def test_matches_bucket_name(multiple_findings):
    finding = find_matching_finding(
        "Explain the risk for sentinel-demo-bucket",
        multiple_findings,
    )

    assert finding is not None
    assert finding["bucket_name"] == "sentinel-demo-bucket"


def test_missing_resource_returns_safe_message(multiple_findings):
    result = analyze_question(
        "Explain the RDS database encryption issue",
        multiple_findings,
    )

    assert "couldn't find a matching" in result["answer"].lower()
    assert result["priority"] == "LOW"


def test_specific_remediation_selects_correct_finding(multiple_findings):
    result = analyze_question(
        "How do I fix the S3 bucket policy?",
        multiple_findings,
    )

    assert "s3_bucket_policy" in result["answer"]
    assert "Review the bucket policy" in result["answer"]
    assert result["priority"] == "MEDIUM"


def test_specific_explanation_selects_correct_finding(multiple_findings):
    result = analyze_question(
        "Explain the EC2 SSH exposure risk",
        multiple_findings,
    )

    assert "SSH access is open to the internet" in result["answer"]
    assert "unauthorized login attempts" in result["answer"]
    assert result["priority"] == "HIGH"


def test_general_priority_question_keeps_highest_priority(multiple_findings):
    result = analyze_question(
        "Which issue should I fix first?",
        multiple_findings,
    )

    assert result["priority"] == "HIGH"
    assert "s3_public_access_block" in result["answer"]
