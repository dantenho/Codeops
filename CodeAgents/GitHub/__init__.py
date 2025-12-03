"""
GitHub Integration - Process optimization comments and feedback.

Parses GitHub PR comments, detects optimization patterns,
and creates training materials for continuous improvement.
"""

from .comment_processor import (
    CommentProcessor,
    CommentSeverity,
    CommentType,
    OptimizationComment,
    CodeSnippet,
)
from .optimization_detector import (
    OptimizationDetector,
    DetectedOptimization,
    OptimizationCategory,
    OptimizationImpact,
)
from .optimization_catalog import (
    OptimizationCatalog,
    CatalogEntry,
)
from .optimization_service import OptimizationService

__all__ = [
    # Comment Processing
    "CommentProcessor",
    "CommentSeverity",
    "CommentType",
    "OptimizationComment",
    "CodeSnippet",

    # Optimization Detection
    "OptimizationDetector",
    "DetectedOptimization",
    "OptimizationCategory",
    "OptimizationImpact",

    # Catalog
    "OptimizationCatalog",
    "CatalogEntry",

    # Service
    "OptimizationService",
]

__version__ = "0.1.0"
