"""
Module: telemetry.py
Purpose: Backend telemetry service for EudoraX Prototype API.

Provides telemetry collection, aggregation, and reporting endpoints
for monitoring agent operations across the CodeAgents ecosystem.

Agent: ClaudeCode
Created: 2025-12-04T12:00:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger("backend.telemetry")


class OperationType(str, Enum):
    """Types of operations that can be logged."""
    CREATE = "CREATE"
    REFACTOR = "REFACTOR"
    DEBUG = "DEBUG"
    DELETE = "DELETE"
    MODIFY = "MODIFY"
    ANALYZE = "ANALYZE"


class OperationStatus(str, Enum):
    """Status of an operation."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"
    PENDING = "PENDING"


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class TelemetryEvent:
    """
    [CREATE] Generic telemetry event structure.
    
    Captures any type of event for monitoring and analysis.
    """
    event_type: str
    agent_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationMetric:
    """
    [CREATE] Metrics for a single operation.
    
    Captures performance and quality data for analysis.
    """
    operation_id: str
    agent_id: str
    operation_type: OperationType
    duration_ms: int
    status: OperationStatus
    file_path: Optional[str] = None
    lines_changed: int = 0
    complexity_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BackendTelemetryService:
    """
    [CREATE] Centralized telemetry service for the backend API.
    
    Aggregates telemetry from all agents and provides:
    - Real-time metrics collection
    - Historical data analysis
    - Performance reporting
    - Error tracking
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the telemetry service.
        
        Args:
            storage_path: Path for persistent storage. Defaults to ./telemetry_data
        """
        self.storage_path = storage_path or Path("./telemetry_data")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._events: List[TelemetryEvent] = []
        self._metrics: List[OperationMetric] = []
        self._max_in_memory = 1000
        
        logger.info(f"BackendTelemetryService initialized. Storage: {self.storage_path}")
    
    def record_event(self, event: TelemetryEvent) -> str:
        """
        [CREATE] Record a telemetry event.
        
        Args:
            event: The event to record
            
        Returns:
            str: Event ID for reference
        """
        self._events.append(event)
        
        if len(self._events) > self._max_in_memory:
            self._flush_events()
        
        return f"evt_{event.timestamp}_{event.agent_id}"
    
    def record_metric(self, metric: OperationMetric) -> str:
        """
        [CREATE] Record an operation metric.
        
        Args:
            metric: The metric to record
            
        Returns:
            str: Metric ID for reference
        """
        self._metrics.append(metric)
        
        if len(self._metrics) > self._max_in_memory:
            self._flush_metrics()
        
        return metric.operation_id
    
    def get_agent_summary(self, agent_id: str, limit: int = 100) -> Dict[str, Any]:
        """
        [CREATE] Get performance summary for an agent.
        
        Args:
            agent_id: The agent to summarize
            limit: Maximum number of records to analyze
            
        Returns:
            Dict containing summary statistics
        """
        agent_metrics = [m for m in self._metrics if m.agent_id == agent_id][-limit:]
        
        if not agent_metrics:
            return {
                "agent_id": agent_id,
                "total_operations": 0,
                "message": "No metrics found for this agent"
            }
        
        total_ops = len(agent_metrics)
        successful = sum(1 for m in agent_metrics if m.status == OperationStatus.SUCCESS)
        avg_duration = sum(m.duration_ms for m in agent_metrics) / total_ops
        
        return {
            "agent_id": agent_id,
            "total_operations": total_ops,
            "success_rate": (successful / total_ops) * 100,
            "average_duration_ms": round(avg_duration, 2),
            "operations_by_type": self._count_by_type(agent_metrics),
            "recent_operations": [asdict(m) for m in agent_metrics[-5:]]
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        [CREATE] Get overall system health metrics.
        
        Returns:
            Dict containing system-wide health data
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_events_in_memory": len(self._events),
            "total_metrics_in_memory": len(self._metrics),
            "storage_path": str(self.storage_path),
            "status": "healthy"
        }
    
    def _count_by_type(self, metrics: List[OperationMetric]) -> Dict[str, int]:
        """Count operations by type."""
        counts: Dict[str, int] = {}
        for m in metrics:
            op_type = m.operation_type.value
            counts[op_type] = counts.get(op_type, 0) + 1
        return counts
    
    def _flush_events(self) -> None:
        """Flush events to persistent storage."""
        if not self._events:
            return
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filepath = self.storage_path / f"events_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([asdict(e) for e in self._events], f, indent=2)
        
        self._events = []
        logger.info(f"Flushed events to {filepath}")
    
    def _flush_metrics(self) -> None:
        """Flush metrics to persistent storage."""
        if not self._metrics:
            return
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filepath = self.storage_path / f"metrics_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([asdict(m) for m in self._metrics], f, indent=2)
        
        self._metrics = []
        logger.info(f"Flushed metrics to {filepath}")


# Lazy singleton - only created when accessed
_telemetry_service: Optional[BackendTelemetryService] = None


def get_telemetry_service() -> BackendTelemetryService:
    """
    [CREATE] Get the singleton telemetry service instance.
    
    Uses lazy initialization to avoid import-time side effects.
    
    Returns:
        BackendTelemetryService: The singleton instance
    """
    global _telemetry_service
    if _telemetry_service is None:
        _telemetry_service = BackendTelemetryService()
    return _telemetry_service
