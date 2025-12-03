"""
Vibe Engine - Core orchestrator for vibe coding.

Coordinates intent parsing, context assembly, code generation,
and quality assessment for intuitive flow-state development.
"""

import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from .intent_parser import IntentParser
from .context_optimizer import ContextOptimizer
from ..models.vibe_session import (
    VibeSession,
    VibeResult,
    VibeIntent,
    VibeConfidence,
)


class VibeEngine:
    """
    Main engine for vibe coding.

    Orchestrates the complete flow from natural language input
    to optimized code generation with minimal token usage.
    """

    def __init__(
        self,
        memory_service=None,
        token_tracker=None,
        pattern_library=None,
        codebase_path: Optional[Path] = None,
    ):
        """
        Initialize vibe engine.

        Args:
            memory_service: Memory service for retrieving context
            token_tracker: Token tracker for usage monitoring
            pattern_library: Pattern library for templates
            codebase_path: Path to codebase for context retrieval
        """
        self.intent_parser = IntentParser()
        self.context_optimizer = ContextOptimizer(
            memory_service=memory_service,
            token_counter=self._count_tokens
        )
        self.memory_service = memory_service
        self.token_tracker = token_tracker
        self.pattern_library = pattern_library
        self.codebase_path = codebase_path

        # Active sessions
        self._sessions: dict[str, VibeSession] = {}

    def start_session(self, agent_id: str) -> VibeSession:
        """
        Start a new vibe coding session.

        Args:
            agent_id: Agent identifier

        Returns:
            New VibeSession
        """
        session = VibeSession(
            session_id=str(uuid.uuid4()),
            agent_id=agent_id,
        )

        self._sessions[session.session_id] = session
        return session

    def generate(
        self,
        user_input: str,
        agent_id: str,
        session_id: Optional[str] = None,
        max_tokens: int = 2000,
        model_name: str = "claude-sonnet-4-5",
    ) -> VibeResult:
        """
        Generate code from natural language input.

        This is the main vibe coding method that orchestrates the entire flow.

        Args:
            user_input: Natural language description
            agent_id: Agent identifier
            session_id: Optional existing session ID
            max_tokens: Maximum tokens for context
            model_name: LLM model to use

        Returns:
            VibeResult with generated code and metrics
        """
        start_time = time.time()

        # Get or create session
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
        else:
            session = self.start_session(agent_id)

        # Step 1: Parse intent
        intent = self.intent_parser.parse(user_input)

        # Step 2: Match patterns
        matched_patterns = self._match_patterns(intent)
        intent.matched_patterns = [p["pattern_id"] for p in matched_patterns]

        # Step 3: Assemble optimized context
        context = self.context_optimizer.assemble_context(
            intent=intent,
            max_tokens=max_tokens,
            agent_id=agent_id,
            codebase_path=self.codebase_path,
        )

        # Step 4: Generate code (placeholder - integrate with actual LLM)
        generated_code, explanation = self._generate_code(
            intent, context, matched_patterns
        )

        # Step 5: Assess quality
        quality_score = self._assess_quality(generated_code, intent)

        # Step 6: Calculate token usage
        input_tokens = context.total_tokens + self._count_tokens(user_input)
        output_tokens = self._count_tokens(generated_code + explanation)
        total_tokens = input_tokens + output_tokens

        # Calculate cost
        from ...Training.src.training.models.token_metrics import calculate_cost
        cost = calculate_cost(input_tokens, output_tokens, model_name)

        # Step 7: Generate suggestions
        next_steps = self._suggest_next_steps(intent, generated_code)
        improvements = self._suggest_improvements(generated_code, quality_score)
        warnings = self._check_warnings(generated_code, intent)

        # Create result
        result = VibeResult(
            session_id=session.session_id,
            intent=intent,
            generated_code=generated_code,
            explanation=explanation,
            confidence_score=self._map_confidence_to_score(intent.confidence),
            estimated_quality=quality_score,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            context=context,
            generation_time_ms=int((time.time() - start_time) * 1000),
            next_steps=next_steps,
            improvements=improvements,
            warnings=warnings,
        )

        # Add to session
        session.add_iteration(result)

        # Track tokens if tracker available
        if self.token_tracker:
            self._record_token_usage(agent_id, session.session_id, result)

        return result

    def refine(
        self,
        session_id: str,
        refinement_request: str,
        max_tokens: int = 2000,
    ) -> VibeResult:
        """
        Refine previous generation based on feedback.

        Args:
            session_id: Existing session ID
            refinement_request: What to improve
            max_tokens: Maximum tokens for context

        Returns:
            New VibeResult with refined code
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self._sessions[session_id]
        if not session.iterations:
            raise ValueError("No previous iterations to refine")

        previous_result = session.iterations[-1]

        # Parse refinement as new intent
        refinement_intent = self.intent_parser.parse(refinement_request)

        # Use previous code as context
        combined_input = f"{previous_result.intent.raw_input}\n\nRefine: {refinement_request}"

        # Generate with refinement context
        return self.generate(
            user_input=combined_input,
            agent_id=session.agent_id,
            session_id=session_id,
            max_tokens=max_tokens,
        )

    def get_session(self, session_id: str) -> Optional[VibeSession]:
        """Get an active session by ID."""
        return self._sessions.get(session_id)

    def end_session(self, session_id: str, user_accepted: bool = False):
        """
        End a vibe coding session.

        Args:
            session_id: Session to end
            user_accepted: Whether user accepted the final result
        """
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.ended_at = datetime.utcnow()
            session.user_accepted = user_accepted

            # Learn from session if accepted
            if user_accepted and self.memory_service:
                self._learn_from_session(session)

            # Remove from active sessions
            del self._sessions[session_id]

    def _match_patterns(self, intent: VibeIntent) -> list[dict]:
        """Match intent against pattern library."""
        if not self.pattern_library:
            return []

        matched = []

        # In full implementation, query pattern library
        # For now, return placeholder
        if intent.target == "api" and intent.language == "python":
            matched.append({
                "pattern_id": "fastapi_endpoint",
                "match_score": 85.0,
                "template": "# FastAPI endpoint template",
            })

        return matched

    def _generate_code(
        self,
        intent: VibeIntent,
        context,
        patterns: list
    ) -> tuple[str, str]:
        """
        Generate code based on intent, context, and patterns.

        This is a placeholder - in full implementation, this would call
        the LLM API with the assembled context.

        Args:
            intent: Parsed intent
            context: Assembled context
            patterns: Matched patterns

        Returns:
            Tuple of (generated_code, explanation)
        """
        # Placeholder implementation
        code_template = f"""
