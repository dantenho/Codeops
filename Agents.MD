# 🤖 AGENTS.MD — SOTA Protocol for Coding Agents

> **Version:** 3.0 | **Last Updated:** 2025-12-03
> **Scope:** Mandatory instructions and code structure templates for all AI agents

---

## 📌 PURPOSE STATEMENT

This document establishes **inviolable rules** and **structural code templates** that all coding agents must follow. These are not suggestions — they are **obligations**.

---

## 🔧 ENVIRONMENT REQUIREMENTS

### Mandatory Package Managers — DO NOT USE NPM/PIP DIRECTLY

| Tool | Purpose | Why Required |
|------|---------|--------------|
| **NVM** | Node.js version management | Prevents Node version mismatches across agents |
| **UV** | Python package management | 10-100x faster than pip, lockfile-based, deterministic |

```bash
❌ FORBIDDEN: npm install, pip install
✅ REQUIRED:  nvm use + package-lock.json, uv pip install
```

### File Location

This `Agents.MD` file MUST reside in the **root** of the workspace.

---

## ⚡ TERMINAL EXECUTION PROTOCOL

### Mandatory Auto-Run Usage

To ensure high-velocity development, agents **MUST** set `SafeToAutoRun` to `True` for all verified safe operations.

| Operation Category | SafeToAutoRun | Examples |
|-------------------|---------------|----------|
| **Information Gathering** | ✅ `True` | `ls`, `dir`, `cat`, `grep`, `git status`, `git log` |
| **Environment Setup** | ✅ `True` | `uv pip install`, `nvm use`, `mkdir`, `touch` |
| **Verification** | ✅ `True` | `npm test`, `pytest`, `npm run build` |
| **Destructive/Critical** | ❌ `False` | `rm`, `del`, `git clean`, `git reset`, deployment commands |

### Workflow Acceleration

When generating `.md` workflows, agents **MUST** utilize turbo annotations to minimize user friction:

```
// turbo      -> Auto-runs the immediate next command
// turbo-all  -> Auto-runs ALL commands in the workflow (Requires extreme confidence)
```

---

## 📋 AGENTS COVERED BY THIS PROTOCOL

| Agent | Log Identifier | Primary Strength |
|-------|---------------|------------------|
| Grok.IA (Cline) | `GrokIA` | Contextual analysis, intelligent refactoring |
| Gemini CLI Flash 2.5 | `GeminiFlash25` | Fast execution, simple tasks |
| Gemini CLI Pro 2.5 | `GeminiPro25` | Complex tasks, deep analysis |
| Gemini Pro 3.0 | `GeminiPro30` | Advanced reasoning, architecture |
| Jules | `Jules` | CI/CD automation, DevOps |
| Claude Code | `ClaudeCode` | Precise coding, documentation |
| Composer (Cursor) | `Composer` | Real-time editing, IDE integration |

---

## ⚠️ TASK ASSIGNMENT RULES

### CRITICAL: Never Assign Same Task to Multiple Agents

```
❌ FORBIDDEN: Duplicate task assignment
❌ FORBIDDEN: Overlapping responsibilities
✅ REQUIRED:  Single agent per task
✅ REQUIRED:  Clear ownership boundaries
```

---

## 📝 MANDATORY DOCUMENTATION PROTOCOL

### WRITETODO — Every Code Operation Must Include

```
├── [OPERATION_TAG] at comment start ([CREATE], [REFACTOR], [DEBUG])
├── Detailed description of purpose
├── All parameters with types, descriptions, constraints
├── Return values with types and edge cases
├── Exceptions/errors that may be raised
├── Usage examples
├── Complexity analysis (Big O) for critical functions
├── Side effects documentation
├── Design patterns used (if applicable)
├── Thread safety notes (if applicable)
├── Agent signature: "Agent: {AgentName}"
└── Timestamp: ISO 8601 format
```

---

## 🗂️ TELEMETRY SYSTEM

### Directory Structure

```
CodeAgents/
├── GrokIA/
│   ├── logs/
│   ├── errors/
│   └── analysis/
├── GeminiFlash25/
│   ├── logs/
│   ├── errors/
│   └── analysis/
├── GeminiPro25/
│   ├── logs/
│   ├── errors/
│   └── analysis/
├── GeminiPro30/
│   ├── logs/
│   ├── errors/
│   └── analysis/
├── Jules/
│   ├── logs/
│   ├── errors/
│   └── analysis/
├── ClaudeCode/
│   ├── logs/
│   ├── errors/
│   └── analysis/
└── Composer/
    ├── logs/
    ├── errors/
    └── analysis/
```

