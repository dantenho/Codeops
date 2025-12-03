"""
[CREATE] Training Manager Service

Core logic for managing training sessions and progress.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:20:00Z
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from ..models.session import TrainingSession, SessionType, SessionStatus
from ..models.activity import TrainingActivity, ActivityType, ActivityStatus
from ..models.progress import AgentProgress
from .config_service import ConfigService
from .threndia_service import ThrendiaService
from ..data.progress_repository import get_progress_repository


class TrainingManager:
    """
    Manages the lifecycle of training sessions and agent progress.
    """

    def __init__(self, base_path: Path, threndia_service: Optional[ThrendiaService] = None):
        self.base_path = base_path
        self.config_service = ConfigService(base_path / "config")
        self.threndia_service = threndia_service or ThrendiaService(base_path, self.config_service)
        self.data_path = base_path / "data"
        self.data_path.mkdir(exist_ok=True)
        self._threndia_cache: Dict[str, Dict[str, Any]] = {}
        self._latest_threndia_metadata: Dict[str, Dict[str, Any]] = {}

        # Initialize progress repository
        self.progress_repo = get_progress_repository(self.data_path / "progress")

    def initialize_agent(self, agent_id: str) -> AgentProgress:
        """Initialize a new agent progress record."""
        profile = self.config_service.get_agent_profile(agent_id)
        if not profile:
            raise ValueError(f"Unknown agent: {agent_id}")

        progress = AgentProgress(
            agent_id=agent_id,
            current_level=profile.get("current_level", 1)
        )
        self._save_progress(progress)
        return progress

    def start_session(self, agent_id: str, session_type: SessionType = SessionType.DAILY) -> TrainingSession:
        """Start a new training session for an agent."""
        progress = self.get_progress(agent_id)
        if not progress:
            progress = self.initialize_agent(agent_id)

        threndia_settings = self._get_threndia_settings(agent_id)
        resolved_session_type = self._resolve_session_type(session_type, threndia_settings)
        focus_areas = threndia_settings.get("focus_topics", []) if threndia_settings else []
        # Generate activities based on schedule and level
        activities = self._generate_activities(
            agent_id,
            resolved_session_type,
            progress.current_level,
            threndia_settings=threndia_settings,
        )
        metadata = self.get_threndia_metadata(agent_id)

        notes = ""
        if threndia_settings and threndia_settings.get("mutual_cooperation"):
            notes = "Threndia mutual cooperation enabled"
        if metadata and metadata.get("intel_batch_id"):
            notes = f"{notes} | intel_batch_id={metadata['intel_batch_id']}".strip(" |")

        session = TrainingSession(
            session_id=str(uuid.uuid4()),
            agent_id=agent_id,
            session_type=resolved_session_type,
            scheduled_for=datetime.now(timezone.utc),
            status=SessionStatus.IN_PROGRESS,
            activities=activities,
            focus_areas=focus_areas,
            notes=notes,
        )

        # In a real implementation, we would save the session state here
        return session

    def _generate_activities(
        self,
        agent_id: str,
        session_type: SessionType,
        level: int,
        *,
        threndia_settings: Optional[Dict[str, Any]] = None,
    ) -> List[TrainingActivity]:
        """Generate appropriate activities for the session."""
        schedule_config = self.config_service.get_schedule(session_type.value)
        activities = []

        # Example: Generate a simple syntax drill
        if "syntax_drill" in [a["type"] for a in schedule_config.get("activities", [])]:
            activities.append(TrainingActivity(
                activity_id=str(uuid.uuid4()),
                activity_type=ActivityType.SYNTAX_DRILL,
                title="Python List Comprehensions",
                description="Convert the following loops to list comprehensions...",
                difficulty=level,
                xp_reward=50
            ))

        if threndia_settings and self.threndia_service:
            market_activities, metadata = self.threndia_service.generate_market_activities(agent_id)
            if market_activities:
                activities.extend(market_activities)
            if metadata:
                self._latest_threndia_metadata[agent_id] = metadata

        return activities

    def get_progress(self, agent_id: str) -> Optional[AgentProgress]:
        """Load agent progress from disk."""
        return self.progress_repo.load(agent_id)

    def _save_progress(self, progress: AgentProgress, create_snapshot: bool = False) -> None:
        """
        Save agent progress to disk.

        Args:
            progress: AgentProgress to save
            create_snapshot: Whether to create historical snapshot
        """
        self.progress_repo.save(progress, create_snapshot=create_snapshot)

    def update_progress_after_session(
        self,
        agent_id: str,
        session: TrainingSession,
        create_snapshot: bool = True
    ) -> AgentProgress:
        """
        Update agent progress after completing a training session.

        Args:
            agent_id: Agent identifier
            session: Completed training session
            create_snapshot: Whether to create historical snapshot

        Returns:
            Updated AgentProgress
        """
        progress = self.get_progress(agent_id)
        if not progress:
            progress = self.initialize_agent(agent_id)

        # Update XP from session
        total_xp = session.total_xp_earned
        progress.xp.total += total_xp

        # Check for level up
        from ..models.progress import LEVEL_THRESHOLDS
        for level, threshold in sorted(LEVEL_THRESHOLDS.items(), reverse=True):
            if progress.xp.total >= threshold:
                progress.current_level = level
                break

        # Update streaks
        progress.daily_streak.current += 1
        if progress.daily_streak.current > progress.daily_streak.longest:
            progress.daily_streak.longest = progress.daily_streak.current
        progress.daily_streak.last_activity = datetime.now(timezone.utc).date()

        # Save with snapshot
        self._save_progress(progress, create_snapshot=create_snapshot)

        return progress

    def _get_threndia_settings(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Return cached Threndia configuration for an agent."""
        if agent_id not in self._threndia_cache:
            settings = self.config_service.get_threndia_settings(agent_id)
            self._threndia_cache[agent_id] = settings or {}
        cached = self._threndia_cache.get(agent_id) or None
        return cached

    def _resolve_session_type(
        self,
        requested_type: SessionType,
        threndia_settings: Optional[Dict[str, Any]],
    ) -> SessionType:
        """Adjust session type if Threndia specifies a dedicated mode."""
        if threndia_settings and threndia_settings.get("default_session_type") == "market_analysis":
            return SessionType.MARKET_ANALYSIS
        return requested_type

    def get_threndia_metadata(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Expose latest Threndia metadata to consumers."""
        return self._latest_threndia_metadata.get(agent_id)
