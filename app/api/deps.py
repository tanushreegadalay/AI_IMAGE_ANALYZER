"""FastAPI dependency injection: config, cache, analyzer service."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from app.cache import get_cache_backend
from app.service import AnalyzerService

if TYPE_CHECKING:
    from app.cache.backend import CacheBackend
    from app.config import Settings


@lru_cache(maxsize=1)
def get_config() -> "Settings":
    """Return cached settings (loaded once)."""
    from app.config import get_settings
    return get_settings()


@lru_cache(maxsize=1)
def get_cache() -> "CacheBackend":
    """Return cache backend (singleton per process)."""
    return get_cache_backend(get_config())


@lru_cache(maxsize=1)
def get_analyzer_service() -> AnalyzerService:
    """Return analyzer service (singleton per process)."""
    return AnalyzerService(settings=get_config(), cache=get_cache())
