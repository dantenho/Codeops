"""
Module: ames_integration.py
Purpose: Integration with Agent Metrics & Evaluation System (AMES).

This module provides integration between the Agent Training System and AMES
for logging training results, tracking performance metrics, and identifying
areas for improvement.

Agent: ClaudeCode
Created: 2025-12-03T00:00:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from ..models import ActivityResult, TrainingSession


class AMESIntegration:
    """
    Integration with Agent Metrics & Evaluation System.

    Logs training results to AMES telemetry structure and provides
    performance analytics.

    Attributes:
        base_path: Base path to CodeAgents directory
        agent_id: Agent identifier

    Examples:
        >>> ames = AMESIntegration(agent_id="ClaudeCode")
        >>> ames.log_training_session(session)
        >>> metrics = ames.get_performance_metrics()
    """

    def __init__(self, agent_id: str, base_path: Optional[Path] = None):
        """
        Initialize AMES integration.

        Args:
            agent_id: Agent identifier (e.g., "ClaudeCode")
            base_path: Base path to CodeAgents directory

        Time Complexity: O(1)
        """
        self.agent_id = agent_id

        if base_path is None:
            # Default to CodeAgents directory
            base_path = Path(__file__).parent.parent.parent.parent.parent / "CodeAgents"

        self.base_path = Path(base_path)
        self.agent_path = self.base_path / agent_id
        self.logs_path = self.agent_path / "logs"
        self.analysis_path = self.agent_path / "analysis"

        # Ensure directories exist
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self.analysis_path.mkdir(parents=True, exist_ok=True)

    def log_training_session(self, session: TrainingSession) -> Path:
        """
        Log training session to AMES telemetry.

        Creates a log file following Agents.MD protocol:
        log_{TIMESTAMP}_{SHORT_HASH}.json

        Args:
            session: Completed training session

        Returns:
            Path to created log file

        Time Complexity: O(n) where n is number of results
        Space Complexity: O(n) for log data

        Examples:
            >>> ames = AMESIntegration(agent_id="ClaudeCode")
            >>> log_path = ames.log_training_session(session)
            >>> log_path.exists()
            True
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

        # Generate short hash from session ID
        short_hash = hashlib.sha256(session.session_id.encode()).hexdigest()[:6]

        filename = f"log_{timestamp}_{short_hash}.json"
        log_path = self.logs_path / filename

        log_data = {
            "agent": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "training_session",
            "target": session.session_id,
            "status": session.status.value,
            "session_type": session.session_type.value,
            "metrics": {
                "total_xp_earned": session.total_xp_earned,
                "average_score": session.average_score,
                "completion_rate": session.completion_rate,
                "pass_rate": session.pass_rate,
                "activities_completed": len(session.results),
                "activities_total": len(session.activities),
            },
            "duration_minutes": (
                (session.completed_at - session.started_at).total_seconds() / 60
                if session.started_at and session.completed_at
                else None
            ),
            "focus_areas": session.focus_areas,
        }

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)

        return log_path

    def log_activity_result(self, result: ActivityResult) -> Path:
        """
        Log individual activity result to AMES telemetry.

        Args:
            result: Completed activity result

        Returns:
            Path to created log file

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        short_hash = hashlib.sha256(result.activity.activity_id.encode()).hexdigest()[:6]

        filename = f"log_{timestamp}_{short_hash}.json"
        log_path = self.logs_path / filename

        log_data = {
            "agent": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "training_activity",
            "target": result.activity.activity_id,
            "status": "completed" if result.passed else "failed",
            "activity_type": result.activity.activity_type.value,
            "language": result.activity.language,
            "difficulty": result.activity.difficulty,
            "metrics": {
                "score": result.score,
                "passed": result.passed,
                "attempts": result.attempts,
                "duration_minutes": result.duration_minutes,
                "xp_earned": result.xp_earned,
            },
            "errors": result.errors,
        }

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)

        return log_path

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Analyze performance metrics from historical logs.

        Reads all log files and computes aggregate metrics for AMES integration.

        Returns:
            Dictionary of performance metrics

        Time Complexity: O(n) where n is number of log files
        Space Complexity: O(n) for all log data
        """
        logs = list(self.logs_path.glob("log_*.json"))

        if not logs:
            return {
                "total_sessions": 0,
                "total_activities": 0,
                "average_score": 0.0,
                "average_xp_per_session": 0.0,
            }

        total_sessions = 0
        total_activities = 0
        total_score = 0.0
        total_xp = 0
        score_count = 0

        for log_file in logs:
            with open(log_file, "r", encoding="utf-8") as f:
                log_data = json.load(f)

            if log_data["operation"] == "training_session":
                total_sessions += 1
                metrics = log_data.get("metrics", {})
                total_xp += metrics.get("total_xp_earned", 0)
                avg_score = metrics.get("average_score", 0)
                if avg_score > 0:
                    total_score += avg_score
                    score_count += 1

            elif log_data["operation"] == "training_activity":
                total_activities += 1

        return {
            "total_sessions": total_sessions,
            "total_activities": total_activities,
            "average_score": total_score / score_count if score_count > 0 else 0.0,
            "average_xp_per_session": total_xp / total_sessions if total_sessions > 0 else 0.0,
            "total_xp": total_xp,
        }

    def generate_training_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Generate comprehensive training report.

        Creates a markdown report with training statistics and recommendations.

        Args:
            output_path: Path to save report (defaults to analysis directory)

        Returns:
            Path to created report file

        Time Complexity: O(n) where n is number of logs
        Space Complexity: O(n)
        """
        if output_path is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            output_path = self.analysis_path / f"training_report_{timestamp}.md"

        metrics = self.get_performance_metrics()

        report = f"""# Training Report - {self.agent_id}

**Generated:** {datetime.now(timezone.utc).isoformat()}

---

## Summary Statistics

- **Total Sessions:** {metrics['total_sessions']}
- **Total Activities:** {metrics['total_activities']}
- **Average Score:** {metrics['average_score']:.2f}%
- **Average XP per Session:** {metrics['average_xp_per_session']:.0f}
- **Total XP Earned:** {metrics['total_xp']}

---

## AMES Integration

This training data is automatically integrated with the Agent Metrics & Evaluation System (AMES).

All training sessions and activities are logged to:
- Logs: `CodeAgents/{self.agent_id}/logs/`
- Analysis: `CodeAgents/{self.agent_id}/analysis/`

---

*Generated by Agent Training System v1.0*
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        return output_path
