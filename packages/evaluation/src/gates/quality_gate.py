"""
Quality Gates - Automated quality threshold enforcement.

Defines quality gates for different stages:
- Commit: Minimum standards for version control
- Pull Request: Standards for code review
- Production: High standards for deployment
"""

from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class QualityThresholds(BaseModel):
    """Quality thresholds for a gate."""
    overall_score: float = 70.0
    complexity_score: float = 70.0
    type_coverage: float = 60.0
    docstring_coverage: float = 60.0
    test_coverage: float = 60.0
    maintainability_index: float = 50.0
    max_complexity: int = 15
    critical_security_issues: int = 0
    high_security_issues: int = 0


class QualityGate(BaseModel):
    """Quality gate configuration."""
    name: str
    description: str
    thresholds: QualityThresholds
    strict_mode: bool = False
    block_on_failure: bool = True


class QualityGateResult(BaseModel):
    """Result of quality gate check."""
    gate_name: str
    passed: bool
    score: float
    failures: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    details: Dict = Field(default_factory=dict)


# Predefined quality gates
QUALITY_GATES = {
    "commit": QualityGate(
        name="commit",
        description="Minimum standards for committing code",
        thresholds=QualityThresholds(
            overall_score=70.0,
            complexity_score=75.0,
            type_coverage=60.0,
            docstring_coverage=70.0,
            test_coverage=80.0,
            maintainability_index=50.0,
            max_complexity=15,
            critical_security_issues=0,
            high_security_issues=0,
        ),
        strict_mode=False,
        block_on_failure=True,
    ),

    "pull_request": QualityGate(
        name="pull_request",
        description="Standards for pull request approval",
        thresholds=QualityThresholds(
            overall_score=85.0,
            complexity_score=80.0,
            type_coverage=70.0,
            docstring_coverage=90.0,
            test_coverage=90.0,
            maintainability_index=60.0,
            max_complexity=12,
            critical_security_issues=0,
            high_security_issues=0,
        ),
        strict_mode=True,
        block_on_failure=True,
    ),

    "production": QualityGate(
        name="production",
        description="High standards for production deployment",
        thresholds=QualityThresholds(
            overall_score=95.0,
            complexity_score=85.0,
            type_coverage=80.0,
            docstring_coverage=95.0,
            test_coverage=95.0,
            maintainability_index=70.0,
            max_complexity=10,
            critical_security_issues=0,
            high_security_issues=0,
        ),
        strict_mode=True,
        block_on_failure=True,
    ),

    "basic": QualityGate(
        name="basic",
        description="Basic quality standards",
        thresholds=QualityThresholds(
            overall_score=60.0,
            complexity_score=60.0,
            type_coverage=40.0,
            docstring_coverage=50.0,
            test_coverage=50.0,
            maintainability_index=40.0,
            max_complexity=20,
            critical_security_issues=0,
            high_security_issues=1,
        ),
        strict_mode=False,
        block_on_failure=False,
    ),
}


def load_custom_gates(config_path: Path) -> Dict[str, QualityGate]:
    """
    Load custom quality gates from YAML config.

    Args:
        config_path: Path to quality thresholds YAML

    Returns:
        Dict of quality gate name to QualityGate
    """
    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        gates = {}

        if "quality_gates" in config:
            for gate_name, gate_config in config["quality_gates"].items():
                # Convert config to QualityGate
                thresholds = QualityThresholds(**gate_config.get("thresholds", {}))

                gate = QualityGate(
                    name=gate_name,
                    description=gate_config.get("description", ""),
                    thresholds=thresholds,
                    strict_mode=gate_config.get("strict_mode", False),
                    block_on_failure=gate_config.get("block_on_failure", True),
                )

                gates[gate_name] = gate

        return gates

    except Exception as e:
        print(f"Warning: Failed to load custom gates: {e}")
        return {}


def get_quality_gate(
    name: str,
    custom_config_path: Optional[Path] = None
) -> Optional[QualityGate]:
    """
    Get quality gate by name.

    Args:
        name: Gate name
        custom_config_path: Optional path to custom config

    Returns:
        QualityGate or None if not found
    """
    # Check custom gates first
    if custom_config_path:
        custom_gates = load_custom_gates(custom_config_path)
        if name in custom_gates:
            return custom_gates[name]

    # Check predefined gates
    return QUALITY_GATES.get(name)


