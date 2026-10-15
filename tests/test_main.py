
from fastapi import Request
from fastapi.testclient import TestClient

from backend.errors import resource_not_found
from backend.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "SentinelAI API is running!",
        "status": "online",
        "environment": "development",
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "SentinelAI",
    }


def test_resource_not_found_error():
    error = resource_not_found("Conversation not found")

    assert error.status_code == 404
    assert error.detail == "Conversation not found"


def test_api_error_handler():
    async def trigger_api_error(request: Request):
        raise resource_not_found("Conversation not found")

    app.add_api_route(
        "/_test-api-error",
        trigger_api_error,
        methods=["GET"],
    )

    try:
        response = client.get("/_test-api-error")

        assert response.status_code == 404
        assert response.json() == {
            "error": {
                "message": "Conversation not found",
                "status_code": 404,
            }
        }
    finally:
        app.router.routes[:] = [
            route
            for route in app.router.routes
            if getattr(route, "path", None) != "/_test-api-error"
        ]


def test_create_scan_accepts_valid_request():
    response = client.post(
        "/scans/",
        json={
            "region": "ap-south-1",
            "scan_name": "Security Audit",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Scan analysis completed using mock data"
    assert data["scan"] == {
        "region": "ap-south-1",
        "scan_name": "Security Audit",
    }
    assert data["source"] == "mock_data"
    assert len(data["findings"]) == 2
    assert data["findings"][0]["status"] == "PASS"
    assert data["findings"][1]["status"] == "WARNING"


def test_create_scan_rejects_empty_region():
    response = client.post(
        "/scans/",
        json={
            "region": "",
            "scan_name": "Security Audit",
        },
    )

    assert response.status_code == 422
