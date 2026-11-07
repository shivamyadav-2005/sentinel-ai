
import pytest

from backend.services.risk_scoring import (
    calculate_risk_score,
    classify_risk,
)


@pytest.mark.parametrize(
    ("severity", "status", "expected_score", "expected_level"),
    [
        ("HIGH", "WARNING", 90, "HIGH"),
        ("MEDIUM", "WARNING", 65, "MEDIUM"),
        ("LOW", "WARNING", 35, "LOW"),
        ("INFO", "PASS", 0, "INFO"),
        ("HIGH", "PASS", 60, "MEDIUM"),
        ("MEDIUM", "PASS", 35, "LOW"),
        ("UNKNOWN", "WARNING", 10, "LOW"),
        ("UNKNOWN", "PASS", 0, "INFO"),
    ],
)
def test_calculate_risk_score(
    severity,
    status,
    expected_score,
    expected_level,
):
    result = calculate_risk_score(
        {
            "severity": severity,
            "status": status,
        }
    )

    assert result["score"] == expected_score
    assert result["level"] == expected_level


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (100, "HIGH"),
        (70, "HIGH"),
        (69, "MEDIUM"),
        (40, "MEDIUM"),
        (39, "LOW"),
        (1, "LOW"),
        (0, "INFO"),
    ],
)
def test_classify_risk(score, expected):
    assert classify_risk(score) == expected


def test_risk_score_contains_explanation():
    result = calculate_risk_score(
        {
            "severity": "HIGH",
            "status": "WARNING",
        }
    )

    assert result["factors"]
    assert "HIGH severity" in result["explanation"]
    assert "WARNING" in result["explanation"]
    assert "90/100" in result["explanation"]


def test_risk_score_is_always_between_zero_and_100():
    result = calculate_risk_score(
        {
            "severity": "HIGH",
            "status": "WARNING",
        }
    )

    assert 0 <= result["score"] <= 100
