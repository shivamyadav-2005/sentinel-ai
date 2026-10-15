
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


def test_scan_request_rejects_whitespace_only_region():
    with pytest.raises(ValidationError):
        ScanRequest(
            region="   ",
            scan_name="Security Audit",
        )


def test_scan_request_rejects_whitespace_only_scan_name():
    with pytest.raises(ValidationError):
        ScanRequest(
            region="ap-south-1",
            scan_name="   ",
        )


def test_scan_request_strips_surrounding_whitespace():
    request = ScanRequest(
        region="  ap-south-1  ",
        scan_name="  Security Audit  ",
    )

    assert request.region == "ap-south-1"
    assert request.scan_name == "Security Audit"


def test_scan_request_rejects_invalid_region_format():
    with pytest.raises(ValidationError):
        ScanRequest(
            region="abc",
            scan_name="Security Audit",
        )


def test_scan_request_accepts_valid_region_format():
    request = ScanRequest(
        region="eu-west-2",
        scan_name="Security Audit",
    )

    assert request.region == "eu-west-2"
