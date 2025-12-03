"""
Error Intelligence System - Smart error handling and recovery.

Analyzes errors, diagnoses root causes, and implements
self-healing mechanisms for automated recovery.
"""

from .error_intelligence import (
    ErrorIntelligence,
    ErrorAnalysis,
    ErrorCategory,
    ErrorSeverity,
    RootCause,
    RecoveryStrategy,
)
from .diagnosis_engine import DiagnosisEngine
from .self_healing import (
    SelfHealing,
    HealingResult,
    HealingStatus,
    CircuitBreaker,
)

__all__ = [
    # Error Intelligence
    "ErrorIntelligence",
    "ErrorAnalysis",
    "ErrorCategory",
    "ErrorSeverity",
    "RootCause",
    "RecoveryStrategy",

    # Diagnosis
    "DiagnosisEngine",

    # Self-Healing
    "SelfHealing",
    "HealingResult",
    "HealingStatus",
    "CircuitBreaker",
]

__version__ = "0.1.0"