### File Naming Convention

```
{TYPE}_{TIMESTAMP}_{SHORT_HASH}.json

Examples:
├── log_2025-12-03T14-30-00_a1b2c3.json
├── error_2025-12-03T14-30-00_d4e5f6.json
└── analysis_2025-12-03T14-30-00_g7h8i9.json
```

---

## 📊 JSON SCHEMAS FOR TELEMETRY

### Operation Log Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OperationLog",
  "type": "object",
  "required": ["agent", "timestamp", "operation", "target", "status"],
  "properties": {
    "agent": {
      "type": "string",
      "enum": ["GrokIA", "GeminiFlash25", "GeminiPro25", "GeminiPro30", "Jules", "ClaudeCode", "Composer"]
    },
    "timestamp": { "type": "string", "format": "date-time" },
    "operation": { "type": "string", "enum": ["CREATE", "REFACTOR", "DEBUG", "DELETE", "MODIFY", "ANALYZE"] },
    "target": {
      "type": "object",
      "properties": {
        "file": { "type": "string" },
        "function": { "type": "string" },
        "lines": { "type": "object", "properties": { "start": { "type": "integer" }, "end": { "type": "integer" } } }
      }
    },
    "status": { "type": "string", "enum": ["SUCCESS", "FAILURE", "PARTIAL", "PENDING"] },
    "duration_ms": { "type": "integer" },
    "context": { "type": "object" }
  }
}
```

### Error Log Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ErrorLog",
  "type": "object",
  "required": ["agent", "timestamp", "error_type", "message", "severity"],
  "properties": {
    "agent": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "error_type": { "type": "string" },
    "message": { "type": "string" },
    "severity": { "type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"] },
    "stack_trace": { "type": "string" },
    "root_cause_analysis": {
      "type": "object",
      "properties": {
        "identified": { "type": "boolean" },
        "cause": { "type": "string" },
        "suggested_fix": { "type": "string" }
      }
    },
    "affected_files": { "type": "array", "items": { "type": "string" } },
    "reproduction_steps": { "type": "array", "items": { "type": "string" } }
  }
}
```

---

## 🐙 GITHUB INTEGRATION & MERGE PROTOCOL

### Branch Naming Convention

All agents **MUST** use the following branch naming structure:

```
agent/{AgentName}/{feature-description}
```

**Examples:**

- `agent/Jules/ci-pipeline-setup`
- `agent/ClaudeCode/api-documentation`

### Pull Request & Merge Rules

1. **Validation:** All PRs must pass the `agent-validation` workflow (Docstrings, Telemetry, Code Quality).
2. **Merge Orchestrator:** Do **NOT** merge manually. Use the `Merge Orchestrator` workflow to handle conflicts and agent synchronization.
3. **Commit Messages:** Must follow the format: `[AgentName] Description of change`.

### Workflow Triggers

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `agent-validation` | PR Open/Sync | Validates compliance with Agents.MD |
| `merge-orchestrator` | PR + Label | Smart merging & conflict resolution |
| `branch-sync` | Schedule/Push | Keeps `develop` and `agent/*` branches in sync |

---

# 🐍 MANDATORY CODE STRUCTURE — PYTHON

## All agents MUST follow this structural template when writing Python code

---

## MODULE HEADER TEMPLATE

```python
"""
Module: {module_name}.py
Purpose: {One-line description of module purpose}.

{Extended description explaining the module's role, main components,
and how it fits into the larger system architecture.}

Agent: {AgentName}
Created: {ISO_TIMESTAMP}
Operation: [CREATE]
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional, TypeVar

# Type variables for generic implementations
T = TypeVar("T")
```

---

## ENUM CLASS TEMPLATE

