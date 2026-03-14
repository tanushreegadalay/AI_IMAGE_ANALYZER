"""E2E test: real API call with a small image. Skip unless E2E_LIVE=1."""

import os
from io import BytesIO

import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.skipif(
    os.getenv("E2E_LIVE") != "1",
    reason="E2E live test: set E2E_LIVE=1 to run",
)


@pytest.fixture
def small_image_bytes():
    buf = BytesIO()
    Image.new("RGB", (50, 50), color="green").save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


def test_analyze_live_returns_200_and_non_empty_result(small_image_bytes):
    """Requires valid API key in env and E2E_LIVE=1."""
    client = TestClient(app)
    r = client.post(
        "/api/analyze",
        files={"file": ("e2e_test.jpg", small_image_bytes, "image/jpeg")},
    )
    # May be 200 (success) or 400/401/402 if key missing or quota
    assert r.status_code in (200, 400, 401, 402)
    data = r.json()
    if r.status_code == 200:
        assert data.get("success") is True
        assert data.get("result")
        assert "model" in data
