"""
Vibe Session models for tracking vibe coding sessions.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class VibeConfidence(str, Enum):
    """Confidence level in pattern matching and code generation."""

    VERY_HIGH = "very_high"  # 90%+ confidence
    HIGH = "high"            # 75-90% confidence
    MEDIUM = "medium"        # 60-75% confidence
    LOW = "low"              # 40-60% confidence
    VERY_LOW = "very_low"    # <40% confidence


class VibeIntent(BaseModel):
    """Parsed intent from natural language input."""

    raw_input: str = Field(description="Original user input")

    # Parsed components
    action: str = Field(description="Primary action: create, modify, refactor, test, etc.")
    target: str = Field(description="What to act on: function, class, API, etc.")
    language: Optional[str] = Field(default=None, description="Programming language")
    framework: Optional[str] = Field(default=None, description="Framework if applicable")

    # Pattern matching
    matched_patterns: List[str] = Field(default_factory=list, description="Matched pattern IDs")
    confidence: VibeConfidence = Field(default=VibeConfidence.MEDIUM)

    # Context requirements
    requires_context: List[str] = Field(
        default_factory=list,
        description="Context types needed: db_schema, auth, models, etc."
    )

    # Extracted details
    keywords: List[str] = Field(default_factory=list)
    entities: Dict[str, str] = Field(default_factory=dict, description="Extracted entities")

    # Token budget
    estimated_complexity: str = Field(default="simple", description="simple, moderate, complex")
    recommended_token_budget: int = Field(default=1000)


class VibeContext(BaseModel):
    """Assembled context for code generation."""

    # Retrieved context pieces
    relevant_code: List[Dict] = Field(default_factory=list, description="Relevant code snippets")
    patterns: List[Dict] = Field(default_factory=list, description="Matched patterns/templates")
    agent_memory: List[Dict] = Field(default_factory=list, description="Agent's past learnings")

    # Token accounting
    total_tokens: int = 0
    token_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Tokens by source: code, patterns, memory, etc."
    )

    # Optimization metadata
    compression_applied: bool = False
    truncated_items: List[str] = Field(default_factory=list)
    cache_hits: int = 0


class VibeResult(BaseModel):
    """Result of a vibe coding operation."""

    session_id: str
    intent: VibeIntent

    # Generated output
    generated_code: str = Field(default="", description="Generated code")
    explanation: str = Field(default="", description="Explanation of the code")

    # Quality metrics
    confidence_score: float = Field(ge=0.0, le=100.0)
    estimated_quality: float = Field(default=0.0, ge=0.0, le=100.0)

    # Token usage
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

    # Context used
    context: Optional[VibeContext] = None

    # Timing
    generation_time_ms: int = 0

    # Follow-up suggestions
    next_steps: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)

    # Warnings/errors
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    @property
    def is_successful(self) -> bool:
        """Check if generation was successful."""
        return len(self.errors) == 0 and len(self.generated_code) > 0

    @property
    def needs_refinement(self) -> bool:
        """Check if result needs refinement."""
        return (
            self.confidence_score < 70
            or len(self.warnings) > 0
            or len(self.improvements) > 0
        )


class VibeSession(BaseModel):
    """A complete vibe coding session with multiple iterations."""

    session_id: str
    agent_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None

    # Session history
    iterations: List[VibeResult] = Field(default_factory=list)

    # Cumulative metrics
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0

    # Session quality
    final_quality_score: float = 0.0
    user_accepted: bool = False

    # Learning
    patterns_learned: List[str] = Field(default_factory=list)
    errors_encountered: List[str] = Field(default_factory=list)

    def add_iteration(self, result: VibeResult):
        """Add an iteration result to the session."""
        self.iterations.append(result)
        self.total_input_tokens += result.input_tokens
        self.total_output_tokens += result.output_tokens
        self.total_cost_usd += result.cost_usd

        # Update quality score (weighted toward later iterations)
        if self.iterations:
            weights = [i + 1 for i in range(len(self.iterations))]
            total_weight = sum(weights)
            self.final_quality_score = sum(
                result.estimated_quality * weight
                for result, weight in zip(self.iterations, weights)
            ) / total_weight

    @property
    def iteration_count(self) -> int:
        """Number of iterations in this session."""
        return len(self.iterations)

    @property
    def average_confidence(self) -> float:
        """Average confidence across all iterations."""
        if not self.iterations:
            return 0.0
        return sum(r.confidence_score for r in self.iterations) / len(self.iterations)

    @property
    def efficiency_score(self) -> float:
        """Quality per token spent."""
        if self.total_input_tokens + self.total_output_tokens == 0:
            return 0.0
        total_tokens = self.total_input_tokens + self.total_output_tokens
        return (self.final_quality_score / total_tokens) * 100


class VibePattern(BaseModel):
    """A code generation pattern/template."""

    pattern_id: str
    name: str
    description: str

    # Pattern matching
    intent_keywords: List[str] = Field(description="Keywords that trigger this pattern")
    language: str
    framework: Optional[str] = None

    # Requirements
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Required context: imports, models, etc."
    )

    # Template
    template: str = Field(description="Code template with placeholders")
    placeholders: List[Dict] = Field(
        default_factory=list,
        description="Placeholder definitions with types and constraints"
    )

    # Metadata
    token_cost: int = Field(description="Estimated tokens for this pattern")
    complexity: str = Field(default="simple", description="simple, moderate, complex")
    quality_score: float = Field(default=85.0, ge=0.0, le=100.0)

    # Usage statistics
    use_count: int = 0
    success_rate: float = 0.0
    avg_quality_score: float = 0.0

    # Examples
    example_input: Optional[str] = None
    example_output: Optional[str] = None

    def matches_intent(self, intent: VibeIntent) -> float:
        """
        Calculate match score for this pattern against an intent.

        Returns:
            Match score 0-100
        """
        score = 0.0

        # Language match (critical)
        if intent.language and self.language:
            if intent.language.lower() == self.language.lower():
                score += 40.0
            else:
                return 0.0  # Wrong language = no match

        # Keyword matching
        matched_keywords = set(intent.keywords) & set(self.intent_keywords)
        if self.intent_keywords:
            keyword_score = (len(matched_keywords) / len(self.intent_keywords)) * 40.0
            score += keyword_score

        # Framework match (bonus)
        if intent.framework and self.framework:
            if intent.framework.lower() == self.framework.lower():
                score += 20.0

        return min(100.0, score)