```python
class StatusEnum(Enum):
    """
    [CREATE] Enumeration of possible states.

    Represents the lifecycle states of an operation,
    from initialization through completion or failure.

    Attributes:
        PENDING: Operation is queued but not started
        IN_PROGRESS: Operation is actively running
        SUCCESS: Operation completed successfully
        FAILED: Operation encountered an error

    Example:
        >>> status = StatusEnum.PENDING
        >>> if status == StatusEnum.PENDING:
        ...     print("Waiting to start")
        Waiting to start

    Agent: {AgentName}
    Timestamp: {ISO_TIMESTAMP}
    """

    PENDING = auto()
    IN_PROGRESS = auto()
    SUCCESS = auto()
    FAILED = auto()
```

---

## IMMUTABLE DATACLASS TEMPLATE (frozen=True)

```python
@dataclass(frozen=True)
class ImmutableEntity:
    """
    [CREATE] Immutable representation of an entity.

    Contains metadata and verification information. Immutability
    ensures data integrity throughout the processing pipeline.

    Attributes:
        name (str): Human-readable identifier.
            Must be non-empty and contain only alphanumeric characters,
            hyphens, and underscores.
        version (str): Semantic version string (e.g., "1.2.3").
            Must follow semver format: MAJOR.MINOR.PATCH
        checksum (str): SHA-256 hash of contents.
            Used for integrity verification.
        created_at (datetime): Timestamp of creation.
            Timezone-aware datetime in UTC.
        metadata (dict[str, Any]): Additional properties.
            Optional key-value pairs for custom metadata.

    Example:
        >>> entity = ImmutableEntity(
        ...     name="my-entity",
        ...     version="2.1.0",
        ...     checksum="a8b9c...",
        ...     created_at=datetime.now(timezone.utc),
        ...     metadata={"key": "value"}
        ... )
        >>> print(entity.name)
        my-entity

    Raises:
        ValueError: If name is empty or contains invalid characters
        ValueError: If version doesn't follow semver format

    Complexity:
        Time: O(1) for instantiation
        Space: O(n) where n is metadata size

    Agent: {AgentName}
    Timestamp: {ISO_TIMESTAMP}
    """

    name: str
    version: str
    checksum: str
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        [CREATE] Validates attributes after initialization.

        Performs comprehensive validation of all properties
        to ensure data integrity.

        Raises:
            ValueError: If any validation check fails

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        if not self.name or not self.name.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                f"Invalid name: '{self.name}'. "
                "Must be non-empty, alphanumeric with hyphens/underscores."
            )
```

---

## MUTABLE DATACLASS TEMPLATE

```python
@dataclass
class MutableResult:
    """
    [CREATE] Captures the outcome of an operation.

    Mutable dataclass that accumulates results,
    including status, timing, and any errors encountered.

    Attributes:
        operation_id (str): Unique identifier for this operation.
        status (StatusEnum): Current state of the operation.
        started_at (Optional[datetime]): When operation began.
        completed_at (Optional[datetime]): When operation finished.
        error_message (Optional[str]): Error details if failed.
        logs (list[str]): Chronological log entries.

    Example:
        >>> result = MutableResult(operation_id="op-001")
        >>> result.add_log("Operation started")
        >>> print(result.duration_seconds)
        45.2

    Agent: {AgentName}
    Timestamp: {ISO_TIMESTAMP}
    """

    operation_id: str
    status: StatusEnum = StatusEnum.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    logs: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> Optional[float]:
        """
        [CREATE] Calculates operation duration in seconds.

        Computes the elapsed time between start and completion.
        Returns None if operation hasn't started or completed.

        Returns:
            Optional[float]: Duration in seconds, or None if incomplete.

        Example:
            >>> result.started_at = datetime(2025, 1, 1, 10, 0, 0)
            >>> result.completed_at = datetime(2025, 1, 1, 10, 1, 30)
            >>> result.duration_seconds
            90.0

        Complexity:
            Time: O(1)
            Space: O(1)

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def add_log(self, message: str) -> None:
        """
        [CREATE] Appends a timestamped entry to logs.

        Adds a log entry with automatic timestamp prefix for
        chronological tracking of events.

        Args:
            message (str): Log message to record.
                Should be descriptive and actionable.

        Returns:
            None

        Side Effects:
            - Modifies self.logs list

        Example:
            >>> result.add_log("Starting health check")
            >>> print(result.logs[-1])
            [2025-12-03T10:05:00Z] Starting health check

        Complexity:
            Time: O(1) amortized
            Space: O(n) where n is message length

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        self.logs.append(f"[{timestamp}] {message}")
```

