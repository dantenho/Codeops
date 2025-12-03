"""
GitHub integration modules for optimization detection and processing.

This package provides:
- Optimization detection in code reviews
- Comment processing and analysis
- Optimization service for code improvements
- Optimization catalog management
"""

from .optimization_detector import OptimizationDetector
from .optimization_service import OptimizationService
from .comment_processor import CommentProcessor

__all__ = [
    "OptimizationDetector",
    "OptimizationService",
    "CommentProcessor",
]
