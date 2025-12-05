"""
Configuration for the Suggestion Tunnel system.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings


class TunnelSettings(BaseSettings):
    """Settings for the Suggestion Tunnel."""

    # Tunnel configuration
    TUNNEL_ENABLED: bool = True
    TUNNEL_LOG_LEVEL: str = "INFO"

    # Antigravity filter settings
    ANTIGRAVITY_STRICT_MODE: bool = True  # If True, only CRITICAL and HIGH severity pass
    ANTIGRAVITY_MIN_SEVERITY: str = "HIGH"  # minimum severity to pass (HIGH or CRITICAL)

    # Channel settings
    DEFAULT_CHANNEL_NAME: str = "cursor-ide-main"
    AUTO_CREATE_CHANNELS: bool = True

    # Bin settings
    MAX_BIN_SIZE: int = 100  # Maximum suggestions per bin
    AUTO_CLOSE_BINS: bool = True  # Auto-close bins after processing
    BIN_RETENTION_HOURS: int = 24  # How long to keep closed bins

    # File exclusions (patterns)
    EXCLUDE_PATHS: List[str] = [
        "tests/**",
        "**/*.test.py",
        "**/*.test.ts",
        "**/*.test.js",
        "node_modules/**",
        "venv/**",
        ".venv/**",
        "build/**",
        "dist/**",
        ".git/**",
        "__pycache__/**",
        "*.pyc",
    ]

    # Cursor IDE integration
    CURSOR_WEBHOOK_ENABLED: bool = False
    CURSOR_WEBHOOK_SECRET: Optional[str] = None
    CURSOR_WATCH_FILE: Optional[str] = None  # Path to watch for file-based integration

    # Claude Code integration
    CLAUDE_CALLBACK_ENABLED: bool = True
    CLAUDE_CALLBACK_TIMEOUT: int = 30  # seconds

    # API settings
    API_BASE_URL: str = "http://localhost:8000"
    API_TUNNEL_PREFIX: str = "/tunnel"

    # Redis (for async processing via Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_ENABLED: bool = False  # Enable for async processing

    # Antigravity Consultant (Gemini) settings
    GOOGLE_API_KEY: Optional[str] = None  # Google API key for Gemini
    CONSULTANT_ENABLED: bool = True  # Enable Gemini-powered Consultant
    CONSULTANT_MODEL: str = "gemini-2.5-pro-exp-0827"  # Gemini model to use
    CONSULTANT_AUTO_START_LOOP: bool = False  # Auto-start evaluation loop on startup

    # Evaluation loop settings
    EVALUATION_MIN_HOURS: float = 1.0  # Minimum hours between evaluations
    EVALUATION_MAX_HOURS: float = 3.0  # Maximum hours between evaluations

    # Reward settings
    BASE_TOKEN_AMOUNT: int = 100  # Base tokens for acceptable performance
    EXCELLENT_THRESHOLD: int = 90  # Score needed for excellent rating
    ACCEPTABLE_THRESHOLD: int = 60  # Score needed for acceptable rating
    MAX_MULTIPLIER: float = 2.0  # Maximum bonus multiplier

    class Config:
        env_file = ".env"
        env_prefix = "TUNNEL_"


# Global settings instance
settings = TunnelSettings()