---

## ABSTRACT BASE CLASS TEMPLATE

```python
class BaseStrategy(ABC):
    """
    [CREATE] Abstract base class for strategies.

    Defines the interface for different approaches. Subclasses
    implement specific logic while maintaining consistent API.

    This follows the Strategy design pattern, allowing runtime
    selection of behavior.

    Attributes:
        name (str): Strategy identifier for logging and metrics.
        logger (logging.Logger): Strategy-specific logger instance.

    Example:
        >>> class ConcreteStrategy(BaseStrategy):
        ...     @property
        ...     def name(self) -> str:
        ...         return "concrete"
        ...
        ...     def execute(self, data):
        ...         # Implementation
        ...         pass
        ...
        ...     def validate(self, result):
        ...         return result.status == StatusEnum.SUCCESS

    Design Pattern: Strategy Pattern

    Agent: {AgentName}
    Timestamp: {ISO_TIMESTAMP}
    """

    def __init__(self) -> None:
        """
        [CREATE] Initializes the strategy.

        Sets up logging infrastructure for strategy operations.

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        self.logger = logging.getLogger(f"strategy.{self.name}")

    @property
    @abstractmethod
    def name(self) -> str:
        """
        [CREATE] Returns the strategy identifier.

        Must be implemented by subclasses to provide unique
        strategy identification for logging and metrics.

        Returns:
            str: Unique strategy name

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        ...

    @abstractmethod
    def execute(self, data: Any) -> MutableResult:
        """
        [CREATE] Executes the strategy.

        Implements the core logic for this strategy.
        Must handle all phases: preparation, execution, validation.

        Args:
            data (Any): Input data for processing.

        Returns:
            MutableResult: Outcome of the operation.

        Raises:
            ExecutionError: If execution fails irrecoverably
            ValidationError: If pre-execution validation fails

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        ...

    @abstractmethod
    def validate(self, result: MutableResult) -> bool:
        """
        [CREATE] Validates execution success.

        Performs post-execution validation to confirm
        the operation completed correctly.

        Args:
            result (MutableResult): The result to validate.

        Returns:
            bool: True if valid, False otherwise.

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        ...
```

---

## CONCRETE CLASS TEMPLATE

```python
class ConcreteStrategy(BaseStrategy):
    """
    [CREATE] Implements a concrete strategy.

    Provides specific implementation with configurable parameters
    and comprehensive error handling.

    Configuration:
        - param1: Description of parameter 1
        - param2: Description of parameter 2

    Attributes:
        param1 (int): First configuration parameter.
        param2 (int): Second configuration parameter.

    Example:
        >>> strategy = ConcreteStrategy(param1=10, param2=30)
        >>> result = strategy.execute(data)
        >>> if not strategy.validate(result):
        ...     print("Validation failed")

    Complexity:
        Time: O(n) where n is data size
        Space: O(1) constant memory usage

    Agent: {AgentName}
    Timestamp: {ISO_TIMESTAMP}
    """

    def __init__(
        self,
        param1: int = 1,
        param2: int = 30,
    ) -> None:
        """
        [CREATE] Initializes the concrete strategy.

        Args:
            param1 (int): First parameter.
                Default: 1. Must be positive integer.
            param2 (int): Second parameter.
                Default: 30. Must be positive integer.

        Raises:
            ValueError: If param1 or param2 <= 0

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        super().__init__()

        if param1 <= 0:
            raise ValueError(f"param1 must be positive, got {param1}")
        if param2 <= 0:
            raise ValueError(f"param2 must be positive, got {param2}")

        self.param1 = param1
        self.param2 = param2

    @property
    def name(self) -> str:
        """
        [CREATE] Returns strategy identifier.

        Returns:
            str: "concrete"

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        return "concrete"

    def execute(self, data: Any) -> MutableResult:
        """
        [CREATE] Executes the concrete strategy.

        Performs the main operation with logging and error handling.

        Args:
            data (Any): Input data to process.

        Returns:
            MutableResult: Operation outcome with logs.

        Algorithm:
            1. Generate unique operation ID
            2. Initialize result tracking
            3. Process data in batches
            4. Validate each batch
            5. Mark operation complete

        Complexity:
            Time: O(n) where n is data size
            Space: O(log_entries)

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        operation_id = self._generate_operation_id()
        result = MutableResult(operation_id=operation_id)
        result.started_at = datetime.now(timezone.utc)
        result.status = StatusEnum.IN_PROGRESS

        result.add_log(f"Starting operation with param1={self.param1}")

        # Main logic here

        result.status = StatusEnum.SUCCESS
        result.completed_at = datetime.now(timezone.utc)
        result.add_log("Operation completed successfully")

        return result

    def validate(self, result: MutableResult) -> bool:
        """
        [CREATE] Validates operation success.

        Checks status and performs verification.

        Args:
            result (MutableResult): Result to validate.

        Returns:
            bool: True if valid.

        Validation Checks:
            1. Status is SUCCESS
            2. No errors in logs
            3. Duration within acceptable range

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        return result.status == StatusEnum.SUCCESS

    def _generate_operation_id(self) -> str:
        """
        [CREATE] Generates unique operation identifier.

        Creates a deterministic but unique ID based on
        current timestamp.

        Returns:
            str: Unique operation ID in format "op-{hash[:8]}"

        Complexity:
            Time: O(1)
            Space: O(1)

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        import hashlib
        timestamp = datetime.now(timezone.utc).isoformat()
        hash_digest = hashlib.sha256(timestamp.encode()).hexdigest()
        return f"op-{hash_digest[:8]}"
```

