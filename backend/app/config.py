"""Application configuration using Pydantic BaseSettings.

All settings are loaded from environment variables or a .env file.
Use ``get_settings()`` everywhere instead of instantiating Settings directly
so the lru_cache singleton is respected.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the LexAI backend.

    Attributes:
        GEMINI_API_KEY: Google Gemini API key. Required — no default.
        GEMINI_MODEL: Gemini generative model name.
        GEMINI_EMBEDDING_MODEL: Gemini embedding model identifier.
        MAX_FILE_SIZE_MB: Maximum allowed upload file size in megabytes.
        UPLOAD_DIR: Filesystem path for storing uploaded files.
        CHROMA_DIR: Filesystem path for persisting ChromaDB collections.
        CORS_ORIGINS: List of allowed CORS origins for the API.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    GEMINI_API_KEY: str = Field(..., description="Google Gemini API key")
    GEMINI_MODEL: str = Field(
        default="gemini-1.5-flash", description="Gemini generative model name"
    )
    GEMINI_EMBEDDING_MODEL: str = Field(
        default="models/text-embedding-004",
        description="Gemini embedding model identifier",
    )
    MAX_FILE_SIZE_MB: int = Field(
        default=10, description="Maximum upload file size in megabytes"
    )
    UPLOAD_DIR: str = Field(
        default="./uploads", description="Directory for uploaded files"
    )
    CHROMA_DIR: str = Field(
        default="./chroma_db", description="Directory for ChromaDB persistence"
    )
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    Returns:
        The application ``Settings`` instance. Cached after first call so
        environment variables are only read once per process.
    """
    return Settings()
