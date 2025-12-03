"""
[CREATE] Reflex Service for Training System

Provides reflexive learning capabilities with reflection prompts,
self-assessment, and adaptive learning recommendations.

Agent: ClaudeCode
Timestamp: 2025-12-03T10:30:00Z
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import yaml

from ..models.progress import AgentProgress
from ..models.session import TrainingSession, SessionType, SessionStatus
from .config_service import ConfigService


class ReflexService:
    """
    [CREATE] Handles reflexive learning operations.

    Provides reflection prompts, self-assessment, learning pattern analysis,
    and adaptive recommendations based on agent performance.

    Agent: ClaudeCode
    Timestamp: 2025-12-03T10:30:00Z
    """

    def __init__(self, base_path: Path):
        """
        [CREATE] Initialize reflex service.

        Args:
            base_path: Base path for training system configuration

        Agent: ClaudeCode
        Timestamp: 2025-12-03T10:30:00Z
        """
        self.base_path = base_path
        self.config_service = ConfigService(base_path / "config")
        self.reflection_path = base_path / "data" / "reflections"
        self.reflection_path.mkdir(parents=True, exist_ok=True)

    def get_reflection_prompt(self, agent_id: str, context: str = "post_exercise") -> Dict[str, Any]:
        """
        [CREATE] Get appropriate reflection prompt based on context and agent progress.

        Args:
            agent_id: Agent identifier
            context: Reflection context (post_exercise, session_end, weekly_review, etc.)

        Returns:
            Dictionary containing prompt data and metadata

        Agent: ClaudeCode
        Timestamp: 2025-12-03T10:30:00Z
        """
        # Load reflection prompts configuration
        prompts_config = self.config_service.load_config("reflection_prompts.yaml")

        # Get agent progress to determine appropriate prompts
        progress = self._get_agent_progress(agent_id)
        performance_level = self._assess_performance_level(progress)

        # Select prompts based on context and performance
        context_prompts = prompts_config.get("reflection_prompts", {}).get(context, {})

        if context == "post_exercise":
            # Adaptive prompting based on performance
            if performance_level == "struggling":
                additional = prompts_config.get("adaptive_prompting", {}).get("struggling_agent", {}).get("additional_prompts", [])
                context_prompts["adaptive"] = additional
            elif performance_level == "excelling":
                additional = prompts_config.get("adaptive_prompting", {}).get("excelling_agent", {}).get("additional_prompts", [])
                context_prompts["adaptive"] = additional

        return {
            "context": context,
            "prompts": context_prompts,
            "performance_level": performance_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": agent_id
        }

    def record_reflection(self, agent_id: str, reflection_data: Dict[str, Any]) -> str:
        """
        [CREATE] Record agent reflection response.

        Args:
            agent_id: Agent identifier
            reflection_data: Reflection response data

        Returns:
            Reflection record ID

        Agent: ClaudeCode
        Timestamp: 2025-12-03T10:30:00Z
        """
        reflection_id = f"reflex_{agent_id}_{int(datetime.now(timezone.utc).timestamp())}"

        record = {
            "reflection_id": reflection_id,
            "agent_id": agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": reflection_data,
            "quality_score": self._assess_reflection_quality(reflection_data)
        }

        # Save reflection record
        reflection_file = self.reflection_path / f"{reflection_id}.json"
        with open(reflection_file, 'w') as f:
            json.dump(record, f, indent=2)

        return reflection_id

    def analyze_learning_patterns(self, agent_id: str, days: int = 30) -> Dict[str, Any]:
        """
        [CREATE] Analyze learning patterns from reflections and progress data.

        Args:
            agent_id: Agent identifier
            days: Number of days to analyze

        Returns:
            Analysis results with insights and recommendations

        Agent: ClaudeCode
        Timestamp: 2025-12-03T10:30:00Z
        """
        # Load recent reflections
        recent_reflections = self._load_recent_reflections(agent_id, days)

        # Analyze patterns
        patterns = {
            "consistency_score": self._calculate_consistency_score(recent_reflections),
            "improvement_trends": self._identify_improvement_trends(recent_reflections),
            "challenge_areas": self._identify_challenge_areas(recent_reflections),
            "strength_areas": self._identify_strength_areas(recent_reflections),
            "recommended_adjustments": self._generate_recommendations(recent_reflections)
        }

        return {
            "agent_id": agent_id,
            "analysis_period_days": days,
            "patterns": patterns,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def get_adaptive_recommendations(self, agent_id: str) -> Dict[str, Any]:
        """
        [CREATE] Generate adaptive learning recommendations based on reflex analysis.

        Args:
            agent_id: Agent identifier

        Returns:
            Recommendations for next learning session

        Agent: ClaudeCode
        Timestamp: 2025-12-03T10:30:00Z
        """
        # Analyze recent patterns
        analysis = self.analyze_learning_patterns(agent_id, days=7)

        # Generate recommendations based on analysis
        recommendations = {
            "session_type": self._recommend_session_type(analysis),
            "focus_topics": self._recommend_focus_topics(analysis),
            "difficulty_adjustment": self._recommend_difficulty_adjustment(analysis),
            "learning_strategy": self._recommend_learning_strategy(analysis),
            "estimated_duration": self._estimate_session_duration(analysis)
        }

        return {
            "agent_id": agent_id,
            "recommendations": recommendations,
            "based_on_analysis": analysis,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def _get_agent_progress(self, agent_id: str) -> Optional[AgentProgress]:
        """Get agent progress data."""
        # TODO: Implement progress loading from training manager
        return None

    def _assess_performance_level(self, progress: Optional[AgentProgress]) -> str:
        """Assess current performance level."""
        if not progress:
            return "unknown"

        # Simple assessment based on level and recent activity
        # TODO: Implement more sophisticated assessment
        if progress.current_level <= 1:
            return "beginner"
        elif progress.current_level <= 3:
            return "intermediate"
        else:
            return "advanced"

    def _assess_reflection_quality(self, reflection_data: Dict[str, Any]) -> float:
        """Assess quality of reflection response."""
        quality_score = 0.0

        # Check for specific examples
        if "examples" in str(reflection_data).lower():
            quality_score += 0.3

        # Check for self-awareness
        if any(word in str(reflection_data).lower() for word in ["i learned", "i struggled", "i improved"]):
            quality_score += 0.3

        # Check for actionable insights
        if any(word in str(reflection_data).lower() for word in ["next time", "should", "will try", "plan to"]):
            quality_score += 0.4

        return min(quality_score, 1.0)

    def _load_recent_reflections(self, agent_id: str, days: int) -> List[Dict[str, Any]]:
        """Load recent reflection records."""
        reflections = []
        cutoff_time = datetime.now(timezone.utc).timestamp() - (days * 24 * 60 * 60)

        if self.reflection_path.exists():
            for file_path in self.reflection_path.glob(f"reflex_{agent_id}_*.json"):
                try:
                    with open(file_path, 'r') as f:
                        record = json.load(f)
                        if record.get("timestamp"):
                            record_time = datetime.fromisoformat(record["timestamp"]).timestamp()
                            if record_time >= cutoff_time:
                                reflections.append(record)
                except (json.JSONDecodeError, KeyError):
                    continue

        return sorted(reflections, key=lambda x: x.get("timestamp", ""), reverse=True)

    def _calculate_consistency_score(self, reflections: List[Dict[str, Any]]) -> float:
        """Calculate learning consistency score."""
        if not reflections:
            return 0.0

        # Simple consistency based on number of reflections vs expected
        expected_reflections = len(reflections)  # Assume daily reflections
        actual_reflections = len(reflections)

        return min(actual_reflections / expected_reflections, 1.0)

    def _identify_improvement_trends(self, reflections: List[Dict[str, Any]]) -> List[str]:
        """Identify improvement trends from reflections."""
        trends = []

        # Analyze reflection content for improvement patterns
        improvement_keywords = ["better", "improved", "easier", "mastered", "confident"]
        challenge_keywords = ["struggled", "difficult", "hard", "confusing", "stuck"]

        for reflection in reflections[:5]:  # Last 5 reflections
            content = str(reflection.get("data", "")).lower()
            if any(word in content for word in improvement_keywords):
                trends.append("Positive improvement trend detected")
            elif any(word in content for word in challenge_keywords):
                trends.append("Ongoing challenges identified")

        return list(set(trends))  # Remove duplicates

    def _identify_challenge_areas(self, reflections: List[Dict[str, Any]]) -> List[str]:
        """Identify areas where agent struggles."""
        challenges = []

        # Extract challenge areas from reflection content
        challenge_indicators = ["struggled with", "difficult", "hard", "confusing", "stuck on"]

        for reflection in reflections:
            content = str(reflection.get("data", "")).lower()
            for indicator in challenge_indicators:
                if indicator in content:
                    # Extract topic/area from content (simplified)
                    challenges.append(f"Challenge with {indicator.split()[-1]}")

        return list(set(challenges))[:5]  # Limit to top 5

    def _identify_strength_areas(self, reflections: List[Dict[str, Any]]) -> List[str]:
        """Identify areas where agent excels."""
        strengths = []

        # Extract strength areas from reflection content
        strength_indicators = ["good at", "easy", "mastered", "confident with", "strong in"]

        for reflection in reflections:
            content = str(reflection.get("data", "")).lower()
            for indicator in strength_indicators:
                if indicator in content:
                    strengths.append(f"Strength in {indicator.split()[-1]}")

        return list(set(strengths))[:5]  # Limit to top 5

    def _generate_recommendations(self, reflections: List[Dict[str, Any]]) -> List[str]:
        """Generate learning recommendations based on patterns."""
        recommendations = []

        # Analyze patterns and generate recommendations
        if self._calculate_consistency_score(reflections) < 0.7:
            recommendations.append("Increase reflection frequency for better learning tracking")

        challenges = self._identify_challenge_areas(reflections)
        if challenges:
            recommendations.append(f"Focus additional practice on: {', '.join(challenges[:2])}")

        strengths = self._identify_strength_areas(reflections)
        if strengths:
            recommendations.append(f"Leverage strengths in: {', '.join(strengths[:2])}")

        return recommendations

    def _recommend_session_type(self, analysis: Dict[str, Any]) -> str:
        """Recommend appropriate session type."""
        consistency = analysis.get("patterns", {}).get("consistency_score", 0.5)

        if consistency < 0.5:
            return "foundational"  # Build basics
        elif consistency < 0.8:
            return "daily"  # Standard practice
        else:
            return "advanced"  # Push boundaries

    def _recommend_focus_topics(self, analysis: Dict[str, Any]) -> List[str]:
        """Recommend topics to focus on."""
        challenges = analysis.get("patterns", {}).get("challenge_areas", [])
        return [challenge.replace("Challenge with ", "") for challenge in challenges[:3]]

    def _recommend_difficulty_adjustment(self, analysis: Dict[str, Any]) -> str:
        """Recommend difficulty adjustment."""
        trends = analysis.get("patterns", {}).get("improvement_trends", [])

        if "Positive improvement trend detected" in trends:
            return "increase"
        elif "Ongoing challenges identified" in trends:
            return "decrease"
        else:
            return "maintain"

    def _recommend_learning_strategy(self, analysis: Dict[str, Any]) -> str:
        """Recommend learning strategy."""
        consistency = analysis.get("patterns", {}).get("consistency_score", 0.5)

        if consistency < 0.6:
            return "spaced_repetition"
        elif consistency < 0.8:
            return "interleaved_practice"
        else:
            return "deliberate_practice"

    def _estimate_session_duration(self, analysis: Dict[str, Any]) -> str:
        """Estimate recommended session duration."""
        consistency = analysis.get("patterns", {}).get("consistency_score", 0.5)

        if consistency < 0.5:
            return "30min"
        elif consistency < 0.8:
            return "45min"
        else:
            return "60min"
