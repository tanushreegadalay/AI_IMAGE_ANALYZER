"""Cache backends for analysis results."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.config import Settings

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract cache backend interface."""

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Return cached value for key, or None if missing/expired."""
        ...

    @abstractmethod
    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        """Store value for key. ttl_seconds optional (backend may ignore)."""
        ...


class JsonFileCacheBackend(CacheBackend):
    """File-based cache using a single JSON file. No TTL; suitable for single process."""

    def __init__(self, file_path: str | Path) -> None:
        self._path = Path(file_path)

    def get(self, key: str) -> Optional[str]:
        if not self._path.exists():
            return None
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get(key)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Cache read failed for %s: %s", self._path, e)
            return None

    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        try:
            data = {}
            if self._path.exists():
                try:
                    with open(self._path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, OSError):
                    data = {}
            data[key] = value
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Cache write failed for %s: %s", self._path, e)


def get_cache_backend(settings: "Settings") -> CacheBackend:
    """Return the cache backend configured in settings."""
    if settings.cache_backend.lower() == "diskcache":
        try:
            from app.cache.diskcache_backend import DiskCacheBackend
            return DiskCacheBackend(
                cache_dir=".cache/analyzer",
                ttl_seconds=settings.cache_ttl_seconds,
            )
        except ImportError:
            logger.warning("diskcache not installed, falling back to file cache")
    return JsonFileCacheBackend(settings.cache_file_path)
