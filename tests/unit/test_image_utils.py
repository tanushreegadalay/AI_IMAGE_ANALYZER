"""Unit tests for image normalization and hashing."""

from io import BytesIO

import pytest
from PIL import Image

from app.image_utils import hash_image_bytes, image_to_base64, normalize_image


def test_normalize_image_preserves_small_image():
    img = Image.new("RGB", (100, 100), color="red")
    out_img, jpeg_bytes = normalize_image(img, max_dimension=2048, jpeg_quality=85)
    assert out_img.size == (100, 100)
    assert len(jpeg_bytes) > 0


def test_normalize_image_resizes_large_image():
    img = Image.new("RGB", (3000, 2000), color="green")
    out_img, jpeg_bytes = normalize_image(img, max_dimension=2048, jpeg_quality=85)
    assert max(out_img.size) <= 2048
    assert out_img.size[0] == 2048 or out_img.size[1] == 2048
    assert len(jpeg_bytes) > 0


def test_hash_image_bytes_deterministic():
    data = b"fake jpeg bytes"
    assert hash_image_bytes(data) == hash_image_bytes(data)


def test_hash_image_bytes_different_for_different_input():
    assert hash_image_bytes(b"a") != hash_image_bytes(b"b")


def test_image_to_base64_roundtrip():
    raw = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    b64 = image_to_base64(raw)
    import base64
    decoded = base64.standard_b64decode(b64)
    assert decoded == raw
