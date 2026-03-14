"""Optional diskcache-based backend. Requires diskcache package."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from app.cache.backend import CacheBackend

logger = logging.getLogger(__name__)


class DiskCacheBackend(CacheBackend):
    """Cache backend using diskcache library with TTL support."""

    def __init__(self, cache_dir: str = ".cache/analyzer", ttl_seconds: Optional[int] = None) -> None:
        import diskcache
        self._cache = diskcache.Cache(Path(cache_dir))
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[str]:
        try:
            value = self._cache.get(key)
            return value if value is None else str(value)
        except Exception as e:
            logger.warning("Disk cache get failed: %s", e)
            return None

    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        try:
            ttl = ttl_seconds if ttl_seconds is not None else self._ttl
            self._cache.set(key, value, expire=ttl)
        except Exception as e:
            logger.warning("Disk cache set failed: %s", e)
