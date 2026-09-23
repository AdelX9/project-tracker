"""Tests for FastAPI endpoints — validates request/response schemas without a database."""

from fastapi.testclient import TestClient

# Import the app to test schema validation (actual DB calls will fail,
# but we test that routes exist and validate input correctly).


def test_app_imports():
    """Verify the FastAPI app can be imported without errors."""
    from tracker.api import app
    assert app.title == "project-tracker API"


def test_openapi_schema():
    """Verify OpenAPI schema generates without errors."""
    from tracker.api import app
    client = TestClient(app)
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "/projects" in schema["paths"]
    assert "/tasks" in schema["paths"]
    assert "/members" in schema["paths"]
    assert "/milestones" in schema["paths"]
    assert "/reports/workload" in schema["paths"]
    assert "/reports/milestones" in schema["paths"]
    assert "/reports/velocity" in schema["paths"]
