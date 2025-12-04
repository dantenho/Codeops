"""
Module: metrics.py
Purpose: Agent performance metrics and evaluation for CodeAgents.

Implements the AMES (Agent Metrics & Evaluation System) scoring algorithm
for measuring and comparing AI agent performance across diverse coding tasks.

Agent: ClaudeCode
Created: 2025-12-04T12:00:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("core.metrics")


class ComplexityLevel(Enum):
    """Task complexity levels with score multipliers."""
    EASY = 1.0
    MEDIUM = 1.5
    HARD = 2.0
    COMPLEX = 3.0
    EXPERT = 4.0


class TaskType(str, Enum):
    """Types of coding tasks."""
    CREATE = "create"
    REFACTOR = "refactor"
    DEBUG = "debug"
    OPTIMIZE = "optimize"
    DOCUMENT = "document"
    ANALYZE = "analyze"


@dataclass
class MetricScores:
    """
    [CREATE] Container for all metric dimension scores.
    
    Attributes:
        accuracy: Accuracy score (0-100)
        speed: Speed score (0-100)
        quality: Quality score (0-100)
        adaptability: Adaptability score (0-100)
        reliability: Reliability score (0-100)
    """
    accuracy: float
    speed: float
    quality: float
    adaptability: float
    reliability: float

    def validate(self) -> bool:
        """Validates all scores are within 0-100 range."""
        scores = [self.accuracy, self.speed, self.quality,
                  self.adaptability, self.reliability]
        return all(0 <= s <= 100 for s in scores)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "accuracy": self.accuracy,
            "speed": self.speed,
            "quality": self.quality,
            "adaptability": self.adaptability,
            "reliability": self.reliability
        }


@dataclass
class TaskContext:
    """
    [CREATE] Context information for a coding task.
    
    Attributes:
        task_type: Type of task performed
        complexity: Difficulty level
        language: Programming language used
        lines_of_code: Total lines produced/modified
        duration_seconds: Time taken to complete
    """
    task_type: TaskType
    complexity: ComplexityLevel
    language: str
    lines_of_code: int
    duration_seconds: float


@dataclass
class EvaluationResult:
    """
    [CREATE] Result of an agent evaluation.
    
    Contains the composite score, breakdown, and contextual data.
    """
    composite_score: float
    base_score: float
    complexity_bonus: float
    language_modifier: float
    grade: str
    percentile: int
    adjusted_scores: Dict[str, float]
    context: Dict[str, Any]
    breakdown: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentEvaluator:
    """
    [CREATE] Evaluates AI coding agent performance.
    
    Implements the AMES scoring algorithm to calculate composite scores
    across multiple dimensions.
    
    Example:
        >>> evaluator = AgentEvaluator()
        >>> scores = MetricScores(
        ...     accuracy=92.5, speed=85.0, quality=88.5,
        ...     adaptability=78.0, reliability=95.0
        ... )
        >>> context = TaskContext(
        ...     task_type=TaskType.CREATE,
        ...     complexity=ComplexityLevel.HARD,
        ...     language="python",
        ...     lines_of_code=350,
        ...     duration_seconds=180.5
        ... )
        >>> result = evaluator.calculate_composite_score(scores, context)
        >>> print(f"Final Score: {result.composite_score:.2f}")
    """

    DIMENSION_WEIGHTS = {
        "accuracy": 0.25,
        "speed": 0.20,
        "quality": 0.25,
        "adaptability": 0.15,
        "reliability": 0.15
    }

    TASK_TYPE_WEIGHTS = {
        TaskType.CREATE: {"accuracy": 1.1, "quality": 1.1, "speed": 0.9},
        TaskType.REFACTOR: {"quality": 1.2, "reliability": 1.1, "speed": 0.8},
        TaskType.DEBUG: {"accuracy": 1.2, "reliability": 1.1, "speed": 1.0},
        TaskType.OPTIMIZE: {"speed": 1.2, "quality": 1.0, "accuracy": 1.0},
        TaskType.DOCUMENT: {"quality": 1.3, "accuracy": 0.9, "speed": 0.9},
        TaskType.ANALYZE: {"accuracy": 1.1, "quality": 1.1, "adaptability": 1.1}
    }

    LANGUAGE_MODIFIERS = {
        "python": 1.0,
        "javascript": 1.0,
        "typescript": 1.05,
        "go": 1.1,
        "rust": 1.2,
        "java": 1.05,
        "cpp": 1.15,
        "c": 1.2,
        "haskell": 1.25,
        "assembly": 1.5
    }

    def __init__(self) -> None:
        """Initialize the agent evaluator."""
        self.agent_history: List[EvaluationResult] = []

    def calculate_composite_score(
        self,
        scores: MetricScores,
        context: TaskContext
    ) -> EvaluationResult:
        """
        [CREATE] Calculate the composite evaluation score.
        
        Args:
            scores: Raw scores for each dimension
            context: Task context information
            
        Returns:
            EvaluationResult with composite score and breakdown
            
        Raises:
            ValueError: If scores are invalid (outside 0-100 range)
        """
        if not scores.validate():
            raise ValueError("All scores must be between 0 and 100")

        task_mods = self.TASK_TYPE_WEIGHTS.get(
            context.task_type,
            {"accuracy": 1.0, "speed": 1.0, "quality": 1.0}
        )

        adjusted_scores = {
            "accuracy": scores.accuracy * task_mods.get("accuracy", 1.0),
            "speed": scores.speed * task_mods.get("speed", 1.0),
            "quality": scores.quality * task_mods.get("quality", 1.0),
            "adaptability": scores.adaptability * task_mods.get("adaptability", 1.0),
            "reliability": scores.reliability * task_mods.get("reliability", 1.0)
        }

        base_score = sum(
            adjusted_scores[dim] * weight
            for dim, weight in self.DIMENSION_WEIGHTS.items()
        )

        complexity_bonus = self._calculate_complexity_bonus(base_score, context.complexity)

        lang_modifier = self.LANGUAGE_MODIFIERS.get(context.language.lower(), 1.0)

        final_score = min(100, (base_score + complexity_bonus) * lang_modifier)

        grade = self._score_to_grade(final_score)
        percentile = self._calculate_percentile(final_score)

        result = EvaluationResult(
            composite_score=round(final_score, 2),
            base_score=round(base_score, 2),
            complexity_bonus=round(complexity_bonus, 2),
            language_modifier=lang_modifier,
            grade=grade,
            percentile=percentile,
            adjusted_scores={k: round(v, 2) for k, v in adjusted_scores.items()},
            context={
                "task_type": context.task_type.value,
                "complexity": context.complexity.name,
                "language": context.language,
                "lines_of_code": context.lines_of_code,
                "duration_seconds": context.duration_seconds
            },
            breakdown=self._generate_breakdown(scores, adjusted_scores, context)
        )

        self.agent_history.append(result)
        return result

    def _calculate_complexity_bonus(
        self,
        base_score: float,
        complexity: ComplexityLevel
    ) -> float:
        """Calculate bonus points for task complexity."""
        if base_score < 60:
            return 0.0

        multiplier = complexity.value
        bonus = (base_score / 100) * (multiplier - 1) * 20
        return min(bonus, 20.0)

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 97: return "A+"
        elif score >= 93: return "A"
        elif score >= 90: return "A-"
        elif score >= 87: return "B+"
        elif score >= 83: return "B"
        elif score >= 80: return "B-"
        elif score >= 77: return "C+"
        elif score >= 73: return "C"
        elif score >= 70: return "C-"
        elif score >= 67: return "D+"
        elif score >= 63: return "D"
        elif score >= 60: return "D-"
        else: return "F"

    def _calculate_percentile(self, score: float) -> int:
        """Calculate percentile rank based on history."""
        if not self.agent_history:
            return 50

        historical_scores = [h.composite_score for h in self.agent_history]
        below_count = sum(1 for s in historical_scores if s < score)
        return int((below_count / len(historical_scores)) * 100)

    def _generate_breakdown(
        self,
        raw_scores: MetricScores,
        adjusted_scores: Dict[str, float],
        context: TaskContext
    ) -> Dict[str, Any]:
        """Generate detailed score breakdown."""
        return {
            "raw_scores": raw_scores.to_dict(),
            "weights_applied": self.DIMENSION_WEIGHTS,
            "task_modifiers": self.TASK_TYPE_WEIGHTS.get(context.task_type, {}),
            "contribution": {
                dim: round(adjusted_scores[dim] * weight, 2)
                for dim, weight in self.DIMENSION_WEIGHTS.items()
            }
        }

    def get_agent_summary(self, agent_name: str) -> Dict[str, Any]:
        """
        [CREATE] Generate performance summary for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dict with summary statistics and trends
        """
        if not self.agent_history:
            return {"error": "No evaluation history available"}

        scores = [h.composite_score for h in self.agent_history]

        return {
            "agent": agent_name,
            "total_evaluations": len(scores),
            "average_score": round(sum(scores) / len(scores), 2),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "latest_score": scores[-1] if scores else None,
            "trend": self._calculate_trend(scores),
            "grade_distribution": self._grade_distribution()
        }

    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate performance trend."""
        if len(scores) < 3:
            return "insufficient_data"

        recent = scores[-3:]
        avg_recent = sum(recent) / len(recent)
        avg_total = sum(scores) / len(scores)

        diff = avg_recent - avg_total

        if diff > 2: return "📈 improving"
        elif diff < -2: return "📉 declining"
        else: return "➡️ stable"

    def _grade_distribution(self) -> Dict[str, int]:
        """Calculate grade distribution from history."""
        distribution: Dict[str, int] = {}
        for entry in self.agent_history:
            grade = entry.grade
            distribution[grade] = distribution.get(grade, 0) + 1
        return distribution


# Lazy singleton
_evaluator: Optional[AgentEvaluator] = None


def get_evaluator() -> AgentEvaluator:
    """
    [CREATE] Get the singleton evaluator instance.
    
    Returns:
        AgentEvaluator: The singleton instance
    """
    global _evaluator
    if _evaluator is None:
        _evaluator = AgentEvaluator()
    return _evaluator
