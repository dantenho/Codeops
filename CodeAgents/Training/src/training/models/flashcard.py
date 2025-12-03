"""
[CREATE] Flashcard and Spaced Repetition Models

Implements SM-2 algorithm data structures.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:00:00Z
"""

from __future__ import annotations

from datetime import datetime, date, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, computed_field


class FlashcardCategory(str, Enum):
    """Categories of flashcards."""
    SYNTAX = "syntax"
    CONCEPT = "concept"
    PATTERN = "pattern"
    IDIOM = "idiom"
    STDLIB = "stdlib"
    ARCHITECTURE = "architecture"


class ReviewRating(int, Enum):
    """SM-2 review ratings."""
    AGAIN = 0   # Complete failure
    HARD = 1    # Correct but difficult
    GOOD = 2    # Correct with moderate effort
    EASY = 3    # Effortless recall


class ReviewHistory(BaseModel):
    """Record of a single review."""
    date: datetime
    rating: ReviewRating
    interval_before: float
    interval_after: float
    ease_before: float
    ease_after: float


class SpacedRepetitionData(BaseModel):
    """SM-2 algorithm state for a flashcard."""
    interval_days: float = 0
    ease_factor: float = 2.5
    repetitions: int = 0
    next_review: date = Field(default_factory=date.today)
    history: List[ReviewHistory] = Field(default_factory=list)
    lapses: int = 0
    is_leech: bool = False


class FlashcardFront(BaseModel):
    """Front side of a flashcard (question)."""
    question: str
    code_snippet: Optional[str] = None
    hints: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None


class FlashcardBack(BaseModel):
    """Back side of a flashcard (answer)."""
    answer: str
    explanation: str
    related_concepts: List[str] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)


class Flashcard(BaseModel):
    """
    [CREATE] Complete flashcard with spaced repetition data.

    Represents a single learning unit with question/answer
    and SM-2 scheduling information.
    """
    card_id: str
    deck_id: str
    category: FlashcardCategory
    front: FlashcardFront
    back: FlashcardBack
    sr_data: SpacedRepetitionData = Field(default_factory=SpacedRepetitionData)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    suspended: bool = False

    @computed_field
    @property
    def is_due(self) -> bool:
        """Check if card is due for review."""
        return date.today() >= self.sr_data.next_review

    @computed_field
    @property
    def is_new(self) -> bool:
        """Check if card has never been reviewed."""
        return self.sr_data.repetitions == 0

    @computed_field
    @property
    def maturity(self) -> str:
        """Get maturity level based on interval."""
        if self.sr_data.interval_days < 21:
            return "learning"
        elif self.sr_data.interval_days < 90:
            return "young"
        else:
            return "mature"


class FlashcardDeck(BaseModel):
    """Collection of flashcards with metadata."""
    deck_id: str
    name: str
    description: str
    level: int = Field(..., ge=1, le=5)
    cards: List[Flashcard] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @computed_field
    @property
    def total_cards(self) -> int:
        return len(self.cards)

    @computed_field
    @property
    def due_cards(self) -> int:
        return sum(1 for c in self.cards if c.is_due and not c.suspended)

    @computed_field
    @property
    def new_cards(self) -> int:
        return sum(1 for c in self.cards if c.is_new and not c.suspended)
