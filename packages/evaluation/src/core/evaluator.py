"""
Code Evaluator - Main evaluation engine.

Orchestrates comprehensive code evaluation including:
- Quality metrics analysis
- Test coverage analysis
- Performance benchmarking
- Integration with quality gates
"""

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from ..metrics.code_quality import (
    CodeQualityAnalyzer,
    CodeQualityMetrics,
    analyze_code_quality,
)


class EvaluationContext(BaseModel):
    """Context for code evaluation."""
    code: str
    language: str = "python"
    file_path: Optional[str] = None
    intent: Optional[str] = None  # Original intent/purpose
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    strict_mode: bool = False
    include_tests: bool = False
    test_code: Optional[str] = None


class EvaluationResult(BaseModel):
    """Complete evaluation result."""
    evaluation_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context: EvaluationContext

    # Quality Metrics
    quality_metrics: CodeQualityMetrics

    # Test Results
    test_coverage: float = 0.0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_total: int = 0

    # Performance
    evaluation_time_ms: int = 0

    # Decision
    passes_quality_gate: bool = False
    quality_gate_name: Optional[str] = None
    gate_failures: List[str] = Field(default_factory=list)

    # Recommendations
    priority_fixes: List[str] = Field(default_factory=list)
    suggested_improvements: List[str] = Field(default_factory=list)

    # Summary
    summary: str = ""
    can_commit: bool = False
    can_deploy: bool = False


