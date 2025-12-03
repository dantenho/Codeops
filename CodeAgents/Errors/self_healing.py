"""
Self-Healing System - Automated error recovery.

Implements self-healing mechanisms including auto-retry,
dependency installation, configuration correction, and rollback.
"""

import subprocess
import time
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .error_intelligence import ErrorAnalysis, RecoveryStrategy


class HealingStatus(str, Enum):
    """Status of healing attempt."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class HealingResult(BaseModel):
    """Result of healing attempt."""
    strategy_id: str
    status: HealingStatus
    message: str
    steps_completed: int = 0
    steps_total: int = 0
    duration_seconds: float = 0.0
    side_effects: List[str] = Field(default_factory=list)
    rollback_available: bool = False


class CircuitBreaker:
    """
    Circuit breaker pattern for external services.

    Prevents repeated calls to failing services.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            timeout_seconds: Seconds before trying again
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failures: Dict[str, int] = {}
        self.opened_at: Dict[str, float] = {}

    def is_open(self, service: str) -> bool:
        """Check if circuit is open for service."""
        if service not in self.opened_at:
            return False

        # Check if timeout has passed
        elapsed = time.time() - self.opened_at[service]
        if elapsed > self.timeout_seconds:
            # Reset circuit
            self.failures[service] = 0
            del self.opened_at[service]
            return False

        return True

    def record_success(self, service: str):
        """Record successful call."""
        self.failures[service] = 0
        if service in self.opened_at:
            del self.opened_at[service]

    def record_failure(self, service: str):
        """Record failed call."""
        self.failures[service] = self.failures.get(service, 0) + 1

        if self.failures[service] >= self.failure_threshold:
            self.opened_at[service] = time.time()


