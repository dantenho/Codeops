"""
Example: Basic Usage of Agent Training System

This script demonstrates how to use the Agent Training System programmatically.

Agent: ClaudeCode
Created: 2025-12-03T00:00:00Z
Operation: [CREATE]
"""

from datetime import date, datetime, timezone
from pathlib import Path

from training.config import ConfigManager
from training.models import (
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
from training.services import SM2SpacedRepetition
from training.utils import AMESIntegration


def example_1_configuration():
    """Example 1: Load and use configuration."""
    print("=" * 60)
    print("EXAMPLE 1: Configuration Management")
    print("=" * 60)

    # Load configuration
    config = ConfigManager()

    # Get training schedule
    schedule = config.get_training_schedule()
    daily = schedule["schedule"]["daily"]
    print(f"\nDaily Training Schedule:")
    print(f"  Duration: {daily['duration_minutes']} minutes")
    print(f"  Time: {daily['time']}")

    # Get agent profile
    agent_config = config.get_agent_config("ClaudeCode")
    print(f"\nClaudeCode Profile:")
    print(f"  Display Name: {agent_config['display_name']}")
    print(f"  Specializations: {', '.join(agent_config['specializations'])}")
    print(f"  Primary Languages: {', '.join(agent_config['primary_languages'])}")

    # Get difficulty curve
    level_1 = config.get_level_config(1)
    print(f"\nLevel 1 ({level_1['name']}):")
    print(f"  XP Required: {level_1['xp_required']}")
    print(f"  Concepts: {', '.join(level_1['concepts'])}")


def example_2_training_activity():
    """Example 2: Create and complete a training activity."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Training Activity")
    print("=" * 60)

    # Create an activity
    activity = TrainingActivity(
        activity_id="act_python_variables_001",
        activity_type=ActivityType.EXERCISE,
        content_id="Level_01/01_syntax/variables.py",
        duration_minutes=15,
        difficulty=1,
        language="python",
    )

    print(f"\nCreated Activity:")
    print(f"  ID: {activity.activity_id}")
    print(f"  Type: {activity.activity_type.value}")
    print(f"  Language: {activity.language}")
    print(f"  Difficulty: {activity.difficulty}/5")

    # Simulate completion
    activity.status = ActivityStatus.COMPLETED

    # Create result
    started = datetime.now(timezone.utc)
    import time

    time.sleep(0.1)  # Simulate work
    completed = datetime.now(timezone.utc)

    result = ActivityResult(
        activity=activity,
        started_at=started,
        completed_at=completed,
        score=85.0,
        passed=True,
        attempts=1,
        feedback="Good work! Variables created correctly.",
        xp_earned=50,
    )

    print(f"\nActivity Result:")
    print(f"  Score: {result.score}/100")
    print(f"  Passed: {result.passed}")
    print(f"  XP Earned: {result.xp_earned}")
    print(f"  Duration: {result.duration_seconds:.2f} seconds")


def example_3_training_session():
    """Example 3: Create and manage a training session."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Training Session")
    print("=" * 60)

    # Create session
    session = TrainingSession(
        session_id="sess_claude_daily_001",
        agent_id="ClaudeCode",
        session_type=SessionType.DAILY,
        scheduled_at=datetime.now(timezone.utc),
        focus_areas=["python", "syntax"],
    )

    print(f"\nCreated Session:")
    print(f"  ID: {session.session_id}")
    print(f"  Agent: {session.agent_id}")
    print(f"  Type: {session.session_type.value}")
    print(f"  Focus: {', '.join(session.focus_areas)}")

    # Start session
    session.start()
    print(f"\nSession Status: {session.status.value}")

    # Add activities
    for i in range(3):
        activity = TrainingActivity(
            activity_id=f"act_exercise_{i}",
            activity_type=ActivityType.EXERCISE,
            content_id=f"exercise_{i}",
            duration_minutes=10,
            difficulty=1,
            language="python",
        )
        session.add_activity(activity)

    print(f"Added {len(session.activities)} activities")

    # Complete session
    session.complete()
    print(f"\nSession completed!")
    print(f"  Total XP: {session.total_xp_earned}")
    print(f"  Completion Rate: {session.completion_rate:.1f}%")


