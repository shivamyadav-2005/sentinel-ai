
import pytest
from pydantic import ValidationError

from backend.schemas import ScanRequest


def test_scan_request_accepts_valid_data():
    request = ScanRequest(
        region="ap-south-1",
        scan_name="Security Audit",
    )

    assert request.region == "ap-south-1"
    assert request.scan_name == "Security Audit"


def test_scan_request_rejects_empty_region():
    with pytest.raises(ValidationError):
        ScanRequest(
            region="",
            scan_name="Security Audit",
        )


def test_scan_request_rejects_empty_scan_name():
    with pytest.raises(ValidationError):
        ScanRequest(
            region="ap-south-1",
            scan_name="",
        )
