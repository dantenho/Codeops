"""
[CREATE] Threndia Integration Service

Provides cooperative workflows between the Threndia branch and
Eudora-X Pylorix, including intel ingestion, activity generation,
and AMES-compliant telemetry logging.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..models.activity import ActivityType, TrainingActivity
from ..models.session import TrainingSession
from .config_service import ConfigService


class ThrendiaService:
    """
    [CREATE] Coordinates Threndia intel ingestion and telemetry.

    Args:
        base_path: Path to `CodeAgents/Training`.
        config_service: Shared configuration loader.
    """

    def __init__(self, base_path: Path, config_service: ConfigService):
        self.base_path = base_path
        self.config_service = config_service
        self.intel_dir = self.base_path / "ThrendiaData" / "intel"
        self.intel_dir.mkdir(parents=True, exist_ok=True)
        self.logs_root = self.base_path.parent  # CodeAgents directory

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #

    def sync_intel(self, agent_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        [DEBUG] Simulate syncing intel packets from Threndia feeds.

        Returns a summary payload and emits telemetry when not dry-running.
        """
        settings = self._require_settings(agent_id)
        payloads, sources = self._load_intel_payloads(settings)
        batch_id = self._generate_batch_id(settings)

        summary = {
            "agent_id": agent_id,
            "intel_batch_id": batch_id,
            "payload_count": len(payloads),
            "sources": sources,
            "mutual_cooperation": settings.get("mutual_cooperation", False),
        }

        if not dry_run:
            log_payload = {
                "operation": "threndia_sync",
                "intel_batch_id": batch_id,
                "sources": sources,
                "payload_count": len(payloads),
                "mutual_cooperation": settings.get("mutual_cooperation", False),
            }
            self._write_log(agent_id, log_payload)

        return summary

    def generate_market_activities(
        self,
        agent_id: str,
        limit: int = 3,
    ) -> Tuple[List[TrainingActivity], Dict[str, Any]]:
        """
        [CREATE] Convert intel packets into research activities.
        """
        settings = self._require_settings(agent_id)
        payloads, sources = self._load_intel_payloads(settings)
        batch_id = self._generate_batch_id(settings)

        activities: List[TrainingActivity] = []
        for item in payloads[:limit]:
            topic = item.get("category") or item.get("topic") or "market_analysis"
            activity = TrainingActivity(
                activity_id=str(uuid.uuid4()),
                activity_type=ActivityType.RESEARCH,
                title=item.get("title") or f"Threndia Insight: {topic}",
                description=item.get("summary") or "Review intel packet and extract action items.",
                difficulty=item.get("difficulty", 3),
                xp_reward=item.get("xp_reward", 75),
                required_resources=[item.get("source", "threndia-placeholder")],
                metadata={
                    "intel_batch_id": batch_id,
                    "source": item.get("source"),
                    "category": topic,
                    "risk_level": item.get("risk_level"),
                },
            )
            activities.append(activity)

        metadata = {
            "intel_batch_id": batch_id,
            "sources": sources,
            "payload_count": len(payloads),
        }

        return activities, metadata

    def record_market_session(
        self,
        session: TrainingSession,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Path]:
        """
        [CREATE] Emit telemetry for a Threndia-informed session.
        """
        settings = self._require_settings(session.agent_id)
        log_payload = {
            "operation": "market_analysis_session",
            "session_id": session.session_id,
            "session_type": session.session_type.value,
            "activities": len(session.activities),
            "intel_batch_id": (metadata or {}).get("intel_batch_id"),
            "sources": (metadata or {}).get("sources", []),
            "mutual_cooperation": settings.get("mutual_cooperation", False),
        }
        return self._write_log(session.agent_id, log_payload)

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #

    def _require_settings(self, agent_id: str) -> Dict[str, Any]:
        settings = self.config_service.get_threndia_settings(agent_id)
        if not settings:
            raise ValueError(f"Threndia settings not found for agent '{agent_id}'")
        return settings

    def _load_intel_payloads(self, settings: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
        payloads: List[Dict[str, Any]] = []
        sources: List[str] = []

        for file_path in sorted(self.intel_dir.glob("*.json")):
            try:
                with open(file_path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                    payloads.append(data)
                    sources.append(data.get("source") or file_path.name)
            except (json.JSONDecodeError, OSError):
                continue

        if not payloads:
            focus_topics = settings.get("focus_topics") or ["market_overview"]
            for topic in focus_topics:
                payloads.append(
                    {
                        "title": f"Focus Review: {topic}",
                        "summary": f"Placeholder intel for {topic}. Replace with Threndia feed output.",
                        "source": "threndia-placeholder",
                        "category": topic,
                        "difficulty": 3,
                        "risk_level": "moderate",
                    }
                )
            sources = ["threndia-placeholder"]

        return payloads, sorted(set(sources))

    def _generate_batch_id(self, settings: Dict[str, Any]) -> str:
        prefix = settings.get("intel_batch_prefix") or "threndia-intel"
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _write_log(self, agent_id: str, payload: Dict[str, Any]) -> Path:
        agent_dir = self.logs_root / agent_id
        logs_dir = agent_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        filename = f"log_{timestamp}_{uuid.uuid4().hex[:6]}.json"
        log_path = logs_dir / filename

        output = {
            "agent": agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **payload,
        }

        with open(log_path, "w", encoding="utf-8") as handle:
            json.dump(output, handle, indent=2)

        return log_path
