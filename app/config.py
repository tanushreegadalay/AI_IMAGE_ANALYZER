"""Application configuration loaded from environment."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _sanitize_env(value: Optional[str]) -> Optional[str]:
    """Trim surrounding quotes from dotenv values, if present."""
    if value and (
        (value.startswith('"') and value.endswith('"'))
        or (value.startswith("'") and value.endswith("'"))
    ):
        return value[1:-1]
    return value


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ai_model: str = Field(default="gpt-4o", alias="AI_MODEL")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")

    cache_backend: str = Field(default="file", alias="CACHE_BACKEND")
    cache_ttl_seconds: Optional[int] = Field(default=None, alias="CACHE_TTL_SECONDS")
    cache_file_path: str = Field(default="image_cache.json", alias="CACHE_FILE_PATH")

    max_image_dimension: int = Field(default=2048, alias="MAX_IMAGE_DIMENSION")
    jpeg_quality: int = Field(default=85, alias="JPEG_QUALITY")

    @property
    def openai_api_key_sanitized(self) -> Optional[str]:
        return _sanitize_env(self.openai_api_key)

    @property
    def gemini_api_key_sanitized(self) -> Optional[str]:
        return _sanitize_env(self.gemini_api_key)

    @property
    def anthropic_api_key_sanitized(self) -> Optional[str]:
        return _sanitize_env(self.anthropic_api_key)

    def get_api_key_for_model(self, model: str) -> Optional[str]:
        """Return the API key for the given model provider."""
        model_lower = model.lower()
        if model_lower.startswith("gpt") or model_lower.startswith("openai"):
            return self.openai_api_key_sanitized
        if model_lower.startswith("gemini") or model_lower.startswith("google"):
            return self.gemini_api_key_sanitized
        if model_lower.startswith("claude") or model_lower.startswith("anthropic"):
            return self.anthropic_api_key_sanitized
        return self.gemini_api_key_sanitized


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance (load env once)."""
    return Settings()
