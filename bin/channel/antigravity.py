"""
Antigravity Filter - Filters suggestions for critical code issues only.
No optimization suggestions pass through.

Can optionally use the Antigravity Consultant (Gemini) for additional validation.
"""
from typing import List, Optional, TYPE_CHECKING
from .models import Suggestion, SuggestionType, SeverityLevel

if TYPE_CHECKING:
    from .consultant import AntigravityConsultant


class AntigravityFilter:
    """
    Antigravity: A gravity-defying filter that only lets CRITICAL issues through.
    Blocks all optimization suggestions and non-critical improvements.
    """

    # Keywords that indicate optimization (blocked)
    OPTIMIZATION_KEYWORDS = [
        "optimize", "performance", "faster", "efficient", "improve",
        "refactor", "clean", "simplify", "enhance", "better",
        "best practice", "convention", "style", "formatting"
    ]

    # Keywords that indicate critical issues (allowed)
    CRITICAL_KEYWORDS = [
        "error", "bug", "crash", "fail", "break", "vulnerability",
        "security", "leak", "undefined", "null", "exception",
        "critical", "fatal", "corrupt", "loss", "invalid"
    ]

    # Critical types that always pass
    CRITICAL_TYPES = {
        SuggestionType.SECURITY_VULNERABILITY,
        SuggestionType.RUNTIME_ERROR,
        SuggestionType.BREAKING_CHANGE,
        SuggestionType.BUG_FIX,
        SuggestionType.TYPE_ERROR,
        SuggestionType.LOGIC_ERROR,
    }

    @classmethod
    def is_critical(cls, suggestion: Suggestion) -> bool:
        """
        Determine if a suggestion is critical.
        Returns True only for critical code issues.
        """
        # Always allow critical types
        if suggestion.type in cls.CRITICAL_TYPES:
            return True

        # Always block if severity is too low
        if suggestion.severity not in {SeverityLevel.CRITICAL, SeverityLevel.HIGH}:
            return False

        # Check description for optimization keywords (block)
        description_lower = suggestion.description.lower()
        if any(keyword in description_lower for keyword in cls.OPTIMIZATION_KEYWORDS):
            # Unless it also contains critical keywords
            if not any(keyword in description_lower for keyword in cls.CRITICAL_KEYWORDS):
                return False

        # Check if it's a critical refactor (structural issues only)
        if suggestion.type == SuggestionType.CRITICAL_REFACTOR:
            # Must contain critical keywords
            return any(keyword in description_lower for keyword in cls.CRITICAL_KEYWORDS)

        return True

    @classmethod
    def filter(cls, suggestions: List[Suggestion]) -> List[Suggestion]:
        """
        Filter a list of suggestions, keeping only critical issues.
        """
        filtered = []
        for suggestion in suggestions:
            if cls.is_critical(suggestion):
                suggestion.processed_by_antigravity = True
                filtered.append(suggestion)
        return filtered

    @classmethod
    async def filter_with_consultant(
        cls,
        suggestions: List[Suggestion],
        consultant: "AntigravityConsultant",
        agent_id: Optional[str] = None
    ) -> List[Suggestion]:
        """
        Filter suggestions with Consultant (Gemini) validation.

        This is the ULTIMATE filter - first passes basic Antigravity check,
        then the Consultant (Gemini 2.5 Pro Flash) makes the final judgment.

        Args:
            suggestions: Suggestions to filter
            consultant: The Antigravity Consultant
            agent_id: Optional agent ID for tracking

        Returns:
            Only suggestions approved by both Antigravity AND the Consultant
        """
        # First pass: Basic Antigravity filter
        basic_filtered = cls.filter(suggestions)

        if not basic_filtered:
            return []

        # Second pass: Consultant examination
        examinations = await consultant.examine_batch(basic_filtered, agent_id)

        # Only keep suggestions the Consultant deems critical
        final_filtered = []
        for suggestion, examination in zip(basic_filtered, examinations):
            if examination.get("is_critical", False):
                # Add Consultant's verdict to metadata
                suggestion.metadata["consultant_verdict"] = examination.get("verdict")
                suggestion.metadata["consultant_confidence"] = examination.get("confidence")
                suggestion.metadata["consultant_reasoning"] = examination.get("reasoning")
                final_filtered.append(suggestion)

        return final_filtered

    @classmethod
    def explain_rejection(cls, suggestion: Suggestion) -> str:
        """
        Explain why a suggestion was rejected by Antigravity.
        """
        if suggestion.type not in cls.CRITICAL_TYPES:
            return f"Suggestion type '{suggestion.type}' is not critical"

        if suggestion.severity not in {SeverityLevel.CRITICAL, SeverityLevel.HIGH}:
            return f"Severity level '{suggestion.severity}' is too low"

        description_lower = suggestion.description.lower()
        if any(keyword in description_lower for keyword in cls.OPTIMIZATION_KEYWORDS):
            if not any(keyword in description_lower for keyword in cls.CRITICAL_KEYWORDS):
                return "Detected as optimization suggestion (not critical)"

        return "Does not meet critical criteria"
