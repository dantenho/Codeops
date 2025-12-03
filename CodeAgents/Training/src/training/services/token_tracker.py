"""
Token tracking service for monitoring and optimizing LLM token usage.

Provides real-time tracking, aggregation, and analysis of token consumption
across training sessions and operations.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

from ..models.token_metrics import (
    TokenMetrics,
    SessionTokenSummary,
    AgentTokenStats,
    TokenBudget,
    TokenOptimizationSuggestion,
    calculate_cost,
)


class TokenTracker:
    """
    Service for tracking and analyzing token usage.

    Stores metrics to disk for persistence and provides aggregation
    and analysis capabilities.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize token tracker.

        Args:
            data_dir: Directory for storing token metrics (default: ./token_metrics)
        """
        self.data_dir = Path(data_dir or "token_metrics")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory caches for current session
        self._current_session_metrics: Dict[str, List[TokenMetrics]] = defaultdict(list)
        self._session_summaries: Dict[str, SessionTokenSummary] = {}

    def record_operation(
        self,
        session_id: str,
        agent_id: str,
        operation_id: str,
        prompt_tokens: int = 0,
        context_tokens: int = 0,
        user_input_tokens: int = 0,
        completion_tokens: int = 0,
        cached_tokens: int = 0,
        output_quality_score: float = 0.0,
        context_utilization_score: float = 0.0,
        model_name: str = "claude-sonnet-4-5",
        operation_type: str = "unknown",
        language: Optional[str] = None,
    ) -> TokenMetrics:
        """
        Record token usage for a single operation.

        Args:
            session_id: Training session ID
            agent_id: Agent performing the operation
            operation_id: Unique operation identifier
            prompt_tokens: Base prompt tokens
            context_tokens: RAG-retrieved context tokens
            user_input_tokens: User query tokens
            completion_tokens: Generated output tokens
            cached_tokens: Reused cached tokens
            output_quality_score: Quality score (0-100)
            context_utilization_score: % of context used (0-100)
            model_name: LLM model used
            operation_type: Type of operation
            language: Programming language if applicable

        Returns:
            TokenMetrics object with calculated fields
        """
        # Calculate cost
        total_input = prompt_tokens + context_tokens + user_input_tokens - cached_tokens
        cost = calculate_cost(total_input, completion_tokens, model_name)

        # Create metrics object
        metrics = TokenMetrics(
            session_id=session_id,
            agent_id=agent_id,
            operation_id=operation_id,
            prompt_tokens=prompt_tokens,
            context_tokens=context_tokens,
            user_input_tokens=user_input_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
            output_quality_score=output_quality_score,
            context_utilization_score=context_utilization_score,
            cost_usd=cost,
            model_name=model_name,
            operation_type=operation_type,
            language=language,
        )

        # Store in memory
        self._current_session_metrics[session_id].append(metrics)

        # Persist to disk
        self._save_operation_metrics(metrics)

        # Update session summary
        self._update_session_summary(session_id, agent_id, metrics)

        return metrics

    def get_session_summary(self, session_id: str) -> Optional[SessionTokenSummary]:
        """
        Get aggregated token summary for a session.

        Args:
            session_id: Training session ID

        Returns:
            SessionTokenSummary or None if session not found
        """
        if session_id in self._session_summaries:
            return self._session_summaries[session_id]

        # Try loading from disk
        return self._load_session_summary(session_id)

    def get_agent_stats(
        self,
        agent_id: str,
        days: int = 30
    ) -> AgentTokenStats:
        """
        Get aggregated token statistics for an agent.

        Args:
            agent_id: Agent identifier
            days: Number of days to analyze (default: 30)

        Returns:
            AgentTokenStats with lifetime and recent statistics
        """
        stats = AgentTokenStats(agent_id=agent_id)

        # Load all metrics for agent
        metrics_list = self._load_agent_metrics(agent_id, days)

        if not metrics_list:
            return stats

        # Calculate aggregations
        sessions = set()
        total_tokens = 0
        total_input = 0
        total_output = 0
        total_cost = 0.0
        total_quality = 0.0
        total_efficiency = 0.0
        total_cache_hit = 0.0

        best_efficiency = 0.0
        best_session = None
        worst_efficiency = float("inf")
        worst_session = None

        # Daily aggregations
        daily_tokens: Dict[str, int] = defaultdict(int)
        daily_quality: Dict[str, List[float]] = defaultdict(list)

        for metric in metrics_list:
            sessions.add(metric.session_id)
            total_tokens += metric.total_tokens
            total_input += metric.total_input_tokens
            total_output += metric.total_output_tokens
            total_cost += metric.cost_usd
            total_quality += metric.output_quality_score
            total_efficiency += metric.efficiency_score

            # Track best/worst
            if metric.efficiency_score > best_efficiency:
                best_efficiency = metric.efficiency_score
                best_session = metric.session_id
            if metric.efficiency_score < worst_efficiency:
                worst_efficiency = metric.efficiency_score
                worst_session = metric.session_id

            # Daily aggregations
            day_key = metric.timestamp.date().isoformat()
            daily_tokens[day_key] += metric.total_tokens
            daily_quality[day_key].append(metric.output_quality_score)

        num_operations = len(metrics_list)
        num_sessions = len(sessions)

        # Update stats
        stats.total_sessions = num_sessions
        stats.total_operations = num_operations
        stats.lifetime_tokens = total_tokens
        stats.lifetime_input_tokens = total_input
        stats.lifetime_output_tokens = total_output
        stats.lifetime_cost_usd = total_cost

        stats.avg_tokens_per_session = total_tokens / num_sessions if num_sessions > 0 else 0
        stats.avg_tokens_per_operation = total_tokens / num_operations if num_operations > 0 else 0
        stats.avg_quality_score = total_quality / num_operations if num_operations > 0 else 0
        stats.avg_efficiency_score = total_efficiency / num_operations if num_operations > 0 else 0

        stats.best_efficiency_session = best_session
        stats.best_efficiency_score = best_efficiency
        stats.worst_efficiency_session = worst_session
        stats.worst_efficiency_score = worst_efficiency

        stats.recent_sessions = list(sessions)

        # Build trends
        for day in sorted(daily_tokens.keys()):
            stats.token_trend.append(daily_tokens[day])
            avg_quality = sum(daily_quality[day]) / len(daily_quality[day])
            stats.quality_trend.append(avg_quality)

        return stats

    def check_budget(
        self,
        metrics: TokenMetrics,
        budget: TokenBudget
    ) -> Dict[str, any]:
        """
        Check if token usage is within budget and generate warnings/suggestions.

        Args:
            metrics: Token metrics to check
            budget: Token budget configuration

        Returns:
            Dictionary with status, warnings, and suggestions
        """
        result = {
            "within_budget": budget.is_within_budget(metrics),
            "near_budget": budget.is_near_budget(metrics),
            "warnings": [],
            "suggestions": [],
        }

        # Check hard limits
        if metrics.total_tokens > budget.max_tokens:
            result["warnings"].append(
                f"Exceeded total token budget: {metrics.total_tokens} > {budget.max_tokens}"
            )

        if metrics.context_tokens > budget.max_context_tokens:
            result["warnings"].append(
                f"Exceeded context token budget: {metrics.context_tokens} > {budget.max_context_tokens}"
            )

        if metrics.completion_tokens > budget.max_completion_tokens:
            result["warnings"].append(
                f"Exceeded completion token budget: {metrics.completion_tokens} > {budget.max_completion_tokens}"
            )

        # Check soft warnings
        if budget.should_warn(metrics):
            result["warnings"].append("Exceeded warning thresholds")

        # Generate suggestions
        if metrics.context_utilization_score < 50:
            result["suggestions"].append(
                "Low context utilization - consider reducing context size"
            )

        if metrics.cache_hit_rate < 20 and budget.allow_caching:
            result["suggestions"].append(
                "Low cache hit rate - consider enabling more aggressive caching"
            )

        if metrics.output_quality_score < budget.min_quality_score:
            result["suggestions"].append(
                f"Output quality below threshold: {metrics.output_quality_score} < {budget.min_quality_score}"
            )

        return result

    def analyze_optimization_opportunities(
        self,
        session_id: str
    ) -> List[TokenOptimizationSuggestion]:
        """
        Analyze a session and generate token optimization suggestions.

        Args:
            session_id: Training session to analyze

        Returns:
            List of optimization suggestions ranked by priority
        """
        suggestions = []

        metrics_list = self._current_session_metrics.get(session_id, [])
        if not metrics_list:
            return suggestions

        # Analyze patterns
        total_context = sum(m.context_tokens for m in metrics_list)
        avg_utilization = sum(m.context_utilization_score for m in metrics_list) / len(metrics_list)

        # Suggestion 1: Reduce context if underutilized
        if avg_utilization < 40 and total_context > 1000:
            estimated_savings = int(total_context * 0.5)
            suggestions.append(
                TokenOptimizationSuggestion(
                    suggestion_id=f"{session_id}_reduce_context",
                    session_id=session_id,
                    operation_id="aggregate",
                    issue_type="underutilized_context",
                    severity="high",
                    description=f"Context utilization is low ({avg_utilization:.1f}%). Consider reducing context size.",
                    current_tokens=total_context,
                    current_cost_usd=sum(m.cost_usd for m in metrics_list),
                    current_quality_score=sum(m.output_quality_score for m in metrics_list) / len(metrics_list),
                    suggested_action="Reduce RAG context retrieval limit by 50%",
                    estimated_tokens_saved=estimated_savings,
                    estimated_cost_saved_usd=calculate_cost(estimated_savings, 0),
                    estimated_quality_impact=-5.0,  # Minimal impact expected
                    priority=1,
                    automated=True,
                )
            )

        # Suggestion 2: Enable caching for repeated patterns
        avg_cache_rate = sum(m.cache_hit_rate for m in metrics_list) / len(metrics_list)
        if avg_cache_rate < 30:
            suggestions.append(
                TokenOptimizationSuggestion(
                    suggestion_id=f"{session_id}_enable_caching",
                    session_id=session_id,
                    operation_id="aggregate",
                    issue_type="low_cache_utilization",
                    severity="medium",
                    description=f"Cache hit rate is low ({avg_cache_rate:.1f}%). Enable prompt caching.",
                    current_tokens=sum(m.total_tokens for m in metrics_list),
                    current_cost_usd=sum(m.cost_usd for m in metrics_list),
                    current_quality_score=sum(m.output_quality_score for m in metrics_list) / len(metrics_list),
                    suggested_action="Enable prompt caching for system prompts",
                    estimated_tokens_saved=int(sum(m.prompt_tokens for m in metrics_list) * 0.6),
                    estimated_cost_saved_usd=sum(m.cost_usd for m in metrics_list) * 0.3,
                    estimated_quality_impact=0.0,
                    priority=2,
                    automated=True,
                )
            )

        # Sort by priority
        suggestions.sort(key=lambda s: s.priority)

        return suggestions

    def _update_session_summary(
        self,
        session_id: str,
        agent_id: str,
        metrics: TokenMetrics
    ):
        """Update in-memory session summary with new metrics."""
        if session_id not in self._session_summaries:
            self._session_summaries[session_id] = SessionTokenSummary(
                session_id=session_id,
                agent_id=agent_id,
                start_time=metrics.timestamp,
            )

        summary = self._session_summaries[session_id]
        summary.total_operations += 1
        summary.total_prompt_tokens += metrics.prompt_tokens
        summary.total_context_tokens += metrics.context_tokens
        summary.total_user_input_tokens += metrics.user_input_tokens
        summary.total_completion_tokens += metrics.completion_tokens
        summary.total_cached_tokens += metrics.cached_tokens
        summary.total_cost_usd += metrics.cost_usd

        # Update operation counts
        summary.operations_by_type[metrics.operation_type] = (
            summary.operations_by_type.get(metrics.operation_type, 0) + 1
        )

        # Recalculate averages
        n = summary.total_operations
        summary.average_quality_score = (
            (summary.average_quality_score * (n - 1) + metrics.output_quality_score) / n
        )
        summary.average_context_utilization = (
            (summary.average_context_utilization * (n - 1) + metrics.context_utilization_score) / n
        )
        summary.average_efficiency_score = (
            (summary.average_efficiency_score * (n - 1) + metrics.efficiency_score) / n
        )

        summary.end_time = metrics.timestamp

        # Save to disk
        self._save_session_summary(summary)

    def _save_operation_metrics(self, metrics: TokenMetrics):
        """Save operation metrics to disk."""
        # Organize by agent and date
        date_str = metrics.timestamp.date().isoformat()
        metrics_dir = self.data_dir / "operations" / metrics.agent_id / date_str
        metrics_dir.mkdir(parents=True, exist_ok=True)

        file_path = metrics_dir / f"{metrics.operation_id}.json"
        with open(file_path, "w") as f:
            json.dump(metrics.model_dump(), f, indent=2, default=str)

    def _save_session_summary(self, summary: SessionTokenSummary):
        """Save session summary to disk."""
        summaries_dir = self.data_dir / "sessions"
        summaries_dir.mkdir(parents=True, exist_ok=True)

        file_path = summaries_dir / f"{summary.session_id}.json"
        with open(file_path, "w") as f:
            json.dump(summary.model_dump(), f, indent=2, default=str)

    def _load_session_summary(self, session_id: str) -> Optional[SessionTokenSummary]:
        """Load session summary from disk."""
        file_path = self.data_dir / "sessions" / f"{session_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, "r") as f:
            data = json.load(f)
            return SessionTokenSummary(**data)

    def _load_agent_metrics(
        self,
        agent_id: str,
        days: int = 30
    ) -> List[TokenMetrics]:
        """Load all metrics for an agent within the specified time range."""
        metrics_list = []
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)

        agent_dir = self.data_dir / "operations" / agent_id
        if not agent_dir.exists():
            return metrics_list

        # Iterate through date directories
        for date_dir in sorted(agent_dir.iterdir()):
            if not date_dir.is_dir():
                continue

            # Parse date from directory name
            try:
                dir_date = datetime.fromisoformat(date_dir.name).date()
                if dir_date < cutoff_date:
                    continue
            except ValueError:
                continue

            # Load all operation files in this date
            for metrics_file in date_dir.glob("*.json"):
                with open(metrics_file, "r") as f:
                    data = json.load(f)
                    metrics_list.append(TokenMetrics(**data))

        return metrics_list
