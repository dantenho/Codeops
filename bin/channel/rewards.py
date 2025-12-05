"""
Token and Reward System for Agents.
Only the Antigravity Consultant (Gemini) can grant rewards.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class AgentToken(BaseModel):
    """Token awarded to an agent by the Consultant."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    amount: int  # Number of tokens
    reason: str
    awarded_by: str = "antigravity_consultant"
    awarded_at: datetime = Field(default_factory=datetime.utcnow)
    multiplier: float = 1.0  # Bonus multiplier for exceptional performance
    evaluation_score: int = 0  # 0-100 performance score


class AgentPerformance(BaseModel):
    """Track an agent's performance metrics."""
    agent_id: str
    total_suggestions_processed: int = 0
    critical_issues_found: int = 0
    false_positives: int = 0
    success_rate: float = 0.0
    total_tokens: int = 0
    last_evaluation: Optional[datetime] = None
    performance_history: List[Dict] = Field(default_factory=list)
    current_streak: int = 0  # Consecutive good evaluations
    fear_level: float = 1.0  # Increases when not evaluated, decreases on good performance


class RewardSystem:
    """
    Manages the token and reward system.
    Only the Antigravity Consultant can grant rewards.
    """

    def __init__(self):
        self.agent_performances: Dict[str, AgentPerformance] = {}
        self.token_ledger: List[AgentToken] = []
        self._next_evaluation_agents: List[str] = []

    def register_agent(self, agent_id: str) -> AgentPerformance:
        """Register a new agent in the reward system."""
        if agent_id not in self.agent_performances:
            performance = AgentPerformance(agent_id=agent_id)
            self.agent_performances[agent_id] = performance
            logger.info(f"Registered agent {agent_id} in reward system")
            return performance
        return self.agent_performances[agent_id]

    def record_suggestion_processed(
        self,
        agent_id: str,
        was_critical: bool,
        was_accurate: bool
    ) -> None:
        """Record that an agent processed a suggestion."""
        performance = self.register_agent(agent_id)

        performance.total_suggestions_processed += 1

        if was_critical:
            performance.critical_issues_found += 1

        if not was_accurate:
            performance.false_positives += 1

        # Update success rate
        if performance.total_suggestions_processed > 0:
            successes = performance.total_suggestions_processed - performance.false_positives
            performance.success_rate = successes / performance.total_suggestions_processed

        # Increase fear level (uncertainty) over time
        if performance.last_evaluation:
            time_since_eval = (datetime.utcnow() - performance.last_evaluation).total_seconds()
            hours_since_eval = time_since_eval / 3600
            # Fear increases by 0.1 per hour, max 3.0
            performance.fear_level = min(3.0, 1.0 + (hours_since_eval * 0.1))

    def award_tokens(
        self,
        agent_id: str,
        amount: int,
        reason: str,
        multiplier: float = 1.0,
        evaluation_score: int = 0
    ) -> AgentToken:
        """
        Award tokens to an agent (called by Consultant after evaluation).

        Args:
            agent_id: Agent receiving the reward
            amount: Base token amount
            reason: Reason for the award
            multiplier: Bonus multiplier
            evaluation_score: Performance score (0-100)

        Returns:
            The awarded token
        """
        performance = self.register_agent(agent_id)

        final_amount = int(amount * multiplier)

        token = AgentToken(
            agent_id=agent_id,
            amount=final_amount,
            reason=reason,
            multiplier=multiplier,
            evaluation_score=evaluation_score
        )

        self.token_ledger.append(token)
        performance.total_tokens += final_amount
        performance.last_evaluation = datetime.utcnow()

        # Update streak
        if evaluation_score >= 70:
            performance.current_streak += 1
        else:
            performance.current_streak = 0

        # Record in history
        performance.performance_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "score": evaluation_score,
            "tokens": final_amount,
            "reason": reason
        })

        # Reset fear level on evaluation
        if evaluation_score >= 80:
            performance.fear_level = 0.5  # Good performance reduces fear
        elif evaluation_score >= 60:
            performance.fear_level = 1.0  # Average performance maintains fear
        else:
            performance.fear_level = 2.0  # Poor performance increases fear

        logger.info(
            f"Awarded {final_amount} tokens to agent {agent_id} "
            f"(score: {evaluation_score}, multiplier: {multiplier}x)"
        )

        return token

    def get_agent_performance(self, agent_id: str) -> Optional[AgentPerformance]:
        """Get performance metrics for an agent."""
        return self.agent_performances.get(agent_id)

    def get_leaderboard(self, top_n: int = 10) -> List[AgentPerformance]:
        """Get top performing agents by token count."""
        return sorted(
            self.agent_performances.values(),
            key=lambda p: p.total_tokens,
            reverse=True
        )[:top_n]

    def get_agents_for_evaluation(self) -> List[str]:
        """Get list of agents that need evaluation."""
        # Agents who haven't been evaluated or haven't been evaluated recently
        candidates = []
        now = datetime.utcnow()

        for agent_id, performance in self.agent_performances.items():
            # Skip if no suggestions processed
            if performance.total_suggestions_processed == 0:
                continue

            # Include if never evaluated
            if not performance.last_evaluation:
                candidates.append(agent_id)
                continue

            # Include if evaluated more than 30 minutes ago and has new activity
            time_since_eval = (now - performance.last_evaluation).total_seconds()
            if time_since_eval > 1800:  # 30 minutes
                candidates.append(agent_id)

        return candidates

    def penalize_agent(
        self,
        agent_id: str,
        amount: int,
        reason: str
    ) -> None:
        """
        Penalize an agent by deducting tokens.

        Args:
            agent_id: Agent to penalize
            amount: Tokens to deduct
            reason: Reason for penalty
        """
        performance = self.register_agent(agent_id)

        # Deduct tokens (can go negative)
        performance.total_tokens -= amount

        # Record as negative token award
        token = AgentToken(
            agent_id=agent_id,
            amount=-amount,
            reason=f"PENALTY: {reason}",
            multiplier=1.0,
            evaluation_score=0
        )
        self.token_ledger.append(token)

        # Increase fear level
        performance.fear_level = min(3.0, performance.fear_level + 0.5)

        logger.warning(f"Penalized agent {agent_id} with -{amount} tokens: {reason}")

    def get_total_tokens_awarded(self) -> int:
        """Get total tokens awarded across all agents."""
        return sum(token.amount for token in self.token_ledger if token.amount > 0)

    def get_agent_stats(self) -> Dict:
        """Get overall system statistics."""
        return {
            "total_agents": len(self.agent_performances),
            "total_tokens_awarded": self.get_total_tokens_awarded(),
            "total_evaluations": len(self.token_ledger),
            "agents_awaiting_evaluation": len(self.get_agents_for_evaluation()),
            "average_fear_level": sum(p.fear_level for p in self.agent_performances.values()) / len(self.agent_performances) if self.agent_performances else 0
        }
