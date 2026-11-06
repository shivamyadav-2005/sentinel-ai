
from typing import Any


def analyze_question(
    question: str,
    findings: list[dict[str, Any]],
) -> dict[str, str]:
    """Generate a deterministic response from supplied scan findings."""

    normalized_question = question.lower()

    high_findings = [
        finding
        for finding in findings
        if finding.get("severity") == "HIGH"
    ]

    warning_findings = [
        finding
        for finding in findings
        if finding.get("status") == "WARNING"
    ]

    if not findings:
        return {
            "answer": "No scan findings were provided. Run a security scan first.",
            "priority": "LOW",
            "source": "rule_based_analysis",
        }

    if any(
        word in normalized_question
        for word in ["priority", "first", "urgent", "important", "critical"]
    ):
        if high_findings:
            finding = high_findings[0]
            answer = (
                f"Your highest-priority finding is "
                f"{finding.get('check', 'a security check')} "
                f"with {finding.get('severity')} severity. "
                f"{finding.get('explanation', finding.get('message', ''))}"
            )
            priority = "HIGH"
        elif warning_findings:
            finding = warning_findings[0]
            answer = (
                f"Review {finding.get('check', 'the security finding')} first. "
                f"{finding.get('explanation', finding.get('message', ''))}"
            )
            priority = "MEDIUM"
        else:
            answer = "No warning or HIGH severity findings were reported in this scan."
            priority = "LOW"

    elif any(
        word in normalized_question
        for word in ["fix", "remediation", "resolve", "repair"]
    ):
        if high_findings:
            finding = high_findings[0]
        elif warning_findings:
            finding = warning_findings[0]
        else:
            finding = findings[0]

        steps = finding.get("remediation", [])
        answer = (
            f"Recommended remediation for "
            f"{finding.get('check', 'this finding')}:\n"
            + "\n".join(
                f"{index}. {step}"
                for index, step in enumerate(steps, start=1)
            )
        ) if steps else (
            "No remediation steps are available for this finding yet."
        )
        priority = finding.get("severity", "LOW")

    elif any(
        word in normalized_question
        for word in ["explain", "impact", "risk", "why"]
    ):
        finding = high_findings[0] if high_findings else findings[0]

        answer = (
            f"Finding: {finding.get('message', 'No message available.')}\n\n"
            f"Explanation: {finding.get('explanation', 'Not available.')}\n\n"
            f"Potential impact: "
            f"{finding.get('potential_impact', 'Not available.')}"
        )
        priority = finding.get("severity", "LOW")

    else:
        answer = (
            f"Scan summary: {len(findings)} findings were provided. "
            f"{len(high_findings)} have HIGH severity and "
            f"{len(warning_findings)} have WARNING status."
        )

        if high_findings:
            answer += (
                f" Highest priority: "
                f"{high_findings[0].get('message', 'Review the HIGH severity finding.')}"
            )

        answer += (
            "\n\nYou can ask about priorities, risks, explanations, "
            "or remediation steps."
        )
        priority = "HIGH" if high_findings else (
            "MEDIUM" if warning_findings else "LOW"
        )

    return {
        "answer": answer,
        "priority": priority,
        "source": "rule_based_analysis",
    }
