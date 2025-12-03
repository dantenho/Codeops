#!/usr/bin/env python3
"""
[CREATE] Telemetry Logging System for EudoraX Prototype
Agent: GrokIA
Timestamp: 2025-12-03T10:28:00Z
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from dataclasses import dataclass, field
from enum import Enum, auto


class OperationType(Enum):
    """Operation types for telemetry logging."""
    CREATE = auto()
    REFACTOR = auto()
    DEBUG = auto()
    DELETE = auto()
    MODIFY = auto()
    ANALYZE = auto()


class OperationStatus(Enum):
    """Status types for operations."""
    SUCCESS = auto()
    FAILURE = auto()
    PARTIAL = auto()
    PENDING = auto()


@dataclass
class TelemetryEntry:
    """
    [CREATE] Telemetry entry data structure.

    Represents a single operation's telemetry data following
    the EudoraX Protocol specifications.
    """
    agent: str
    operation: OperationType
    target_file: str
    status: OperationStatus
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    target_function: Optional[str] = None
    lines: Optional[tuple[int, int]] = None
    duration_ms: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert telemetry entry to dictionary format."""
        return {
            "agent": self.agent,
            "timestamp": self.timestamp.isoformat(),
            "operation": self.operation.name,
            "target": {
                "file": self.target_file,
                "function": self.target_function,
                "lines": {"start": self.lines[0], "end": self.lines[1]} if self.lines else None
            },
            "status": self.status.name,
            "duration_ms": self.duration_ms,
            "context": self.context,
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """Convert telemetry entry to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class TelemetryLogger:
    """
    [CREATE] Telemetry logging system for agent operations.

    Provides centralized logging with file organization by agent
    following the EudoraX directory structure.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize telemetry logger.

        Args:
            base_path: Base directory for telemetry logs.
                       Defaults to 'CodeAgents' in current directory.
        """
        self.base_path = base_path or Path("CodeAgents")
        self.logger = logging.getLogger("telemetry")

        # Ensure base directory exists
        self.base_path.mkdir(exist_ok=True)

    def _get_agent_directory(self, agent: str) -> Path:
        """Get agent-specific directory path."""
        agent_dir = self.base_path / agent
        agent_dir.mkdir(exist_ok=True)
        return agent_dir

    def _generate_filename(self, agent: str) -> str:
        """Generate timestamped filename for telemetry entry."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        hash_suffix = agent.lower().replace(".", "")[:8]
        return f"log_{timestamp}_{hash_suffix}.json"

    def log_operation(self, entry: TelemetryEntry) -> Path:
        """
        Log an operation to agent-specific directory.

        Args:
            entry: TelemetryEntry containing operation data.

        Returns:
            Path to the created log file.
        """
        agent_dir = self._get_agent_directory(entry.agent)
        filename = self._generate_filename(entry.agent)
        file_path = agent_dir / "logs" / filename

        # Ensure logs subdirectory exists
        logs_dir = agent_dir / "logs"
        logs_dir.mkdir(exist_ok=True)

        # Write telemetry entry
        with open(file_path, "w") as f:
            f.write(entry.to_json())

        self.logger.info(f"Logged operation to {file_path}")
        return file_path

    def log_error(self, agent: str, error_type: str, message: str,
                  severity: str, stack_trace: Optional[str] = None,
                  affected_files: Optional[list[str]] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        Log an error to agent-specific error directory.

        Args:
            agent: Agent identifier.
            error_type: Type of error.
            message: Error message.
            severity: Error severity (LOW, MEDIUM, HIGH, CRITICAL).
            stack_trace: Optional stack trace.
            affected_files: List of affected files.
            metadata: Additional error metadata.

        Returns:
            Path to the created error log file.
        """
        agent_dir = self._get_agent_directory(agent)
        errors_dir = agent_dir / "errors"
        errors_dir.mkdir(exist_ok=True)

        # Generate error filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        hash_suffix = agent.lower().replace(".", "")[:8]
        filename = f"error_{timestamp}_{hash_suffix}.json"
        file_path = errors_dir / filename

        # Create error entry
        error_entry = {
            "agent": agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": error_type,
            "message": message,
            "severity": severity,
            "stack_trace": stack_trace,
            "affected_files": affected_files or [],
            "root_cause_analysis": {
                "identified": False,
                "cause": None,
                "suggested_fix": None
            },
            "metadata": metadata or {}
        }

        # Write error log
        with open(file_path, "w") as f:
            json.dump(error_entry, f, indent=2)

        self.logger.error(f"Logged error to {file_path}: {message}")
        return file_path

    def get_agent_logs(self, agent: str, limit: int = 10) -> list[Dict[str, Any]]:
        """
        Retrieve recent logs for an agent.

        Args:
            agent: Agent identifier.
            limit: Maximum number of logs to return.

        Returns:
            List of recent telemetry entries.
        """
        agent_dir = self._get_agent_directory(agent)
        logs_dir = agent_dir / "logs"

        if not logs_dir.exists():
            return []

        # Get all log files and sort by modification time
        log_files = list(logs_dir.glob("log_*.json"))
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        logs = []
        for log_file in log_files[:limit]:
            try:
                with open(log_file) as f:
                    logs.append(json.load(f))
            except (json.JSONDecodeError, FileNotFoundError) as e:
                self.logger.warning(f"Could not read log file {log_file}: {e}")

        return logs

    def create_analysis_entry(self, agent: str, analysis_type: str,
                            results: Dict[str, Any]) -> Path:
        """
        Create analysis entry for agent performance data.

        Args:
            agent: Agent identifier.
            analysis_type: Type of analysis performed.
            results: Analysis results data.

        Returns:
            Path to the created analysis file.
        """
        agent_dir = self._get_agent_directory(agent)
        analysis_dir = agent_dir / "analysis"
        analysis_dir.mkdir(exist_ok=True)

        # Generate analysis filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        hash_suffix = agent.lower().replace(".", "")[:8]
        filename = f"analysis_{timestamp}_{hash_suffix}.json"
        file_path = analysis_dir / filename

        # Create analysis entry
        analysis_entry = {
            "agent": agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": analysis_type,
            "results": results
        }

        # Write analysis file
        with open(file_path, "w") as f:
            json.dump(analysis_entry, f, indent=2)

        self.logger.info(f"Created analysis entry at {file_path}")
        return file_path


def main():
    """Example usage and testing of telemetry logger."""
    import argparse

    parser = argparse.ArgumentParser(description="Telemetry logging utility")
    parser.add_argument("--agent", required=True, help="Agent identifier")
    parser.add_argument("--operation", choices=[op.name for op in OperationType],
                       required=True, help="Operation type")
    parser.add_argument("--file", required=True, help="Target file path")
    parser.add_argument("--status", choices=[st.name for st in OperationStatus],
                       required=True, help="Operation status")
    parser.add_argument("--duration", type=int, help="Duration in milliseconds")
    parser.add_argument("--function", help="Target function name")
    parser.add_argument("--lines", help="Line range (e.g., '1,50')")

    args = parser.parse_args()

    # Parse line range
    lines = None
    if args.lines:
        start, end = map(int, args.lines.split(","))
        lines = (start, end)

    # Create telemetry entry
    entry = TelemetryEntry(
        agent=args.agent,
        operation=OperationType[args.operation],
        target_file=args.file,
        status=OperationStatus[args.status],
        target_function=args.function,
        lines=lines,
        duration_ms=args.duration,
        context={"cli_invocation": True},
        metadata={"source": "telemetry_logger.py"}
    )

    # Log the operation
    logger = TelemetryLogger()
    log_path = logger.log_operation(entry)

    print(f"✅ Logged operation to: {log_path}")
    print(f"📄 Entry:\n{entry.to_json()}")


if __name__ == "__main__":
    main()
