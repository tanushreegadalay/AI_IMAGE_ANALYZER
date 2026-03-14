"""Image normalization, encoding, and hashing for the analyzer."""

from __future__ import annotations

import base64
import hashlib
from io import BytesIO
from typing import Tuple

from PIL import Image


def normalize_image(
    pil_image: Image.Image,
    max_dimension: int = 2048,
    jpeg_quality: int = 85,
) -> Tuple[Image.Image, bytes]:
    """
    Resize image so max side <= max_dimension (preserve aspect ratio),
    convert to RGB if needed, encode to JPEG bytes.
    Returns (PIL image, jpeg_bytes).
    """
    img = pil_image.convert("RGB") if pil_image.mode != "RGB" else pil_image.copy()
    w, h = img.size
    if w > max_dimension or h > max_dimension:
        ratio = min(max_dimension / w, max_dimension / h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=jpeg_quality)
    buf.seek(0)
    jpeg_bytes = buf.getvalue()
    return img, jpeg_bytes


def image_to_base64(jpeg_bytes: bytes) -> str:
    """Encode JPEG bytes to base64 string (no data URL prefix)."""
    return base64.standard_b64encode(jpeg_bytes).decode("utf-8")


def hash_image_bytes(jpeg_bytes: bytes) -> str:
    """MD5 hash of image bytes for cache key. Same bytes -> same hash."""
    return hashlib.md5(jpeg_bytes).hexdigest()
