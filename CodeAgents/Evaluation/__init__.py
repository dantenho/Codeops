"""
Code Evaluation System - Automated quality assessment.

Evaluates generated code across multiple dimensions:
- Static analysis (complexity, maintainability)
- Testing (coverage, pass rate)
- Standards compliance (linting, formatting)
- Performance (estimated complexity)
- AI-specific metrics (token efficiency, context utilization)
"""

from .core.evaluator import CodeEvaluator
from .metrics.code_quality import CodeQualityMetrics
from .gates.quality_gate import QualityGate

__all__ = [
    "CodeEvaluator",
    "CodeQualityMetrics",
    "QualityGate",
]

__version__ = "0.1.0"
