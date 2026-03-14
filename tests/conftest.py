"""Pytest fixtures for AI Image Analyzer tests."""

from io import BytesIO
from unittest.mock import MagicMock

import pytest
from PIL import Image


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Minimal valid JPEG bytes (1x1 red pixel)."""
    img = Image.new("RGB", (1, 1), color="red")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def sample_image_bytes_100x100() -> bytes:
    """Larger test image (100x100) for normalization tests."""
    img = Image.new("RGB", (100, 100), color="blue")
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=90)
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def mock_cache():
    """In-memory cache backend for tests."""
    storage = {}

    class MockCache:
        def get(self, key: str):
            return storage.get(key)

        def set(self, key: str, value: str, ttl_seconds=None):
            storage[key] = value

    return MockCache()


@pytest.fixture
def mock_settings():
    """Settings with test model and API key (for unit tests that don't call real API)."""
    settings = MagicMock()
    settings.ai_model = "gpt-4o"
    settings.max_image_dimension = 2048
    settings.jpeg_quality = 85
    settings.cache_ttl_seconds = None
    settings.get_api_key_for_model = MagicMock(return_value="sk-test-key")
    return settings
