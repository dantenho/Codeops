"""
Telemetry and Logging System.

Provides comprehensive logging, metrics, and telemetry
for evaluating workflow performance.
"""

import json
import logging
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Logs directory
LOGS_DIR = Path(__file__).parent.parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class TelemetryEvent:
    """Telemetry event data."""
    timestamp: str
    event_type: str
    component: str
    action: str
    duration_ms: float
    status: str
    metadata: Dict[str, Any]
    error: Optional[str] = None


class TelemetryLogger:
    """Telemetry logger for tracking system events."""

    def __init__(self, component: str, log_file: str = None):
        self.component = component
        self.log_file = log_file or LOGS_DIR / f"{component}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.events: List[TelemetryEvent] = []

        # Configure Python logger
        self.logger = logging.getLogger(component)
        self.logger.setLevel(logging.DEBUG)

        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        ))
        self.logger.addHandler(console)

        # File handler
        file_handler = logging.FileHandler(LOGS_DIR / f"{component}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        self.logger.addHandler(file_handler)

    def log_event(
        self,
        event_type: str,
        action: str,
        duration_ms: float,
        status: str,
        metadata: Dict[str, Any] = None,
        error: str = None
    ) -> TelemetryEvent:
        """Log a telemetry event."""
        event = TelemetryEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            component=self.component,
            action=action,
            duration_ms=duration_ms,
            status=status,
            metadata=metadata or {},
            error=error
        )

        self.events.append(event)

        # Write to JSONL file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(asdict(event)) + "\n")

        # Also log to standard logger
        level = logging.ERROR if error else logging.INFO
        self.logger.log(level, f"{event_type}:{action} - {status} ({duration_ms:.2f}ms)")

        return event

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message)
        self.log_event("log", "info", 0, "ok", kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message)
        self.log_event("log", "warning", 0, "warning", kwargs)

    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error message."""
        error_str = str(error) if error else None
        self.logger.error(message)
        self.log_event("log", "error", 0, "error", kwargs, error_str)

    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics."""
        if not self.events:
            return {"total_events": 0}

        durations = [e.duration_ms for e in self.events if e.duration_ms > 0]
        errors = [e for e in self.events if e.error]

        return {
            "total_events": len(self.events),
            "total_errors": len(errors),
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "error_rate": len(errors) / len(self.events) if self.events else 0
        }


def track_execution(logger: TelemetryLogger, event_type: str = "execution"):
    """Decorator to track function execution."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            error = None
            status = "success"
            result = None

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                status = "error"
                raise
            finally:
                duration = (time.time() - start) * 1000
                logger.log_event(
                    event_type=event_type,
                    action=func.__name__,
                    duration_ms=duration,
                    status=status,
                    metadata={"args": str(args)[:100], "kwargs": str(kwargs)[:100]},
                    error=error
                )

            return result
        return wrapper
    return decorator


# =============================================================================
# WORKFLOW TELEMETRY
# =============================================================================

class WorkflowTelemetry:
    """Telemetry for LangGraph workflows."""

    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.logger = TelemetryLogger(f"workflow_{workflow_name}")
        self.node_times: Dict[str, List[float]] = {}
        self.run_count = 0

    def track_node(self, node_name: str):
        """Create a context manager for tracking node execution."""
        return NodeTracker(self, node_name)

    def record_node_time(self, node_name: str, duration_ms: float, status: str):
        """Record node execution time."""
        if node_name not in self.node_times:
            self.node_times[node_name] = []
        self.node_times[node_name].append(duration_ms)

        self.logger.log_event(
            event_type="node",
            action=node_name,
            duration_ms=duration_ms,
            status=status,
            metadata={"run_count": self.run_count}
        )

    def start_run(self):
        """Start a new workflow run."""
        self.run_count += 1
        self.logger.info(f"Starting workflow run #{self.run_count}")

    def end_run(self, status: str, metadata: Dict = None):
        """End a workflow run."""
        self.logger.log_event(
            event_type="workflow",
            action="complete",
            duration_ms=0,
            status=status,
            metadata={"run_count": self.run_count, **(metadata or {})}
        )

    def get_node_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for each node."""
        stats = {}
        for node, times in self.node_times.items():
            if times:
                stats[node] = {
                    "count": len(times),
                    "avg_ms": sum(times) / len(times),
                    "max_ms": max(times),
                    "min_ms": min(times),
                    "total_ms": sum(times)
                }
        return stats


class NodeTracker:
    """Context manager for tracking node execution."""

    def __init__(self, telemetry: WorkflowTelemetry, node_name: str):
        self.telemetry = telemetry
        self.node_name = node_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000
        status = "error" if exc_type else "success"
        self.telemetry.record_node_time(self.node_name, duration, status)


# =============================================================================
# GLOBAL LOGGERS
# =============================================================================

# Create global loggers for each component
orchestrator_logger = TelemetryLogger("orchestrator")
integration_logger = TelemetryLogger("integration")
node_logger = TelemetryLogger("nodes")
test_logger = TelemetryLogger("tests")


def get_logger(component: str) -> TelemetryLogger:
    """Get or create a logger for a component."""
    return TelemetryLogger(component)


# =============================================================================
# TEST UTILITIES
# =============================================================================

class TestTelemetry:
    """Telemetry utilities for tests."""

    def __init__(self):
        self.logger = test_logger
        self.test_results: List[Dict[str, Any]] = []

    def record_test(
        self,
        test_name: str,
        passed: bool,
        duration_ms: float,
        error: str = None
    ):
        """Record a test result."""
        result = {
            "name": test_name,
            "passed": passed,
            "duration_ms": duration_ms,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)

        self.logger.log_event(
            event_type="test",
            action=test_name,
            duration_ms=duration_ms,
            status="pass" if passed else "fail",
            error=error
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary."""
        passed = [t for t in self.test_results if t["passed"]]
        failed = [t for t in self.test_results if not t["passed"]]

        return {
            "total": len(self.test_results),
            "passed": len(passed),
            "failed": len(failed),
            "pass_rate": len(passed) / len(self.test_results) if self.test_results else 0,
            "total_duration_ms": sum(t["duration_ms"] for t in self.test_results),
            "failures": [{"name": t["name"], "error": t["error"]} for t in failed]
        }


# Global test telemetry
test_telemetry = TestTelemetry()


if __name__ == "__main__":
    # Test the telemetry system
    logger = get_logger("test")

    logger.info("Starting telemetry test")

    @track_execution(logger, "function")
    def sample_function(x):
        time.sleep(0.1)
        return x * 2

    result = sample_function(5)
    print(f"Result: {result}")

    logger.info("Test complete")
    print(f"\nMetrics: {logger.get_metrics()}")
