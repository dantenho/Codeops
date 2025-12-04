"""
Core Backend Modules for EudoraX Prototype.

Contains telemetry, metrics, and utility services.
"""

from .telemetry import (
    get_telemetry_service,
    BackendTelemetryService,
    TelemetryEvent,
    OperationMetric,
    OperationType,
    OperationStatus,
    ErrorSeverity
)

__all__ = [
    "get_telemetry_service",
    "BackendTelemetryService",
    "TelemetryEvent",
    "OperationMetric",
    "OperationType",
    "OperationStatus",
    "ErrorSeverity"
]
