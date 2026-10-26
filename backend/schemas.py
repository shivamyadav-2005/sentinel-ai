
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScanRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    region: str = Field(min_length=1)
    scan_name: str = Field(min_length=1, max_length=100)

    @field_validator("region")
    @classmethod
    def validate_region_format(cls, value: str) -> str:
        pattern = r"^[a-z]{2}(?:-gov)?-[a-z]+-\d+$"

        if not re.fullmatch(pattern, value):
            raise ValueError(
                "Region must follow a format such as ap-south-1"
            )

        return value


class ScanFinding(BaseModel):
    model_config = ConfigDict(extra="allow")

    bucket_name: str
    check: str
    status: Literal["PASS", "WARNING"]
    severity: Literal["INFO", "MEDIUM", "HIGH"]
    message: str
    details: dict[str, Any] | None = None
    explanation: str
    potential_impact: str
    remediation: list[str] = Field(min_length=1)


class ScanResponse(BaseModel):
    message: str
    scan: ScanRequest
    findings: list[ScanFinding]
    source: Literal["mock_data"]
