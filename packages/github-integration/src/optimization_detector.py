"""
Optimization Detector - Identify and categorize code optimizations.

Analyzes optimization comments to extract patterns,
create learning materials, and track improvements.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field

from .comment_processor import OptimizationComment, CommentType


class OptimizationCategory(str, Enum):
    """Categories of optimizations."""
    ALGORITHMIC = "algorithmic"  # Better algorithm choice
    DATA_STRUCTURE = "data_structure"  # Better data structure
    LANGUAGE_FEATURE = "language_feature"  # Use language-specific features
    LIBRARY_USAGE = "library_usage"  # Use standard library better
    MEMORY = "memory"  # Memory optimization
    CPU = "cpu"  # CPU optimization
    IO = "io"  # I/O optimization
    CACHING = "caching"  # Add caching
    LAZY_EVALUATION = "lazy_evaluation"  # Lazy loading/evaluation
    PARALLELIZATION = "parallelization"  # Parallel processing
    CODE_STRUCTURE = "code_structure"  # Better code organization
    TYPE_HINTS = "type_hints"  # Add type annotations
    ERROR_HANDLING = "error_handling"  # Better error handling
    SECURITY = "security"  # Security improvements
    READABILITY = "readability"  # Code readability


class OptimizationImpact(str, Enum):
    """Impact level of optimization."""
    HIGH = "high"  # Significant performance/quality gain
    MEDIUM = "medium"  # Moderate improvement
    LOW = "low"  # Minor improvement
    NEGLIGIBLE = "negligible"  # Minimal impact


class DetectedOptimization(BaseModel):
    """Detected optimization pattern."""
    optimization_id: str
    category: OptimizationCategory
    impact: OptimizationImpact
    title: str
    description: str
    pattern_before: str  # Anti-pattern
    pattern_after: str  # Recommended pattern
    language: str = "python"
    explanation: str = ""
    examples: List[str] = Field(default_factory=list)
    related_comment_ids: List[str] = Field(default_factory=list)
    occurrence_count: int = 1
    success_rate: float = 0.0  # % of times this fix worked
    avg_improvement: float = 0.0  # Average quality score improvement


class OptimizationDetector:
    """
    Detect and categorize code optimization patterns.

    Learns from GitHub comments to build a catalog of
    optimization patterns and anti-patterns.
    """

    # Common optimization patterns
    KNOWN_PATTERNS = {
        "list_comprehension": {
            "category": OptimizationCategory.LANGUAGE_FEATURE,
            "impact": OptimizationImpact.LOW,
            "before": r"for .+ in .+:\s+.+\.append\(",
            "after": "[item for item in iterable]",
            "keywords": ["list comprehension", "comprehension", "for loop"],
            "explanation": "List comprehensions are more concise and often faster than explicit loops.",
        },
        "generator_expression": {
            "category": OptimizationCategory.MEMORY,
            "impact": OptimizationImpact.MEDIUM,
            "before": r"list\(.+for .+ in",
            "after": "(item for item in iterable)",
            "keywords": ["generator", "memory", "iterator"],
            "explanation": "Generator expressions use less memory for large datasets.",
        },
        "dict_get": {
            "category": OptimizationCategory.LANGUAGE_FEATURE,
            "impact": OptimizationImpact.LOW,
            "before": r"if .+ in .+:\s+.+ = .+\[.+\]\s+else:",
            "after": "value = dict.get(key, default)",
            "keywords": ["dict.get", "dictionary", "default value"],
            "explanation": "dict.get() is cleaner and safer than manual key checking.",
        },
        "join_strings": {
            "category": OptimizationCategory.CPU,
            "impact": OptimizationImpact.MEDIUM,
            "before": r"for .+ in .+:\s+.+ \+= ",
            "after": "result = ''.join(items)",
            "keywords": ["string concatenation", "join", "performance"],
            "explanation": "str.join() is much faster than repeated string concatenation.",
        },
        "set_membership": {
            "category": OptimizationCategory.DATA_STRUCTURE,
            "impact": OptimizationImpact.HIGH,
            "before": r"if .+ in \[.+\]:",
            "after": "if item in set_items:",
            "keywords": ["set", "membership test", "performance"],
            "explanation": "Set membership tests are O(1) vs O(n) for lists.",
        },
        "enumerate": {
            "category": OptimizationCategory.LANGUAGE_FEATURE,
            "impact": OptimizationImpact.LOW,
            "before": r"for i in range\(len\(.+\)\):",
            "after": "for i, item in enumerate(items):",
            "keywords": ["enumerate", "index", "iteration"],
            "explanation": "enumerate() is more Pythonic and readable.",
        },
        "context_manager": {
            "category": OptimizationCategory.ERROR_HANDLING,
            "impact": OptimizationImpact.MEDIUM,
            "before": r"\.open\(.+\).*\.close\(\)",
            "after": "with open(file) as f:",
            "keywords": ["context manager", "with", "resource management"],
            "explanation": "Context managers ensure proper resource cleanup.",
        },
        "defaultdict": {
            "category": OptimizationCategory.DATA_STRUCTURE,
            "impact": OptimizationImpact.MEDIUM,
            "before": r"if .+ not in .+:\s+.+\[.+\] = ",
            "after": "from collections import defaultdict",
            "keywords": ["defaultdict", "dictionary", "initialization"],
            "explanation": "defaultdict eliminates need for existence checking.",
        },
        "f_strings": {
            "category": OptimizationCategory.LANGUAGE_FEATURE,
            "impact": OptimizationImpact.LOW,
            "before": r'["\'].+%s.+["\'] %|.+\.format\(',
            "after": 'f"value: {variable}"',
            "keywords": ["f-string", "formatting", "string interpolation"],
            "explanation": "f-strings are faster and more readable.",
        },
        "any_all": {
            "category": OptimizationCategory.LANGUAGE_FEATURE,
            "impact": OptimizationImpact.LOW,
            "before": r"for .+ in .+:\s+if .+:\s+return True",
            "after": "return any(condition for item in items)",
            "keywords": ["any", "all", "boolean", "iteration"],
            "explanation": "Built-in any/all are optimized and short-circuit.",
        },
    }

    def __init__(self):
        """Initialize optimization detector."""
        self.detected_optimizations: Dict[str, DetectedOptimization] = {}
        self._load_known_patterns()

    def _load_known_patterns(self):
        """Load known optimization patterns."""
        for pattern_id, pattern_info in self.KNOWN_PATTERNS.items():
            optimization = DetectedOptimization(
                optimization_id=pattern_id,
                category=pattern_info["category"],
                impact=pattern_info["impact"],
                title=pattern_id.replace("_", " ").title(),
                description=pattern_info["explanation"],
                pattern_before=pattern_info["before"],
                pattern_after=pattern_info["after"],
                explanation=pattern_info["explanation"],
                occurrence_count=0,
            )

            self.detected_optimizations[pattern_id] = optimization

    def analyze_comment(
        self,
        comment: OptimizationComment
    ) -> List[DetectedOptimization]:
        """
        Analyze a comment for optimization patterns.

        Args:
            comment: Optimization comment to analyze

        Returns:
            List of detected optimizations
        """
        detected = []

        # Skip if not an optimization/performance comment
        if comment.comment_type not in [
            CommentType.OPTIMIZATION,
            CommentType.PERFORMANCE,
        ]:
            return detected

        # Match against known patterns
        for pattern_id, pattern_info in self.KNOWN_PATTERNS.items():
            keywords = pattern_info.get("keywords", [])

            # Check if comment mentions this optimization
            comment_lower = comment.description.lower()
            if any(keyword in comment_lower for keyword in keywords):
                # Get or create optimization
                if pattern_id in self.detected_optimizations:
                    optimization = self.detected_optimizations[pattern_id]
                    optimization.occurrence_count += 1
                    optimization.related_comment_ids.append(comment.comment_id)
                else:
                    optimization = DetectedOptimization(
                        optimization_id=pattern_id,
                        category=pattern_info["category"],
                        impact=pattern_info["impact"],
                        title=pattern_id.replace("_", " ").title(),
                        description=pattern_info["explanation"],
                        pattern_before=pattern_info["before"],
                        pattern_after=pattern_info["after"],
                        explanation=pattern_info["explanation"],
                        related_comment_ids=[comment.comment_id],
                    )
                    self.detected_optimizations[pattern_id] = optimization

                detected.append(optimization)

        # Try to extract new patterns from code snippets
        if comment.code_before and comment.code_after:
            new_pattern = self._extract_new_pattern(comment)
            if new_pattern:
                detected.append(new_pattern)

        return detected

    def _extract_new_pattern(
        self,
        comment: OptimizationComment
    ) -> Optional[DetectedOptimization]:
        """
        Extract a new optimization pattern from comment.

        Args:
            comment: Comment with before/after code

        Returns:
            New DetectedOptimization or None
        """
        if not comment.code_before or not comment.code_after:
            return None

        # Generate pattern ID
        pattern_id = f"custom_{comment.comment_id}"

        # Determine category from comment type and keywords
        category = self._infer_category(comment)

        # Determine impact from severity
        impact = self._infer_impact(comment)

        # Create optimization
        optimization = DetectedOptimization(
            optimization_id=pattern_id,
            category=category,
            impact=impact,
            title=comment.title,
            description=comment.description,
            pattern_before=comment.code_before.code,
            pattern_after=comment.code_after.code,
            language=comment.code_after.language,
            explanation=comment.description,
            related_comment_ids=[comment.comment_id],
        )

        self.detected_optimizations[pattern_id] = optimization

        return optimization

    def _infer_category(self, comment: OptimizationComment) -> OptimizationCategory:
        """Infer optimization category from comment."""
        desc_lower = comment.description.lower()

        if any(word in desc_lower for word in ["algorithm", "complexity", "o("]):
            return OptimizationCategory.ALGORITHMIC

        if any(word in desc_lower for word in ["memory", "heap", "allocation"]):
            return OptimizationCategory.MEMORY

        if any(word in desc_lower for word in ["cpu", "performance", "speed"]):
            return OptimizationCategory.CPU

        if any(word in desc_lower for word in ["cache", "caching", "memoize"]):
            return OptimizationCategory.CACHING

        if any(word in desc_lower for word in ["security", "vulnerable", "sanitize"]):
            return OptimizationCategory.SECURITY

        if any(word in desc_lower for word in ["readable", "clean", "clear"]):
            return OptimizationCategory.READABILITY

        if any(word in desc_lower for word in ["type", "annotation", "hint"]):
            return OptimizationCategory.TYPE_HINTS

        return OptimizationCategory.CODE_STRUCTURE

    def _infer_impact(self, comment: OptimizationComment) -> OptimizationImpact:
        """Infer optimization impact from comment."""
        from .comment_processor import CommentSeverity

        severity_to_impact = {
            CommentSeverity.BLOCKER: OptimizationImpact.HIGH,
            CommentSeverity.CRITICAL: OptimizationImpact.HIGH,
            CommentSeverity.MAJOR: OptimizationImpact.MEDIUM,
            CommentSeverity.MINOR: OptimizationImpact.LOW,
            CommentSeverity.INFO: OptimizationImpact.NEGLIGIBLE,
        }

        return severity_to_impact.get(comment.severity, OptimizationImpact.MEDIUM)

    def get_top_optimizations(
        self,
        limit: int = 10,
        category: Optional[OptimizationCategory] = None,
    ) -> List[DetectedOptimization]:
        """
        Get most common optimizations.

        Args:
            limit: Maximum number to return
            category: Filter by category

        Returns:
            List of optimizations sorted by occurrence
        """
        optimizations = list(self.detected_optimizations.values())

        # Filter by category
        if category:
            optimizations = [
                opt for opt in optimizations
                if opt.category == category
            ]

        # Sort by occurrence count
        optimizations.sort(key=lambda x: x.occurrence_count, reverse=True)

        return optimizations[:limit]

    def get_high_impact_optimizations(self) -> List[DetectedOptimization]:
        """Get high-impact optimizations."""
        return [
            opt for opt in self.detected_optimizations.values()
            if opt.impact == OptimizationImpact.HIGH
        ]

    def get_optimization_stats(self) -> Dict:
        """Get optimization statistics."""
        optimizations = list(self.detected_optimizations.values())

        if not optimizations:
            return {
                "total": 0,
                "by_category": {},
                "by_impact": {},
                "total_occurrences": 0,
            }

        return {
            "total": len(optimizations),
            "by_category": {
                category.value: len([
                    opt for opt in optimizations
                    if opt.category == category
                ])
                for category in OptimizationCategory
            },
            "by_impact": {
                impact.value: len([
                    opt for opt in optimizations
                    if opt.impact == impact
                ])
                for impact in OptimizationImpact
            },
            "total_occurrences": sum(opt.occurrence_count for opt in optimizations),
            "avg_occurrences": sum(opt.occurrence_count for opt in optimizations) / len(optimizations),
        }

    def create_training_material(
        self,
        optimization: DetectedOptimization
    ) -> str:
        """
        Create training material from optimization.

        Args:
            optimization: Optimization to create material for

        Returns:
            Markdown-formatted training content
        """
        content = f"""# {optimization.title}

## Category
{optimization.category.value}

## Impact
{optimization.impact.value}

## Description
{optimization.description}

## Before (Anti-pattern)
```{optimization.language}
{optimization.pattern_before}
```

## After (Recommended)
```{optimization.language}
{optimization.pattern_after}
```

## Explanation
{optimization.explanation}

## Statistics
- Occurrences: {optimization.occurrence_count}
- Success Rate: {optimization.success_rate:.1%}
- Avg Improvement: {optimization.avg_improvement:.1f}

## Related Comments
{len(optimization.related_comment_ids)} comment(s)
"""

        return content
