class CodeOpsError(Exception):
    """Base exception for all CodeOps errors."""
    pass

class AgentError(CodeOpsError):
    """Agent-related errors."""
    pass

class TelemetryError(CodeOpsError):
    """Telemetry logging errors."""
    pass

class RAGError(CodeOpsError):
    """RAG/vector store errors."""
    pass

class ConfigurationError(CodeOpsError):
    """Configuration loading errors."""
    pass
