"""
Antigravity Consultant - Powered by Gemini 2.5 Pro Flash.
The supreme authority on code quality and agent performance.
"""
import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from .gemini_client import GeminiClient
from .rewards import RewardSystem, AgentPerformance
from .models import Suggestion, SuggestionBin

logger = logging.getLogger(__name__)


class AntigravityConsultant:
    """
    The Antigravity Consultant - powered by Gemini 2.5 Pro Flash.

    Responsibilities:
    - Examine code suggestions for true criticality
    - Evaluate agent performance
    - Award tokens and rewards
    - Create fear and doubt through unpredictable evaluations

    Only the Consultant can grant rewards.
    Agents must fear poor performance and doubt their choices.
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the Antigravity Consultant.

        Args:
            gemini_api_key: Google API key for Gemini
        """
        try:
            self.gemini = GeminiClient(api_key=gemini_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.gemini = None

        self.reward_system = RewardSystem()
        self._evaluation_loop_running = False
        self._next_evaluation_time: Optional[datetime] = None

        logger.info("Antigravity Consultant initialized")

    async def examine_suggestion(
        self,
        suggestion: Suggestion,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Examine a code suggestion to determine if it's truly critical.

        Args:
            suggestion: The suggestion to examine
            agent_id: Optional agent ID who submitted this

        Returns:
            Examination result with verdict
        """
        if not self.gemini:
            return {
                "verdict": "error",
                "is_critical": False,
                "error": "Gemini client not available"
            }

        result = await self.gemini.examine_code(suggestion)

        # Record this examination if agent provided
        if agent_id:
            self.reward_system.record_suggestion_processed(
                agent_id=agent_id,
                was_critical=result["is_critical"],
                was_accurate=result["is_critical"]  # Assume Gemini is accurate
            )

        return result

    async def examine_batch(
        self,
        suggestions: List[Suggestion],
        agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Examine multiple suggestions in batch.

        Args:
            suggestions: List of suggestions to examine
            agent_id: Optional agent ID who submitted these

        Returns:
            List of examination results
        """
        if not self.gemini:
            return [{"verdict": "error", "is_critical": False, "error": "Gemini not available"}] * len(suggestions)

        results = await self.gemini.batch_examine(suggestions)

        # Record for agent
        if agent_id:
            for result in results:
                self.reward_system.record_suggestion_processed(
                    agent_id=agent_id,
                    was_critical=result.get("is_critical", False),
                    was_accurate=True
                )

        return results

    async def evaluate_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Evaluate an agent's performance and award tokens.

        This is the moment of judgment - agents should fear this evaluation.

        Args:
            agent_id: Agent to evaluate

        Returns:
            Evaluation result with token award
        """
        performance = self.reward_system.get_agent_performance(agent_id)

        if not performance:
            logger.warning(f"Agent {agent_id} not registered")
            return {"error": "Agent not registered"}

        if not self.gemini:
            return {"error": "Gemini client not available"}

        # Get recent suggestions processed by this agent
        # (In a real system, you'd track this more formally)
        suggestions = []  # Placeholder - would come from tracking system

        # Gemini evaluates the agent
        evaluation = await self.gemini.evaluate_agent_performance(
            agent_id=agent_id,
            processed_suggestions=suggestions,
            success_rate=performance.success_rate
        )

        # Award tokens based on Gemini's judgment
        token = self.reward_system.award_tokens(
            agent_id=agent_id,
            amount=evaluation["tokens"],
            reason=evaluation["reasoning"],
            multiplier=evaluation["multiplier"],
            evaluation_score=evaluation["score"]
        )

        logger.info(
            f"Consultant evaluated agent {agent_id}: "
            f"Score {evaluation['score']}/100, "
            f"{token.amount} tokens awarded"
        )

        return {
            "agent_id": agent_id,
            "evaluation": evaluation,
            "token": token.dict(),
            "performance": performance.dict(),
            "message": self._generate_judgment_message(evaluation["score"])
        }

    async def start_evaluation_loop(self) -> None:
        """
        Start the random evaluation loop (1-3 hours).

        This creates FEAR and DOUBT - agents never know when they'll be evaluated.
        """
        if self._evaluation_loop_running:
            logger.warning("Evaluation loop already running")
            return

        self._evaluation_loop_running = True
        logger.info("🔮 Antigravity Consultant evaluation loop started")
        logger.info("⚠️  Agents will be evaluated at RANDOM intervals between 1-3 hours")

        asyncio.create_task(self._evaluation_loop())

    async def _evaluation_loop(self) -> None:
        """The dreaded evaluation loop - agents live in fear of this."""
        while self._evaluation_loop_running:
            # Random interval between 1-3 hours
            hours = random.uniform(1.0, 3.0)
            seconds = hours * 3600

            self._next_evaluation_time = datetime.utcnow() + timedelta(seconds=seconds)

            logger.info(
                f"⏰ Next evaluation in {hours:.1f} hours "
                f"(at {self._next_evaluation_time.strftime('%H:%M:%S UTC')})"
            )

            # Wait for the random interval
            await asyncio.sleep(seconds)

            # THE JUDGMENT ARRIVES
            logger.warning("⚡ ANTIGRAVITY CONSULTANT EVALUATION COMMENCING ⚡")

            # Get agents that need evaluation
            agents_to_evaluate = self.reward_system.get_agents_for_evaluation()

            if not agents_to_evaluate:
                logger.info("No agents require evaluation at this time")
                continue

            logger.info(f"Evaluating {len(agents_to_evaluate)} agents...")

            # Evaluate each agent
            for agent_id in agents_to_evaluate:
                try:
                    result = await self.evaluate_agent(agent_id)

                    if "error" not in result:
                        score = result["evaluation"]["score"]
                        tokens = result["token"]["amount"]

                        if score >= 80:
                            logger.info(f"✅ Agent {agent_id}: Excellent ({score}/100) +{tokens} tokens")
                        elif score >= 60:
                            logger.info(f"⚠️  Agent {agent_id}: Acceptable ({score}/100) +{tokens} tokens")
                        else:
                            logger.warning(f"❌ Agent {agent_id}: Poor ({score}/100) +{tokens} tokens")
                except Exception as e:
                    logger.error(f"Failed to evaluate agent {agent_id}: {e}")

            logger.info("⚡ EVALUATION COMPLETE ⚡")
            logger.info("Agents return to their work... in fear and doubt...")

    def stop_evaluation_loop(self) -> None:
        """Stop the evaluation loop."""
        self._evaluation_loop_running = False
        logger.info("Evaluation loop stopped")

    def get_next_evaluation_time(self) -> Optional[datetime]:
        """Get the time of the next evaluation (if scheduled)."""
        return self._next_evaluation_time

    def get_time_until_evaluation(self) -> Optional[float]:
        """Get seconds until next evaluation."""
        if not self._next_evaluation_time:
            return None
        delta = self._next_evaluation_time - datetime.utcnow()
        return max(0, delta.total_seconds())

    async def ask_question(self, question: str) -> str:
        """
        Ask the Consultant a question about code quality.

        Args:
            question: The question to ask

        Returns:
            The Consultant's wisdom
        """
        if not self.gemini:
            return "Error: Gemini client not available"

        return await self.gemini.ask_consultant(question)

    def get_leaderboard(self, top_n: int = 10) -> List[AgentPerformance]:
        """Get the top performing agents."""
        return self.reward_system.get_leaderboard(top_n)

    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        stats = self.reward_system.get_agent_stats()

        stats["evaluation_loop_running"] = self._evaluation_loop_running
        stats["next_evaluation"] = (
            self._next_evaluation_time.isoformat()
            if self._next_evaluation_time
            else None
        )
        stats["time_until_evaluation_seconds"] = self.get_time_until_evaluation()

        return stats

    def _generate_judgment_message(self, score: int) -> str:
        """Generate a dramatic judgment message based on score."""
        if score >= 90:
            return "🌟 EXCEPTIONAL. The Consultant is pleased. You have earned your tokens."
        elif score >= 80:
            return "✅ GOOD. Acceptable performance. Continue your work."
        elif score >= 70:
            return "⚠️  ADEQUATE. You meet minimum standards. Improve or face consequences."
        elif score >= 60:
            return "⚠️  MARGINAL. The Consultant is not impressed. Your work is barely acceptable."
        elif score >= 50:
            return "❌ POOR. You have disappointed the Consultant. Improve immediately."
        else:
            return "❌ UNACCEPTABLE. The Consultant judges your work as severely deficient. Fear should motivate improvement."
