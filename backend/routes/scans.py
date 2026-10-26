
from typing import Any

from fastapi import APIRouter

from backend.schemas import ScanRequest, ScanResponse
from backend.services.s3_mock_data import (
    get_mock_bucket_name,
    get_mock_bucket_policy,
    get_mock_public_access_block,
)
from backend.services.s3_scanner import (
    analyze_bucket_policy,
    analyze_bucket_public_access,
)

router = APIRouter(prefix="/scans", tags=["Scans"])


def add_remediation_guidance(
    finding: dict[str, Any],
) -> dict[str, Any]:
    """Attach rule-based explanation, impact, and remediation."""

    check = finding.get("check")
    status = finding.get("status")

    if check == "s3_public_access_block":
        if status == "PASS":
            explanation = (
                "The four S3 Block Public Access settings are enabled "
                "in the supplied demo configuration."
            )
            impact = (
                "These settings help prevent common public-access paths, "
                "but do not prove every possible access path is safe."
            )
            remediation = [
                "Keep all four public-access block settings enabled "
                "unless a documented business requirement says otherwise.",
                "Review bucket policies, access point policies, and "
                "other applicable permissions separately.",
                "Verify the settings in the intended AWS account during "
                "a real audit."
            ]
        else:
            explanation = (
                "One or more public-access block settings are missing, "
                "disabled, or could not be verified in the demo data."
            )
            impact = (
                "Depending on other permissions, this configuration may "
                "allow unintended public access to stored objects."
            )
            remediation = [
                "Review all four S3 Block Public Access settings.",
                "Enable appropriate account-level and bucket-level "
                "public-access protections.",
                "Review bucket policies, access point policies, and "
                "object permissions.",
                "Verify the configuration in the correct AWS account."
            ]

    elif check == "s3_bucket_policy":
        if status == "WARNING":
            explanation = (
                "The supplied policy contains an Allow statement with "
                "a wildcard principal (*). This can grant broad access, "
                "depending on the action, resource, conditions, and "
                "other applicable controls."
            )
            impact = (
                "If the statement permits access to sensitive objects, "
                "data could be exposed to unintended users. A wildcard "
                "principal alone does not prove the bucket is public."
            )
            remediation = [
                "Inspect the bucket policy statement containing "
                'Principal set to "*".',
                "Review its Effect, Action, Resource, and Condition "
                "elements to understand the access it may grant.",
                "If broad access is unnecessary, replace the wildcard "
                "principal with the specific account, role, or service "
                "that requires access.",
                "Review S3 Block Public Access settings where appropriate.",
                "Test the intended access and validate the final policy "
                "before deploying changes."
            ]
        else:
            explanation = (
                "The basic policy checks did not detect the specific "
                "wildcard-principal Allow pattern they look for."
            )
            impact = (
                "This is not a guarantee that the policy is safe. "
                "The scanner does not evaluate every AWS authorization "
                "rule or effective permission."
            )
            remediation = [
                "Review the full bucket policy for excessive permissions.",
                "Check identity policies, access point policies, and "
                "other applicable access controls.",
                "Verify effective permissions in AWS before treating "
                "the bucket as secure."
            ]

    else:
        explanation = (
            "This check does not yet have a dedicated explanation."
        )
        impact = (
            "Review the finding and its configuration details to "
            "determine whether action is required."
        )
        remediation = [
            "Inspect the finding and the relevant configuration.",
            "Verify the result against the actual cloud environment."
        ]

    return {
        **finding,
        "explanation": explanation,
        "potential_impact": impact,
        "remediation": remediation,
    }


@router.post("/", response_model=ScanResponse)
def create_scan(request: ScanRequest) -> ScanResponse:
    # Local mock data only; no AWS API calls are made.
    bucket_name = get_mock_bucket_name()
    public_access_block = get_mock_public_access_block()
    bucket_policy = get_mock_bucket_policy()

    raw_findings = [
        analyze_bucket_public_access(
            bucket_name,
            public_access_block,
        ),
        analyze_bucket_policy(
            bucket_name,
            bucket_policy,
        ),
    ]

    findings = [
        add_remediation_guidance(finding)
        for finding in raw_findings
    ]

    return ScanResponse(
        message="Scan analysis completed using mock data",
        scan=request,
        findings=findings,
        source="mock_data",
    )
