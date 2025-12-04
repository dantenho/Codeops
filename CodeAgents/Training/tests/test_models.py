"""
Module: test_models.py
Purpose: Unit tests for Training System data models.

Tests all Pydantic models for correct validation, computed properties,
and business logic.

Agent: ClaudeCode
Created: 2025-12-03T00:00:00Z
Operation: [CREATE]
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from src.training.models import (
    ActivityResult,
    ActivityStatus,
    ActivityType,
    AgentProgress,
    Badge,
    Flashcard,
    FlashcardBack,
    FlashcardCategory,
    FlashcardDeck,
    FlashcardFront,
    ReviewRating,
    SessionStatus,
    SessionType,
    SpacedRepetitionData,
    TrainingActivity,
    TrainingSession,
)


class TestTrainingActivity:
    """Test TrainingActivity model."""

    def test_create_activity(self):
        """Test creating a valid training activity."""
        activity = TrainingActivity(
            activity_id="act_test_001",
            activity_type=ActivityType.EXERCISE,
            content_id="level1/syntax/variables.py",
            duration_minutes=15,
            difficulty=1,
            language="python",
        )

        assert activity.activity_id == "act_test_001"
        assert activity.activity_type == ActivityType.EXERCISE
        assert activity.language == "python"
        assert activity.status == ActivityStatus.PENDING

    def test_invalid_language(self):
        """Test that invalid language raises error."""
        with pytest.raises(ValueError):
            TrainingActivity(
                activity_id="act_test_002",
                activity_type=ActivityType.EXERCISE,
                content_id="test",
                duration_minutes=15,
                language="invalid_lang",
            )

    def test_duration_validation(self):
        """Test duration must be between 1-180 minutes."""
        with pytest.raises(ValueError):
            TrainingActivity(
                activity_id="act_test_003",
                activity_type=ActivityType.EXERCISE,
                content_id="test",
                duration_minutes=200,  # Too long
            )


class TestActivityResult:
    """Test ActivityResult model."""

    def test_duration_calculation(self):
        """Test duration properties calculate correctly."""
        activity = TrainingActivity(
            activity_id="act_test_001",
            activity_type=ActivityType.EXERCISE,
            content_id="test",
            duration_minutes=15,
        )

        started = datetime.now(timezone.utc)
        completed = started + timedelta(minutes=10)

        result = ActivityResult(
            activity=activity,
            started_at=started,
            completed_at=completed,
            score=85.0,
            passed=True,
        )

        assert result.duration_seconds == 600.0
        assert result.duration_minutes == 10.0


class TestTrainingSession:
    """Test TrainingSession model."""

    def test_create_session(self):
        """Test creating a training session."""
        session = TrainingSession(
            session_id="sess_test_001",
            agent_id="ClaudeCode",
            session_type=SessionType.DAILY,
            scheduled_at=datetime.now(timezone.utc),
        )

        assert session.status == SessionStatus.PENDING
        assert len(session.activities) == 0
        assert session.total_xp_earned == 0

    def test_session_lifecycle(self):
        """Test session start and complete methods."""
        session = TrainingSession(
            session_id="sess_test_002",
            agent_id="ClaudeCode",
            session_type=SessionType.DAILY,
            scheduled_at=datetime.now(timezone.utc),
        )

        # Start session
        session.start()
        assert session.status == SessionStatus.IN_PROGRESS
        assert session.started_at is not None

        # Complete session
        session.complete()
        assert session.status == SessionStatus.COMPLETED
        assert session.completed_at is not None

    def test_computed_properties(self):
        """Test session computed properties."""
        session = TrainingSession(
            session_id="sess_test_003",
            agent_id="ClaudeCode",
            session_type=SessionType.DAILY,
            scheduled_at=datetime.now(timezone.utc),
        )

        # Add activities
        for i in range(3):
            activity = TrainingActivity(
                activity_id=f"act_test_{i}",
                activity_type=ActivityType.EXERCISE,
                content_id=f"test_{i}",
                duration_minutes=10,
            )
            session.add_activity(activity)

        assert len(session.activities) == 3
        assert session.completion_rate == 0.0

        # Add results
        result = ActivityResult(
            activity=session.activities[0],
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            score=90.0,
            passed=True,
            xp_earned=50,
        )
        session.record_result(result)

        assert session.completion_rate == pytest.approx(33.33, 0.1)
        assert session.average_score == 90.0
        assert session.pass_rate == 100.0
        assert session.total_xp_earned == 50


class TestFlashcard:
    """Test Flashcard model."""

    def test_create_flashcard(self):
        """Test creating a flashcard."""
        flashcard = Flashcard(
            id="FC-PY-0001",
            category=FlashcardCategory.SYNTAX,
            language="python",
            level=1,
            difficulty=1,
            front=FlashcardFront(question="What is a variable?"),
            back=FlashcardBack(answer="A named storage location"),
            sr_data=SpacedRepetitionData(next_review=date.today()),
        )

        assert flashcard.id == "FC-PY-0001"
        assert flashcard.is_new
        assert flashcard.maturity == "new"

    def test_flashcard_maturity(self):
        """Test flashcard maturity levels."""
        # New card
        flashcard = Flashcard(
            id="FC-PY-0001",
            category=FlashcardCategory.SYNTAX,
            language="python",
            level=1,
            difficulty=1,
            front=FlashcardFront(question="Test"),
            back=FlashcardBack(answer="Test"),
            sr_data=SpacedRepetitionData(
                next_review=date.today(),
                repetitions=0,
            ),
        )
        assert flashcard.maturity == "new"

        # Learning card
        flashcard.sr_data.repetitions = 2
        flashcard.sr_data.interval_days = 10
        assert flashcard.maturity == "learning"

        # Mature card
        flashcard.sr_data.interval_days = 25
        assert flashcard.maturity == "mature"

    def test_is_due(self):
        """Test is_due property."""
        # Due today
        flashcard = Flashcard(
            id="FC-PY-0001",
            category=FlashcardCategory.SYNTAX,
            language="python",
            level=1,
            difficulty=1,
            front=FlashcardFront(question="Test"),
            back=FlashcardBack(answer="Test"),
            sr_data=SpacedRepetitionData(next_review=date.today()),
        )
        assert flashcard.is_due

        # Not due (tomorrow)
        flashcard.sr_data.next_review = date.today() + timedelta(days=1)
        assert not flashcard.is_due


class TestFlashcardDeck:
    """Test FlashcardDeck model."""

    def test_deck_computed_properties(self):
        """Test deck computed properties."""
        deck = FlashcardDeck(
            deck_id="deck_test",
            name="Test Deck",
            description="Test",
            language="python",
            level=1,
        )

        # Add cards
        for i in range(5):
            card = Flashcard(
                id=f"FC-PY-{i:04d}",
                category=FlashcardCategory.SYNTAX,
                language="python",
                level=1,
                difficulty=1,
                front=FlashcardFront(question=f"Q{i}"),
                back=FlashcardBack(answer=f"A{i}"),
                sr_data=SpacedRepetitionData(
                    next_review=date.today() if i < 3 else date.today() + timedelta(days=1),
                    repetitions=0 if i < 2 else 1,
                ),
            )
            deck.cards.append(card)

        assert deck.total_cards == 5
        assert deck.new_cards == 2  # First 2 cards have repetitions=0
        assert deck.due_cards == 3  # First 3 cards are due today


class TestAgentProgress:
    """Test AgentProgress model."""

    def test_create_progress(self):
        """Test creating agent progress."""
        progress = AgentProgress(agent_id="ClaudeCode")

        assert progress.current_level == 1
        assert progress.xp.total == 0
        assert progress.daily_streak.current == 0

    def test_add_xp(self):
        """Test adding XP."""
        progress = AgentProgress(agent_id="ClaudeCode")

        progress.add_xp(100, category="exercise", language="python")

        assert progress.xp.total == 100
        assert progress.xp.by_category["exercise"] == 100
        assert progress.xp.by_language["python"] == 100

    def test_level_up(self):
        """Test automatic level up."""
        progress = AgentProgress(agent_id="ClaudeCode")

        # Should be level 1
        assert progress.current_level == 1

        # Add XP to reach level 2 (500 XP required)
        progress.add_xp(500)
        assert progress.current_level == 2

        # Add XP to reach level 3 (1500 XP total required)
        progress.add_xp(1000)
        assert progress.current_level == 3

    def test_streak_tracking(self):
        """Test streak update logic."""
        progress = AgentProgress(agent_id="ClaudeCode")

        # First activity
        progress.update_streak()
        assert progress.daily_streak.current == 1
        assert progress.daily_streak.longest == 1

        # Same day (simulate by not changing last_activity)
        progress.update_streak()
        assert progress.daily_streak.current == 1

        # Next day (simulate)
        progress.daily_streak.last_activity = datetime.now(timezone.utc) - timedelta(days=1)
        progress.update_streak()
        assert progress.daily_streak.current == 2
        assert progress.daily_streak.longest == 2

    def test_add_badge(self):
        """Test adding badges."""
        progress = AgentProgress(agent_id="ClaudeCode")

        badge = Badge(
            id="badge_first_session",
            name="First Session",
            description="Completed first training session",
            icon="🎯",
            earned_at=datetime.now(timezone.utc),
            category="milestone",
        )

        progress.add_badge(badge)
        assert len(progress.badges) == 1

        # Adding same badge should not duplicate
        progress.add_badge(badge)
        assert len(progress.badges) == 1
