"""Unit tests for AnalyzerService."""

from unittest.mock import patch

import pytest

# Skip entire module if litellm not installed (needed by app.llm.client)
pytest.importorskip("litellm")

from app.exceptions import ApiKeyMissingError, QuotaExceededError
from app.schemas import AnalysisSuccess
from app.service.analyzer import AnalyzerService


def test_analyze_returns_cached_result_when_cache_hit(mock_cache, mock_settings, sample_image_bytes):
    # Pre-populate cache with a known hash (we need the hash the service will use)
    from app.image_utils import hash_image_bytes, normalize_image
    from PIL import Image
    from io import BytesIO
    pil = Image.open(BytesIO(sample_image_bytes))
    _, jpeg_bytes = normalize_image(pil, max_dimension=2048, jpeg_quality=85)
    h = hash_image_bytes(jpeg_bytes)
    mock_cache.set(h, "Cached analysis text")

    service = AnalyzerService(settings=mock_settings, cache=mock_cache)
    result = service.analyze(image_bytes=sample_image_bytes)
    assert isinstance(result, AnalysisSuccess)
    assert result.cached is True
    assert result.result == "Cached analysis text"
    assert result.model == mock_settings.ai_model


def test_analyze_raises_api_key_missing_when_no_key(mock_cache, sample_image_bytes):
    from unittest.mock import MagicMock
    settings = MagicMock()
    settings.ai_model = "gpt-4o"
    settings.max_image_dimension = 2048
    settings.jpeg_quality = 85
    settings.cache_ttl_seconds = None
    settings.get_api_key_for_model = MagicMock(return_value=None)
    service = AnalyzerService(settings=settings, cache=mock_cache)
    with pytest.raises(ApiKeyMissingError) as exc_info:
        service.analyze(image_bytes=sample_image_bytes)
    assert exc_info.value.code == "API_KEY_MISSING"


@patch("app.service.analyzer.analyze_image_with_llm")
def test_analyze_calls_llm_and_returns_success_on_cache_miss(
    mock_llm, mock_cache, mock_settings, sample_image_bytes
):
    mock_llm.return_value = "AI analysis result here"
    service = AnalyzerService(settings=mock_settings, cache=mock_cache)
    result = service.analyze(image_bytes=sample_image_bytes)
    assert isinstance(result, AnalysisSuccess)
    assert result.cached is False
    assert result.result == "AI analysis result here"
    mock_llm.assert_called_once()
    # Check cache was written
    from app.image_utils import hash_image_bytes, normalize_image
    from PIL import Image
    from io import BytesIO
    pil = Image.open(BytesIO(sample_image_bytes))
    _, jpeg_bytes = normalize_image(pil, max_dimension=2048, jpeg_quality=85)
    h = hash_image_bytes(jpeg_bytes)
    assert mock_cache.get(h) == "AI analysis result here"


@patch("app.service.analyzer.analyze_image_with_llm")
def test_analyze_raises_quota_exceeded_when_llm_raises(mock_llm, mock_cache, mock_settings, sample_image_bytes):
    from app.exceptions import QuotaExceededError
    mock_llm.side_effect = QuotaExceededError("Quota exceeded")
    service = AnalyzerService(settings=mock_settings, cache=mock_cache)
    with pytest.raises(QuotaExceededError):
        service.analyze(image_bytes=sample_image_bytes, max_retries=1)
