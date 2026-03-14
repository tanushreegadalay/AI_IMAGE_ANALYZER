"""API tests for POST /api/analyze."""

from io import BytesIO

import pytest

# Skip entire module if litellm not installed (needed by app.llm.client)
pytest.importorskip("litellm")

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def small_image_bytes():
    buf = BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_analyze_success_returns_200_and_result(client, small_image_bytes):
    from app.schemas import AnalysisSuccess
    from unittest.mock import MagicMock
    from app.api.deps import get_analyzer_service

    mock_svc = MagicMock()
    mock_svc.analyze.return_value = AnalysisSuccess(
        result="Test analysis result.",
        cached=False,
        model="gpt-4o",
    )
    app.dependency_overrides[get_analyzer_service] = lambda: mock_svc

    try:
        r = client.post(
            "/api/analyze",
            files={"file": ("test.jpg", small_image_bytes, "image/jpeg")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["result"] == "Test analysis result."
        assert data["cached"] is False
        assert data["model"] == "gpt-4o"
    finally:
        app.dependency_overrides.pop(get_analyzer_service, None)


def test_analyze_api_key_missing_returns_400(client, small_image_bytes):
    from app.exceptions import ApiKeyMissingError
    from unittest.mock import MagicMock
    from app.api.deps import get_analyzer_service

    mock_svc = MagicMock()
    mock_svc.analyze.side_effect = ApiKeyMissingError("No API key for gpt-4o", provider="gpt-4o")
    app.dependency_overrides[get_analyzer_service] = lambda: mock_svc

    try:
        r = client.post(
            "/api/analyze",
            files={"file": ("test.jpg", small_image_bytes, "image/jpeg")},
        )
        assert r.status_code == 400
        data = r.json()
        assert data["success"] is False
        assert data["error"]["code"] == "API_KEY_MISSING"
        assert "message" in data["error"]
    finally:
        app.dependency_overrides.pop(get_analyzer_service, None)


def test_analyze_empty_file_returns_400(client):
    r = client.post(
        "/api/analyze",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert r.status_code == 400
    data = r.json()
    assert data["success"] is False
    assert data["error"]["code"] == "ANALYSIS_FAILED"
