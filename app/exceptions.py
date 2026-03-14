"""Domain exceptions for the analyzer service."""

from __future__ import annotations

from typing import Literal, Optional

ErrorCode = Literal[
    "QUOTA_EXCEEDED",
    "API_KEY_INVALID",
    "API_KEY_MISSING",
    "ANALYSIS_FAILED",
]


class AnalysisException(Exception):
    """Base exception for analyzer domain errors."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class QuotaExceededError(AnalysisException):
    """API quota or rate limit exceeded."""

    def __init__(self, message: str = "API quota exceeded.") -> None:
        super().__init__("QUOTA_EXCEEDED", message)


class ApiKeyInvalidError(AnalysisException):
    """API key is invalid, expired, or revoked."""

    def __init__(self, message: str = "API key is invalid or expired.") -> None:
        super().__init__("API_KEY_INVALID", message)


class ApiKeyMissingError(AnalysisException):
    """No API key configured for the requested provider."""

    def __init__(self, message: str, provider: Optional[str] = None) -> None:
        self.provider = provider
        super().__init__("API_KEY_MISSING", message)


class AnalysisFailedError(AnalysisException):
    """Analysis request failed (network, server error, etc.)."""

    def __init__(self, message: str) -> None:
        super().__init__("ANALYSIS_FAILED", message)
