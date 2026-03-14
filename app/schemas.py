"""Request/response and domain schemas for the analyzer API."""

from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Structured error for API and service layer."""

    code: Literal[
        "QUOTA_EXCEEDED",
        "API_KEY_INVALID",
        "API_KEY_MISSING",
        "ANALYSIS_FAILED",
    ]
    message: str


class AnalysisSuccess(BaseModel):
    """Successful analysis response."""

    success: Literal[True] = True
    result: str
    cached: bool
    model: str


class AnalysisError(BaseModel):
    """Error response with structured error detail."""

    success: Literal[False] = False
    error: ErrorDetail


AnalysisResponse = Union[AnalysisSuccess, AnalysisError]


class AnalyzeOptions(BaseModel):
    """Optional per-request overrides for analysis."""

    model: Optional[str] = Field(default=None, description="Override default model for this request")
