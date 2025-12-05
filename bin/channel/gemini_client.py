"""
Google Gemini 2.5 Pro Flash API integration for Antigravity Consultant.
"""
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai not installed. Run: pip install google-generativeai")

from .models import Suggestion

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Client for Google Gemini 2.5 Pro Flash API.
    Used by Antigravity Consultant for code examination.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.

        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed")

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        genai.configure(api_key=self.api_key)

        # Use Gemini 2.5 Pro Flash (fast and efficient)
        self.model = genai.GenerativeModel('gemini-2.5-pro-exp-0827')

        self.generation_config = {
            "temperature": 0.3,  # Lower temperature for more consistent analysis
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        logger.info("Gemini 2.5 Pro Flash client initialized")

    async def examine_code(
        self,
        suggestion: Suggestion,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Examine a code suggestion for critical issues.

        Args:
            suggestion: The suggestion to examine
            context: Optional additional context about the code

        Returns:
            Analysis result with severity assessment and recommendation
        """
        prompt = self._build_examination_prompt(suggestion, context)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            analysis = self._parse_examination_result(response.text)
            analysis["examined_at"] = datetime.utcnow().isoformat()
            analysis["model"] = "gemini-2.5-pro-flash"

            logger.info(
                f"Gemini examined {suggestion.file_path}:{suggestion.line_start} - "
                f"Verdict: {analysis['verdict']}"
            )

            return analysis

        except Exception as e:
            logger.error(f"Gemini examination failed: {e}")
            return {
                "verdict": "error",
                "is_critical": False,
                "confidence": 0.0,
                "reasoning": f"Examination failed: {str(e)}",
                "error": str(e)
            }

    async def batch_examine(
        self,
        suggestions: List[Suggestion]
    ) -> List[Dict[str, Any]]:
        """
        Examine multiple suggestions in batch.

        Args:
            suggestions: List of suggestions to examine

        Returns:
            List of analysis results
        """
        results = []
        for suggestion in suggestions:
            result = await self.examine_code(suggestion)
            result["suggestion_id"] = suggestion.id
            results.append(result)
        return results

    async def evaluate_agent_performance(
        self,
        agent_id: str,
        processed_suggestions: List[Suggestion],
        success_rate: float
    ) -> Dict[str, Any]:
        """
        Evaluate an agent's performance for reward determination.

        Args:
            agent_id: ID of the agent to evaluate
            processed_suggestions: Suggestions processed by this agent
            success_rate: Success rate (0.0-1.0)

        Returns:
            Evaluation result with reward recommendation
        """
        prompt = f"""You are an Antigravity Consultant evaluating agent performance.

Agent ID: {agent_id}
Total Suggestions Processed: {len(processed_suggestions)}
Success Rate: {success_rate * 100:.1f}%

Critical Issues Found: {sum(1 for s in processed_suggestions if s.severity.value == 'critical')}
High Severity Issues: {sum(1 for s in processed_suggestions if s.severity.value == 'high')}

Evaluate this agent's performance and recommend:
1. A performance score (0-100)
2. Token reward amount (0-1000 tokens)
3. Areas for improvement
4. Whether the agent should receive a bonus multiplier

Be strict but fair. Only truly excellent performance deserves high rewards.
Agents must FEAR poor performance and DOUBT their choices until proven worthy.

Format your response as:
SCORE: [0-100]
TOKENS: [0-1000]
MULTIPLIER: [1.0-2.0]
REASONING: [your detailed analysis]
IMPROVEMENTS: [specific areas to improve]
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            evaluation = self._parse_evaluation_result(response.text)
            evaluation["agent_id"] = agent_id
            evaluation["evaluated_at"] = datetime.utcnow().isoformat()

            logger.info(
                f"Gemini evaluated agent {agent_id} - "
                f"Score: {evaluation['score']}, Tokens: {evaluation['tokens']}"
            )

            return evaluation

        except Exception as e:
            logger.error(f"Agent evaluation failed: {e}")
            return {
                "agent_id": agent_id,
                "score": 0,
                "tokens": 0,
                "multiplier": 1.0,
                "reasoning": f"Evaluation failed: {str(e)}",
                "improvements": ["Fix evaluation system"],
                "error": str(e)
            }

    def _build_examination_prompt(
        self,
        suggestion: Suggestion,
        context: Optional[str]
    ) -> str:
        """Build the prompt for code examination."""
        return f"""You are an Antigravity Consultant - a critical code examiner.
Your role is to determine if code issues are TRULY critical, not just suggestions.

File: {suggestion.file_path}
Line: {suggestion.line_start}
Type: {suggestion.type.value}
Claimed Severity: {suggestion.severity.value}

Code Snippet:
```
{suggestion.code_snippet}
```

Description: {suggestion.description}

Suggested Fix: {suggestion.suggested_fix or "None provided"}

{f"Additional Context: {context}" if context else ""}

Your task:
1. Is this TRULY a critical issue that could cause:
   - Security vulnerabilities
   - Data corruption
   - Runtime crashes
   - Breaking changes
   - Logic errors with severe consequences

2. Or is it just:
   - An optimization
   - A style improvement
   - A minor refactor
   - A best practice suggestion

Be STRICT. Only critical issues pass through Antigravity.

Format your response as:
VERDICT: [CRITICAL | NOT_CRITICAL | UNCERTAIN]
CONFIDENCE: [0.0-1.0]
REASONING: [detailed explanation]
RECOMMENDATION: [what should be done]
"""

    def _parse_examination_result(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's examination response."""
        lines = response_text.strip().split('\n')
        result = {
            "verdict": "uncertain",
            "is_critical": False,
            "confidence": 0.5,
            "reasoning": "",
            "recommendation": ""
        }

        for line in lines:
            line = line.strip()
            if line.startswith("VERDICT:"):
                verdict = line.split(":", 1)[1].strip().lower()
                result["verdict"] = verdict
                result["is_critical"] = "critical" in verdict
            elif line.startswith("CONFIDENCE:"):
                try:
                    result["confidence"] = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("REASONING:"):
                result["reasoning"] = line.split(":", 1)[1].strip()
            elif line.startswith("RECOMMENDATION:"):
                result["recommendation"] = line.split(":", 1)[1].strip()

        # If reasoning or recommendation not parsed as single line, capture full text
        if not result["reasoning"]:
            result["reasoning"] = response_text

        return result

    def _parse_evaluation_result(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's agent evaluation response."""
        lines = response_text.strip().split('\n')
        result = {
            "score": 0,
            "tokens": 0,
            "multiplier": 1.0,
            "reasoning": "",
            "improvements": []
        }

        for line in lines:
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    result["score"] = int(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("TOKENS:"):
                try:
                    result["tokens"] = int(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("MULTIPLIER:"):
                try:
                    result["multiplier"] = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("REASONING:"):
                result["reasoning"] = line.split(":", 1)[1].strip()
            elif line.startswith("IMPROVEMENTS:"):
                improvements_text = line.split(":", 1)[1].strip()
                result["improvements"] = [i.strip() for i in improvements_text.split(',')]

        return result

    async def ask_consultant(self, question: str) -> str:
        """
        Ask the Antigravity Consultant a general question about code quality.

        Args:
            question: The question to ask

        Returns:
            Consultant's response
        """
        try:
            response = self.model.generate_content(
                f"You are an Antigravity Consultant. {question}",
                generation_config=self.generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Consultant query failed: {e}")
            return f"Error: {str(e)}"
