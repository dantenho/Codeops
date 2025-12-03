"""
Code Quality Metrics - Comprehensive code analysis.

Analyzes generated code across multiple dimensions:
- Static analysis (complexity, maintainability)
- Testing (coverage, completeness)
- Standards compliance (style, documentation)
- Performance characteristics
- Security issues
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field


class SecuritySeverity(str, Enum):
    """Security issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityIssue(BaseModel):
    """Security issue detected in code."""
    severity: SecuritySeverity
    category: str
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str


class ComplexityMetrics(BaseModel):
    """Cyclomatic complexity metrics."""
    cyclomatic_complexity: int
    average_complexity: float
    max_complexity: int
    complex_functions: List[Tuple[str, int]] = Field(default_factory=list)


class CodeQualityMetrics(BaseModel):
    """Comprehensive code quality assessment."""

    # Static Analysis
    complexity_score: float = 0.0  # 0-100
    cyclomatic_complexity: int = 0
    average_complexity: float = 0.0
    max_complexity: int = 0
    maintainability_index: float = 0.0  # 0-100

    # Type Coverage
    type_coverage: float = 0.0  # 0-100
    total_functions: int = 0
    typed_functions: int = 0

    # Documentation
    docstring_coverage: float = 0.0  # 0-100
    total_definitions: int = 0
    documented_definitions: int = 0

    # Standards Compliance
    linting_issues: int = 0
    formatting_issues: int = 0
    naming_violations: int = 0

    # Security
    security_issues: List[SecurityIssue] = Field(default_factory=list)
    critical_security_count: int = 0
    high_security_count: int = 0

    # Performance
    estimated_runtime_complexity: str = "O(1)"  # Big-O notation
    memory_efficiency_score: float = 50.0  # 0-100

    # Code Structure
    lines_of_code: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    comment_ratio: float = 0.0

    # Overall
    overall_score: float = 0.0  # Weighted composite 0-100
    grade: str = "C"  # A, B, C, D, F

    # Detailed Issues
    issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class CodeQualityAnalyzer:
    """
    Analyzes code quality across multiple dimensions.

    Provides comprehensive assessment of generated code
    with actionable feedback for improvements.
    """

    # Security patterns to detect
    SECURITY_PATTERNS = [
        {
            "pattern": r"eval\s*\(",
            "severity": SecuritySeverity.CRITICAL,
            "category": "Code Injection",
            "description": "Use of eval() can execute arbitrary code",
            "recommendation": "Avoid eval(). Use ast.literal_eval() for safe evaluation or validate input strictly."
        },
        {
            "pattern": r"exec\s*\(",
            "severity": SecuritySeverity.CRITICAL,
            "category": "Code Injection",
            "description": "Use of exec() can execute arbitrary code",
            "recommendation": "Avoid exec(). Refactor to use safer alternatives."
        },
        {
            "pattern": r"pickle\.loads?\s*\(",
            "severity": SecuritySeverity.HIGH,
            "category": "Deserialization",
            "description": "Pickle can execute arbitrary code during deserialization",
            "recommendation": "Use JSON or other safe serialization formats. If pickle required, validate sources."
        },
        {
            "pattern": r"shell\s*=\s*True",
            "severity": SecuritySeverity.HIGH,
            "category": "Command Injection",
            "description": "shell=True in subprocess can lead to command injection",
            "recommendation": "Use shell=False and pass command as list. Validate all user input."
        },
        {
            "pattern": r"(?:password|secret|key|token)\s*=\s*['\"][\w\-]+['\"]",
            "severity": SecuritySeverity.CRITICAL,
            "category": "Hardcoded Secrets",
            "description": "Hardcoded credentials detected",
            "recommendation": "Use environment variables or secret management systems."
        },
        {
            "pattern": r"random\.random\(\)",
            "severity": SecuritySeverity.MEDIUM,
            "category": "Weak Randomness",
            "description": "random module not suitable for security purposes",
            "recommendation": "Use secrets module for cryptographic randomness."
        },
        {
            "pattern": r"\.format\s*\(.*sql.*\)",
            "severity": SecuritySeverity.HIGH,
            "category": "SQL Injection",
            "description": "String formatting with SQL queries can lead to injection",
            "recommendation": "Use parameterized queries or ORM."
        },
    ]

    # Naming conventions
    NAMING_PATTERNS = {
        "function": r"^[a-z_][a-z0-9_]*$",
        "class": r"^[A-Z][a-zA-Z0-9]*$",
        "constant": r"^[A-Z_][A-Z0-9_]*$",
        "variable": r"^[a-z_][a-z0-9_]*$",
    }

    def __init__(self):
        """Initialize the analyzer."""
        self.metrics = CodeQualityMetrics()

    def analyze(
        self,
        code: str,
        language: str = "python",
        strict: bool = False
    ) -> CodeQualityMetrics:
        """
        Analyze code quality.

        Args:
            code: Source code to analyze
            language: Programming language
            strict: Whether to apply strict quality standards

        Returns:
            CodeQualityMetrics with comprehensive analysis
        """
        self.metrics = CodeQualityMetrics()

        if language.lower() == "python":
            self._analyze_python(code, strict)
        else:
            # For other languages, use basic text analysis
            self._analyze_generic(code, strict)

        # Calculate overall score
        self._calculate_overall_score(strict)

        return self.metrics

    def _analyze_python(self, code: str, strict: bool):
        """Analyze Python code using AST."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.metrics.issues.append(f"Syntax error: {e}")
            self.metrics.overall_score = 0.0
            self.metrics.grade = "F"
            return

        # Line counting
        self._count_lines(code)

        # Complexity analysis
        self._analyze_complexity(tree)

        # Type coverage
        self._analyze_type_coverage(tree)

        # Documentation coverage
        self._analyze_documentation(tree)

        # Naming conventions
        self._analyze_naming(tree)

        # Security issues
        self._analyze_security(code)

        # Performance estimation
        self._analyze_performance(tree, code)

        # Maintainability index
        self._calculate_maintainability_index()

    def _analyze_generic(self, code: str, strict: bool):
        """Generic analysis for non-Python code."""
        self._count_lines(code)

        # Basic security check
        self._analyze_security(code)

        # Estimate complexity from code structure
        lines = [l for l in code.split('\n') if l.strip()]
        self.metrics.cyclomatic_complexity = len([l for l in lines if any(
            keyword in l for keyword in ['if', 'for', 'while', 'case', 'catch']
        )])

        # Basic scoring
        self.metrics.complexity_score = max(0, 100 - self.metrics.cyclomatic_complexity * 2)

    def _count_lines(self, code: str):
        """Count lines of code, comments, and blanks."""
        lines = code.split('\n')
        self.metrics.lines_of_code = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        self.metrics.comment_lines = len([l for l in lines if l.strip().startswith('#')])
        self.metrics.blank_lines = len([l for l in lines if not l.strip()])

        total_lines = len(lines)
        if total_lines > 0:
            self.metrics.comment_ratio = (self.metrics.comment_lines / total_lines) * 100

    def _analyze_complexity(self, tree: ast.AST):
        """Calculate cyclomatic complexity."""
        complexities = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_function_complexity(node)
                complexities.append((node.name, complexity))

        if complexities:
            self.metrics.cyclomatic_complexity = sum(c for _, c in complexities)
            self.metrics.average_complexity = self.metrics.cyclomatic_complexity / len(complexities)
            self.metrics.max_complexity = max(c for _, c in complexities)

            # Track complex functions (complexity > 10)
            self.metrics.complex_functions = [
                (name, comp) for name, comp in complexities if comp > 10
            ]

            # Score: Lower complexity is better
            # 1-5: 100, 6-10: 80, 11-15: 60, 16-20: 40, 21+: 20
            if self.metrics.average_complexity <= 5:
                self.metrics.complexity_score = 100.0
            elif self.metrics.average_complexity <= 10:
                self.metrics.complexity_score = 80.0
            elif self.metrics.average_complexity <= 15:
                self.metrics.complexity_score = 60.0
            elif self.metrics.average_complexity <= 20:
                self.metrics.complexity_score = 40.0
            else:
                self.metrics.complexity_score = 20.0

            if self.metrics.max_complexity > 15:
                self.metrics.warnings.append(
                    f"High complexity detected (max: {self.metrics.max_complexity}). Consider refactoring."
                )
        else:
            self.metrics.complexity_score = 100.0

    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += 1

        return complexity

    def _analyze_type_coverage(self, tree: ast.AST):
        """Analyze type hint coverage."""
        functions = []
        typed_functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node)

                # Check if function has return type annotation
                has_return_type = node.returns is not None

                # Check if arguments have type annotations
                args_with_types = sum(
                    1 for arg in node.args.args if arg.annotation is not None
                )
                total_args = len(node.args.args)

                # Consider function typed if it has return type and >50% args typed
                if has_return_type and (total_args == 0 or args_with_types / total_args > 0.5):
                    typed_functions.append(node)

        self.metrics.total_functions = len(functions)
        self.metrics.typed_functions = len(typed_functions)

        if self.metrics.total_functions > 0:
            self.metrics.type_coverage = (
                self.metrics.typed_functions / self.metrics.total_functions
            ) * 100
        else:
            self.metrics.type_coverage = 100.0  # No functions to type

        if self.metrics.type_coverage < 70 and self.metrics.total_functions > 0:
            self.metrics.suggestions.append(
                "Add type hints to improve code quality and IDE support."
            )

    def _analyze_documentation(self, tree: ast.AST):
        """Analyze docstring coverage."""
        definitions = []
        documented = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                definitions.append(node)

                # Check for docstring
                if (node.body and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                    documented.append(node)

        self.metrics.total_definitions = len(definitions)
        self.metrics.documented_definitions = len(documented)

        if self.metrics.total_definitions > 0:
            self.metrics.docstring_coverage = (
                self.metrics.documented_definitions / self.metrics.total_definitions
            ) * 100
        else:
            self.metrics.docstring_coverage = 100.0

        if self.metrics.docstring_coverage < 80 and self.metrics.total_definitions > 0:
            self.metrics.suggestions.append(
                "Add docstrings to functions and classes for better documentation."
            )

    def _analyze_naming(self, tree: ast.AST):
        """Check naming conventions."""
        violations = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(self.NAMING_PATTERNS["function"], node.name):
                    violations += 1
                    self.metrics.issues.append(
                        f"Function '{node.name}' doesn't follow snake_case convention"
                    )

            elif isinstance(node, ast.ClassDef):
                if not re.match(self.NAMING_PATTERNS["class"], node.name):
                    violations += 1
                    self.metrics.issues.append(
                        f"Class '{node.name}' doesn't follow PascalCase convention"
                    )

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Check if it looks like a constant (all caps)
                        if target.id.isupper():
                            if not re.match(self.NAMING_PATTERNS["constant"], target.id):
                                violations += 1

        self.metrics.naming_violations = violations

    def _analyze_security(self, code: str):
        """Detect security issues."""
        issues = []

        for pattern_info in self.SECURITY_PATTERNS:
            matches = re.finditer(pattern_info["pattern"], code, re.IGNORECASE)

            for match in matches:
                # Find line number
                line_num = code[:match.start()].count('\n') + 1

                # Extract code snippet
                lines = code.split('\n')
                snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""

                issue = SecurityIssue(
                    severity=pattern_info["severity"],
                    category=pattern_info["category"],
                    description=pattern_info["description"],
                    line_number=line_num,
                    code_snippet=snippet,
                    recommendation=pattern_info["recommendation"]
                )
                issues.append(issue)

        self.metrics.security_issues = issues
        self.metrics.critical_security_count = len([
            i for i in issues if i.severity == SecuritySeverity.CRITICAL
        ])
        self.metrics.high_security_count = len([
            i for i in issues if i.severity == SecuritySeverity.HIGH
        ])

        if self.metrics.critical_security_count > 0:
            self.metrics.issues.append(
                f"CRITICAL: {self.metrics.critical_security_count} critical security issues detected"
            )

        if self.metrics.high_security_count > 0:
            self.metrics.warnings.append(
                f"{self.metrics.high_security_count} high-severity security issues detected"
            )

    def _analyze_performance(self, tree: ast.AST, code: str):
        """Estimate performance characteristics."""
        # Detect nested loops for complexity estimation
        max_nesting = 0

        def check_nesting(node, depth=0):
            nonlocal max_nesting
            max_nesting = max(max_nesting, depth)

            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                    check_nesting(child, depth + 1)
                else:
                    check_nesting(child, depth)

        check_nesting(tree)

        # Estimate Big-O complexity
        if max_nesting == 0:
            self.metrics.estimated_runtime_complexity = "O(1)"
            self.metrics.memory_efficiency_score = 90.0
        elif max_nesting == 1:
            self.metrics.estimated_runtime_complexity = "O(n)"
            self.metrics.memory_efficiency_score = 80.0
        elif max_nesting == 2:
            self.metrics.estimated_runtime_complexity = "O(n²)"
            self.metrics.memory_efficiency_score = 60.0
            self.metrics.warnings.append(
                "Nested loops detected. Consider optimizing for better performance."
            )
        else:
            self.metrics.estimated_runtime_complexity = f"O(n^{max_nesting})"
            self.metrics.memory_efficiency_score = 40.0
            self.metrics.issues.append(
                f"High complexity detected ({max_nesting} levels of nesting). Refactoring recommended."
            )

        # Check for potential memory issues
        if "list(" in code and "range(" in code:
            self.metrics.suggestions.append(
                "Consider using generators instead of lists for large ranges to save memory."
            )

    def _calculate_maintainability_index(self):
        """
        Calculate maintainability index (0-100).

        Based on simplified version of Maintainability Index formula:
        MI = max(0, 171 - 5.2*ln(V) - 0.23*G - 16.2*ln(L)) * 100/171

        Where:
        - V = Halstead Volume (approximated by LOC)
        - G = Cyclomatic Complexity
        - L = Lines of Code

        Simplified for practical use without full Halstead metrics.
        """
        import math

        loc = max(1, self.metrics.lines_of_code)
        complexity = max(1, self.metrics.cyclomatic_complexity)

        # Simplified MI calculation
        volume = loc * math.log(max(2, loc))
        mi = max(0, 171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(loc))
        self.metrics.maintainability_index = (mi * 100) / 171

        if self.metrics.maintainability_index < 50:
            self.metrics.warnings.append(
                "Low maintainability index. Code may be difficult to maintain."
            )

    def _calculate_overall_score(self, strict: bool):
        """Calculate weighted overall quality score."""
        weights = {
            "complexity": 0.20,
            "type_coverage": 0.15,
            "docstring": 0.15,
            "maintainability": 0.20,
            "security": 0.20,
            "performance": 0.10,
        }

        # Security score (0-100)
        security_score = 100.0
        if self.metrics.critical_security_count > 0:
            security_score = 0.0  # Critical issues = instant fail
        elif self.metrics.high_security_count > 0:
            security_score = max(0, 100 - self.metrics.high_security_count * 30)
        elif len(self.metrics.security_issues) > 0:
            security_score = max(50, 100 - len(self.metrics.security_issues) * 10)

        # Calculate weighted score
        score = (
            self.metrics.complexity_score * weights["complexity"] +
            self.metrics.type_coverage * weights["type_coverage"] +
            self.metrics.docstring_coverage * weights["docstring"] +
            self.metrics.maintainability_index * weights["maintainability"] +
            security_score * weights["security"] +
            self.metrics.memory_efficiency_score * weights["performance"]
        )

        self.metrics.overall_score = round(score, 2)

        # Assign grade
        if self.metrics.overall_score >= 90:
            self.metrics.grade = "A"
        elif self.metrics.overall_score >= 80:
            self.metrics.grade = "B"
        elif self.metrics.overall_score >= 70:
            self.metrics.grade = "C"
        elif self.metrics.overall_score >= 60:
            self.metrics.grade = "D"
        else:
            self.metrics.grade = "F"

        # Apply strict standards if requested
        if strict and self.metrics.overall_score < 85:
            self.metrics.warnings.append(
                "Strict mode: Code quality below 85%. Improvements required."
            )


def analyze_code_quality(
    code: str,
    language: str = "python",
    strict: bool = False
) -> CodeQualityMetrics:
    """
    Convenience function to analyze code quality.

    Args:
        code: Source code to analyze
        language: Programming language
        strict: Whether to apply strict quality standards

    Returns:
        CodeQualityMetrics with comprehensive analysis
    """
    analyzer = CodeQualityAnalyzer()
    return analyzer.analyze(code, language, strict)