def check_quality_gate(
    evaluation_result,  # EvaluationResult (avoid circular import)
    gate: QualityGate
) -> QualityGateResult:
    """
    Check if evaluation result passes quality gate.

    Args:
        evaluation_result: EvaluationResult to check
        gate: QualityGate to check against

    Returns:
        QualityGateResult with pass/fail status
    """
    metrics = evaluation_result.quality_metrics
    thresholds = gate.thresholds

    failures = []
    warnings = []
    details = {}

    # Check overall score
    if metrics.overall_score < thresholds.overall_score:
        failures.append(
            f"Overall score {metrics.overall_score:.1f} < {thresholds.overall_score}"
        )
    details["overall_score"] = {
        "actual": metrics.overall_score,
        "threshold": thresholds.overall_score,
        "passed": metrics.overall_score >= thresholds.overall_score,
    }

    # Check complexity score
    if metrics.complexity_score < thresholds.complexity_score:
        failures.append(
            f"Complexity score {metrics.complexity_score:.1f} < {thresholds.complexity_score}"
        )
    details["complexity_score"] = {
        "actual": metrics.complexity_score,
        "threshold": thresholds.complexity_score,
        "passed": metrics.complexity_score >= thresholds.complexity_score,
    }

    # Check max complexity
    if metrics.max_complexity > thresholds.max_complexity:
        failures.append(
            f"Max complexity {metrics.max_complexity} > {thresholds.max_complexity}"
        )
    details["max_complexity"] = {
        "actual": metrics.max_complexity,
        "threshold": thresholds.max_complexity,
        "passed": metrics.max_complexity <= thresholds.max_complexity,
    }

    # Check type coverage
    if metrics.type_coverage < thresholds.type_coverage:
        failures.append(
            f"Type coverage {metrics.type_coverage:.1f}% < {thresholds.type_coverage}%"
        )
    details["type_coverage"] = {
        "actual": metrics.type_coverage,
        "threshold": thresholds.type_coverage,
        "passed": metrics.type_coverage >= thresholds.type_coverage,
    }

    # Check docstring coverage
    if metrics.docstring_coverage < thresholds.docstring_coverage:
        failures.append(
            f"Docstring coverage {metrics.docstring_coverage:.1f}% < {thresholds.docstring_coverage}%"
        )
    details["docstring_coverage"] = {
        "actual": metrics.docstring_coverage,
        "threshold": thresholds.docstring_coverage,
        "passed": metrics.docstring_coverage >= thresholds.docstring_coverage,
    }

    # Check test coverage
    if evaluation_result.context.include_tests:
        if evaluation_result.test_coverage < thresholds.test_coverage:
            failures.append(
                f"Test coverage {evaluation_result.test_coverage:.1f}% < {thresholds.test_coverage}%"
            )
        details["test_coverage"] = {
            "actual": evaluation_result.test_coverage,
            "threshold": thresholds.test_coverage,
            "passed": evaluation_result.test_coverage >= thresholds.test_coverage,
        }

    # Check maintainability
    if metrics.maintainability_index < thresholds.maintainability_index:
        failures.append(
            f"Maintainability index {metrics.maintainability_index:.1f} < {thresholds.maintainability_index}"
        )
    details["maintainability_index"] = {
        "actual": metrics.maintainability_index,
        "threshold": thresholds.maintainability_index,
        "passed": metrics.maintainability_index >= thresholds.maintainability_index,
    }

    # Check security issues
    if metrics.critical_security_count > thresholds.critical_security_issues:
        failures.append(
            f"Critical security issues: {metrics.critical_security_count} (max: {thresholds.critical_security_issues})"
        )
    details["critical_security"] = {
        "actual": metrics.critical_security_count,
        "threshold": thresholds.critical_security_issues,
        "passed": metrics.critical_security_count <= thresholds.critical_security_issues,
    }

    if metrics.high_security_count > thresholds.high_security_issues:
        failures.append(
            f"High security issues: {metrics.high_security_count} (max: {thresholds.high_security_issues})"
        )
    details["high_security"] = {
        "actual": metrics.high_security_count,
        "threshold": thresholds.high_security_issues,
        "passed": metrics.high_security_count <= thresholds.high_security_issues,
    }

    # Add warnings for near-threshold values
    for key, detail in details.items():
        if detail["passed"]:
            # Check if within 10% of threshold
            actual = detail["actual"]
            threshold = detail["threshold"]

            # For "less than" thresholds
            if key in ["max_complexity", "critical_security", "high_security"]:
                if actual > threshold * 0.7:
                    warnings.append(f"{key}: approaching threshold")
            # For "greater than" thresholds
            else:
                if actual < threshold * 1.1:
                    warnings.append(f"{key}: close to threshold")

    # Determine if passed
    passed = len(failures) == 0

    return QualityGateResult(
        gate_name=gate.name,
        passed=passed,
        score=metrics.overall_score,
        failures=failures,
        warnings=warnings,
        details=details,
    )


def get_recommended_gate(overall_score: float) -> str:
    """
    Recommend quality gate based on score.

    Args:
        overall_score: Overall quality score

    Returns:
        Recommended gate name
    """
    if overall_score >= 95:
        return "production"
    elif overall_score >= 85:
        return "pull_request"
    elif overall_score >= 70:
        return "commit"
    else:
        return "basic"


def create_gate_report(
    evaluation_result,  # EvaluationResult
    gate_result: QualityGateResult
) -> str:
    """
    Create human-readable gate report.

    Args:
        evaluation_result: EvaluationResult
        gate_result: QualityGateResult

    Returns:
        Formatted report string
    """
    lines = [
        f"Quality Gate: {gate_result.gate_name}",
        f"Status: {'✓ PASSED' if gate_result.passed else '✗ FAILED'}",
        f"Score: {gate_result.score:.1f}/100",
        "",
    ]

    if gate_result.failures:
        lines.append("Failures:")
        for failure in gate_result.failures:
            lines.append(f"  ✗ {failure}")
        lines.append("")

    if gate_result.warnings:
        lines.append("Warnings:")
        for warning in gate_result.warnings:
            lines.append(f"  ⚠ {warning}")
        lines.append("")

    # Detailed metrics
    lines.append("Detailed Metrics:")
    for key, detail in gate_result.details.items():
        status = "✓" if detail["passed"] else "✗"
        lines.append(
            f"  {status} {key}: {detail['actual']:.1f} "
            f"(threshold: {detail['threshold']:.1f})"
        )

    return "\n".join(lines)