class SelfHealing:
    """
    Self-healing system for automated error recovery.

    Implements various healing strategies including:
    - Auto-retry with exponential backoff
    - Automatic dependency installation
    - Configuration auto-correction
    - Rollback to last known good state
    """

    def __init__(
        self,
        auto_install_packages: bool = False,
        max_retry_attempts: int = 3,
        require_confirmation: bool = True,
    ):
        """
        Initialize self-healing system.

        Args:
            auto_install_packages: Whether to auto-install missing packages
            max_retry_attempts: Maximum retry attempts
            require_confirmation: Whether to require user confirmation
        """
        self.auto_install_packages = auto_install_packages
        self.max_retry_attempts = max_retry_attempts
        self.require_confirmation = require_confirmation

        self.circuit_breaker = CircuitBreaker()
        self.healing_history: List[HealingResult] = []

    def attempt_healing(
        self,
        error_analysis: ErrorAnalysis,
        operation: Optional[Callable] = None,
    ) -> HealingResult:
        """
        Attempt to heal error.

        Args:
            error_analysis: Error analysis with recovery strategies
            operation: Optional operation to retry after healing

        Returns:
            HealingResult with outcome
        """
        if not error_analysis.recommended_strategy:
            return HealingResult(
                strategy_id="none",
                status=HealingStatus.SKIPPED,
                message="No recommended strategy available",
            )

        # Get recommended strategy
        strategy = next(
            (s for s in error_analysis.recovery_strategies
             if s.strategy_id == error_analysis.recommended_strategy),
            None
        )

        if not strategy:
            return HealingResult(
                strategy_id=error_analysis.recommended_strategy,
                status=HealingStatus.FAILED,
                message="Recommended strategy not found",
            )

        # Check if strategy requires confirmation
        if self.require_confirmation and not strategy.automated:
            return HealingResult(
                strategy_id=strategy.strategy_id,
                status=HealingStatus.SKIPPED,
                message="Strategy requires user confirmation",
            )

        # Execute strategy
        start_time = time.time()

        if strategy.strategy_id == "install_package":
            result = self._install_missing_package(error_analysis, strategy)
        elif strategy.strategy_id == "retry_connection":
            result = self._retry_with_backoff(operation, strategy)
        elif strategy.strategy_id == "check_path":
            result = self._verify_file_path(error_analysis, strategy)
        else:
            result = HealingResult(
                strategy_id=strategy.strategy_id,
                status=HealingStatus.SKIPPED,
                message=f"Strategy '{strategy.strategy_id}' not automated",
                steps_total=len(strategy.steps),
            )

        result.duration_seconds = time.time() - start_time

        # Store in history
        self.healing_history.append(result)

        return result

    def _install_missing_package(
        self,
        error_analysis: ErrorAnalysis,
        strategy: RecoveryStrategy,
    ) -> HealingResult:
        """Install missing Python package."""
        if not self.auto_install_packages:
            return HealingResult(
                strategy_id=strategy.strategy_id,
                status=HealingStatus.SKIPPED,
                message="Auto-install disabled - manual installation required",
            )

        # Extract package name from error message
        import re
        match = re.search(r"No module named '(.+?)'", error_analysis.error_message)
        if not match:
            return HealingResult(
                strategy_id=strategy.strategy_id,
                status=HealingStatus.FAILED,
                message="Could not extract package name from error",
            )

        package_name = match.group(1)

        # Handle package name mapping (e.g., cv2 -> opencv-python)
        package_map = {
            "cv2": "opencv-python",
            "PIL": "Pillow",
            "yaml": "PyYAML",
        }
        install_name = package_map.get(package_name, package_name)

        try:
            # Install package
            result = subprocess.run(
                ["pip", "install", install_name],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                return HealingResult(
                    strategy_id=strategy.strategy_id,
                    status=HealingStatus.SUCCESS,
                    message=f"Successfully installed {install_name}",
                    steps_completed=len(strategy.steps),
                    steps_total=len(strategy.steps),
                    side_effects=[f"Installed package: {install_name}"],
                )
            else:
                return HealingResult(
                    strategy_id=strategy.strategy_id,
                    status=HealingStatus.FAILED,
                    message=f"Failed to install {install_name}: {result.stderr}",
                )

        except subprocess.TimeoutExpired:
            return HealingResult(
                strategy_id=strategy.strategy_id,
                status=HealingStatus.FAILED,
                message="Package installation timed out",
            )
        except Exception as e:
            return HealingResult(
                strategy_id=strategy.strategy_id,
                status=HealingStatus.FAILED,
                message=f"Installation error: {e}",
            )

    def _retry_with_backoff(
        self,
        operation: Optional[Callable],
        strategy: RecoveryStrategy,
    ) -> HealingResult:
        """Retry operation with exponential backoff."""
        if not operation:
            return HealingResult(
                strategy_id=strategy.strategy_id,
                status=HealingStatus.SKIPPED,
                message="No operation provided to retry",
            )

        service_name = "unknown"

        # Check circuit breaker
        if self.circuit_breaker.is_open(service_name):
            return HealingResult(
                strategy_id=strategy.strategy_id,
                status=HealingStatus.FAILED,
                message="Circuit breaker open - too many recent failures",
            )

        attempts = 0
        max_attempts = min(self.max_retry_attempts, 5)
        backoff_seconds = 1

        while attempts < max_attempts:
            try:
                # Attempt operation
                result = operation()

                # Success!
                self.circuit_breaker.record_success(service_name)

                return HealingResult(
                    strategy_id=strategy.strategy_id,
                    status=HealingStatus.SUCCESS,
                    message=f"Operation succeeded after {attempts + 1} attempt(s)",
                    steps_completed=attempts + 1,
                    steps_total=max_attempts,
                )

            except Exception as e:
                attempts += 1
                self.circuit_breaker.record_failure(service_name)

                if attempts >= max_attempts:
                    return HealingResult(
                        strategy_id=strategy.strategy_id,
                        status=HealingStatus.FAILED,
                        message=f"Operation failed after {attempts} attempts: {e}",
                        steps_completed=attempts,
                        steps_total=max_attempts,
                    )

                # Exponential backoff
                time.sleep(backoff_seconds)
                backoff_seconds *= 2

        return HealingResult(
            strategy_id=strategy.strategy_id,
            status=HealingStatus.FAILED,
            message="Max retry attempts reached",
        )

    def _verify_file_path(
        self,
        error_analysis: ErrorAnalysis,
        strategy: RecoveryStrategy,
    ) -> HealingResult:
        """Verify and suggest correct file path."""
        # Extract file path from error message
        import re
        match = re.search(r"No such file or directory: '(.+?)'", error_analysis.error_message)
        if not match:
            return HealingResult(
                strategy_id=strategy.strategy_id,
                status=HealingStatus.FAILED,
                message="Could not extract file path from error",
            )

        missing_path = Path(match.group(1))

        # Check if it exists
        if missing_path.exists():
            return HealingResult(
                strategy_id=strategy.strategy_id,
                status=HealingStatus.SUCCESS,
                message="File exists - may have been a transient error",
                steps_completed=1,
                steps_total=len(strategy.steps),
            )

        # Try to find similar files
        if missing_path.parent.exists():
            similar_files = self._find_similar_files(missing_path)

            if similar_files:
                return HealingResult(
                    strategy_id=strategy.strategy_id,
                    status=HealingStatus.PARTIAL,
                    message=f"File not found, but found similar: {similar_files}",
                    steps_completed=1,
                    steps_total=len(strategy.steps),
                )

        return HealingResult(
            strategy_id=strategy.strategy_id,
            status=HealingStatus.FAILED,
            message="File not found and no similar files detected",
        )

    def _find_similar_files(self, target_path: Path) -> List[str]:
        """Find files with similar names."""
        if not target_path.parent.exists():
            return []

        similar = []
        target_name = target_path.name.lower()

        for file in target_path.parent.iterdir():
            if file.is_file():
                file_name = file.name.lower()

                # Check for substring match or similar extension
                if (target_name in file_name or file_name in target_name or
                    target_path.suffix == file.suffix):
                    similar.append(file.name)

        return similar[:5]  # Return top 5

    def auto_retry(
        self,
        operation: Callable,
        max_attempts: Optional[int] = None,
    ) -> Tuple[bool, Any, Optional[Exception]]:
        """
        Decorator-style auto-retry for operations.

        Args:
            operation: Operation to retry
            max_attempts: Optional override for max attempts

        Returns:
            Tuple of (success, result, error)
        """
        attempts = max_attempts or self.max_retry_attempts
        backoff_seconds = 1

        last_error = None

        for attempt in range(attempts):
            try:
                result = operation()
                return True, result, None

            except Exception as e:
                last_error = e

                if attempt < attempts - 1:
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2

        return False, None, last_error

    def get_healing_stats(self) -> Dict:
        """Get healing statistics."""
        if not self.healing_history:
            return {
                "total_attempts": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
            }

        total = len(self.healing_history)
        success = len([h for h in self.healing_history if h.status == HealingStatus.SUCCESS])
        failed = len([h for h in self.healing_history if h.status == HealingStatus.FAILED])

        return {
            "total_attempts": total,
            "success_count": success,
            "failure_count": failed,
            "success_rate": (success / total * 100) if total > 0 else 0.0,
            "avg_duration": sum(h.duration_seconds for h in self.healing_history) / total if total > 0 else 0.0,
        }
