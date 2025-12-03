"""
[CREATE] Agent Skeleton Structure Generator

Generates standardized directory structures for agents organized by AgentID
and Timestamp, with subdirectories for training, rules, methods, files,
database, and memory.

Agent: Composer
Timestamp: 2025-12-03T15:00:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger("core.skeleton_generator")


class SkeletonGenerator:
    """
    [CREATE] Generates agent skeleton directory structures.

    Creates standardized directory hierarchies for agents with timestamped
    organization and minimal placeholder files.

    Attributes:
        base_path (Path): Base path for CodeAgents directory
        agent_base_path (Path): Base path for agent-specific structures

    Example:
        >>> generator = SkeletonGenerator()
        >>> generator.create_agent_skeleton("Composer")
        >>> generator.create_timestamped_structure("Composer", "2025-12-03T15-00-00Z")

    Complexity:
        Time: O(1) - directory creation is constant time
        Space: O(1) - minimal memory usage

    Agent: Composer
    Timestamp: 2025-12-03T15:00:00Z
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        [CREATE] Initialize skeleton generator.

        Args:
            base_path (Optional[Path]): Base path for CodeAgents directory.
                Default: None (auto-detect from current file location).

        Agent: Composer
        Timestamp: 2025-12-03T15:00:00Z
        """
        if base_path is None:
            # Auto-detect from current file location
            current_file = Path(__file__)
            self.base_path = current_file.parent.parent
        else:
            self.base_path = Path(base_path)

        self.agent_base_path = self.base_path / "ID"
        self.agent_base_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Skeleton generator initialized at {self.base_path}")

    def create_agent_skeleton(
        self,
        agent_id: str,
        timestamp: Optional[str] = None
    ) -> Path:
        """
        [CREATE] Create agent skeleton structure.

        Creates a timestamped directory structure for an agent with all
        required subdirectories and placeholder files.

        Args:
            agent_id (str): Agent identifier (e.g., "Composer", "ClaudeCode").
                Must be non-empty and valid directory name.
            timestamp (Optional[str]): ISO 8601 timestamp string.
                Default: None (auto-generate current timestamp).
                Format: "YYYY-MM-DDTHH-MM-SSZ"

        Returns:
            Path: Path to the created timestamped structure.

        Raises:
            ValueError: If agent_id is empty or invalid
            OSError: If directory creation fails

        Example:
            >>> generator = SkeletonGenerator()
            >>> path = generator.create_agent_skeleton("Composer")
            >>> print(path)
            CodeAgents/ID/Composer/2025-12-03T15-00-00Z

        Complexity:
            Time: O(1) - directory operations are constant
            Space: O(1)

        Agent: Composer
        Timestamp: 2025-12-03T15:00:00Z
        """
        if not agent_id or not agent_id.strip():
            raise ValueError("agent_id must be non-empty")

        # Generate timestamp if not provided
        if timestamp is None:
            timestamp = self._generate_timestamp()

        # Create timestamped structure
        return self.create_timestamped_structure(agent_id, timestamp)

    def create_timestamped_structure(
        self,
        agent_id: str,
        timestamp: str
    ) -> Path:
        """
        [CREATE] Create timestamped directory structure for an agent.

        Creates all subdirectories and placeholder files according to
        the standardized skeleton structure.

        Args:
            agent_id (str): Agent identifier.
            timestamp (str): ISO 8601 timestamp string.
                Format: "YYYY-MM-DDTHH-MM-SSZ"

        Returns:
            Path: Path to the created structure.

        Raises:
            OSError: If directory creation fails

        Example:
            >>> generator = SkeletonGenerator()
            >>> path = generator.create_timestamped_structure(
            ...     "Composer",
            ...     "2025-12-03T15-00-00Z"
            ... )

        Complexity:
            Time: O(1) - directory operations
            Space: O(1)

        Agent: Composer
        Timestamp: 2025-12-03T15:00:00Z
        """
        # Create agent directory if it doesn't exist
        agent_dir = self.agent_base_path / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped directory
        timestamp_dir = agent_dir / timestamp
        timestamp_dir.mkdir(parents=True, exist_ok=True)

        # Create all subdirectories
        subdirs = [
            "training/sessions",
            "training/activities",
            "rules",
            "methods",
            "files/code",
            "files/configs",
            "files/artifacts",
            "database/migrations",
            "database/seeds",
            "memory/context",
            "memory/knowledge",
            "memory/reflections",
        ]

        for subdir in subdirs:
            (timestamp_dir / subdir).mkdir(parents=True, exist_ok=True)

        # Create placeholder files
        self._create_placeholder_files(agent_id, timestamp, timestamp_dir)

        logger.info(
            f"Created skeleton structure for {agent_id} at {timestamp_dir}"
        )

        return timestamp_dir

    def _create_placeholder_files(
        self,
        agent_id: str,
        timestamp: str,
        base_path: Path
    ) -> None:
        """
        [CREATE] Create all placeholder files in the skeleton structure.

        Args:
            agent_id (str): Agent identifier.
            timestamp (str): ISO 8601 timestamp string.
            base_path (Path): Base path for the timestamped structure.

        Agent: Composer
        Timestamp: 2025-12-03T15:00:00Z
        """
        # Training progress.json
        progress_file = base_path / "training" / "progress.json"
        if not progress_file.exists():
            progress_data = {
                "agent_id": agent_id,
                "timestamp": timestamp,
                "level": 1,
                "xp": 0,
                "sessions_completed": 0,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(progress_data, f, indent=2)

        # Rules protocols.md
        protocols_file = base_path / "rules" / "protocols.md"
        if not protocols_file.exists():
            protocols_content = f"""# {agent_id} Protocols
