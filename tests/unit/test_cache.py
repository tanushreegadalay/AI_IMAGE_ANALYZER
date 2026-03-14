"""Unit tests for cache backends."""

import tempfile
from pathlib import Path

import pytest

from app.cache.backend import JsonFileCacheBackend


def test_json_file_cache_get_missing_returns_none():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        backend = JsonFileCacheBackend(path)
        assert backend.get("nonexistent") is None
    finally:
        Path(path).unlink(missing_ok=True)


def test_json_file_cache_set_and_get():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        backend = JsonFileCacheBackend(path)
        backend.set("k1", "v1")
        assert backend.get("k1") == "v1"
        backend.set("k2", "v2")
        assert backend.get("k1") == "v1"
        assert backend.get("k2") == "v2"
    finally:
        Path(path).unlink(missing_ok=True)


def test_json_file_cache_get_invalid_file_returns_none():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        f.write(b"not valid json")
        path = f.name
    try:
        backend = JsonFileCacheBackend(path)
        assert backend.get("any") is None
    finally:
        Path(path).unlink(missing_ok=True)