# Generated {intent.target} in {intent.language or 'python'}
# Action: {intent.action}

def {intent.entities.get('function_name', 'example_function')}():
    \"\"\"
    {intent.raw_input}
    \"\"\"
    # Implementation here
    pass
"""

        explanation = f"""
This code implements a {intent.target} based on your request to {intent.action}.

The function signature and structure follow {intent.language or 'Python'} best practices.
Context was assembled from {len(context.relevant_code)} relevant code snippets.
"""

        return code_template.strip(), explanation.strip()

    def _assess_quality(self, code: str, intent: VibeIntent) -> float:
        """
        Assess quality of generated code.

        Args:
            code: Generated code
            intent: Original intent

        Returns:
            Quality score 0-100
        """
        score = 50.0  # Base score

        # Has content
        if len(code) > 100:
            score += 10

        # Has docstring
        if '"""' in code or "'''" in code:
            score += 10

        # Has error handling
        if "try:" in code or "except" in code:
            score += 5

        # Matches language
        if intent.language == "python":
            if "def " in code:
                score += 10
            if ":" in code:
                score += 5

        # Has type hints (Python)
        if "->" in code:
            score += 10

        return min(100.0, score)

    def _suggest_next_steps(self, intent: VibeIntent, code: str) -> list[str]:
        """Suggest next steps after generation."""
        suggestions = []

        if intent.target == "function":
            suggestions.append("Add unit tests for this function")
            suggestions.append("Add error handling for edge cases")

        if intent.target == "api":
            suggestions.append("Add authentication middleware")
            suggestions.append("Create Pydantic models for request/response")
            suggestions.append("Add API documentation")

        if not ("test" in code.lower() or "Test" in code):
            suggestions.append("Create test cases")

        return suggestions

    def _suggest_improvements(self, code: str, quality_score: float) -> list[str]:
        """Suggest improvements for generated code."""
        improvements = []

        if quality_score < 70:
            improvements.append("Add more comprehensive error handling")
            improvements.append("Improve documentation and comments")

        if '"""' not in code:
            improvements.append("Add docstrings to functions/classes")

        if "->" not in code and "def " in code:
            improvements.append("Add type hints for better code quality")

        return improvements

    def _check_warnings(self, code: str, intent: VibeIntent) -> list[str]:
        """Check for potential issues in generated code."""
        warnings = []

        if "TODO" in code or "FIXME" in code:
            warnings.append("Code contains TODO/FIXME markers")

        if intent.confidence == VibeConfidence.LOW:
            warnings.append("Low confidence in intent parsing - verify output carefully")

        if len(code) < 50:
            warnings.append("Generated code seems too short - may need refinement")

        return warnings

    def _map_confidence_to_score(self, confidence: VibeConfidence) -> float:
        """Map confidence enum to numeric score."""
        mapping = {
            VibeConfidence.VERY_HIGH: 95.0,
            VibeConfidence.HIGH: 85.0,
            VibeConfidence.MEDIUM: 70.0,
            VibeConfidence.LOW: 50.0,
            VibeConfidence.VERY_LOW: 30.0,
        }
        return mapping.get(confidence, 50.0)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        # Use memory service's counter if available
        if self.memory_service and hasattr(self.memory_service, 'count_tokens'):
            return self.memory_service.count_tokens(text)

        # Fallback: rough estimation
        return len(text) // 4

    def _record_token_usage(self, agent_id: str, session_id: str, result: VibeResult):
        """Record token usage in tracker."""
        if not self.token_tracker:
            return

        try:
            self.token_tracker.record_operation(
                session_id=session_id,
                agent_id=agent_id,
                operation_id=str(uuid.uuid4()),
                context_tokens=result.context.total_tokens if result.context else 0,
                user_input_tokens=self._count_tokens(result.intent.raw_input),
                completion_tokens=result.output_tokens,
                output_quality_score=result.estimated_quality,
                context_utilization_score=self._calculate_context_utilization(result),
                operation_type="vibe_code_generation",
                language=result.intent.language,
            )
        except Exception as e:
            # Don't fail generation if tracking fails
            pass

    def _calculate_context_utilization(self, result: VibeResult) -> float:
        """Calculate how much of the context was actually used."""
        if not result.context or result.context.total_tokens == 0:
            return 0.0

        # Simple heuristic: ratio of output to context size
        # Higher ratio suggests better context utilization
        utilization = min(100.0, (result.output_tokens / result.context.total_tokens) * 100)

        return utilization

    def _learn_from_session(self, session: VibeSession):
        """
        Learn from a successful session.

        Store patterns and outcomes in memory for future use.

        Args:
            session: Completed session
        """
        if not self.memory_service or not session.iterations:
            return

        final_result = session.iterations[-1]

        # Store the successful pattern
        learning_content = f"""
Intent: {final_result.intent.raw_input}
Action: {final_result.intent.action}
Target: {final_result.intent.target}
Language: {final_result.intent.language}

Generated Code:
{final_result.generated_code}

Quality Score: {final_result.estimated_quality}
Token Efficiency: {session.efficiency_score}
"""

        try:
            self.memory_service.add_training_material(
                topic=f"{final_result.intent.action}_{final_result.intent.target}",
                file_name=f"vibe_session_{session.session_id}.md",
                content=learning_content,
                agent_id=session.agent_id,
            )
        except Exception as e:
            # Don't fail if learning fails
            pass

    def get_stats(self) -> dict:
        """Get engine statistics."""
        return {
            "active_sessions": len(self._sessions),
            "cache_stats": self.context_optimizer.get_cache_stats(),
        }