Timestamp: {timestamp}
Agent: {agent_id}

## Protocols
- [ ] Protocol 1
- [ ] Protocol 2

## Notes
This file contains protocol definitions and guidelines for {agent_id}.
"""
            with open(protocols_file, "w", encoding="utf-8") as f:
                f.write(protocols_content)

        # Rules constraints.yaml
        constraints_file = base_path / "rules" / "constraints.yaml"
        if not constraints_file.exists():
            constraints_content = f"""# {agent_id} Constraints
# Created: {timestamp}
# Agent: {agent_id}

constraints:
  token_budget:
    max_tokens: 100000
    warning_threshold: 80000

  quality_gates:
    min_quality_score: 70
    min_efficiency_score: 3.0

  performance:
    max_duration_ms: 30000
    timeout_seconds: 60
"""
            with open(constraints_file, "w", encoding="utf-8") as f:
                f.write(constraints_content)

        # Rules guidelines.json
        guidelines_file = base_path / "rules" / "guidelines.json"
        if not guidelines_file.exists():
            guidelines_data = {
                "agent_id": agent_id,
                "timestamp": timestamp,
                "guidelines": [
                    "Follow Agents.MD protocol standards",
                    "Maintain code quality thresholds",
                    "Log all operations to telemetry",
                    "Update progress after each session"
                ],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            with open(guidelines_file, "w", encoding="utf-8") as f:
                json.dump(guidelines_data, f, indent=2)

        # Methods __init__.py
        methods_init_file = base_path / "methods" / "__init__.py"
        if not methods_init_file.exists():
            methods_init_content = f'''"""
{agent_id} Methods Module
Timestamp: {timestamp}
Agent: {agent_id}

This module contains core methods and utilities for {agent_id}.
"""

from __future__ import annotations

__all__ = []
'''
            with open(methods_init_file, "w", encoding="utf-8") as f:
                f.write(methods_init_content)

        # Methods core_methods.py
        core_methods_file = base_path / "methods" / "core_methods.py"
        if not core_methods_file.exists():
            core_methods_content = f'''"""
[CREATE] Core Methods for {agent_id}

Core functionality and methods for {agent_id} operations.

Agent: {agent_id}
Timestamp: {timestamp}
Operation: [CREATE]
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def example_method(param: str) -> Dict[str, Any]:
    """
    [CREATE] Example method template.

    Args:
        param (str): Example parameter.

    Returns:
        Dict[str, Any]: Example return value.

    Agent: {agent_id}
    Timestamp: {timestamp}
    """
    return {{"result": param}}
'''
            with open(core_methods_file, "w", encoding="utf-8") as f:
                f.write(core_methods_content)

        # Methods utilities.py
        utilities_file = base_path / "methods" / "utilities.py"
        if not utilities_file.exists():
            utilities_content = f'''"""
[CREATE] Utility Functions for {agent_id}

Utility functions and helpers for {agent_id} operations.

Agent: {agent_id}
Timestamp: {timestamp}
Operation: [CREATE]
"""

from __future__ import annotations

from typing import Any, Dict


