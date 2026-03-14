"""Analyzer service: orchestrate cache, image normalization, and LLM calls."""

from __future__ import annotations

import logging
import time
from io import BytesIO
from typing import TYPE_CHECKING, Optional

from PIL import Image

from app.cache.backend import CacheBackend
from app.exceptions import ApiKeyMissingError, AnalysisException, QuotaExceededError
from app.image_utils import hash_image_bytes, image_to_base64, normalize_image
from app.llm.client import analyze_image_with_llm
from app.schemas import AnalysisSuccess

if TYPE_CHECKING:
    from app.config import Settings

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 3


class AnalyzerService:
    """Orchestrates image analysis: normalize -> cache lookup -> LLM -> cache set."""

    def __init__(
        self,
        settings: "Settings",
        cache: CacheBackend,
    ) -> None:
        self._settings = settings
        self._cache = cache

    def analyze(
        self,
        image_bytes: bytes,
        model_override: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> AnalysisSuccess:
        """
        Analyze image and return structured success result.
        Raises ApiKeyMissingError, QuotaExceededError, or other AnalysisException on failure.
        """
        # Normalize image for consistent cache key and smaller payload
        pil_image = Image.open(BytesIO(image_bytes))
        _, jpeg_bytes = normalize_image(
            pil_image,
            max_dimension=self._settings.max_image_dimension,
            jpeg_quality=self._settings.jpeg_quality,
        )
        image_hash = hash_image_bytes(jpeg_bytes)
        model = model_override or self._settings.ai_model
        api_key = self._settings.get_api_key_for_model(model)

        if not api_key:
            provider = model.split("/")[0] if "/" in model else model
            raise ApiKeyMissingError(
                f"No API key found for {provider}. Set OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY.",
                provider=provider,
            )

        # Cache lookup
        cached = self._cache.get(image_hash)
        if cached is not None:
            logger.info("Cache hit for image hash %s", image_hash[:12])
            return AnalysisSuccess(result=cached, cached=True, model=model)

        # LLM call with retries for quota
        image_b64 = image_to_base64(jpeg_bytes)
        for attempt in range(max_retries):
            try:
                start = time.monotonic()
                result = analyze_image_with_llm(
                    model=model,
                    api_key=api_key,
                    image_base64=image_b64,
                )
                elapsed = time.monotonic() - start
                logger.info("Analysis completed in %.2fs (attempt %d)", elapsed, attempt + 1)
                self._cache.set(
                    image_hash,
                    result,
                    ttl_seconds=self._settings.cache_ttl_seconds,
                )
                return AnalysisSuccess(result=result, cached=False, model=model)
            except QuotaExceededError as e:
                if attempt < max_retries - 1:
                    wait_time = min(30 * (2 ** attempt), 300)
                    logger.warning("Quota exceeded, retrying in %ds (%d/%d)", wait_time, attempt + 1, max_retries)
                    time.sleep(wait_time)
                else:
                    raise
            except AnalysisException:
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning("Analysis failed, retrying in %ds: %s", wait_time, e)
                    time.sleep(wait_time)
                else:
                    from app.exceptions import AnalysisFailedError
                    raise AnalysisFailedError(str(e)) from e

        from app.exceptions import AnalysisFailedError
        raise AnalysisFailedError("Analysis failed after retries.")
