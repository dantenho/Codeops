"""
[CREATE] Configuration Service

Handles loading and validation of YAML configurations.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:15:00Z
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, cast

import yaml


class ConfigService:
    """Service for loading and accessing configuration files."""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self._cache: Dict[str, Any] = {}

    def load_config(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file."""
        if filename in self._cache:
            cached = self._cache[filename]
            if not isinstance(cached, dict):
                raise ValueError(
                    f"Cached configuration for {filename} must be a mapping at the root, "
                    f"got {type(cached).__name__}."
                )
            return cast(Dict[str, Any], cached)

        file_path = self.config_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            loaded_config = yaml.safe_load(f)

        if not isinstance(loaded_config, dict):
            raise ValueError(
                f"Configuration file {filename} must contain a mapping at the root, "
                f"got {type(loaded_config).__name__}."
            )

        config = cast(Dict[str, Any], loaded_config)
        self._cache[filename] = config
        return config

    def get_agent_profile(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get profile for a specific agent."""
        config = self.load_config("agent_profiles.yaml")
        return config.get("agents", {}).get(agent_name)

    def get_schedule(self, schedule_type: str = "daily") -> Dict[str, Any]:
        """Get training schedule configuration."""
        config = self.load_config("training_schedule.yaml")
        return config.get("schedule", {}).get(schedule_type, {})

    def get_difficulty_curve(self, level: int) -> Dict[str, Any]:
        """Get difficulty configuration for a level."""
        config = self.load_config("difficulty_curves.yaml")
        return config.get("levels", {}).get(level, {})

    def get_threndia_settings(self, agent_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Return Threndia integration settings for an agent.

        Args:
            agent_name: Agent identifier. Defaults to EudoraX-Pylorix if omitted.

        Returns:
            Dictionary containing resolved Threndia settings or None if unavailable.
        """
        profile_name = agent_name or "EudoraX-Pylorix"
        profile = self.get_agent_profile(profile_name)
        if not profile:
            return None

        threndia_cfg = profile.get("threndia")
        if not threndia_cfg:
            return None

        api_token_env = threndia_cfg.get("api_token_env", "THRENDIA_API_TOKEN")
        scrape_freq_env = threndia_cfg.get("scrape_freq_env", "THRENDIA_SCRAPE_FREQ_MINUTES")

        resolved_settings = {
            "agent_id": profile_name,
            "roles": profile.get("roles", []),
            "intel_sources": profile.get("intel_sources", []),
            "telemetry_namespace": profile.get("telemetry_namespace", ""),
            "shared_storage_path": profile.get("shared_storage_path"),
            "focus_topics": threndia_cfg.get("tagging", {}).get("market_focus_topics", []),
            "intel_batch_prefix": threndia_cfg.get("tagging", {}).get("intel_batch_prefix"),
            "default_session_type": threndia_cfg.get("default_session_type", "market_analysis"),
            "api_token": os.getenv(api_token_env),
            "scrape_frequency_minutes": _safe_int_env(scrape_freq_env, default=60),
            "mutual_cooperation": profile.get("telemetry_namespace") == "mutual_cooperation",
        }

        return resolved_settings


def _safe_int_env(env_key: str, default: int = 0) -> int:
    """Helper to safely parse integer environment variables."""
    raw_value = os.getenv(env_key)
    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError:
        return default
