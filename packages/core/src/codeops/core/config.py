from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration for CodeOps."""

    # Environment
    ENV: str = "development"
    DEBUG: bool = False

    # Paths
    WORKSPACE_ROOT: str = "."

    # Database
    DATABASE_URL: Optional[str] = None
    CHROMA_DB_PATH: str = "./chroma_db"

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
