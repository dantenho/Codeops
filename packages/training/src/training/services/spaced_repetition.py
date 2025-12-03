"""
Module: spaced_repetition.py
Purpose: SM-2 Spaced Repetition Algorithm implementation.

This module implements the SuperMemo 2 (SM-2) algorithm for optimal flashcard
scheduling. The algorithm calculates review intervals based on performance
ratings to maximize long-term retention.

Agent: ClaudeCode
Created: 2025-12-03T00:00:00Z
Operation: [CREATE]
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Tuple

from ..models.flashcard import Flashcard, ReviewHistory, ReviewRating


class SM2SpacedRepetition:
    """
    SM-2 (SuperMemo 2) spaced repetition algorithm implementation.

    The SM-2 algorithm calculates optimal review intervals based on:
    - Ease factor (how easy the card is to remember)
    - Repetition count (how many times reviewed successfully)
    - Review rating (again/hard/good/easy)

    Algorithm Details:
    - Initial ease factor: 2.5
    - Minimum ease factor: 1.3
    - Ease adjustments based on rating
    - Interval calculation using ease factor
    - Leech detection after 8 lapses

    References:
        https://www.supermemo.com/en/blog/application-of-a-computer-to-improve-the-results-obtained-in-working-with-the-supermemo-method

    Examples:
        >>> sm2 = SM2SpacedRepetition()
        >>> next_review, new_ease = sm2.calculate_next_review(
        ...     flashcard, ReviewRating.GOOD, response_time_ms=3500
        ... )
    """

    # Configuration constants
    INITIAL_EASE = 2.5
    MIN_EASE = 1.3
    EASE_BONUS = 0.15
    EASE_PENALTY = 0.2
    LEECH_THRESHOLD = 8

    # Learning steps (in minutes) for new cards
    LEARNING_STEPS = [1, 10]  # 1 minute, then 10 minutes
    GRADUATING_INTERVAL = 1  # 1 day
    EASY_INTERVAL = 4  # 4 days

    def calculate_next_review(
        self,
        flashcard: Flashcard,
        rating: ReviewRating,
        response_time_ms: int,
    ) -> Tuple[date, float]:
        """
        Calculate next review date and updated ease factor.

        Implements the core SM-2 algorithm logic:
        1. Handle failures (rating = AGAIN)
        2. Calculate new ease factor based on rating
        3. Calculate new interval based on repetitions and ease
        4. Return next review date and ease factor

        Args:
            flashcard: Flashcard being reviewed
            rating: ReviewRating (AGAIN=0, HARD=1, GOOD=2, EASY=3)
            response_time_ms: Response time in milliseconds

        Returns:
            Tuple of (next_review_date, new_ease_factor)

        Time Complexity: O(1)
        Space Complexity: O(1)

        Examples:
            >>> card = create_flashcard()  # New card
            >>> next_date, ease = sm2.calculate_next_review(card, ReviewRating.GOOD, 2000)
            >>> next_date  # Should be 1 day from today
            >>> ease  # Should be 2.5 (unchanged for GOOD)
        """
        sr_data = flashcard.sr_data
        current_ease = sr_data.ease_factor
        current_interval = sr_data.interval_days
        repetitions = sr_data.repetitions

        # Calculate new ease factor
        new_ease = self._calculate_ease_factor(current_ease, rating)

        # Calculate new interval and repetitions
        if rating == ReviewRating.AGAIN:
            # Failed review - reset
            new_interval = 0
            new_repetitions = 0
        elif flashcard.is_new or current_interval == 0:
            # New card or relearning
            new_interval, new_repetitions = self._handle_new_card(rating, repetitions)
        else:
            # Review card
            new_interval = self._calculate_review_interval(
                current_interval, new_ease, rating, repetitions
            )
            new_repetitions = repetitions + 1

        # Calculate next review date
        next_review = date.today() + timedelta(days=int(new_interval))

        return next_review, new_ease

    def _calculate_ease_factor(self, current_ease: float, rating: ReviewRating) -> float:
        """
        Calculate new ease factor based on rating.

        Ease factor adjustments:
        - AGAIN (0): -0.2 (penalty for failure)
        - HARD (1): -0.15 (penalty for difficulty)
        - GOOD (2): 0 (no change)
        - EASY (3): +0.15 (bonus for ease)

        Args:
            current_ease: Current ease factor
            rating: ReviewRating

        Returns:
            New ease factor (minimum 1.3)

        Time Complexity: O(1)
        """
        if rating == ReviewRating.AGAIN:
            new_ease = current_ease - self.EASE_PENALTY
        elif rating == ReviewRating.HARD:
            new_ease = current_ease - (self.EASE_PENALTY * 0.75)
        elif rating == ReviewRating.GOOD:
            new_ease = current_ease
        else:  # EASY
            new_ease = current_ease + self.EASE_BONUS

        return max(new_ease, self.MIN_EASE)

    def _handle_new_card(self, rating: ReviewRating, repetitions: int) -> Tuple[float, int]:
        """
        Handle scheduling for new or relearning cards.

        New cards go through learning steps before graduating:
        1. First step: 1 minute
        2. Second step: 10 minutes
        3. Graduate to daily reviews

        Args:
            rating: ReviewRating
            repetitions: Current repetition count

        Returns:
            Tuple of (interval_days, new_repetitions)

        Time Complexity: O(1)
        """
        if rating == ReviewRating.EASY:
            # Skip learning steps
            return self.EASY_INTERVAL, 1
        elif rating == ReviewRating.GOOD:
            # Graduate to daily reviews
            return self.GRADUATING_INTERVAL, 1
        else:
            # Stay in learning (convert minutes to days)
            step_index = min(repetitions, len(self.LEARNING_STEPS) - 1)
            interval_minutes = self.LEARNING_STEPS[step_index]
            return interval_minutes / (24 * 60), repetitions + 1

    def _calculate_review_interval(
        self,
        current_interval: float,
        ease_factor: float,
        rating: ReviewRating,
        repetitions: int,
    ) -> float:
        """
        Calculate review interval for mature cards.

        SM-2 interval calculation:
        - HARD: interval * 1.2
        - GOOD: interval * ease_factor
        - EASY: interval * ease_factor * 1.3

        Args:
            current_interval: Current interval in days
            ease_factor: Current ease factor
            rating: ReviewRating
            repetitions: Current repetition count

        Returns:
            New interval in days

        Time Complexity: O(1)
        """
        if rating == ReviewRating.HARD:
            new_interval = current_interval * 1.2
        elif rating == ReviewRating.GOOD:
            new_interval = current_interval * ease_factor
        else:  # EASY
            new_interval = current_interval * ease_factor * 1.3

        # Enforce minimum and maximum intervals
        new_interval = max(new_interval, 1)  # Minimum 1 day
        new_interval = min(new_interval, 365)  # Maximum 1 year

        return new_interval

    def record_review(
        self,
        flashcard: Flashcard,
        rating: ReviewRating,
        response_time_ms: int,
    ) -> Flashcard:
        """
        Record a review and update flashcard state.

        Updates:
        - Next review date
        - Ease factor
        - Repetition count
        - Review history
        - Lapse count (if failed)
        - Leech status (if lapses >= threshold)

        Args:
            flashcard: Flashcard being reviewed
            rating: ReviewRating given
            response_time_ms: Response time in milliseconds

        Returns:
            Updated flashcard

        Time Complexity: O(1)
        Space Complexity: O(1) amortized (history append)

        Examples:
            >>> sm2 = SM2SpacedRepetition()
            >>> updated_card = sm2.record_review(card, ReviewRating.GOOD, 2500)
            >>> updated_card.sr_data.next_review  # Updated review date
            >>> updated_card.sr_data.repetitions  # Incremented
        """
        sr_data = flashcard.sr_data
        old_interval = sr_data.interval_days
        old_ease = sr_data.ease_factor

        # Calculate new values
        next_review, new_ease = self.calculate_next_review(
            flashcard, rating, response_time_ms
        )
        new_interval = (next_review - date.today()).days

        # Update SR data
        sr_data.last_review = date.today()
        sr_data.next_review = next_review
        sr_data.ease_factor = new_ease
        sr_data.interval_days = new_interval

        # Update repetitions
        if rating == ReviewRating.AGAIN:
            sr_data.repetitions = 0
            sr_data.lapses += 1
            # Check for leech
            if sr_data.lapses >= self.LEECH_THRESHOLD:
                sr_data.is_leech = True
        else:
            sr_data.repetitions += 1

        # Record in history
        history_entry = ReviewHistory(
            date=datetime.now(timezone.utc),
            rating=rating,
            response_time_ms=response_time_ms,
            interval_before=old_interval,
            interval_after=new_interval,
            ease_before=old_ease,
            ease_after=new_ease,
        )
        sr_data.history.append(history_entry)

        # Update flashcard timestamp
        flashcard.updated_at = datetime.now(timezone.utc)

        return flashcard

    def get_due_cards(
        self,
        flashcards: list[Flashcard],
        max_new: int = 20,
        max_reviews: int = 100,
    ) -> Tuple[list[Flashcard], list[Flashcard]]:
        """
        Get cards due for review, separated into new and review.

        Args:
            flashcards: List of all flashcards
            max_new: Maximum new cards to return
            max_reviews: Maximum review cards to return

        Returns:
            Tuple of (new_cards, review_cards)

        Time Complexity: O(n) where n is number of flashcards
        Space Complexity: O(n) for filtered lists
        """
        new_cards = []
        review_cards = []

        for card in flashcards:
            if card.suspended:
                continue

            if card.is_new and len(new_cards) < max_new:
                new_cards.append(card)
            elif card.is_due and not card.is_new and len(review_cards) < max_reviews:
                review_cards.append(card)

        return new_cards, review_cards
