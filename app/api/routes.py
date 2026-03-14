"""FastAPI routes for the analyzer API."""

from __future__ import annotations

import logging
from typing import Annotated, Optional, Union

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.api.deps import get_analyzer_service
from app.exceptions import (
    AnalysisException,
    ApiKeyInvalidError,
    ApiKeyMissingError,
    QuotaExceededError,
)
from app.schemas import AnalysisError, AnalysisSuccess, ErrorDetail
from app.service import AnalyzerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyzer"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}


@router.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@router.post(
    "/analyze",
    response_model=None,
    responses={
        200: {"description": "Success", "model": AnalysisSuccess},
        400: {"description": "Bad request / missing API key", "model": AnalysisError},
        401: {"description": "Invalid API key", "model": AnalysisError},
        402: {"description": "Quota exceeded", "model": AnalysisError},
        502: {"description": "Analysis failed", "model": AnalysisError},
    },
)
async def analyze(
    file: Annotated[UploadFile, File(description="Image file (JPEG or PNG)")],
    model: Annotated[Optional[str], Form(description="Optional model override")] = None,
    service: Annotated[AnalyzerService, Depends(get_analyzer_service)] = None,
) -> Union[AnalysisSuccess, AnalysisError]:
    """
    Upload an image and get AI-driven analysis.
    Returns structured success or error with code and message.
    """
    if file.content_type and file.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        return JSONResponse(
            status_code=400,
            content=AnalysisError(
                success=False,
                error=ErrorDetail(
                    code="ANALYSIS_FAILED",
                    message=f"Unsupported content type: {file.content_type}. Use image/jpeg or image/png.",
                ),
            ).model_dump(),
        )

    try:
        image_bytes = await file.read()
    except Exception as e:
        logger.exception("Failed to read uploaded file: %s", e)
        return JSONResponse(
            status_code=400,
            content=AnalysisError(
                success=False,
                error=ErrorDetail(code="ANALYSIS_FAILED", message="Failed to read uploaded file."),
            ).model_dump(),
        )

    if not image_bytes:
        return JSONResponse(
            status_code=400,
            content=AnalysisError(
                success=False,
                error=ErrorDetail(code="ANALYSIS_FAILED", message="Empty file."),
            ).model_dump(),
        )

    try:
        result = service.analyze(image_bytes=image_bytes, model_override=model)
        return result
    except ApiKeyMissingError as e:
        logger.warning("API key missing: %s", e.message)
        return JSONResponse(
            status_code=400,
            content=AnalysisError(
                success=False,
                error=ErrorDetail(code=e.code, message=e.message),
            ).model_dump(),
        )
    except ApiKeyInvalidError as e:
        logger.warning("API key invalid: %s", e.message)
        return JSONResponse(
            status_code=401,
            content=AnalysisError(
                success=False,
                error=ErrorDetail(code=e.code, message=e.message),
            ).model_dump(),
        )
    except QuotaExceededError as e:
        logger.warning("Quota exceeded: %s", e.message)
        return JSONResponse(
            status_code=402,
            content=AnalysisError(
                success=False,
                error=ErrorDetail(code=e.code, message=e.message),
            ).model_dump(),
        )
    except AnalysisException as e:
        logger.exception("Analysis failed: %s", e.message)
        return JSONResponse(
            status_code=502,
            content=AnalysisError(
                success=False,
                error=ErrorDetail(code=e.code, message=e.message),
            ).model_dump(),
        )