def example_utility(data: Dict[str, Any]) -> bool:
    """
    [CREATE] Example utility function.

    Args:
        data (Dict[str, Any]): Input data.

    Returns:
        bool: Example return value.

    Agent: {agent_id}
    Timestamp: {timestamp}
    """
    return bool(data)
'''
            with open(utilities_file, "w", encoding="utf-8") as f:
                f.write(utilities_content)

        # Database schema.sql
        schema_file = base_path / "database" / "schema.sql"
        if not schema_file.exists():
            schema_content = f"""-- {agent_id} Database Schema
-- Created: {timestamp}
-- Agent: {agent_id}

-- Example table structure
CREATE TABLE IF NOT EXISTS agent_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    status TEXT NOT NULL,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_agent_timestamp
ON agent_operations(agent_id, timestamp);
"""
            with open(schema_file, "w", encoding="utf-8") as f:
                f.write(schema_content)

        # Memory context README.md
        context_readme_file = base_path / "memory" / "context" / "README.md"
        if not context_readme_file.exists():
            context_readme_content = f"""# Context Memory
Agent: {agent_id}
Timestamp: {timestamp}

## Purpose
This directory stores contextual memory and conversation history for {agent_id}.

## Structure
- Recent context files
- Conversation histories
- Context snapshots
"""
            with open(context_readme_file, "w", encoding="utf-8") as f:
                f.write(context_readme_content)

        # Memory knowledge README.md
        knowledge_readme_file = base_path / "memory" / "knowledge" / "README.md"
        if not knowledge_readme_file.exists():
            knowledge_readme_content = f"""# Knowledge Base
Agent: {agent_id}
Timestamp: {timestamp}

## Purpose
This directory stores extracted knowledge and learned patterns for {agent_id}.

## Structure
- Knowledge graphs
- Learned patterns
- Extracted insights
"""
            with open(knowledge_readme_file, "w", encoding="utf-8") as f:
                f.write(knowledge_readme_content)

        # Memory reflections README.md
        reflections_readme_file = base_path / "memory" / "reflections" / "README.md"
        if not reflections_readme_file.exists():
            reflections_readme_content = f"""# Reflections
Agent: {agent_id}
Timestamp: {timestamp}

## Purpose
This directory stores self-reflection and learning insights for {agent_id}.

## Structure
- Reflection logs
- Learning insights
- Self-assessment reports
"""
            with open(reflections_readme_file, "w", encoding="utf-8") as f:
                f.write(reflections_readme_content)

    def _generate_timestamp(self) -> str:
        """
        [CREATE] Generate ISO 8601 formatted timestamp.

        Returns:
            str: Timestamp in format "YYYY-MM-DDTHH-MM-SSZ"

        Agent: Composer
        Timestamp: 2025-12-03T15:00:00Z
        """
        now = datetime.now(timezone.utc)
        # Format: YYYY-MM-DDTHH-MM-SSZ (safe for directory names)
        return now.strftime("%Y-%m-%dT%H-%M-%SZ")

    def create_for_all_agents(self, agent_ids: list[str]) -> Dict[str, Path]:
        """
        [CREATE] Create skeleton structures for multiple agents.

        Args:
            agent_ids (list[str]): List of agent identifiers.

        Returns:
            Dict[str, Path]: Mapping of agent_id to created path.

        Example:
            >>> generator = SkeletonGenerator()
            >>> paths = generator.create_for_all_agents(["Composer", "ClaudeCode"])
            >>> print(paths["Composer"])

        Agent: Composer
        Timestamp: 2025-12-03T15:00:00Z
        """
        results = {}
        timestamp = self._generate_timestamp()

        for agent_id in agent_ids:
            try:
                path = self.create_timestamped_structure(agent_id, timestamp)
                results[agent_id] = path
                logger.info(f"Created skeleton for {agent_id}")
            except Exception as e:
                logger.error(f"Failed to create skeleton for {agent_id}: {e}")
                results[agent_id] = None

        return results


def create_skeleton_generator(base_path: Optional[Path] = None) -> SkeletonGenerator:
    """
    [CREATE] Factory function to create a skeleton generator instance.

    Args:
        base_path (Optional[Path]): Base path for CodeAgents directory.
            Default: None (auto-detect).

    Returns:
        SkeletonGenerator: Configured generator instance.

    Example:
        >>> generator = create_skeleton_generator()
        >>> generator.create_agent_skeleton("Composer")

    Agent: Composer
    Timestamp: 2025-12-03T15:00:00Z
    """
    return SkeletonGenerator(base_path)
