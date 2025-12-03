"""
Error Intelligence - Smart error detection and analysis.

Analyzes errors to extract patterns, classify types,
and provide intelligent diagnosis with recovery suggestions.
"""

import re
import traceback
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class ErrorCategory(str, Enum):
    """Error categories."""
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGIC = "logic"
    INTEGRATION = "integration"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    NETWORK = "network"
    SECURITY = "security"
    TYPE = "type"
    IMPORT = "import"
    ATTRIBUTE = "attribute"
    INDEX = "index"
    KEY = "key"
    VALUE = "value"
    TIMEOUT = "timeout"
    PERMISSION = "permission"


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    CRITICAL = "critical"  # System cannot function
    HIGH = "high"  # Feature broken
    MEDIUM = "medium"  # Partial functionality
    LOW = "low"  # Minor issue
    INFO = "info"  # Informational


class RootCause(BaseModel):
    """Root cause analysis."""
    category: ErrorCategory
    description: str
    confidence: float  # 0-100
    evidence: List[str] = Field(default_factory=list)
    likely_location: Optional[str] = None
    likely_line: Optional[int] = None


class RecoveryStrategy(BaseModel):
    """Recovery strategy for an error."""
    strategy_id: str
    name: str
    description: str
    steps: List[str]
    automated: bool = False
    success_rate: float = 0.0
    estimated_time_seconds: int = 0
    requires_user_input: bool = False
    side_effects: List[str] = Field(default_factory=list)


class ErrorAnalysis(BaseModel):
    """Complete error analysis."""
    error_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Error Details
    error_type: str
    error_message: str
    stack_trace: str

    # Classification
    category: ErrorCategory
    severity: ErrorSeverity

    # Analysis
    root_causes: List[RootCause] = Field(default_factory=list)
    contributing_factors: List[str] = Field(default_factory=list)

    # Recovery
    recovery_strategies: List[RecoveryStrategy] = Field(default_factory=list)
    recommended_strategy: Optional[str] = None

    # Context
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_context: Optional[str] = None
    environment: Dict[str, str] = Field(default_factory=dict)

    # Similarity
    similar_errors: List[str] = Field(default_factory=list)
    seen_before: bool = False
    previous_solutions: List[str] = Field(default_factory=list)


