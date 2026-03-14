"""LLM client for vision API calls via LiteLLM."""

from __future__ import annotations

import logging
from typing import Optional

import litellm

from app.exceptions import (
    ApiKeyInvalidError,
    AnalysisFailedError,
    QuotaExceededError,
)

logger = logging.getLogger(__name__)

DEFAULT_PROMPT = "Analyze this image professionally. Provide detailed insights about what you see."


def analyze_image_with_llm(
    model: str,
    api_key: str,
    image_base64: str,
    prompt: str = DEFAULT_PROMPT,
) -> str:
    """
    Call vision LLM with the given image and prompt.
    Raises QuotaExceededError, ApiKeyInvalidError, or AnalysisFailedError on failure.
    """
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
            ],
        }
    ]

    try:
        response = litellm.completion(
            model=model,
            messages=messages,
            api_key=api_key,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        error_str = str(e).lower()
        if "quota" in error_str or "429" in error_str:
            logger.warning("LLM quota/rate limit: %s", e)
            raise QuotaExceededError(
                "API quota or rate limit exceeded. Retry later or upgrade your plan."
            ) from e
        if "403" in error_str or "forbidden" in error_str or "invalid" in error_str or "invalid_api_key" in error_str:
            logger.warning("LLM API key error: %s", e)
            raise ApiKeyInvalidError(
                "API key is invalid, expired, or revoked. Please check your key and try again."
            ) from e
        logger.exception("LLM analysis failed: %s", e)
        raise AnalysisFailedError(str(e)) from e
