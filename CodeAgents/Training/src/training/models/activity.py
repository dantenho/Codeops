"""
[CREATE] Training Activity Models

Defines all activity types, their properties, and validation.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:00:00Z
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ActivityType(str, Enum):
    """Types of training activities."""
    FLASHCARD_REVIEW = "flashcard_review"
    CODING_EXERCISE = "coding_exercise"
    ALGORITHM_CHALLENGE = "algorithm_challenge"
    ASSESSMENT = "assessment"
    REFLECTION = "reflection"
    SYNTAX_DRILL = "syntax_drill"


class ActivityStatus(str, Enum):
    """Status of an activity."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class TrainingActivity(BaseModel):
    """
    [CREATE] Represents a single training activity.

    Attributes:
        activity_id: Unique identifier
        activity_type: Type of activity
        title: Display title
        description: Detailed instructions
        difficulty: 1-5 scale
        estimated_duration_minutes: Expected time
        xp_reward: Experience points for completion
        required_resources: URLs or file paths
    """
    activity_id: str
    activity_type: ActivityType
    title: str
    description: str
    difficulty: int = Field(1, ge=1, le=5)
    estimated_duration_minutes: int = Field(15, ge=1)
    xp_reward: int = Field(50, ge=0)
    required_resources: List[str] = Field(default_factory=list)
    language: Optional[str] = None
    status: ActivityStatus = ActivityStatus.PENDING
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        valid_languages = {
            "python", "javascript", "typescript", "go",
            "rust", "java", "cpp", "c", "bash"
        }
        if v is not None and v.lower() not in valid_languages:
            raise ValueError(f"Invalid language: {v}")
        return v.lower() if v else None


class ActivityResult(BaseModel):
    """
    [CREATE] Result of completing a training activity.

    Attributes:
        activity: The completed activity
        started_at: Start timestamp
        completed_at: Completion timestamp
        score: 0-100 score
        passed: Whether it met the threshold
        feedback: Qualitative feedback
    """
    activity: TrainingActivity
    started_at: datetime
    completed_at: datetime
    score: float = Field(0.0, ge=0.0, le=100.0)
    passed: bool = False
    feedback: str = ""
    xp_earned: int = Field(0, ge=0)
    errors: List[str] = Field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        """Calculate actual duration in seconds."""
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def duration_minutes(self) -> float:
        """Calculate actual duration in minutes."""
        return self.duration_seconds / 60.0
