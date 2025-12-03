"""
[CREATE] Agent Progress Tracking Models

Tracks learning progress, achievements, and statistics.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:00:00Z
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import ClassVar, Dict, List, Optional
from pydantic import BaseModel, Field, computed_field

class SkillLevel(BaseModel):
    """Proficiency in a specific skill or language."""
    skill: str
    level: int = Field(1, ge=1, le=10)
    xp: int = Field(0, ge=0)
    last_practiced: Optional[datetime] = None
    practice_count: int = 0


class Streak(BaseModel):
    """Training streak tracking."""
    current: int = 0
    longest: int = 0
    last_activity: Optional[datetime] = None


class Badge(BaseModel):
    """Achievement badge."""
    id: str
    name: str
    description: str
    icon: str
    earned_at: datetime
    category: str


class WeaknessArea(BaseModel):
    """Identified area needing improvement."""
    skill: str
    error_rate: float
    recommended_exercises: List[str] = Field(default_factory=list)
    priority: str = "medium"  # low, medium, high, critical
    identified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StrengthArea(BaseModel):
    """Identified strong area."""
    skill: str
    mastery_score: float
    evidence: List[str] = Field(default_factory=list)


class ExperiencePoints(BaseModel):
    """XP tracking."""
    total: int = 0
    this_week: int = 0
    this_month: int = 0
    by_category: Dict[str, int] = Field(default_factory=dict)
    by_language: Dict[str, int] = Field(default_factory=dict)


class CompletionStats(BaseModel):
    """Statistics about completed activities."""
    exercises: Dict[str, int] = Field(default_factory=dict)
    assessments_passed: int = 0
    flashcards_mastered: int = 0
    certifications: List[Dict] = Field(default_factory=list)
    sessions_completed: int = 0


class PerformanceMetrics(BaseModel):
    """Aggregate performance metrics."""
    average_score: float = 0.0
    accuracy_percentile: int = 50
    speed_percentile: int = 50
    consistency_score: float = 0.0
    improvement_rate: float = 0.0


class AgentProgress(BaseModel):
    """
    [CREATE] Complete progress tracking for an agent.

    Aggregates all training data, achievements, and analytics
    for a single agent.
    """
    LEVEL_THRESHOLDS: ClassVar[Dict[int, int]] = {
        1: 0,
        2: 500,
        3: 1500,
        4: 4000,
        5: 10000,
        6: 25000,
        7: 50000,
    }

    agent_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: Optional[datetime] = None

    # Level tracking
    current_level: int = Field(1, ge=1, le=7)
    level_by_language: Dict[str, int] = Field(default_factory=dict)
    skills: List[SkillLevel] = Field(default_factory=list)

    # XP and progression
    xp: ExperiencePoints = Field(default_factory=ExperiencePoints)

    # Streaks
    daily_streak: Streak = Field(default_factory=Streak)
    weekly_streak: Streak = Field(default_factory=Streak)

    # Statistics
    completions: CompletionStats = Field(default_factory=CompletionStats)
    performance: PerformanceMetrics = Field(default_factory=PerformanceMetrics)

    # Skill assessment
    strengths: List[StrengthArea] = Field(default_factory=list)
    weaknesses: List[WeaknessArea] = Field(default_factory=list)

    # Achievements
    badges: List[Badge] = Field(default_factory=list)

    # Scheduling
    next_session: Optional[datetime] = None
    scheduled_focus_areas: List[str] = Field(default_factory=list)

    def add_xp(self, amount: int, category: str = "general", language: Optional[str] = None) -> None:
        """Add XP with category and language tracking."""
        self.xp.total += amount
        self.xp.this_week += amount
        self.xp.this_month += amount
        self.xp.by_category[category] = self.xp.by_category.get(category, 0) + amount

        if language:
            self.xp.by_language[language] = self.xp.by_language.get(language, 0) + amount
        self._check_level_up()

    def _check_level_up(self) -> bool:
        """Check and apply level up if qualified."""
        for level, threshold in sorted(self.LEVEL_THRESHOLDS.items(), reverse=True):
            if self.xp.total >= threshold and level > self.current_level:
                self.current_level = level
                return True
        return False

    def update_streak(self) -> None:
        """Update daily streak based on activity."""
        now = datetime.now(timezone.utc)
        last = self.daily_streak.last_activity
        if last:
            delta = now.date() - last.date()
            if delta.days == 1:
                self.daily_streak.current += 1
            elif delta.days > 1:
                self.daily_streak.current = 1
        else:
            self.daily_streak.current = 1

        self.daily_streak.last_activity = now
        self.last_activity = now
        if self.daily_streak.current > self.daily_streak.longest:
            self.daily_streak.longest = self.daily_streak.current

    def add_badge(self, badge: Badge) -> None:
        """Add a new achievement badge."""
        if not any(b.id == badge.id for b in self.badges):
            self.badges.append(badge)
