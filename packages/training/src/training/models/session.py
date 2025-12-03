"""
[CREATE] Training Session Models

Defines session structure, lifecycle, and aggregation.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:00:00Z
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field

from .activity import TrainingActivity, ActivityResult


class SessionType(str, Enum):
    """Types of training sessions."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    REMEDIAL = "remedial"
    ADVANCEMENT = "advancement"
    CUSTOM = "custom"
    MARKET_ANALYSIS = "market_analysis"


class SessionStatus(str, Enum):
    """Status of a training session."""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ABANDONED = "abandoned"


class TrainingSession(BaseModel):
    """
    [CREATE] Complete training session with activities and results.

    Manages the full lifecycle of a training session from
    scheduling through completion and evaluation.
    """
    model_config = ConfigDict(populate_by_name=True)

    session_id: str
    agent_id: str
    session_type: SessionType
    scheduled_at: datetime = Field(alias="scheduled_for")
    status: SessionStatus = SessionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    activities: List[TrainingActivity] = Field(default_factory=list)
    results: List[ActivityResult] = Field(default_factory=list)
    focus_areas: List[str] = Field(default_factory=list)
    notes: str = ""

    @property
    def scheduled_for(self) -> datetime:
        """Backwards compatible alias for scheduled_at."""
        return self.scheduled_at

    @scheduled_for.setter
    def scheduled_for(self, value: datetime) -> None:
        self.scheduled_at = value

    @computed_field
    @property
    def total_xp_earned(self) -> int:
        """Calculate total XP earned in session."""
        return sum(r.xp_earned for r in self.results)

    @computed_field
    @property
    def average_score(self) -> float:
        """Calculate average score across activities."""
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results) / len(self.results)

    @computed_field
    @property
    def completion_rate(self) -> float:
        """Calculate percentage of activities completed."""
        if not self.activities:
            return 0.0
        return len(self.results) / len(self.activities) * 100

    @computed_field
    @property
    def pass_rate(self) -> float:
        """Calculate percentage of activities passed."""
        if not self.results:
            return 0.0
        passed = sum(1 for r in self.results if r.passed)
        return passed / len(self.results) * 100

    def add_activity(self, activity: TrainingActivity) -> None:
        """Add an activity to the session."""
        self.activities.append(activity)

    def record_result(self, result: ActivityResult) -> None:
        """Record a completed activity result."""
        self.results.append(result)

    def start(self) -> None:
        """Mark session as started."""
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc)
        self.status = SessionStatus.IN_PROGRESS

    def complete(self) -> None:
        """Mark session as completed."""
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc)
        self.completed_at = datetime.now(timezone.utc)
        self.status = SessionStatus.COMPLETED
