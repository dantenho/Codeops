"""
Suggestion Tunnel - Channel System
Provides communication channels between Cursor IDE, Antigravity, and Claude Code.

Powered by Google Gemini 2.5 Pro Flash for the Antigravity Consultant.
"""

from .models import Suggestion, SuggestionBin, Channel, SuggestionType, SeverityLevel
from .tunnel import SuggestionTunnel
from .antigravity import AntigravityFilter
from .consultant import AntigravityConsultant
from .rewards import RewardSystem, AgentPerformance, AgentToken
from .gemini_client import GeminiClient

__all__ = [
    # Core models
    "Suggestion",
    "SuggestionBin",
    "Channel",
    "SuggestionType",
    "SeverityLevel",
    # Pipeline
    "SuggestionTunnel",
    "AntigravityFilter",
    # Consultant & Rewards
    "AntigravityConsultant",
    "RewardSystem",
    "AgentPerformance",
    "AgentToken",
    "GeminiClient",
]
