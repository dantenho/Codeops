"""
[CREATE] Configuration Service

Handles loading and validation of YAML configurations.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:15:00Z
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional, List, cast

class ConfigService:
    """Service for loading and accessing configuration files."""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self._cache: Dict[str, Any] = {}

    def load_config(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file."""
        if filename in self._cache:
            return self._cache[filename]

        file_path = self.config_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            loaded_config = yaml.safe_load(f)

        if not isinstance(loaded_config, dict):
            raise ValueError(f"Configuration file {filename} must contain a mapping at the root.")

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

    def list_agents(self) -> List[str]:
        """
        [CREATE] Retrieve all agent identifiers defined in configuration.

        Purpose:
            Provide orchestrators with a deterministic list of agents without
            duplicating YAML parsing logic throughout the codebase.

        Returns:
            List[str]: Ordered list of agent IDs as declared in agent_profiles.yaml.

        Example:
            >>> ConfigService(Path("config")).list_agents()
            ["GrokIA", "GeminiFlash25", "GeminiPro25"]

        Agent: GPT-5.1 Codex
        Timestamp: 2025-12-03T00:00:00Z
        """
        config = self.load_config("agent_profiles.yaml")
        agents = config.get("agents", {})
        return list(agents.keys())
