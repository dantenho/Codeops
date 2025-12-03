"""
Diagnosis Engine - Advanced error diagnosis with AST analysis.

Performs deep analysis of errors using abstract syntax trees,
static analysis, and pattern matching to provide precise diagnosis.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .error_intelligence import ErrorAnalysis, RootCause, ErrorCategory


class DiagnosisEngine:
    """
    Advanced error diagnosis engine.

    Uses AST analysis and pattern matching to provide
    deep insights into error causes.
    """

    def __init__(self):
        """Initialize diagnosis engine."""
        self.analysis_cache: Dict[str, ErrorAnalysis] = {}

    def diagnose(
        self,
        error_analysis: ErrorAnalysis,
        source_code: Optional[str] = None,
    ) -> ErrorAnalysis:
        """
        Perform deep diagnosis on error.

        Args:
            error_analysis: Initial error analysis
            source_code: Optional source code for AST analysis

        Returns:
            Enhanced error analysis with additional insights
        """
        # Enhance root causes
        if source_code:
            additional_causes = self._analyze_source_code(
                source_code,
                error_analysis
            )
            error_analysis.root_causes.extend(additional_causes)

        # Identify contributing factors
        error_analysis.contributing_factors = self._identify_contributing_factors(
            error_analysis
        )

        # Update confidence scores based on analysis
        self._update_confidence_scores(error_analysis)

        return error_analysis

    def _analyze_source_code(
        self,
        source_code: str,
        error_analysis: ErrorAnalysis
    ) -> List[RootCause]:
        """Analyze source code using AST."""
        additional_causes = []

        try:
            tree = ast.parse(source_code)

            # Check for common anti-patterns
            if error_analysis.error_type == "AttributeError":
                causes = self._check_attribute_error(tree, error_analysis)
                additional_causes.extend(causes)

            elif error_analysis.error_type == "TypeError":
                causes = self._check_type_error(tree, error_analysis)
                additional_causes.extend(causes)

            elif error_analysis.error_type == "NameError":
                causes = self._check_name_error(tree, error_analysis)
                additional_causes.extend(causes)

            elif error_analysis.error_type in ["KeyError", "IndexError"]:
                causes = self._check_access_error(tree, error_analysis)
                additional_causes.extend(causes)

        except SyntaxError:
            # If code has syntax errors, that's a root cause
            additional_causes.append(
                RootCause(
                    category=ErrorCategory.SYNTAX,
                    description="Source code contains syntax errors",
                    confidence=100.0,
                    evidence=["AST parsing failed"],
                )
            )

        return additional_causes

    def _check_attribute_error(
        self,
        tree: ast.AST,
        error_analysis: ErrorAnalysis
    ) -> List[RootCause]:
        """Check for AttributeError patterns."""
        causes = []

        # Extract attribute name from error message
        match = re.search(r"has no attribute '(.+)'", error_analysis.error_message)
        if not match:
            return causes

        attr_name = match.group(1)

        # Check for None assignments
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Check if any target could be None
                if isinstance(node.value, ast.Constant) and node.value.value is None:
                    causes.append(
                        RootCause(
                            category=ErrorCategory.LOGIC,
                            description=f"Variable assigned None, then attribute '{attr_name}' accessed",
                            confidence=70.0,
                            evidence=["None assignment found in code"],
                        )
                    )

        # Check for missing None checks
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr == attr_name:
                    # Check if there's a None check before this access
                    # This is simplified - full implementation would check control flow
                    causes.append(
                        RootCause(
                            category=ErrorCategory.LOGIC,
                            description=f"Attribute '{attr_name}' accessed without None check",
                            confidence=60.0,
                            evidence=["Attribute access found"],
                        )
                    )
                    break

        return causes

    def _check_type_error(
        self,
        tree: ast.AST,
        error_analysis: ErrorAnalysis
    ) -> List[RootCause]:
        """Check for TypeError patterns."""
        causes = []

        # Check for missing type hints
        has_type_hints = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    has_type_hints = True
                    break

        if not has_type_hints:
            causes.append(
                RootCause(
                    category=ErrorCategory.TYPE,
                    description="No type hints found - could prevent type-related errors",
                    confidence=50.0,
                    evidence=["No function annotations found"],
                )
            )

        return causes

    def _check_name_error(
        self,
        tree: ast.AST,
        error_analysis: ErrorAnalysis
    ) -> List[RootCause]:
        """Check for NameError patterns."""
        causes = []

        # Extract undefined name from error message
        match = re.search(r"name '(.+)' is not defined", error_analysis.error_message)
        if not match:
            return causes

        undefined_name = match.group(1)

        # Check for similar names (possible typo)
        defined_names = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined_names.add(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined_names.add(node.id)

        # Find similar names (Levenshtein distance)
        similar = self._find_similar_names(undefined_name, defined_names)
        if similar:
            causes.append(
                RootCause(
                    category=ErrorCategory.SYNTAX,
                    description=f"Possible typo: '{undefined_name}' not found, but similar names exist: {similar}",
                    confidence=80.0,
                    evidence=[f"Similar names: {', '.join(similar)}"],
                )
            )

        return causes

    def _check_access_error(
        self,
        tree: ast.AST,
        error_analysis: ErrorAnalysis
    ) -> List[RootCause]:
        """Check for KeyError/IndexError patterns."""
        causes = []

        # Check for direct access without checking
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript):
                # Check if there's bounds checking or key existence check
                # This is simplified - would need control flow analysis
                if error_analysis.error_type == "KeyError":
                    causes.append(
                        RootCause(
                            category=ErrorCategory.LOGIC,
                            description="Dictionary key accessed without existence check",
                            confidence=60.0,
                            evidence=["Direct subscript access found"],
                        )
                    )
                elif error_analysis.error_type == "IndexError":
                    causes.append(
                        RootCause(
                            category=ErrorCategory.LOGIC,
                            description="List index accessed without bounds check",
                            confidence=60.0,
                            evidence=["Direct subscript access found"],
                        )
                    )
                break

        return causes

    def _identify_contributing_factors(
        self,
        error_analysis: ErrorAnalysis
    ) -> List[str]:
        """Identify contributing factors to error."""
        factors = []

        # Check stack trace depth
        if error_analysis.stack_trace:
            lines = error_analysis.stack_trace.count('\n')
            if lines > 20:
                factors.append("Deep call stack - complex execution path")

        # Check for similar past errors
        if error_analysis.seen_before:
            factors.append("This error has occurred before - may be recurring issue")

        # Category-specific factors
        if error_analysis.category == ErrorCategory.NETWORK:
            factors.append("Network-related - may be intermittent connectivity issue")

        elif error_analysis.category == ErrorCategory.TIMEOUT:
            factors.append("Timeout - operation may be too slow or unoptimized")

        elif error_analysis.category == ErrorCategory.DEPENDENCY:
            factors.append("Dependency issue - check package versions and compatibility")

        elif error_analysis.category == ErrorCategory.CONFIGURATION:
            factors.append("Configuration issue - verify settings and environment variables")

        return factors

    def _update_confidence_scores(self, error_analysis: ErrorAnalysis):
        """Update confidence scores based on evidence."""
        for root_cause in error_analysis.root_causes:
            # Increase confidence if multiple evidence points
            if len(root_cause.evidence) > 2:
                root_cause.confidence = min(100.0, root_cause.confidence + 10)

            # Increase confidence if seen before
            if error_analysis.seen_before:
                root_cause.confidence = min(100.0, root_cause.confidence + 15)

    def _find_similar_names(
        self,
        target: str,
        candidates: Set[str],
        max_distance: int = 2
    ) -> List[str]:
        """Find similar names using Levenshtein distance."""
        similar = []

        for candidate in candidates:
            distance = self._levenshtein_distance(target.lower(), candidate.lower())
            if 0 < distance <= max_distance:
                similar.append(candidate)

        return sorted(similar, key=lambda x: self._levenshtein_distance(target.lower(), x.lower()))

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def generate_diagnostic_report(
        self,
        error_analysis: ErrorAnalysis
    ) -> str:
        """Generate human-readable diagnostic report."""
        lines = [
            f"# Error Diagnostic Report",
            f"",
            f"## Error: {error_analysis.error_type}",
            f"**Message:** {error_analysis.error_message}",
            f"**Category:** {error_analysis.category.value}",
            f"**Severity:** {error_analysis.severity.value}",
            f"",
        ]

        if error_analysis.file_path:
            lines.append(f"**Location:** {error_analysis.file_path}")
            if error_analysis.line_number:
                lines.append(f"**Line:** {error_analysis.line_number}")
            lines.append("")

        # Root causes
        if error_analysis.root_causes:
            lines.append("## Root Causes")
            for i, cause in enumerate(error_analysis.root_causes, 1):
                lines.append(f"{i}. **{cause.description}** (confidence: {cause.confidence:.0f}%)")
                if cause.evidence:
                    lines.append(f"   - Evidence: {', '.join(cause.evidence)}")
            lines.append("")

        # Contributing factors
        if error_analysis.contributing_factors:
            lines.append("## Contributing Factors")
            for factor in error_analysis.contributing_factors:
                lines.append(f"- {factor}")
            lines.append("")

        # Recovery strategies
        if error_analysis.recovery_strategies:
            lines.append("## Recovery Strategies")
            for i, strategy in enumerate(error_analysis.recovery_strategies, 1):
                lines.append(f"### {i}. {strategy.name}")
                if strategy.automated:
                    lines.append("   **(Automated)**")
                lines.append("")
                for j, step in enumerate(strategy.steps, 1):
                    lines.append(f"   {j}. {step}")
                lines.append("")

        # Recommended action
        if error_analysis.recommended_strategy:
            recommended = next(
                (s for s in error_analysis.recovery_strategies
                 if s.strategy_id == error_analysis.recommended_strategy),
                None
            )
            if recommended:
                lines.append(f"## Recommended Action")
                lines.append(f"**{recommended.name}**")
                lines.append("")

        # Similar errors
        if error_analysis.similar_errors:
            lines.append(f"## Similar Errors")
            lines.append(f"Found {len(error_analysis.similar_errors)} similar error(s) in history")
            if error_analysis.seen_before:
                lines.append("⚠️ This exact error has been seen before")
            lines.append("")

        return "\n".join(lines)
