
import pytest
from pydantic import ValidationError

from backend.routes.scans import add_remediation_guidance
from backend.schemas import ScanFinding, ScanResponse


@pytest.mark.parametrize(
    ("check", "status"),
    [
        ("s3_public_access_block", "PASS"),
        ("s3_public_access_block", "WARNING"),
        ("s3_bucket_policy", "WARNING"),
        ("s3_bucket_policy", "PASS"),
        ("unknown_check", "WARNING"),
    ],
)
def test_remediation_guidance_adds_required_fields(check, status):
    finding = {
        "bucket_name": "sentinel-demo-bucket",
        "check": check,
        "status": status,
        "severity": "HIGH" if status == "WARNING" else "INFO",
        "message": "Test security finding",
        "details": {},
    }

    enriched = add_remediation_guidance(finding)

    assert isinstance(enriched["explanation"], str)
    assert enriched["explanation"].strip()
    assert isinstance(enriched["potential_impact"], str)
    assert enriched["potential_impact"].strip()
    assert isinstance(enriched["remediation"], list)
    assert enriched["remediation"]
    assert all(
        isinstance(step, str) and step.strip()
        for step in enriched["remediation"]
    )


def test_wildcard_policy_guidance_explains_context_and_risk():
    finding = {
        "bucket_name": "sentinel-demo-bucket",
        "check": "s3_bucket_policy",
        "status": "WARNING",
        "severity": "HIGH",
        "message": "Wildcard principal detected",
        "details": {"principal": "*"},
    }

    enriched = add_remediation_guidance(finding)

    assert "wildcard principal" in enriched["explanation"].lower()
    assert "does not prove" in enriched["potential_impact"].lower()
    assert any(
        "Principal set to" in step
        for step in enriched["remediation"]
    )


def test_public_access_block_pass_guidance_recommends_reviewing_policies():
    finding = {
        "bucket_name": "sentinel-demo-bucket",
        "check": "s3_public_access_block",
        "status": "PASS",
        "severity": "INFO",
        "message": "All public-access block settings are enabled",
        "details": {},
    }

    enriched = add_remediation_guidance(finding)

    assert "four" in enriched["explanation"].lower()
    assert any(
        "bucket policies" in step.lower()
        for step in enriched["remediation"]
    )


def test_scan_finding_requires_remediation_guidance():
    base_finding = {
        "bucket_name": "sentinel-demo-bucket",
        "check": "s3_bucket_policy",
        "status": "WARNING",
        "severity": "HIGH",
        "message": "Wildcard principal detected",
    }

    with pytest.raises(ValidationError):
        ScanFinding(**base_finding)


def test_scan_finding_accepts_complete_guidance():
    finding = ScanFinding(
        bucket_name="sentinel-demo-bucket",
        check="s3_bucket_policy",
        status="WARNING",
        severity="HIGH",
        message="Wildcard principal detected",
        explanation="The policy contains a wildcard principal.",
        potential_impact="It may permit unintended access.",
        remediation=[
            "Review the policy.",
            "Verify effective permissions.",
        ],
    )

    assert finding.explanation
    assert finding.potential_impact
    assert len(finding.remediation) == 2


def test_scan_response_source_is_limited_to_mock_data():
    with pytest.raises(ValidationError):
        ScanResponse(
            message="Test scan",
            scan={"region": "ap-south-1", "scan_name": "Test"},
            findings=[],
            source="live_aws",
        )
