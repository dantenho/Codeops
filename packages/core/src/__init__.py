"""
Core CodeAgents Modules.

Contains telemetry, access control, metrics, and RAG services.
"""

from .telemetry import (
    TelemetryManager,
    OperationLog,
    ErrorLog,
    telemetry
)

from .access_control import (
    AccessControlManager,
    PermissionLevel,
    ResourceType,
    AgentPermissions,
    access_manager,
    check_terminal_access,
    require_terminal_access
)

from .metrics import (
    AgentEvaluator,
    MetricScores,
    TaskContext,
    EvaluationResult,
    ComplexityLevel,
    TaskType,
    get_evaluator
)

from .rag import (
    RAGEngine,
    SearchResult,
    get_rag_engine
)

from .vector_store import (
    VectorStore,
    VectorStoreConfig
)

__all__ = [
    # Telemetry
    "TelemetryManager",
    "OperationLog",
    "ErrorLog",
    "telemetry",
    # Access Control
    "AccessControlManager",
    "PermissionLevel",
    "ResourceType",
    "AgentPermissions",
    "access_manager",
    "check_terminal_access",
    "require_terminal_access",
    # Metrics
    "AgentEvaluator",
    "MetricScores",
    "TaskContext",
    "EvaluationResult",
    "ComplexityLevel",
    "TaskType",
    "get_evaluator",
    # RAG
    "RAGEngine",
    "SearchResult",
    "get_rag_engine",
    # Vector Store
    "VectorStore",
    "VectorStoreConfig"
]
