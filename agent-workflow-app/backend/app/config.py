"""
Module: app.config
Purpose: Centralized application configuration handling.

Agent: GPT-5.1-Codex
Created: 2025-12-03T23:59:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Sequence


@dataclass
class AppConfig:
    """
    [CREATE] Container for runtime configuration.

    Attributes:
        data_dir (str): Path to directory containing seed JSON files.
        allow_origins (Sequence[str]): Origins allowed by CORS middleware.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T23:59:00Z
    """

    data_dir: str
    allow_origins: Sequence[str]

    @classmethod
    def from_env(cls) -> "AppConfig":
        """
        [CREATE] Build configuration from environment variables.

        Returns:
            AppConfig: Configured instance.
        """

        data_dir = os.getenv("APP_DATA_DIR", "../data")
        allow_origins = tuple(
            origin.strip()
            for origin in os.getenv("APP_ALLOW_ORIGINS", "http://localhost:5173").split(",")
            if origin.strip()
        )
        return cls(data_dir=data_dir, allow_origins=allow_origins)

