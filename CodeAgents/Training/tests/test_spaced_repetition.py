"""
Module: test_spaced_repetition.py
Purpose: Unit tests for SM-2 spaced repetition algorithm.

Tests the SuperMemo 2 algorithm implementation for correct interval
calculation, ease factor adjustment, and review recording.

Agent: ClaudeCode
Created: 2025-12-03T00:00:00Z
Operation: [CREATE]
"""

from datetime import date, timedelta

import pytest

from src.training.models import (
    Flashcard,
    FlashcardBack,
    FlashcardCategory,
    FlashcardFront,
    ReviewRating,
    SpacedRepetitionData,
)
from src.training.services.spaced_repetition import SM2SpacedRepetition


class TestSM2Algorithm:
    """Test SM-2 spaced repetition algorithm."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sm2 = SM2SpacedRepetition()
        self.flashcard = Flashcard(
            id="FC-PY-0001",
            category=FlashcardCategory.SYNTAX,
            language="python",
            level=1,
            difficulty=1,
            front=FlashcardFront(question="What is a variable?"),
            back=FlashcardBack(answer="A named storage location"),
            sr_data=SpacedRepetitionData(next_review=date.today()),
        )

    def test_initial_ease_factor(self):
        """Test initial ease factor is 2.5."""
        assert self.flashcard.sr_data.ease_factor == 2.5

    def test_new_card_good_rating(self):
        """Test new card with GOOD rating graduates to 1 day."""
        next_review, new_ease = self.sm2.calculate_next_review(
            self.flashcard, ReviewRating.GOOD, 2000
        )

        assert next_review == date.today() + timedelta(days=1)
        assert new_ease == 2.5  # Ease unchanged for GOOD

    def test_new_card_easy_rating(self):
        """Test new card with EASY rating skips to 4 days."""
        next_review, new_ease = self.sm2.calculate_next_review(
            self.flashcard, ReviewRating.EASY, 2000
        )

        assert next_review == date.today() + timedelta(days=4)
        assert new_ease == 2.65  # Ease increased by 0.15

    def test_failed_review_resets(self):
        """Test AGAIN rating resets card."""
        # Set up as reviewed card
        self.flashcard.sr_data.repetitions = 5
        self.flashcard.sr_data.interval_days = 10

        next_review, new_ease = self.sm2.calculate_next_review(
            self.flashcard, ReviewRating.AGAIN, 2000
        )

        assert next_review == date.today()  # Immediate review
        assert new_ease < 2.5  # Ease reduced

    def test_ease_factor_minimum(self):
        """Test ease factor doesn't go below minimum 1.3."""
        # Set very low ease
        self.flashcard.sr_data.ease_factor = 1.4

        # Multiple failures
        for _ in range(5):
            _, new_ease = self.sm2.calculate_next_review(
                self.flashcard, ReviewRating.AGAIN, 2000
            )

        assert new_ease >= 1.3  # Should not go below minimum

    def test_interval_growth_good_rating(self):
        """Test interval grows with GOOD ratings."""
        # Set up reviewed card
        self.flashcard.sr_data.repetitions = 3
        self.flashcard.sr_data.interval_days = 10
        ease = 2.5

        next_review, _ = self.sm2.calculate_next_review(
            self.flashcard, ReviewRating.GOOD, 2000
        )

        expected_interval = int(10 * ease)  # 25 days
        actual_interval = (next_review - date.today()).days

        assert actual_interval == expected_interval

    def test_record_review_updates_state(self):
        """Test record_review updates all flashcard state."""
        initial_repetitions = self.flashcard.sr_data.repetitions

        updated = self.sm2.record_review(
            self.flashcard, ReviewRating.GOOD, 2500
        )

        assert updated.sr_data.last_review == date.today()
        assert len(updated.sr_data.history) == 1
        assert updated.sr_data.history[0].rating == ReviewRating.GOOD
        assert updated.sr_data.history[0].response_time_ms == 2500

    def test_leech_detection(self):
        """Test leech detection after 8 failures."""
        for i in range(8):
            self.flashcard = self.sm2.record_review(
                self.flashcard, ReviewRating.AGAIN, 2000
            )

        assert self.flashcard.sr_data.lapses == 8
        assert self.flashcard.sr_data.is_leech

    def test_get_due_cards_filtering(self):
        """Test get_due_cards filters correctly."""
        cards = []

        # Create 10 new cards
        for i in range(10):
            card = Flashcard(
                id=f"FC-PY-{i:04d}",
                category=FlashcardCategory.SYNTAX,
                language="python",
                level=1,
                difficulty=1,
                front=FlashcardFront(question=f"Q{i}"),
                back=FlashcardBack(answer=f"A{i}"),
                sr_data=SpacedRepetitionData(next_review=date.today(), repetitions=0),
            )
            cards.append(card)

        # Create 5 review cards (due today)
        for i in range(10, 15):
            card = Flashcard(
                id=f"FC-PY-{i:04d}",
                category=FlashcardCategory.SYNTAX,
                language="python",
                level=1,
                difficulty=1,
                front=FlashcardFront(question=f"Q{i}"),
                back=FlashcardBack(answer=f"A{i}"),
                sr_data=SpacedRepetitionData(
                    next_review=date.today(),
                    repetitions=2,
                    interval_days=5,
                ),
            )
            cards.append(card)

        # Create 5 cards not due
        for i in range(15, 20):
            card = Flashcard(
                id=f"FC-PY-{i:04d}",
                category=FlashcardCategory.SYNTAX,
                language="python",
                level=1,
                difficulty=1,
                front=FlashcardFront(question=f"Q{i}"),
                back=FlashcardBack(answer=f"A{i}"),
                sr_data=SpacedRepetitionData(
                    next_review=date.today() + timedelta(days=5),
                    repetitions=3,
                    interval_days=10,
                ),
            )
            cards.append(card)

        new_cards, review_cards = self.sm2.get_due_cards(
            cards, max_new=5, max_reviews=3
        )

        assert len(new_cards) == 5  # Limited by max_new
        assert len(review_cards) == 3  # Limited by max_reviews
        assert all(c.is_new for c in new_cards)
        assert all(not c.is_new for c in review_cards)

    def test_hard_rating_reduces_ease(self):
        """Test HARD rating reduces ease factor."""
        initial_ease = self.flashcard.sr_data.ease_factor

        _, new_ease = self.sm2.calculate_next_review(
            self.flashcard, ReviewRating.HARD, 2000
        )

        assert new_ease < initial_ease

    def test_interval_maximum_cap(self):
        """Test interval is capped at 365 days."""
        # Set up very mature card
        self.flashcard.sr_data.repetitions = 20
        self.flashcard.sr_data.interval_days = 350
        self.flashcard.sr_data.ease_factor = 3.0

        next_review, _ = self.sm2.calculate_next_review(
            self.flashcard, ReviewRating.GOOD, 2000
        )

        interval = (next_review - date.today()).days
        assert interval <= 365
