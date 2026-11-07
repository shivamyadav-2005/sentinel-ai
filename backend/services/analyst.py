
import re
from typing import Any

from backend.services.risk_scoring import calculate_risk_score


STOP_WORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how",
    "i", "in", "is", "it", "me", "my", "of", "or", "our", "please",
    "should", "the", "this", "to", "we", "what", "which", "why",
    "with", "first", "most", "important", "urgent", "critical",
    "issue", "issues", "problem", "problems", "security",
    "explain", "impact", "risk", "fix", "repair", "resolve",
    "remediation", "tell", "show", "find", "finding",
}

RESOURCE_TERMS = {
    "s3", "bucket", "policy", "public", "access",
    "ec2", "ssh", "instance", "securitygroup", "port",
    "iam", "mfa", "user", "role", "permission",
    "network", "firewall", "encryption",
}


def tokenize(value: str) -> set[str]:
    """Convert text into normalized searchable tokens."""

    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if token not in STOP_WORDS
    }


def get_finding_tokens(finding: dict[str, Any]) -> set[str]:
    """Collect searchable text from a security finding."""

    searchable_fields = [
        finding.get("check", ""),
        finding.get("message", ""),
        finding.get("bucket_name", ""),
    ]

    searchable_text = " ".join(
        str(value)
        for value in searchable_fields
        if value is not None
    )

    return tokenize(searchable_text)


def find_matching_finding(
    question: str,
    findings: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Find the most relevant finding mentioned in a question."""

    question_tokens = tokenize(question)

    if not question_tokens:
        return None

    best_finding = None
    best_score = 0

    for finding in findings:
        check_tokens = tokenize(str(finding.get("check", "")))
        message_tokens = tokenize(str(finding.get("message", "")))
        bucket_tokens = tokenize(str(finding.get("bucket_name", "")))

        score = (
            len(question_tokens & check_tokens) * 3
            + len(question_tokens & message_tokens)
            + len(question_tokens & bucket_tokens) * 4
        )

        if score > best_score:
            best_score = score
            best_finding = finding

    return best_finding


def has_specific_resource_reference(question: str) -> bool:
    """Check whether a question names a cloud resource or security concept."""

    return bool(tokenize(question) & RESOURCE_TERMS)


def analyze_question(
    question: str,
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate deterministic analysis and risk information."""

    normalized_question = question.lower()
    selected_finding = None

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
            "risk_score": None,
            "risk_level": None,
            "risk_explanation": None,
        }

    matched_finding = find_matching_finding(question, findings)

    if (
        matched_finding is None
        and has_specific_resource_reference(question)
    ):
        return {
            "answer": (
                "I couldn't find a matching security finding for the "
                "resource or issue mentioned in your question. "
                "Check the finding name or run the relevant security scan."
            ),
            "priority": "LOW",
            "source": "rule_based_analysis",
            "risk_score": None,
            "risk_level": None,
            "risk_explanation": None,
        }

    if any(
        word in normalized_question
        for word in ["priority", "first", "urgent", "important", "critical"]
    ):
        selected_finding = matched_finding

        if selected_finding is None:
            if high_findings:
                selected_finding = high_findings[0]
            elif warning_findings:
                selected_finding = warning_findings[0]

        if selected_finding is None:
            answer = (
                "No warning or HIGH severity findings were reported "
                "in this scan."
            )
            priority = "LOW"
        else:
            answer = (
                f"Your selected priority finding is "
                f"{selected_finding.get('check', 'a security check')} "
                f"with {selected_finding.get('severity', 'UNKNOWN')} severity. "
                f"{selected_finding.get('explanation', selected_finding.get('message', ''))}"
            )
            priority = selected_finding.get("severity", "LOW")

            if priority not in {"HIGH", "MEDIUM", "LOW"}:
                priority = "LOW"

    elif any(
        word in normalized_question
        for word in ["fix", "remediation", "resolve", "repair"]
    ):
        selected_finding = matched_finding

        if selected_finding is None:
            if high_findings:
                selected_finding = high_findings[0]
            elif warning_findings:
                selected_finding = warning_findings[0]
            else:
                selected_finding = findings[0]

        steps = selected_finding.get("remediation", [])

        if steps:
            answer = (
                f"Recommended remediation for "
                f"{selected_finding.get('check', 'this finding')}:\n"
                + "\n".join(
                    f"{index}. {step}"
                    for index, step in enumerate(steps, start=1)
                )
            )
        else:
            answer = (
                "No remediation steps are available for this finding yet."
            )

        priority = selected_finding.get("severity", "LOW")

        if priority not in {"HIGH", "MEDIUM", "LOW"}:
            priority = "LOW"

    elif any(
        word in normalized_question
        for word in ["explain", "impact", "risk", "why"]
    ):
        selected_finding = matched_finding

        if selected_finding is None:
            selected_finding = high_findings[0] if high_findings else findings[0]

        answer = (
            f"Finding: {selected_finding.get('message', 'No message available.')}\n\n"
            f"Explanation: {selected_finding.get('explanation', 'Not available.')}\n\n"
            f"Potential impact: "
            f"{selected_finding.get('potential_impact', 'Not available.')}"
        )

        priority = selected_finding.get("severity", "LOW")

        if priority not in {"HIGH", "MEDIUM", "LOW"}:
            priority = "LOW"

    else:
        answer = (
            f"Scan summary: {len(findings)} findings were provided. "
            f"{len(high_findings)} have HIGH severity and "
            f"{len(warning_findings)} have WARNING status."
        )

        if high_findings:
            selected_finding = high_findings[0]
            answer += (
                f" Highest priority: "
                f"{selected_finding.get('message', 'Review the HIGH severity finding.')}"
            )
        elif warning_findings:
            selected_finding = warning_findings[0]
        else:
            selected_finding = findings[0]

        answer += (
            "\n\nYou can ask about priorities, risks, explanations, "
            "or remediation steps."
        )

        priority = "HIGH" if high_findings else (
            "MEDIUM" if warning_findings else "LOW"
        )

    risk_result = (
        calculate_risk_score(selected_finding)
        if selected_finding is not None
        else None
    )

    return {
        "answer": answer,
        "priority": priority,
        "source": "rule_based_analysis",
        "risk_score": risk_result["score"] if risk_result else None,
        "risk_level": risk_result["level"] if risk_result else None,
        "risk_explanation": (
            risk_result["explanation"] if risk_result else None
        ),
    }
