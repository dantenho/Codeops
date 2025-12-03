"""
Vibe Code - Intuitive, flow-state code generation system.

Enables natural language intent → code with smart context assembly
and token optimization.
"""

from .core.vibe_engine import VibeEngine
from .core.intent_parser import IntentParser
from .core.context_optimizer import ContextOptimizer
from .models.vibe_session import VibeSession, VibeResult

__all__ = [
    "VibeEngine",
    "IntentParser",
    "ContextOptimizer",
    "VibeSession",
    "VibeResult",
]

__version__ = "0.1.0"
