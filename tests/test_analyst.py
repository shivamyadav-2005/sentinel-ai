
import pytest
from pydantic import ValidationError

from backend.analyst_schemas import (
    AnalystChatRequest,
    AnalystChatResponse,
)
from backend.services.analyst import analyze_question


@pytest.fixture
def sample_findings():
    return [
        {
            "check": "s3_bucket_policy",
            "status": "WARNING",
            "severity": "HIGH",
            "message": "Wildcard principal detected",
            "explanation": "The bucket policy contains a wildcard principal.",
            "potential_impact": "It may allow unintended access.",
            "remediation": [
                "Review the bucket policy.",
                "Replace unnecessary wildcard principals.",
            ],
        },
        {
            "check": "s3_public_access_block",
            "status": "PASS",
            "severity": "INFO",
            "message": "All public access block settings are enabled",
            "explanation": "All four settings are enabled.",
            "potential_impact": "Public access is restricted by these settings.",
            "remediation": ["Review bucket policies regularly."],
        },
    ]


def test_priority_question_identifies_high_severity(sample_findings):
    result = analyze_question(
        "Which issue should I fix first?",
        sample_findings,
    )

    assert result["priority"] == "HIGH"
    assert "s3_bucket_policy" in result["answer"]


def test_priority_question_handles_warning_without_high_severity():
    findings = [
        {
            "check": "s3_bucket_policy",
            "status": "WARNING",
            "severity": "MEDIUM",
            "message": "Policy requires review",
        }
    ]

    result = analyze_question("What is the priority?", findings)

    assert result["priority"] == "MEDIUM"
    assert "s3_bucket_policy" in result["answer"]


def test_priority_question_handles_no_warnings():
    findings = [
        {
            "check": "s3_public_access_block",
            "status": "PASS",
            "severity": "INFO",
            "message": "All settings enabled",
        }
    ]

    result = analyze_question("What is the most urgent issue?", findings)

    assert result["priority"] == "LOW"
    assert "No warning or HIGH severity" in result["answer"]


def test_remediation_question_returns_steps(sample_findings):
    result = analyze_question(
        "How can I fix this issue?",
        sample_findings,
    )

    assert result["priority"] == "HIGH"
    assert "Review the bucket policy" in result["answer"]
    assert "Replace unnecessary wildcard principals" in result["answer"]


def test_remediation_question_handles_missing_steps():
    findings = [
        {
            "check": "unknown_check",
            "status": "WARNING",
            "severity": "LOW",
            "message": "Unknown finding",
        }
    ]

    result = analyze_question("How do I fix this?", findings)

    assert "No remediation steps are available" in result["answer"]


def test_explanation_question_returns_risk_information(sample_findings):
    result = analyze_question(
        "Explain the potential risk",
        sample_findings,
    )

    assert result["priority"] == "HIGH"
    assert "Wildcard principal detected" in result["answer"]
    assert "Explanation:" in result["answer"]
    assert "Potential impact:" in result["answer"]


def test_general_question_returns_scan_summary(sample_findings):
    result = analyze_question("Give me a summary", sample_findings)

    assert result["priority"] == "HIGH"
    assert "2 findings were provided" in result["answer"]
    assert "1 have HIGH severity" in result["answer"]


def test_empty_findings_returns_safe_response():
    result = analyze_question("Explain the scan", [])

    assert result["priority"] == "LOW"
    assert "No scan findings were provided" in result["answer"]


def test_analysis_response_has_correct_source(sample_findings):
    result = analyze_question("Give me a summary", sample_findings)

    response = AnalystChatResponse(**result)

    assert response.source == "rule_based_analysis"
    assert response.priority == "HIGH"
    assert response.answer


def test_request_accepts_valid_data(sample_findings):
    request = AnalystChatRequest(
        question="Which issue is most important?",
        findings=sample_findings,
    )

    assert request.question
    assert len(request.findings) == 2


def test_request_rejects_empty_question(sample_findings):
    with pytest.raises(ValidationError):
        AnalystChatRequest(question="   ", findings=sample_findings)


def test_request_rejects_empty_findings():
    with pytest.raises(ValidationError):
        AnalystChatRequest(question="Explain the scan", findings=[])


def test_request_rejects_question_over_1000_characters(sample_findings):
    with pytest.raises(ValidationError):
        AnalystChatRequest(
            question="a" * 1001,
            findings=sample_findings,
        )


def test_response_rejects_invalid_priority():
    with pytest.raises(ValidationError):
        AnalystChatResponse(
            answer="Test response",
            priority="CRITICAL",
            source="rule_based_analysis",
        )


def test_response_rejects_invalid_source():
    with pytest.raises(ValidationError):
        AnalystChatResponse(
            answer="Test response",
            priority="HIGH",
            source="live_aws",
        )