def example_4_agent_progress():
    """Example 4: Track agent progress."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Agent Progress Tracking")
    print("=" * 60)

    # Create progress tracker
    progress = AgentProgress(agent_id="ClaudeCode")

    print(f"\nInitial Progress:")
    print(f"  Level: {progress.current_level}")
    print(f"  Total XP: {progress.xp.total}")

    # Add XP
    progress.add_xp(100, category="exercise", language="python")
    print(f"\nAfter earning 100 XP:")
    print(f"  Level: {progress.current_level}")
    print(f"  Total XP: {progress.xp.total}")
    print(f"  Python XP: {progress.xp.by_language.get('python', 0)}")

    # Add more XP to level up
    progress.add_xp(450)  # Total 550, should reach level 2
    print(f"\nAfter earning 450 more XP:")
    print(f"  Level: {progress.current_level}")
    print(f"  Total XP: {progress.xp.total}")

    # Update streak
    progress.update_streak()
    print(f"\nStreak:")
    print(f"  Current: {progress.daily_streak.current} days")
    print(f"  Longest: {progress.daily_streak.longest} days")

    # Add badge
    badge = Badge(
        id="badge_level_2",
        name="Level 2 Achievement",
        description="Reached Level 2",
        icon="🎯",
        earned_at=datetime.now(timezone.utc),
        category="level",
    )
    progress.add_badge(badge)
    print(f"\nBadges: {len(progress.badges)}")


def example_5_flashcards():
    """Example 5: Work with flashcards and spaced repetition."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Flashcards and Spaced Repetition")
    print("=" * 60)

    # Create flashcard
    flashcard = Flashcard(
        id="FC-PY-0001",
        category=FlashcardCategory.SYNTAX,
        language="python",
        level=1,
        difficulty=1,
        front=FlashcardFront(
            question="What is a list comprehension in Python?",
            hints=["It's a concise way to create lists", "Uses square brackets"],
        ),
        back=FlashcardBack(
            answer="A concise way to create lists using a single line of code",
            code="squares = [x**2 for x in range(10)]",
            explanation="List comprehensions provide a compact syntax for creating lists.",
        ),
        tags=["lists", "comprehension", "syntax"],
        sr_data=SpacedRepetitionData(next_review=date.today()),
    )

    print(f"\nFlashcard:")
    print(f"  ID: {flashcard.id}")
    print(f"  Category: {flashcard.category.value}")
    print(f"  Question: {flashcard.front.question}")
    print(f"  Is Due: {flashcard.is_due}")
    print(f"  Maturity: {flashcard.maturity}")

    # Review flashcard
    sm2 = SM2SpacedRepetition()
    updated_card = sm2.record_review(flashcard, ReviewRating.GOOD, 3000)

    print(f"\nAfter Review (GOOD rating):")
    print(f"  Next Review: {updated_card.sr_data.next_review}")
    print(f"  Repetitions: {updated_card.sr_data.repetitions}")
    print(f"  Interval: {updated_card.sr_data.interval_days} days")


def example_6_ames_integration():
    """Example 6: AMES integration."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: AMES Integration")
    print("=" * 60)

    # Create AMES integration
    ames = AMESIntegration(agent_id="ClaudeCode")

    print(f"\nAMES Paths:")
    print(f"  Base: {ames.base_path}")
    print(f"  Agent: {ames.agent_path}")
    print(f"  Logs: {ames.logs_path}")
    print(f"  Analysis: {ames.analysis_path}")

    # Get metrics
    metrics = ames.get_performance_metrics()
    print(f"\nPerformance Metrics:")
    print(f"  Total Sessions: {metrics['total_sessions']}")
    print(f"  Total Activities: {metrics['total_activities']}")
    print(f"  Average Score: {metrics['average_score']:.2f}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("AGENT TRAINING SYSTEM - EXAMPLES")
    print("=" * 60)

    examples = [
        example_1_configuration,
        example_2_training_activity,
        example_3_training_session,
        example_4_agent_progress,
        example_5_flashcards,
        example_6_ames_integration,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n[ERROR] {example.__name__}: {e}")

    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
