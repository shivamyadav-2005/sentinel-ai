
from typing import Any


SEVERITY_BASE_SCORES = {
    "HIGH": 80,
    "MEDIUM": 55,
    "LOW": 25,
    "INFO": 0,
}

STATUS_ADJUSTMENTS = {
    "WARNING": 10,
    "PASS": -20,
}


def classify_risk(score: int) -> str:
    """Classify a numerical risk score."""

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    if score > 0:
        return "LOW"

    return "INFO"


def calculate_risk_score(
    finding: dict[str, Any],
) -> dict[str, Any]:
    """Calculate an explainable prototype risk score."""

    severity = str(finding.get("severity", "UNKNOWN")).upper()
    status = str(finding.get("status", "UNKNOWN")).upper()

    base_score = SEVERITY_BASE_SCORES.get(severity, 0)
    adjustment = STATUS_ADJUSTMENTS.get(status, 0)

    final_score = max(
        0,
        min(100, base_score + adjustment),
    )

    factors = [
        f"Base score from {severity} severity: {base_score}."
    ]

    if status in STATUS_ADJUSTMENTS:
        sign = "+" if adjustment > 0 else ""
        factors.append(
            f"Status adjustment for {status}: {sign}{adjustment}."
        )
    else:
        factors.append(
            f"No scoring adjustment for unknown status: {status}."
        )

    factors.append(f"Final score: {final_score}/100.")

    explanation = " ".join(factors)

    return {
        "score": final_score,
        "level": classify_risk(final_score),
        "factors": factors,
        "explanation": explanation,
    }