class ErrorIntelligence:
    """
    Intelligent error analysis system.

    Analyzes errors, determines root causes, and suggests
    recovery strategies based on patterns and history.
    """

    # Common error patterns
    ERROR_PATTERNS = {
        # Python Import Errors
        "ModuleNotFoundError": {
            "category": ErrorCategory.IMPORT,
            "severity": ErrorSeverity.HIGH,
            "pattern": r"No module named '(.+)'",
            "diagnosis": "Required Python package is not installed or not in PYTHONPATH",
            "strategies": [
                {
                    "id": "install_package",
                    "name": "Install Missing Package",
                    "automated": True,
                    "steps": [
                        "Identify package name from error",
                        "Run: pip install {package}",
                        "Verify installation",
                    ],
                },
                {
                    "id": "check_virtualenv",
                    "name": "Check Virtual Environment",
                    "automated": False,
                    "steps": [
                        "Verify correct virtual environment is activated",
                        "Check: which python",
                        "Activate correct environment if needed",
                    ],
                },
            ],
        },

        "ImportError": {
            "category": ErrorCategory.IMPORT,
            "severity": ErrorSeverity.HIGH,
            "pattern": r"cannot import name '(.+)' from '(.+)'",
            "diagnosis": "Symbol not found in module - may be version mismatch or typo",
            "strategies": [
                {
                    "id": "check_version",
                    "name": "Check Package Version",
                    "automated": True,
                    "steps": [
                        "Check installed version: pip show {package}",
                        "Compare with required version",
                        "Update if needed: pip install --upgrade {package}",
                    ],
                },
                {
                    "id": "verify_spelling",
                    "name": "Verify Import Name",
                    "automated": False,
                    "steps": [
                        "Check documentation for correct import name",
                        "Verify spelling and capitalization",
                        "Check if import has been renamed in newer versions",
                    ],
                },
            ],
        },

        # Type Errors
        "TypeError": {
            "category": ErrorCategory.TYPE,
            "severity": ErrorSeverity.MEDIUM,
            "pattern": r"(.+)",
            "diagnosis": "Type mismatch - value of wrong type used",
            "strategies": [
                {
                    "id": "add_type_checking",
                    "name": "Add Type Validation",
                    "automated": False,
                    "steps": [
                        "Add type hints to function signature",
                        "Add isinstance() checks",
                        "Use mypy for static type checking",
                    ],
                },
            ],
        },

        # Attribute Errors
        "AttributeError": {
            "category": ErrorCategory.ATTRIBUTE,
            "severity": ErrorSeverity.MEDIUM,
            "pattern": r"'(.+)' object has no attribute '(.+)'",
            "diagnosis": "Accessing non-existent attribute on object",
            "strategies": [
                {
                    "id": "check_none",
                    "name": "Check for None",
                    "automated": False,
                    "steps": [
                        "Verify object is not None before accessing",
                        "Add: if obj is not None:",
                        "Use optional chaining if available",
                    ],
                },
                {
                    "id": "verify_attribute",
                    "name": "Verify Attribute Name",
                    "automated": False,
                    "steps": [
                        "Check object documentation for correct attribute name",
                        "Use dir(obj) to see available attributes",
                        "Check for typos in attribute name",
                    ],
                },
            ],
        },

        # File Errors
        "FileNotFoundError": {
            "category": ErrorCategory.RESOURCE,
            "severity": ErrorSeverity.MEDIUM,
            "pattern": r"\[Errno 2\] No such file or directory: '(.+)'",
            "diagnosis": "File does not exist at specified path",
            "strategies": [
                {
                    "id": "check_path",
                    "name": "Verify File Path",
                    "automated": True,
                    "steps": [
                        "Check if file exists: Path(file).exists()",
                        "Verify path is correct (absolute vs relative)",
                        "Check current working directory",
                    ],
                },
                {
                    "id": "create_file",
                    "name": "Create Missing File",
                    "automated": False,
                    "steps": [
                        "Check if file should exist",
                        "Create file with default content if appropriate",
                        "Update code to handle missing files gracefully",
                    ],
                },
            ],
        },

        # Permission Errors
        "PermissionError": {
            "category": ErrorCategory.PERMISSION,
            "severity": ErrorSeverity.HIGH,
            "pattern": r"\[Errno 13\] Permission denied: '(.+)'",
            "diagnosis": "Insufficient permissions to access resource",
            "strategies": [
                {
                    "id": "check_permissions",
                    "name": "Check File Permissions",
                    "automated": True,
                    "steps": [
                        "Check file permissions: ls -la {file}",
                        "Verify user has read/write access",
                        "Change permissions if appropriate: chmod",
                    ],
                },
            ],
        },

        # Connection Errors
        "ConnectionError": {
            "category": ErrorCategory.NETWORK,
            "severity": ErrorSeverity.HIGH,
            "pattern": r"(.+)",
            "diagnosis": "Network connection failed",
            "strategies": [
                {
                    "id": "retry_connection",
                    "name": "Retry with Backoff",
                    "automated": True,
                    "steps": [
                        "Implement exponential backoff",
                        "Retry up to 3 times",
                        "Add timeout to prevent hanging",
                    ],
                },
                {
                    "id": "check_network",
                    "name": "Check Network Configuration",
                    "automated": False,
                    "steps": [
                        "Verify network connectivity",
                        "Check firewall settings",
                        "Verify correct URL/endpoint",
                    ],
                },
            ],
        },

        # Timeout Errors
        "TimeoutError": {
            "category": ErrorCategory.TIMEOUT,
            "severity": ErrorSeverity.MEDIUM,
            "pattern": r"(.+)",
            "diagnosis": "Operation took too long to complete",
            "strategies": [
                {
                    "id": "increase_timeout",
                    "name": "Increase Timeout",
                    "automated": True,
                    "steps": [
                        "Increase timeout value",
                        "Add progress monitoring",
                        "Consider operation may be too slow",
                    ],
                },
                {
                    "id": "optimize_operation",
                    "name": "Optimize Operation",
                    "automated": False,
                    "steps": [
                        "Profile operation to find bottleneck",
                        "Consider caching or pagination",
                        "Split into smaller operations",
                    ],
                },
            ],
        },

        # Key Errors
        "KeyError": {
            "category": ErrorCategory.KEY,
            "severity": ErrorSeverity.MEDIUM,
            "pattern": r"'(.+)'",
            "diagnosis": "Dictionary key does not exist",
            "strategies": [
                {
                    "id": "use_get",
                    "name": "Use dict.get()",
                    "automated": False,
                    "steps": [
                        "Replace dict[key] with dict.get(key, default)",
                        "Provides default value if key missing",
                        "Prevents KeyError exceptions",
                    ],
                },
                {
                    "id": "check_key",
                    "name": "Check Key Existence",
                    "automated": False,
                    "steps": [
                        "Add: if key in dict:",
                        "Handle missing key case explicitly",
                        "Log warning for unexpected missing keys",
                    ],
                },
            ],
        },

        # Index Errors
        "IndexError": {
            "category": ErrorCategory.INDEX,
            "severity": ErrorSeverity.MEDIUM,
            "pattern": r"list index out of range",
            "diagnosis": "Accessing list index that doesn't exist",
            "strategies": [
                {
                    "id": "check_length",
                    "name": "Check List Length",
                    "automated": False,
                    "steps": [
                        "Add: if len(list) > index:",
                        "Verify list is not empty before access",
                        "Use try/except for robust handling",
                    ],
                },
            ],
        },

        # Value Errors
        "ValueError": {
            "category": ErrorCategory.VALUE,
            "severity": ErrorSeverity.MEDIUM,
            "pattern": r"(.+)",
            "diagnosis": "Invalid value provided to function",
            "strategies": [
                {
                    "id": "validate_input",
                    "name": "Add Input Validation",
                    "automated": False,
                    "steps": [
                        "Add validation before function call",
                        "Check value is in expected range/format",
                        "Provide clear error messages",
                    ],
                },
            ],
        },
    }

    def __init__(self, memory_service=None):
        """
        Initialize error intelligence.

        Args:
            memory_service: Optional memory service for error history
        """
        self.memory_service = memory_service
        self.error_history: List[ErrorAnalysis] = []

    def analyze_error(
        self,
        error: Exception,
        context: Optional[Dict] = None,
    ) -> ErrorAnalysis:
        """
        Analyze an error and provide diagnosis.

        Args:
            error: Exception to analyze
            context: Optional context (file, line, code, etc.)

        Returns:
            ErrorAnalysis with diagnosis and recovery strategies
        """
        context = context or {}

        # Generate error ID
        error_id = f"err_{int(datetime.now().timestamp() * 1000)}"

        # Extract error details
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = "".join(traceback.format_tb(error.__traceback__)) if error.__traceback__ else ""

        # Classify error
        category, severity = self._classify_error(error_type, error_message)

        # Analyze root causes
        root_causes = self._analyze_root_causes(
            error_type, error_message, stack_trace, context
        )

        # Get recovery strategies
        recovery_strategies = self._get_recovery_strategies(error_type, error_message)

        # Recommend best strategy
        recommended_strategy = self._recommend_strategy(recovery_strategies)

        # Check for similar errors
        similar_errors, seen_before = self._find_similar_errors(error_type, error_message)

        # Create analysis
        analysis = ErrorAnalysis(
            error_id=error_id,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            category=category,
            severity=severity,
            root_causes=root_causes,
            recovery_strategies=recovery_strategies,
            recommended_strategy=recommended_strategy,
            file_path=context.get("file_path"),
            line_number=context.get("line_number"),
            code_context=context.get("code_context"),
            environment=context.get("environment", {}),
            similar_errors=similar_errors,
            seen_before=seen_before,
        )

        # Store in history
        self.error_history.append(analysis)

        # Store in memory service if available
        if self.memory_service:
            self._store_in_memory(analysis)

        return analysis

    def _classify_error(
        self,
        error_type: str,
        error_message: str
    ) -> Tuple[ErrorCategory, ErrorSeverity]:
        """Classify error by category and severity."""
        # Check known patterns
        if error_type in self.ERROR_PATTERNS:
            pattern_info = self.ERROR_PATTERNS[error_type]
            return pattern_info["category"], pattern_info["severity"]

        # Default classification based on error type
        if "Syntax" in error_type:
            return ErrorCategory.SYNTAX, ErrorSeverity.HIGH
        elif "Import" in error_type or "Module" in error_type:
            return ErrorCategory.IMPORT, ErrorSeverity.HIGH
        elif "Connection" in error_type or "Network" in error_type:
            return ErrorCategory.NETWORK, ErrorSeverity.HIGH
        elif "Timeout" in error_type:
            return ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM
        elif "Permission" in error_type:
            return ErrorCategory.PERMISSION, ErrorSeverity.HIGH
        else:
            return ErrorCategory.RUNTIME, ErrorSeverity.MEDIUM

    def _analyze_root_causes(
        self,
        error_type: str,
        error_message: str,
        stack_trace: str,
        context: Dict
    ) -> List[RootCause]:
        """Analyze and identify root causes."""
        root_causes = []

        # Check known patterns
        if error_type in self.ERROR_PATTERNS:
            pattern_info = self.ERROR_PATTERNS[error_type]

            root_cause = RootCause(
                category=pattern_info["category"],
                description=pattern_info["diagnosis"],
                confidence=85.0,
                evidence=[
                    f"Error type: {error_type}",
                    f"Message: {error_message}",
                ],
            )

            # Extract specific details from error message
            match = re.search(pattern_info["pattern"], error_message)
            if match:
                root_cause.evidence.append(f"Extracted: {match.groups()}")
                root_cause.confidence = 95.0

            root_causes.append(root_cause)

        return root_causes

    def _get_recovery_strategies(
        self,
        error_type: str,
        error_message: str
    ) -> List[RecoveryStrategy]:
        """Get recovery strategies for error."""
        strategies = []

        # Check known patterns
        if error_type in self.ERROR_PATTERNS:
            pattern_info = self.ERROR_PATTERNS[error_type]

            for strategy_info in pattern_info.get("strategies", []):
                strategy = RecoveryStrategy(
                    strategy_id=strategy_info["id"],
                    name=strategy_info["name"],
                    description=strategy_info.get("description", ""),
                    steps=strategy_info["steps"],
                    automated=strategy_info.get("automated", False),
                    success_rate=0.75,  # Default, will be updated from history
                )
                strategies.append(strategy)

        return strategies

    def _recommend_strategy(
        self,
        strategies: List[RecoveryStrategy]
    ) -> Optional[str]:
        """Recommend best recovery strategy."""
        if not strategies:
            return None

        # Prefer automated strategies with high success rate
        automated = [s for s in strategies if s.automated]
        if automated:
            best = max(automated, key=lambda s: s.success_rate)
            return best.strategy_id

        # Otherwise, recommend highest success rate
        best = max(strategies, key=lambda s: s.success_rate)
        return best.strategy_id

    def _find_similar_errors(
        self,
        error_type: str,
        error_message: str
    ) -> Tuple[List[str], bool]:
        """Find similar errors in history."""
        similar = []
        seen_before = False

        for past_error in self.error_history:
            if past_error.error_type == error_type:
                # Exact match
                if past_error.error_message == error_message:
                    seen_before = True
                    similar.append(past_error.error_id)
                # Similar message
                elif error_message in past_error.error_message or past_error.error_message in error_message:
                    similar.append(past_error.error_id)

        return similar, seen_before

    def _store_in_memory(self, analysis: ErrorAnalysis):
        """Store error analysis in memory service."""
        if not self.memory_service:
            return

        try:
            content = f"""# Error Analysis: {analysis.error_type}

## Error Message
{analysis.error_message}

## Category
{analysis.category.value}

## Severity
{analysis.severity.value}

## Root Causes
{chr(10).join(f"- {rc.description} (confidence: {rc.confidence:.0f}%)" for rc in analysis.root_causes)}

## Recovery Strategies
{chr(10).join(f"### {s.name}{chr(10)}{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(s.steps))}" for s in analysis.recovery_strategies)}

## Context
File: {analysis.file_path or 'Unknown'}
Line: {analysis.line_number or 'Unknown'}
"""

            self.memory_service.add_training_material(
                topic=f"error_{analysis.category.value}",
                file_name=f"{analysis.error_id}.md",
                content=content,
                agent_id="system",
            )

        except Exception:
            # Don't fail if storage fails
            pass

    def get_error_stats(self) -> Dict:
        """Get error statistics."""
        if not self.error_history:
            return {
                "total_errors": 0,
                "by_category": {},
                "by_severity": {},
                "unique_types": 0,
            }

        return {
            "total_errors": len(self.error_history),
            "by_category": {
                category.value: len([
                    e for e in self.error_history
                    if e.category == category
                ])
                for category in ErrorCategory
            },
            "by_severity": {
                severity.value: len([
                    e for e in self.error_history
                    if e.severity == severity
                ])
                for severity in ErrorSeverity
            },
            "unique_types": len(set(e.error_type for e in self.error_history)),
            "seen_before_count": len([e for e in self.error_history if e.seen_before]),
        }
