"""
Module: config.py
Purpose: Configuration management for Agent Training System.

This module loads and validates YAML configuration files for training schedules,
agent profiles, difficulty curves, and spaced repetition settings.

Agent: ClaudeCode
Created: 2025-12-03T00:00:00Z
Operation: [CREATE]
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigManager:
    """
    Configuration manager for the Agent Training System.

    Loads and caches YAML configuration files from the config directory.
    Provides type-safe access to configuration values.

    Attributes:
        config_dir: Path to configuration directory
        _cache: Internal cache of loaded configurations

    Examples:
        >>> config = ConfigManager()
        >>> schedule = config.get_training_schedule()
        >>> agents = config.get_agent_profiles()
    """

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize configuration manager.

        Args:
            config_dir: Path to config directory (defaults to ./config)

        Time Complexity: O(1)
        """
        if config_dir is None:
            # Default to config directory relative to package
            package_root = Path(__file__).parent.parent.parent
            config_dir = package_root / "config"

        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Any] = {}

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load and cache a YAML configuration file.

        Args:
            filename: Name of YAML file (without path)

        Returns:
            Parsed YAML as dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is invalid

        Time Complexity: O(n) where n is file size (on first load)
        Space Complexity: O(n) for cached data
        """
        if filename in self._cache:
            return self._cache[filename]

        file_path = self.config_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self._cache[filename] = config
        return config

    def get_training_schedule(self) -> Dict[str, Any]:
        """
        Get training schedule configuration.

        Returns:
            Training schedule config with daily/weekly/monthly/quarterly settings

        Examples:
            >>> config = ConfigManager()
            >>> schedule = config.get_training_schedule()
            >>> daily = schedule["schedule"]["daily"]
            >>> daily["duration_minutes"]  # 30
        """
        return self._load_yaml("training_schedule.yaml")

    def get_agent_profiles(self) -> Dict[str, Any]:
        """
        Get agent profile configurations.

        Returns:
            Agent profiles with specializations, languages, learning styles

        Examples:
            >>> config = ConfigManager()
            >>> profiles = config.get_agent_profiles()
            >>> claude = profiles["agents"]["ClaudeCode"]
            >>> claude["specializations"]  # ["precise_coding", "documentation"]
        """
        return self._load_yaml("agent_profiles.yaml")

    def get_difficulty_curves(self) -> Dict[str, Any]:
        """
        Get difficulty curve and XP reward configuration.

        Returns:
            Difficulty levels with XP requirements and rewards

        Examples:
            >>> config = ConfigManager()
            >>> curves = config.get_difficulty_curves()
            >>> level_1 = curves["levels"][1]
            >>> level_1["xp_required"]  # 0
            >>> level_1["concepts"]  # ["syntax", "data_types", ...]
        """
        return self._load_yaml("difficulty_curves.yaml")

    def get_spaced_repetition(self) -> Dict[str, Any]:
        """
        Get spaced repetition (SM-2) algorithm configuration.

        Returns:
            SM-2 parameters, intervals, ratings, and daily limits

        Examples:
            >>> config = ConfigManager()
            >>> sr = config.get_spaced_repetition()
            >>> sr["parameters"]["initial_ease_factor"]  # 2.5
            >>> sr["daily_limits"]["new_cards"]  # 20
        """
        return self._load_yaml("spaced_repetition.yaml")

    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """
        Get configuration for a specific agent.

        Args:
            agent_id: Agent identifier (e.g., "ClaudeCode")

        Returns:
            Agent-specific configuration

        Raises:
            KeyError: If agent ID not found in profiles

        Examples:
            >>> config = ConfigManager()
            >>> claude_config = config.get_agent_config("ClaudeCode")
            >>> claude_config["display_name"]  # "Claude Code"
        """
        profiles = self.get_agent_profiles()
        if agent_id not in profiles["agents"]:
            raise KeyError(f"Agent profile not found: {agent_id}")
        return profiles["agents"][agent_id]

    def get_level_config(self, level: int) -> Dict[str, Any]:
        """
        Get configuration for a specific difficulty level.

        Args:
            level: Level number (1-5)

        Returns:
            Level configuration with XP requirements and concepts

        Raises:
            KeyError: If level not found

        Examples:
            >>> config = ConfigManager()
            >>> level_3 = config.get_level_config(3)
            >>> level_3["name"]  # "Advanced"
            >>> level_3["xp_required"]  # 1500
        """
        curves = self.get_difficulty_curves()
        if level not in curves["levels"]:
            raise KeyError(f"Level not found: {level}")
        return curves["levels"][level]

    def clear_cache(self) -> None:
        """
        Clear configuration cache.

        Useful for testing or when configuration files have been modified.

        Time Complexity: O(1)
        """
        self._cache.clear()
