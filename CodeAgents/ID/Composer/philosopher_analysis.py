"""
[CREATE] The Philosopher - Critical Analysis and Scoring System

Provides deep philosophical analysis, critical thinking, scoring,
and improvement suggestions for skeleton structures.

Agent: Composer
Timestamp: 2025-12-03T19-06-12Z
Operation: [CREATE]
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("composer.philosopher")


class QualityDimension(Enum):
    """
    [CREATE] Dimensions for quality assessment.

    Represents different aspects of skeleton quality
    that can be evaluated and scored.

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """

    STRUCTURE = auto()
    COMPLETENESS = auto()
    ORGANIZATION = auto()
    DOCUMENTATION = auto()
    CONSISTENCY = auto()
    MAINTAINABILITY = auto()
    SCALABILITY = auto()
    INNOVATION = auto()


@dataclass
class CriticalAnalysis:
    """
    [CREATE] Comprehensive critical analysis of a skeleton.

    Contains philosophical insights, scores, critiques,
    and improvement suggestions.

    Attributes:
        skeleton_id (str): Identifier for the skeleton
        overall_score (float): 0.0-100.0 overall quality score
        dimension_scores (Dict[QualityDimension, float]): Scores per dimension
        strengths (List[str]): Identified strengths
        weaknesses (List[str]): Identified weaknesses
        philosophical_insights (List[str]): Deep insights and observations
        improvement_suggestions (List[str]): Actionable improvement ideas
        critical_questions (List[str]): Unanswered philosophical questions
        thinking_process (List[str]): Reasoning steps taken

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """

    skeleton_id: str
    overall_score: float = 0.0
    dimension_scores: Dict[QualityDimension, float] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    philosophical_insights: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    critical_questions: List[str] = field(default_factory=list)
    thinking_process: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        [CREATE] Convert to dictionary for serialization.

        Returns:
            Dict[str, Any]: Dictionary representation

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        return {
            "skeleton_id": self.skeleton_id,
            "overall_score": self.overall_score,
            "dimension_scores": {dim.name: score for dim, score in self.dimension_scores.items()},
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "philosophical_insights": self.philosophical_insights,
            "improvement_suggestions": self.improvement_suggestions,
            "critical_questions": self.critical_questions,
            "thinking_process": self.thinking_process,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }


class Philosopher:
    """
    [CREATE] The Philosopher - Critical analysis engine.

    Performs deep philosophical analysis of skeleton structures,
    evaluating them across multiple dimensions and providing
    critical insights and improvement suggestions.

    Attributes:
        analysis_history (List[CriticalAnalysis]): Past analyses

    Example:
        >>> philosopher = Philosopher()
        >>> analysis = philosopher.analyze_skeleton(skeleton_metadata)
        >>> print(f"Score: {analysis.overall_score}")
        >>> for insight in analysis.philosophical_insights:
        ...     print(f"Insight: {insight}")

    Design Pattern: Strategy Pattern for different analysis approaches

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """

    def __init__(self) -> None:
        """
        [CREATE] Initialize the philosopher.

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        self.analysis_history: List[CriticalAnalysis] = []
        logger.info("Philosopher initialized")

    def analyze_skeleton(
        self,
        skeleton_metadata: Any,  # SkeletonMetadata from finder
        context: Optional[Dict[str, Any]] = None
    ) -> CriticalAnalysis:
        """
        [CREATE] Perform comprehensive philosophical analysis.

        Args:
            skeleton_metadata: Skeleton metadata from finder
            context (Optional[Dict[str, Any]]): Additional context

        Returns:
            CriticalAnalysis: Complete analysis with scores and insights

        Algorithm:
            1. Evaluate structure and organization
            2. Assess completeness and consistency
            3. Analyze documentation quality
            4. Consider maintainability and scalability
            5. Identify strengths and weaknesses
            6. Generate philosophical insights
            7. Propose improvements
            8. Formulate critical questions

        Complexity:
            Time: O(n) where n is components to analyze
            Space: O(n) for analysis results

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        analysis = CriticalAnalysis(skeleton_id=f"{skeleton_metadata.agent_id}_{skeleton_metadata.timestamp}")

        # Thinking process
        analysis.thinking_process.append(
            f"[THINKING] Beginning analysis of {skeleton_metadata.agent_id} skeleton"
        )

        # Evaluate each dimension
        structure_score = self._evaluate_structure(skeleton_metadata, analysis)
        completeness_score = self._evaluate_completeness(skeleton_metadata, analysis)
        organization_score = self._evaluate_organization(skeleton_metadata, analysis)
        documentation_score = self._evaluate_documentation(skeleton_metadata, analysis)
        consistency_score = self._evaluate_consistency(skeleton_metadata, analysis)
        maintainability_score = self._evaluate_maintainability(skeleton_metadata, analysis)
        scalability_score = self._evaluate_scalability(skeleton_metadata, analysis)
        innovation_score = self._evaluate_innovation(skeleton_metadata, analysis)

        # Store dimension scores
        analysis.dimension_scores[QualityDimension.STRUCTURE] = structure_score
        analysis.dimension_scores[QualityDimension.COMPLETENESS] = completeness_score
        analysis.dimension_scores[QualityDimension.ORGANIZATION] = organization_score
        analysis.dimension_scores[QualityDimension.DOCUMENTATION] = documentation_score
        analysis.dimension_scores[QualityDimension.CONSISTENCY] = consistency_score
        analysis.dimension_scores[QualityDimension.MAINTAINABILITY] = maintainability_score
        analysis.dimension_scores[QualityDimension.SCALABILITY] = scalability_score
        analysis.dimension_scores[QualityDimension.INNOVATION] = innovation_score

        # Calculate weighted overall score
        weights = {
            QualityDimension.STRUCTURE: 0.15,
            QualityDimension.COMPLETENESS: 0.20,
            QualityDimension.ORGANIZATION: 0.15,
            QualityDimension.DOCUMENTATION: 0.10,
            QualityDimension.CONSISTENCY: 0.15,
            QualityDimension.MAINTAINABILITY: 0.10,
            QualityDimension.SCALABILITY: 0.10,
            QualityDimension.INNOVATION: 0.05
        }

        analysis.overall_score = sum(
            analysis.dimension_scores[dim] * weight
            for dim, weight in weights.items()
        )

        # Generate philosophical insights
        self._generate_philosophical_insights(skeleton_metadata, analysis)

        # Formulate critical questions
        self._formulate_critical_questions(skeleton_metadata, analysis)

        # Store in history
        self.analysis_history.append(analysis)

        logger.info(f"Analysis complete: {analysis.skeleton_id} scored {analysis.overall_score:.2f}")

        return analysis

    def _evaluate_structure(self, metadata: Any, analysis: CriticalAnalysis) -> float:
        """
        [CREATE] Evaluate structural quality.

        Returns:
            float: Score 0.0-100.0

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        score = metadata.completeness_score * 100

        if metadata.directory_count >= 6:
            analysis.strengths.append("Complete directory structure present")
        else:
            analysis.weaknesses.append(f"Missing {6 - metadata.directory_count} required directories")

        return score

    def _evaluate_completeness(self, metadata: Any, analysis: CriticalAnalysis) -> float:
        """
        [CREATE] Evaluate completeness.

        Returns:
            float: Score 0.0-100.0

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        score = metadata.completeness_score * 100

        if not metadata.missing_components:
            analysis.strengths.append("All required components present")
        else:
            analysis.weaknesses.append(f"Missing components: {', '.join(metadata.missing_components)}")

        if metadata.file_count > 0:
            analysis.strengths.append(f"Contains {metadata.file_count} files (not empty)")
        else:
            analysis.weaknesses.append("Skeleton appears empty (no files)")

        return score

    def _evaluate_organization(self, metadata: Any, analysis: CriticalAnalysis) -> float:
        """
        [CREATE] Evaluate organizational quality.

        Returns:
            float: Score 0.0-100.0

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        # Base score from structure
        score = 70.0

        # Check timestamp format
        if "T" in metadata.timestamp and "Z" in metadata.timestamp:
            score += 10
            analysis.strengths.append("Proper ISO 8601 timestamp format")
        else:
            analysis.weaknesses.append("Timestamp format may be non-standard")

        # Check path organization
        if "ID" in str(metadata.path) or "Structures" in str(metadata.path):
            score += 10
            analysis.strengths.append("Follows standard organizational pattern")

        # Check file distribution
        if metadata.file_count > 5:
            score += 10

        return min(100.0, score)

    def _evaluate_documentation(self, metadata: Any, analysis: CriticalAnalysis) -> float:
        """
        [CREATE] Evaluate documentation quality.

        Returns:
            float: Score 0.0-100.0

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        score = 50.0  # Base score

        # Check for README files
        readme_count = sum(1 for _ in metadata.path.rglob("README.md"))
        if readme_count > 0:
            score += min(30, readme_count * 10)
            analysis.strengths.append(f"Contains {readme_count} README files")
        else:
            analysis.weaknesses.append("No README documentation found")

        # Check for code documentation
        py_files = list(metadata.path.rglob("*.py"))
        if py_files:
            score += 20

        return min(100.0, score)

    def _evaluate_consistency(self, metadata: Any, analysis: CriticalAnalysis) -> float:
        """
        [CREATE] Evaluate consistency with standards.

        Returns:
            float: Score 0.0-100.0

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        score = 80.0  # Assume consistency unless proven otherwise

        if metadata.missing_components:
            score -= len(metadata.missing_components) * 10

        return max(0.0, min(100.0, score))

    def _evaluate_maintainability(self, metadata: Any, analysis: CriticalAnalysis) -> float:
        """
        [CREATE] Evaluate maintainability.

        Returns:
            float: Score 0.0-100.0

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        score = 60.0

        # Timestamp enables versioning
        if metadata.timestamp:
            score += 20
            analysis.strengths.append("Timestamp enables temporal tracking")

        # Organized structure aids maintenance
        if metadata.directory_count >= 6:
            score += 20

        return min(100.0, score)

    def _evaluate_scalability(self, metadata: Any, analysis: CriticalAnalysis) -> float:
        """
        [CREATE] Evaluate scalability potential.

        Returns:
            float: Score 0.0-100.0

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        score = 70.0

        # Modular structure supports scaling
        if metadata.directory_count >= 6:
            score += 15

        # Database schema suggests scalability
        if (metadata.path / "database" / "schema.sql").exists():
            score += 15

        return min(100.0, score)

    def _evaluate_innovation(self, metadata: Any, analysis: CriticalAnalysis) -> float:
        """
        [CREATE] Evaluate innovation and uniqueness.

        Returns:
            float: Score 0.0-100.0

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        score = 50.0  # Base score

        # Check for custom implementations
        if metadata.file_count > 10:
            score += 20

        # Check for non-standard additions
        all_dirs = {d.name for d in metadata.path.iterdir() if d.is_dir()}
        standard_dirs = {"training", "rules", "methods", "files", "database", "memory"}
        custom_dirs = all_dirs - standard_dirs

        if custom_dirs:
            score += len(custom_dirs) * 10
            analysis.strengths.append(f"Contains custom directories: {', '.join(custom_dirs)}")

        return min(100.0, score)

    def _generate_philosophical_insights(self, metadata: Any, analysis: CriticalAnalysis) -> None:
        """
        [CREATE] Generate deep philosophical insights.

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        insights = []

        # Structure philosophy
        insights.append(
            "[INSIGHT] The skeleton structure represents a form of digital ontology - "
            "a classification system that defines what an agent 'is' and 'has'"
        )

        # Completeness philosophy
        if metadata.completeness_score < 0.5:
            insights.append(
                "[INSIGHT] Incomplete skeletons raise questions about the nature of "
                "existence - can a skeleton 'be' if it lacks essential components?"
            )
        else:
            insights.append(
                "[INSIGHT] Complete skeletons demonstrate the power of standardization - "
                "predictable structures enable systematic reasoning"
            )

        # Temporal philosophy
        insights.append(
            "[INSIGHT] Timestamp-based versioning embodies the Heraclitean principle - "
            "no skeleton can be analyzed twice, as each moment is unique"
        )

        # Organization philosophy
        insights.append(
            "[INSIGHT] The six-directory structure (training/rules/methods/files/database/memory) "
            "mirrors cognitive architecture - separating learning, constraints, actions, "
            "artifacts, state, and experience"
        )

        analysis.philosophical_insights.extend(insights)

    def _formulate_critical_questions(self, metadata: Any, analysis: CriticalAnalysis) -> None:
        """
        [CREATE] Formulate critical philosophical questions.

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        questions = []

        questions.append(
            "[QUESTION] How does skeleton completeness correlate with agent effectiveness?"
        )

        questions.append(
            "[QUESTION] What is the optimal balance between standardization and customization?"
        )

        questions.append(
            "[QUESTION] Can we predict skeleton evolution patterns over time?"
        )

        if metadata.missing_components:
            questions.append(
                f"[QUESTION] Why are {', '.join(metadata.missing_components)} missing? "
                "Is this intentional or an oversight?"
            )

        analysis.critical_questions.extend(questions)

        # Generate improvement suggestions
        if metadata.missing_components:
            for component in metadata.missing_components:
                analysis.improvement_suggestions.append(
                    f"Add missing {component}/ directory with appropriate structure"
                )

        if metadata.file_count == 0:
            analysis.improvement_suggestions.append(
                "Populate skeleton with initial files and documentation"
            )

        if metadata.completeness_score < 0.8:
            analysis.improvement_suggestions.append(
                "Increase completeness by adding missing standard components"
            )


def create_philosopher() -> Philosopher:
    """
    [CREATE] Factory function to create philosopher instance.

    Returns:
        Philosopher: Configured philosopher instance

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """
    return Philosopher()
