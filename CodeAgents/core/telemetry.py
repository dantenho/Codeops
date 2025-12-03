"""
Module: telemetry.py
Purpose: Standardized telemetry logging for AI agents.

Handles structured logging of operations and errors to the CodeAgents
directory structure, ensuring compliance with Agents.MD schemas.

Agent: Antigravity
Created: 2025-12-03T05:10:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import json
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Literal
from dataclasses import dataclass, field, asdict

# Configure logging for the module
logger = logging.getLogger("core.telemetry")

@dataclass
class OperationLog:
    """
    [CREATE] Data structure for operation logs.

    Attributes:
        agent (str): Name of the agent performing the operation.
        operation (str): Type of operation (CREATE, REFACTOR, etc.).
        target (dict): Details about the target (file, function, lines).
        status (str): Outcome of the operation.
        context (dict): Additional context data.
    """
    agent: str
    operation: Literal["CREATE", "REFACTOR", "DEBUG", "DELETE", "MODIFY", "ANALYZE"]
    target: dict[str, Any]
    status: Literal["SUCCESS", "FAILURE", "PARTIAL", "PENDING"]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    duration_ms: int = 0
    context: dict[str, Any] = field(default_factory=dict)

@dataclass
class ErrorLog:
    """
    [CREATE] Data structure for error logs.

    Attributes:
        agent (str): Name of the agent reporting the error.
        error_type (str): Class name or type of error.
        message (str): Error message description.
        severity (str): Severity level (LOW, MEDIUM, HIGH, CRITICAL).
    """
    agent: str
    error_type: str
    message: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    stack_trace: str = ""
    root_cause_analysis: dict[str, Any] = field(default_factory=dict)
    affected_files: list[str] = field(default_factory=list)
    reproduction_steps: list[str] = field(default_factory=list)

class TelemetryManager:
    """
    [CREATE] Manages writing telemetry data to the file system.

    Ensures all logs are written to the correct agent directory
    with the proper naming convention.
    """

    def __init__(self, base_path: str = "CodeAgents"):
        self.base_path = Path(base_path)
        if not self.base_path.exists():
            # In a real scenario, we might want to create it or raise an error
            # For now, we assume the structure exists or we create it
            self.base_path.mkdir(exist_ok=True)

    def log_operation(self, log: OperationLog) -> Path:
        """
        [CREATE] Writes an operation log to disk.

        Args:
            log (OperationLog): The operation data to log.

        Returns:
            Path: The path to the created log file.
        """
        agent_dir = self.base_path / log.agent / "logs"
        agent_dir.mkdir(parents=True, exist_ok=True)

        filename = self._generate_filename("log", log.timestamp)
        file_path = agent_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(asdict(log), f, indent=2)

        logger.info(f"Operation logged: {file_path}")
        return file_path

    def log_error(self, log: ErrorLog) -> Path:
        """
        [CREATE] Writes an error log to disk.

        Args:
            log (ErrorLog): The error data to log.

        Returns:
            Path: The path to the created error file.
        """
        agent_dir = self.base_path / log.agent / "errors"
        agent_dir.mkdir(parents=True, exist_ok=True)

        filename = self._generate_filename("error", log.timestamp)
        file_path = agent_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(asdict(log), f, indent=2)

        logger.error(f"Error logged: {file_path}")
        return file_path

    def _generate_filename(self, prefix: str, timestamp: str) -> str:
        """
        [CREATE] Generates a unique filename based on timestamp.

        Format: {prefix}_{timestamp}_{hash}.json
        """
        # Create a short hash to ensure uniqueness
        hash_input = f"{timestamp}{datetime.now().timestamp()}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:6]

        # Sanitize timestamp for filename
        safe_ts = timestamp.replace(":", "-").replace(".", "-")

        return f"{prefix}_{safe_ts}_{short_hash}.json"

# Singleton instance for easy import
telemetry = TelemetryManager()