---

## MANAGER/FACADE CLASS TEMPLATE

```python
class OperationManager:
    """
    [CREATE] Orchestrates operations across the system.

    Central coordinator for all activities, managing
    strategy selection, execution, and validation.
    Implements the Facade pattern to simplify operations.

    Attributes:
        strategies (dict[str, BaseStrategy]): Registered strategies.
        default_strategy (str): Strategy used when none specified.
        logger (logging.Logger): Manager logger instance.
        history (list[MutableResult]): Past operations.

    Example:
        >>> manager = OperationManager()
        >>> manager.register_strategy(ConcreteStrategy())
        >>>
        >>> result = manager.run(
        ...     data=my_data,
        ...     strategy_name="concrete"
        ... )
        >>>
        >>> if result.status == StatusEnum.FAILED:
        ...     print(result.error_message)

    Design Patterns:
        - Facade: Simplifies complex subsystem
        - Strategy: Pluggable strategies
        - Registry: Strategy registration and lookup

    Thread Safety:
        This class is NOT thread-safe. Use external synchronization
        for concurrent operations.

    Agent: {AgentName}
    Timestamp: {ISO_TIMESTAMP}
    """

    def __init__(self, default_strategy: str = "concrete") -> None:
        """
        [CREATE] Initializes the operation manager.

        Sets up strategy registry and configures default behavior.

        Args:
            default_strategy (str): Strategy name to use by default.
                Default: "concrete". Must match a registered strategy.

        Example:
            >>> manager = OperationManager(default_strategy="advanced")

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        self.strategies: dict[str, BaseStrategy] = {}
        self.default_strategy = default_strategy
        self.logger = logging.getLogger("operation.manager")
        self.history: list[MutableResult] = []

    def register_strategy(self, strategy: BaseStrategy) -> None:
        """
        [CREATE] Registers a strategy.

        Adds a strategy to the registry, making it available
        for operations.

        Args:
            strategy (BaseStrategy): Strategy instance to register.
                Must have unique name property.

        Returns:
            None

        Side Effects:
            - Modifies self.strategies dictionary
            - Logs registration event

        Raises:
            ValueError: If strategy with same name already registered

        Example:
            >>> manager.register_strategy(ConcreteStrategy())
            >>> manager.register_strategy(AdvancedStrategy())

        Complexity:
            Time: O(1)
            Space: O(1)

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        if strategy.name in self.strategies:
            raise ValueError(
                f"Strategy '{strategy.name}' already registered. "
                "Unregister first or use a different name."
            )

        self.strategies[strategy.name] = strategy
        self.logger.info(f"Registered strategy: {strategy.name}")

    def run(
        self,
        data: Any,
        strategy_name: Optional[str] = None,
    ) -> MutableResult:
        """
        [CREATE] Executes an operation.

        Coordinates the full lifecycle: strategy selection,
        execution, and validation.

        Args:
            data (Any): Data to process.
            strategy_name (Optional[str]): Strategy to use.
                Default: None (uses self.default_strategy).

        Returns:
            MutableResult: Complete operation outcome.

        Raises:
            KeyError: If specified strategy not registered

        Example:
            >>> result = manager.run(
            ...     data=my_data,
            ...     strategy_name="concrete"
            ... )
            >>> print(f"Operation {result.operation_id}: {result.status.name}")

        Algorithm:
            1. Select strategy
            2. Log initiation
            3. Execute strategy
            4. Validate result
            5. Record in history
            6. Return result

        Complexity:
            Time: O(strategy_execution_time)
            Space: O(log_entries)

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        strategy_name = strategy_name or self.default_strategy

        if strategy_name not in self.strategies:
            raise KeyError(
                f"Strategy '{strategy_name}' not registered. "
                f"Available: {list(self.strategies.keys())}"
            )

        strategy = self.strategies[strategy_name]

        self.logger.info(f"Starting operation using {strategy_name}")

        result = strategy.execute(data)

        if not strategy.validate(result):
            self.logger.warning("Validation failed")

        self.history.append(result)

        self.logger.info(
            f"Operation {result.operation_id} completed: {result.status.name}"
        )

        return result

    def get_history(
        self,
        status: Optional[StatusEnum] = None,
        limit: int = 100,
    ) -> list[MutableResult]:
        """
        [CREATE] Retrieves filtered operation history.

        Returns past operations matching specified criteria,
        useful for auditing and troubleshooting.

        Args:
            status (Optional[StatusEnum]): Filter by status.
                Default: None (all statuses).
            limit (int): Maximum results to return.
                Default: 100. Must be positive.

        Returns:
            list[MutableResult]: Matching operations, newest first.

        Example:
            >>> failed = manager.get_history(
            ...     status=StatusEnum.FAILED,
            ...     limit=10
            ... )
            >>> for op in failed:
            ...     print(f"{op.operation_id}: {op.error_message}")

        Complexity:
            Time: O(n) where n is history length
            Space: O(min(n, limit))

        Agent: {AgentName}
        Timestamp: {ISO_TIMESTAMP}
        """
        results = self.history.copy()

        if status:
            results = [r for r in results if r.status == status]

        results.sort(
            key=lambda r: r.started_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )

        return results[:limit]
```