class CodeEvaluator:
    """
    Main code evaluation engine.

    Orchestrates comprehensive code evaluation and provides
    actionable feedback for improvement.
    """

    def __init__(
        self,
        quality_analyzer: Optional[CodeQualityAnalyzer] = None,
        default_language: str = "python",
    ):
        """
        Initialize evaluator.

        Args:
            quality_analyzer: Optional custom quality analyzer
            default_language: Default programming language
        """
        self.quality_analyzer = quality_analyzer or CodeQualityAnalyzer()
        self.default_language = default_language

        # Evaluation history
        self._evaluation_history: List[EvaluationResult] = []

    def evaluate(
        self,
        code: str,
        language: Optional[str] = None,
        file_path: Optional[str] = None,
        intent: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        strict_mode: bool = False,
        test_code: Optional[str] = None,
        quality_gate: Optional[str] = None,
    ) -> EvaluationResult:
        """
        Evaluate code comprehensively.

        Args:
            code: Source code to evaluate
            language: Programming language
            file_path: Optional file path
            intent: Original intent/purpose
            agent_id: Agent that generated code
            session_id: Session identifier
            strict_mode: Apply strict quality standards
            test_code: Optional test code
            quality_gate: Quality gate name to check against

        Returns:
            EvaluationResult with comprehensive analysis
        """
        start_time = time.time()

        # Create evaluation ID
        eval_id = f"eval_{int(time.time() * 1000)}"

        # Create context
        context = EvaluationContext(
            code=code,
            language=language or self.default_language,
            file_path=file_path,
            intent=intent,
            agent_id=agent_id,
            session_id=session_id,
            strict_mode=strict_mode,
            include_tests=test_code is not None,
            test_code=test_code,
        )

        # Run quality analysis
        quality_metrics = self.quality_analyzer.analyze(
            code=code,
            language=context.language,
            strict=strict_mode,
        )

        # Analyze tests if provided
        test_coverage = 0.0
        tests_passed = 0
        tests_failed = 0
        tests_total = 0

        if test_code:
            test_results = self._analyze_tests(test_code, code, context.language)
            test_coverage = test_results["coverage"]
            tests_passed = test_results["passed"]
            tests_failed = test_results["failed"]
            tests_total = test_results["total"]

        # Create result
        result = EvaluationResult(
            evaluation_id=eval_id,
            context=context,
            quality_metrics=quality_metrics,
            test_coverage=test_coverage,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            tests_total=tests_total,
            evaluation_time_ms=int((time.time() - start_time) * 1000),
        )

        # Generate recommendations
        self._generate_recommendations(result)

        # Check quality gate if specified
        if quality_gate:
            from ..gates.quality_gate import get_quality_gate, check_quality_gate

            gate = get_quality_gate(quality_gate)
            if gate:
                gate_result = check_quality_gate(result, gate)
                result.passes_quality_gate = gate_result.passed
                result.quality_gate_name = quality_gate
                result.gate_failures = gate_result.failures

        # Determine commit/deploy readiness
        result.can_commit = self._can_commit(result)
        result.can_deploy = self._can_deploy(result)

        # Generate summary
        result.summary = self._generate_summary(result)

        # Store in history
        self._evaluation_history.append(result)

        return result

    def evaluate_file(
        self,
        file_path: Path,
        strict_mode: bool = False,
        quality_gate: Optional[str] = None,
    ) -> EvaluationResult:
        """
        Evaluate code from a file.

        Args:
            file_path: Path to file to evaluate
            strict_mode: Apply strict quality standards
            quality_gate: Quality gate name to check against

        Returns:
            EvaluationResult
        """
        # Detect language from extension
        language_map = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
        }

        language = language_map.get(file_path.suffix.lower(), "unknown")

        # Read code
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        return self.evaluate(
            code=code,
            language=language,
            file_path=str(file_path),
            strict_mode=strict_mode,
            quality_gate=quality_gate,
        )

    def batch_evaluate(
        self,
        files: List[Path],
        strict_mode: bool = False,
        quality_gate: Optional[str] = None,
    ) -> Dict[str, EvaluationResult]:
        """
        Evaluate multiple files.

        Args:
            files: List of file paths
            strict_mode: Apply strict quality standards
            quality_gate: Quality gate name to check against

        Returns:
            Dict mapping file paths to evaluation results
        """
        results = {}

        for file_path in files:
            try:
                result = self.evaluate_file(
                    file_path=file_path,
                    strict_mode=strict_mode,
                    quality_gate=quality_gate,
                )
                results[str(file_path)] = result
            except Exception as e:
                # Create failed result
                results[str(file_path)] = EvaluationResult(
                    evaluation_id=f"eval_failed_{int(time.time() * 1000)}",
                    context=EvaluationContext(
                        code="",
                        language="unknown",
                        file_path=str(file_path),
                    ),
                    quality_metrics=CodeQualityMetrics(
                        overall_score=0.0,
                        grade="F",
                        issues=[f"Failed to evaluate: {e}"],
                    ),
                    summary=f"Evaluation failed: {e}",
                )

        return results

    def _analyze_tests(
        self,
        test_code: str,
        source_code: str,
        language: str
    ) -> Dict:
        """
        Analyze test code and estimate coverage.

        This is a simplified implementation. Full implementation
        would integrate with coverage.py, jest, etc.

        Args:
            test_code: Test code
            source_code: Source code being tested
            language: Programming language

        Returns:
            Dict with test metrics
        """
        # Count test functions
        if language == "python":
            import re
            test_funcs = len(re.findall(r'def test_\w+', test_code))
            source_funcs = len(re.findall(r'def \w+', source_code))

            # Rough coverage estimate based on ratio
            coverage = min(100.0, (test_funcs / max(1, source_funcs)) * 100)

            return {
                "coverage": coverage,
                "passed": test_funcs,  # Assume all pass for now
                "failed": 0,
                "total": test_funcs,
            }

        # Default for other languages
        return {
            "coverage": 0.0,
            "passed": 0,
            "failed": 0,
            "total": 0,
        }

    def _generate_recommendations(self, result: EvaluationResult):
        """Generate priority fixes and improvements."""
        metrics = result.quality_metrics

        # Priority fixes (blocking issues)
        if metrics.critical_security_count > 0:
            result.priority_fixes.append(
                f"FIX CRITICAL: {metrics.critical_security_count} critical security issues must be resolved"
            )

        if metrics.overall_score < 50:
            result.priority_fixes.append(
                f"FIX: Overall quality score ({metrics.overall_score}) is below acceptable threshold"
            )

        if metrics.max_complexity > 20:
            result.priority_fixes.append(
                f"FIX: Maximum complexity ({metrics.max_complexity}) exceeds limit. Refactor complex functions."
            )

        # Suggested improvements (non-blocking)
        if metrics.type_coverage < 70 and metrics.total_functions > 0:
            result.suggested_improvements.append(
                f"Add type hints (current coverage: {metrics.type_coverage:.1f}%)"
            )

        if metrics.docstring_coverage < 80 and metrics.total_definitions > 0:
            result.suggested_improvements.append(
                f"Add docstrings (current coverage: {metrics.docstring_coverage:.1f}%)"
            )

        if result.test_coverage < 80 and result.tests_total > 0:
            result.suggested_improvements.append(
                f"Increase test coverage (current: {result.test_coverage:.1f}%)"
            )

        if metrics.comment_ratio < 10:
            result.suggested_improvements.append(
                "Add more comments to explain complex logic"
            )

        # Add quality-specific suggestions
        result.suggested_improvements.extend(metrics.suggestions)

    def _can_commit(self, result: EvaluationResult) -> bool:
        """Determine if code is ready to commit."""
        metrics = result.quality_metrics

        # Minimum standards for commit
        return (
            metrics.critical_security_count == 0 and
            metrics.overall_score >= 60 and
            len(result.priority_fixes) == 0
        )

    def _can_deploy(self, result: EvaluationResult) -> bool:
        """Determine if code is ready to deploy."""
        metrics = result.quality_metrics

        # Higher standards for deployment
        return (
            self._can_commit(result) and
            metrics.overall_score >= 85 and
            metrics.high_security_count == 0 and
            result.test_coverage >= 80
        )

    def _generate_summary(self, result: EvaluationResult) -> str:
        """Generate human-readable summary."""
        metrics = result.quality_metrics

        lines = [
            f"Code Quality: {metrics.grade} ({metrics.overall_score:.1f}/100)",
            f"Complexity: {metrics.average_complexity:.1f} (max: {metrics.max_complexity})",
            f"Type Coverage: {metrics.type_coverage:.1f}%",
            f"Documentation: {metrics.docstring_coverage:.1f}%",
        ]

        if result.context.include_tests:
            lines.append(f"Test Coverage: {result.test_coverage:.1f}%")

        if metrics.security_issues:
            lines.append(
                f"Security Issues: {len(metrics.security_issues)} "
                f"({metrics.critical_security_count} critical, {metrics.high_security_count} high)"
            )

        if result.passes_quality_gate:
            lines.append(f"✓ Passes quality gate: {result.quality_gate_name}")
        elif result.quality_gate_name:
            lines.append(f"✗ Fails quality gate: {result.quality_gate_name}")

        lines.append("")
        lines.append(f"Ready to commit: {'Yes' if result.can_commit else 'No'}")
        lines.append(f"Ready to deploy: {'Yes' if result.can_deploy else 'No'}")

        return "\n".join(lines)

    def get_evaluation_history(
        self,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[EvaluationResult]:
        """
        Get evaluation history.

        Args:
            agent_id: Filter by agent ID
            session_id: Filter by session ID
            limit: Maximum number of results

        Returns:
            List of evaluation results
        """
        filtered = self._evaluation_history

        if agent_id:
            filtered = [r for r in filtered if r.context.agent_id == agent_id]

        if session_id:
            filtered = [r for r in filtered if r.context.session_id == session_id]

        # Return most recent first
        return sorted(
            filtered,
            key=lambda r: r.timestamp,
            reverse=True
        )[:limit]

    def get_quality_trends(
        self,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict:
        """
        Analyze quality trends over time.

        Args:
            agent_id: Filter by agent ID
            session_id: Filter by session ID

        Returns:
            Dict with trend analysis
        """
        history = self.get_evaluation_history(agent_id, session_id, limit=100)

        if not history:
            return {
                "evaluations_count": 0,
                "average_quality": 0.0,
                "quality_trend": "no_data",
            }

        # Calculate trends
        scores = [r.quality_metrics.overall_score for r in history]
        avg_quality = sum(scores) / len(scores)

        # Simple trend: compare first half vs second half
        if len(scores) >= 4:
            mid = len(scores) // 2
            first_half_avg = sum(scores[:mid]) / mid
            second_half_avg = sum(scores[mid:]) / (len(scores) - mid)

            if second_half_avg > first_half_avg + 5:
                trend = "improving"
            elif second_half_avg < first_half_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "evaluations_count": len(history),
            "average_quality": avg_quality,
            "quality_trend": trend,
            "latest_score": scores[0] if scores else 0.0,
            "best_score": max(scores) if scores else 0.0,
            "worst_score": min(scores) if scores else 0.0,
        }
