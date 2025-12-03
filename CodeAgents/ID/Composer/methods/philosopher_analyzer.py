"""
[CREATE] Philosopher - Critical Analysis Framework

Provides critical thinking, evaluation, scoring, and improvement suggestions
for skeleton structures and agent performance. Implements philosophical
reflection and deep analysis.

Agent: Composer
Timestamp: 2025-12-03T19:15:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("composer.philosopher")


class QualityLevel(Enum):
    """
    [CREATE] Quality assessment levels.

    Agent: Composer
    Timestamp: 2025-12-03T19:15:00Z
    """
    EXCELLENT = auto()
    GOOD = auto()
    ADEQUATE = auto()
    NEEDS_IMPROVEMENT = auto()
    POOR = auto()


@dataclass
class CriticalAnalysis:
    """
    [CREATE] Critical analysis result.

    Contains scores, annotations, improvements, and philosophical reflections.

    Attributes:
        subject (str): What is being analyzed.
        overall_score (float): Overall quality score (0-100).
        quality_level (QualityLevel): Categorical quality assessment.
        strengths (List[str]): Identified strengths.
        weaknesses (List[str]): Identified weaknesses.
        improvements (List[str]): Suggested improvements.
        annotations (List[str]): Critical annotations and thoughts.
        philosophical_reflection (str): Deep philosophical reflection.
        timestamp (datetime): When analysis was performed.

    Agent: Composer
    Timestamp: 2025-12-03T19:15:00Z
    """
    subject: str
    overall_score: float
    quality_level: QualityLevel
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    philosophical_reflection: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PhilosopherAnalyzer:
    """
    [CREATE] Philosopher analyzer for critical evaluation.

    Performs deep critical analysis with scoring, annotations,
    and improvement suggestions. Implements philosophical thinking
    about structure, quality, and design.

    Attributes:
        min_score (float): Minimum acceptable score threshold.
        max_score (float): Maximum possible score.

    Example:
        >>> philosopher = PhilosopherAnalyzer()
        >>> analysis = philosopher.analyze_skeleton(skeleton_data)
        >>> print(f"Score: {analysis.overall_score}/100")

    Complexity:
        Time: O(n) where n is components analyzed
        Space: O(n) for analysis results

    Agent: Composer
    Timestamp: 2025-12-03T19:15:00Z
    """

    def __init__(self, min_score: float = 0.0, max_score: float = 100.0):
        """
        [CREATE] Initialize philosopher analyzer.

        Args:
            min_score (float): Minimum score threshold.
                Default: 0.0.
            max_score (float): Maximum score threshold.
                Default: 100.0.

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        self.min_score = min_score
        self.max_score = max_score
        logger.info("Philosopher analyzer initialized")

    def analyze_skeleton(
        self,
        skeleton_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> CriticalAnalysis:
        """
        [CREATE] Perform critical analysis of a skeleton structure.

        Args:
            skeleton_data (Dict[str, Any]): Skeleton information from finder.
            context (Optional[Dict[str, Any]]): Additional context.
                Default: None.

        Returns:
            CriticalAnalysis: Complete critical analysis result.

        Analysis Dimensions:
            1. Completeness: Are all components present?
            2. Quality: Are files well-structured?
            3. Consistency: Does structure follow standards?
            4. Utility: Is structure actually used?
            5. Evolution: Does it show growth?

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        subject = f"Skeleton: {skeleton_data.get('agent_id', 'Unknown')} - {skeleton_data.get('timestamp', 'Unknown')}"

        # Calculate scores for different dimensions
        completeness_score = self._score_completeness(skeleton_data)
        quality_score = self._score_quality(skeleton_data)
        consistency_score = self._score_consistency(skeleton_data)
        utility_score = self._score_utility(skeleton_data)

        # Weighted overall score
        overall_score = (
            completeness_score * 0.30 +
            quality_score * 0.25 +
            consistency_score * 0.25 +
            utility_score * 0.20
        )

        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)

        # Generate analysis components
        strengths = self._identify_strengths(skeleton_data, {
            "completeness": completeness_score,
            "quality": quality_score,
            "consistency": consistency_score,
            "utility": utility_score,
        })

        weaknesses = self._identify_weaknesses(skeleton_data, {
            "completeness": completeness_score,
            "quality": quality_score,
            "consistency": consistency_score,
            "utility": utility_score,
        })

        improvements = self._suggest_improvements(skeleton_data, weaknesses)

        annotations = self._generate_annotations(skeleton_data, overall_score)

        philosophical_reflection = self._philosophical_reflection(
            skeleton_data, overall_score, strengths, weaknesses
        )

        return CriticalAnalysis(
            subject=subject,
            overall_score=overall_score,
            quality_level=quality_level,
            strengths=strengths,
            weaknesses=weaknesses,
            improvements=improvements,
            annotations=annotations,
            philosophical_reflection=philosophical_reflection,
        )

    def _score_completeness(self, skeleton_data: Dict[str, Any]) -> float:
        """
        [CREATE] Score completeness of skeleton structure.

        Args:
            skeleton_data (Dict[str, Any]): Skeleton information.

        Returns:
            float: Completeness score (0-100).

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        components = skeleton_data.get("components", {})
        required_components = ["training", "rules", "methods", "files", "database", "memory"]

        present_count = sum(1 for comp in required_components if components.get(comp, False))
        completeness_ratio = present_count / len(required_components)

        # Check key files
        key_files = skeleton_data.get("key_files", {})
        key_files_present = sum(1 for exists in key_files.values() if exists)
        key_files_ratio = key_files_present / len(key_files) if key_files else 0.5

        # Combined score
        score = (completeness_ratio * 0.7 + key_files_ratio * 0.3) * 100
        return min(100.0, max(0.0, score))

    def _score_quality(self, skeleton_data: Dict[str, Any]) -> float:
        """
        [CREATE] Score quality of skeleton structure.

        Args:
            skeleton_data (Dict[str, Any]): Skeleton information.

        Returns:
            float: Quality score (0-100).

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        file_counts = skeleton_data.get("file_counts", {})
        total_files = skeleton_data.get("total_files", 0)

        # Quality indicators:
        # - Has actual content (files > 0)
        # - Balanced distribution across components
        # - Not just placeholders

        if total_files == 0:
            return 20.0  # Just placeholders

        # Check for balanced distribution
        non_zero_components = sum(1 for count in file_counts.values() if count > 0)
        balance_score = (non_zero_components / len(file_counts)) * 100 if file_counts else 50.0

        # Content richness (more files = better, but with diminishing returns)
        content_score = min(100.0, total_files * 5.0)

        return (balance_score * 0.6 + content_score * 0.4)

    def _score_consistency(self, skeleton_data: Dict[str, Any]) -> float:
        """
        [CREATE] Score consistency with standards.

        Args:
            skeleton_data (Dict[str, Any]): Skeleton information.

        Returns:
            float: Consistency score (0-100).

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        # Check if structure follows expected patterns
        # - Has proper timestamp format
        # - Follows naming conventions
        # - Has expected directory structure

        score = 80.0  # Base score for following structure

        timestamp = skeleton_data.get("timestamp", "")
        if timestamp and "T" in timestamp and "Z" in timestamp:
            score += 10.0  # Proper timestamp format

        path = skeleton_data.get("path", "")
        if "CodeAgents/ID" in path or "Structures" in path:
            score += 10.0  # Proper location

        return min(100.0, score)

    def _score_utility(self, skeleton_data: Dict[str, Any]) -> float:
        """
        [CREATE] Score utility and actual usage.

        Args:
            skeleton_data (Dict[str, Any]): Skeleton information.

        Returns:
            float: Utility score (0-100).

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        # Check if skeleton is actually being used
        # - Has non-template files
        # - Has actual content in memory/
        # - Has training progress

        file_counts = skeleton_data.get("file_counts", {})
        is_template = skeleton_data.get("is_template", False)

        if is_template:
            return 50.0  # Templates are less "used"

        # Check for actual usage indicators
        memory_files = file_counts.get("memory", 0)
        training_files = file_counts.get("training", 0)
        methods_files = file_counts.get("methods", 0)

        usage_score = 0.0
        if memory_files > 1:  # More than just README
            usage_score += 30.0
        if training_files > 1:
            usage_score += 30.0
        if methods_files > 1:
            usage_score += 40.0

        return min(100.0, usage_score)

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """
        [CREATE] Determine quality level from score.

        Args:
            score (float): Overall score.

        Returns:
            QualityLevel: Quality level enum.

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.ADEQUATE
        elif score >= 40:
            return QualityLevel.NEEDS_IMPROVEMENT
        else:
            return QualityLevel.POOR

    def _identify_strengths(
        self,
        skeleton_data: Dict[str, Any],
        dimension_scores: Dict[str, float]
    ) -> List[str]:
        """
        [CREATE] Identify strengths in skeleton structure.

        Args:
            skeleton_data (Dict[str, Any]): Skeleton information.
            dimension_scores (Dict[str, float]): Scores by dimension.

        Returns:
            List[str]: List of identified strengths.

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        strengths = []

        if dimension_scores.get("completeness", 0) >= 80:
            strengths.append("Complete structure with all required components")

        if dimension_scores.get("consistency", 0) >= 85:
            strengths.append("Follows established standards and conventions")

        file_counts = skeleton_data.get("file_counts", {})
        total_files = skeleton_data.get("total_files", 0)
        if total_files > 10:
            strengths.append(f"Rich content with {total_files} files")

        components = skeleton_data.get("components", {})
        if all(components.values()):
            strengths.append("All component directories present")

        return strengths

    def _identify_weaknesses(
        self,
        skeleton_data: Dict[str, Any],
        dimension_scores: Dict[str, float]
    ) -> List[str]:
        """
        [CREATE] Identify weaknesses in skeleton structure.

        Args:
            skeleton_data (Dict[str, Any]): Skeleton information.
            dimension_scores (Dict[str, float]): Scores by dimension.

        Returns:
            List[str]: List of identified weaknesses.

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        weaknesses = []

        if dimension_scores.get("completeness", 0) < 70:
            weaknesses.append("Missing required components or key files")

        if dimension_scores.get("utility", 0) < 50:
            weaknesses.append("Structure appears unused or minimal")

        file_counts = skeleton_data.get("file_counts", {})
        total_files = skeleton_data.get("total_files", 0)
        if total_files < 5:
            weaknesses.append("Very few files - mostly placeholders")

        if skeleton_data.get("is_template", False):
            weaknesses.append("Template structure - needs actual implementation")

        return weaknesses

    def _suggest_improvements(
        self,
        skeleton_data: Dict[str, Any],
        weaknesses: List[str]
    ) -> List[str]:
        """
        [CREATE] Suggest improvements based on weaknesses.

        Args:
            skeleton_data (Dict[str, Any]): Skeleton information.
            weaknesses (List[str]): Identified weaknesses.

        Returns:
            List[str]: List of improvement suggestions.

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        improvements = []

        if "Missing required components" in str(weaknesses):
            improvements.append("Add missing component directories and placeholder files")

        if "appears unused" in str(weaknesses).lower():
            improvements.append("Populate structure with actual content and usage")

        if "Very few files" in str(weaknesses):
            improvements.append("Expand beyond placeholders - add real implementations")

        file_counts = skeleton_data.get("file_counts", {})
        if file_counts.get("memory", 0) < 2:
            improvements.append("Add reflections and knowledge to memory/ directory")

        if file_counts.get("methods", 0) < 2:
            improvements.append("Implement actual methods beyond templates")

        return improvements

    def _generate_annotations(
        self,
        skeleton_data: Dict[str, Any],
        overall_score: float
    ) -> List[str]:
        """
        [CREATE] Generate critical annotations.

        Args:
            skeleton_data (Dict[str, Any]): Skeleton information.
            overall_score (float): Overall score.

        Returns:
            List[str]: List of annotations.

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        annotations = []

        agent_id = skeleton_data.get("agent_id", "Unknown")
        timestamp = skeleton_data.get("timestamp", "Unknown")

        annotations.append(f"Analyzing skeleton for agent '{agent_id}' created at {timestamp}")

        if overall_score >= 80:
            annotations.append("This skeleton demonstrates good structure and organization")
        elif overall_score >= 60:
            annotations.append("Skeleton is adequate but has room for improvement")
        else:
            annotations.append("Skeleton needs significant work to meet quality standards")

        is_template = skeleton_data.get("is_template", False)
        if is_template:
            annotations.append("Note: This is a template structure - actual usage may differ")

        return annotations

    def _philosophical_reflection(
        self,
        skeleton_data: Dict[str, Any],
        overall_score: float,
        strengths: List[str],
        weaknesses: List[str]
    ) -> str:
        """
        [CREATE] Generate philosophical reflection.

        Args:
            skeleton_data (Dict[str, Any]): Skeleton information.
            overall_score (float): Overall score.
            strengths (List[str]): Identified strengths.
            weaknesses (List[str]): Identified weaknesses.

        Returns:
            str: Philosophical reflection text.

        Agent: Composer
        Timestamp: 2025-12-03T19:15:00Z
        """
        reflection = f"""
        In contemplating this skeleton structure, I am reminded that structure without
        substance is merely scaffolding. A skeleton serves as foundation, but true value
        emerges from how it is inhabited and evolved.

        With a score of {overall_score:.1f}/100, this structure {'demonstrates' if overall_score >= 70 else 'struggles with'}
        {'excellence' if overall_score >= 90 else 'adequacy' if overall_score >= 60 else 'fundamental issues'}.

        The {'strengths' if strengths else 'absence of clear strengths'} {'reveal' if strengths else 'suggests'}
        {'a thoughtful approach' if strengths else 'a need for deeper consideration'} to structure design.
        {'However, ' if weaknesses else ''}{'weaknesses highlight' if weaknesses else ''}
        {'areas requiring attention' if weaknesses else 'a solid foundation'}.

        True quality in structure emerges not from perfection at creation, but from
        continuous evolution, learning, and adaptation. A skeleton is not a destination
        but a beginning.
        """

        return reflection.strip()


def create_philosopher_analyzer() -> PhilosopherAnalyzer:
    """
    [CREATE] Factory function to create philosopher analyzer.

    Returns:
        PhilosopherAnalyzer: Configured analyzer instance.

    Agent: Composer
    Timestamp: 2025-12-03T19:15:00Z
    """
    return PhilosopherAnalyzer()