---

## STANDALONE FUNCTION TEMPLATE

```python
def process_data(
    input_path: Path,
    output_format: str = "json",
    chunk_size: int = 8192,
) -> dict[str, Any]:
    """
    [CREATE] Processes data from file with configurable options.

    Reads file in chunks to handle large files efficiently without
    loading entire contents into memory.

    Args:
        input_path (Path): Path to input file.
            Must be readable file path.
        output_format (str): Output format to use.
            Default: "json". Supports: json, csv, xml.
        chunk_size (int): Bytes to read per iteration.
            Default: 8192. Larger values use more memory but may be faster.

    Returns:
        dict[str, Any]: Processed data with metadata.

    Raises:
        FileNotFoundError: If input_path doesn't exist
        PermissionError: If file is not readable
        ValueError: If output_format is not supported

    Example:
        >>> result = process_data(Path("/data/input.txt"))
        >>> print(result["status"])
        success

        >>> result = process_data(
        ...     Path("/data/input.txt"),
        ...     output_format="csv"
        ... )

    Security Note:
        Validates file paths to prevent directory traversal attacks.

    Complexity:
        Time: O(n) where n is file size
        Space: O(chunk_size) constant memory usage

    Agent: {AgentName}
    Timestamp: {ISO_TIMESTAMP}
    """
    supported_formats = ["json", "csv", "xml"]

    if output_format not in supported_formats:
        raise ValueError(
            f"Format '{output_format}' not supported. "
            f"Available: {supported_formats}"
        )

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    # Processing logic here

    return {
        "status": "success",
        "format": output_format,
        "path": str(input_path),
    }
```

---

## FACTORY FUNCTION TEMPLATE

```python
def create_entity(
    name: str,
    version: str,
    source_path: Path,
    metadata: Optional[dict[str, Any]] = None,
) -> ImmutableEntity:
    """
    [CREATE] Factory function to create validated entity.

    Constructs an ImmutableEntity with automatic checksum calculation
    and metadata enrichment. Validates all inputs before creation.

    Args:
        name (str): Entity name identifier.
            Must be non-empty, alphanumeric with hyphens/underscores.
        version (str): Semantic version string.
            Must follow semver format: MAJOR.MINOR.PATCH
        source_path (Path): Path to source file.
            Must exist and be readable.
        metadata (Optional[dict[str, Any]]): Additional properties.
            Default: None. Merged with auto-generated metadata.

    Returns:
        ImmutableEntity: Fully validated and populated entity.

    Raises:
        FileNotFoundError: If source_path doesn't exist
        ValueError: If name or version is invalid
        PermissionError: If source_path is not readable

    Example:
        >>> entity = create_entity(
        ...     name="my-entity",
        ...     version="2.1.0",
        ...     source_path=Path("/data/entity.dat"),
        ...     metadata={"key": "value"}
        ... )
        >>> print(entity.checksum)
        a8b9c...

    Auto-generated Metadata:
        - created_by: "{AgentName}"
        - creation_method: "create_entity"
        - checksum_algorithm: "sha256"

    Complexity:
        Time: O(n) where n is file size (for checksum)
        Space: O(1) plus metadata size

    Agent: {AgentName}
    Timestamp: {ISO_TIMESTAMP}
    """
    import hashlib

    # Validate file exists
    if not source_path.exists():
        raise FileNotFoundError(f"File not found: {source_path}")

    # Calculate checksum
    hasher = hashlib.sha256()
    with open(source_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    checksum = hasher.hexdigest()

    # Prepare metadata
    final_metadata = {
        "created_by": "{AgentName}",
        "creation_method": "create_entity",
        "checksum_algorithm": "sha256",
    }
    if metadata:
        final_metadata.update(metadata)

    return ImmutableEntity(
        name=name,
        version=version,
        checksum=checksum,
        created_at=datetime.now(timezone.utc),
        metadata=final_metadata,
    )
```

---

## MODULE INITIALIZATION TEMPLATE

```python
# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

if __name__ == "__main__":
    # Example usage demonstration
    # This block only runs when module is executed directly

    logging.basicConfig(level=logging.INFO)

    # Initialize manager
    manager = OperationManager()
    manager.register_strategy(ConcreteStrategy(param1=2))

    print("Module loaded successfully")
    print(f"Registered strategies: {list(manager.strategies.keys())}")
```

---

- [ ] Operation tag added ([CREATE], [REFACTOR], [DEBUG])
- [ ] Full docstring with ALL required elements
- [ ] Type hints on ALL parameters and returns
- [ ] Examples included in documentation
- [ ] Complexity analysis for critical functions
- [ ] Side effects documented
- [ ] Raises section complete
- [ ] Agent signature included
- [ ] Timestamp in ISO 8601 format
- [ ] Telemetry log created in CodeAgents/{Agent}/logs/
- [ ] Error log created if applicable
- [ ] Code passes linting (ruff, mypy, black)

---

## 🚨 ERROR SEVERITY LEVELS

| Level | Description | Required Action |
|-------|-------------|-----------------|
| `LOW` | Warnings, suggested improvements | Document for future review |
| `MEDIUM` | Non-critical bugs, performance degradation | Fix in next iteration |
| `HIGH` | Bugs affecting functionality | Fix before commit |
| `CRITICAL` | Security failures, data loss risk | Stop and fix immediately |

---

## 📎 QUICK REFERENCE

### Operation Tags

| Tag | Usage |
|-----|-------|
| `[CREATE]` | New function/class/module |
| `[REFACTOR]` | Restructuring existing code |
| `[DEBUG]` | Bug fix |
| `[MODIFY]` | Behavior change |
| `[DELETE]` | Code removal |
| `[ANALYZE]` | Analysis without modification |

### Package Manager Commands

```bash
# Node.js — ALWAYS use NVM
nvm use <version>
nvm install <version>

# Python — ALWAYS use UV
uv pip install <package>
uv pip sync requirements.txt
uv venv
```

### Telemetry Path

```
CodeAgents/{AgentID}/{RecordType}/{file}_{timestamp}_{hash}.json
```

---

*This document is the single source of truth for coding protocols.*

*All agents must read and comply before performing any code operations.*
