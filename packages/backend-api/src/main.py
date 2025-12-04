"""
Module: main.py
Purpose: Serve the EudoraX Prototype API and expose evaluation workflows.

Delivers the first functional slice of the system by wiring FastAPI endpoints
to the Agent Metrics & Evaluation System (AMES). Includes typed payload models,
telemetry hooks, and in-memory persistence for quick iteration feedback.

Agent: GPT-5.1-Codex
Created: 2025-12-03T15:35:00Z
Operation: [REFACTOR]
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import sys
from pathlib import Path
# Add core package to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core" / "src"))
from metrics import (
    AgentEvaluator,
    ComplexityLevel,
    MetricScores,
    TaskContext,
    TaskType,
)
from telemetry import OperationLog, TelemetryManager

AGENT_NAME = "GPT-5.1-Codex"
APP_START_TIME = datetime.now(timezone.utc)


class TaskTypeName(str, Enum):
    """Lightweight enum for validating incoming task types."""

    CREATE = "create"
    REFACTOR = "refactor"
    DEBUG = "debug"
    OPTIMIZE = "optimize"
    DOCUMENT = "document"
    ANALYZE = "analyze"


class ComplexityLevelName(str, Enum):
    """Human-friendly complexity labels that align with AMES enums."""

    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    COMPLEX = "COMPLEX"
    EXPERT = "EXPERT"


class MetricScoresPayload(BaseModel):
    """
    [CREATE] Validates raw metric scores prior to evaluation.

    Ensures inputs stay within 0-100 bounds before converting them into
    domain objects consumed by AMES.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    accuracy: float = Field(..., ge=0, le=100, description="Functional correctness score")
    speed: float = Field(..., ge=0, le=100, description="Latency and throughput score")
    quality: float = Field(..., ge=0, le=100, description="Documentation and lint quality")
    adaptability: float = Field(..., ge=0, le=100, description="Context and learning ability")
    reliability: float = Field(..., ge=0, le=100, description="Stability and recovery score")

    class Config:
        extra = "forbid"


class TaskContextPayload(BaseModel):
    """
    [CREATE] Captures contextual metadata for each evaluation request.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    task_type: TaskTypeName = Field(..., description="Task family executed by the agent")
    complexity: ComplexityLevelName = Field(..., description="Difficulty tier of the task")
    language: str = Field(..., min_length=1, description="Primary programming language")
    lines_of_code: int = Field(..., ge=0, le=10000, description="Lines touched during task")
    duration_seconds: float = Field(..., gt=0, description="End-to-end task duration")

    class Config:
        extra = "forbid"


class EvaluationRequest(BaseModel):
    """
    [CREATE] Top-level request envelope for the evaluation endpoint.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    metrics: MetricScoresPayload
    context: TaskContextPayload


class EvaluationResult(BaseModel):
    """
    [CREATE] Serializes the AMES composite output for API responses.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    composite_score: float
    base_score: float
    complexity_bonus: float
    language_modifier: float
    grade: str
    percentile: int
    adjusted_scores: Dict[str, float]
    context: Dict[str, Any]
    breakdown: Dict[str, Any]


class EvaluationEnvelope(BaseModel):
    """
    [CREATE] Response wrapper that adds identifiers and timestamps.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    evaluation_id: UUID
    recorded_at: datetime
    result: EvaluationResult


app = FastAPI(title="EudoraX Prototype API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

telemetry_manager = TelemetryManager(base_path="CodeAgents/ID")
agent_evaluator = AgentEvaluator()
evaluation_history: List[EvaluationEnvelope] = []


def _build_metric_scores(payload: MetricScoresPayload) -> MetricScores:
    """
    [CREATE] Converts a validated payload into the AMES MetricScores object.

    Args:
        payload (MetricScoresPayload): User-provided metrics.

    Returns:
        MetricScores: Domain object ready for evaluation.

    Raises:
        ValueError: If payload values fall outside AMES constraints.

    Example:
        >>> _build_metric_scores(MetricScoresPayload(
        ...     accuracy=90, speed=80, quality=85, adaptability=70, reliability=95
        ... ))

    Complexity:
        Time: O(1)
        Space: O(1)

    Side Effects:
        - None

    Design Patterns:
        - Factory: wraps payload creation into a dedicated helper.

    Thread Safety:
        Thread-safe; no shared state is mutated.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    return MetricScores(
        accuracy=payload.accuracy,
        speed=payload.speed,
        quality=payload.quality,
        adaptability=payload.adaptability,
        reliability=payload.reliability,
    )


def _build_task_context(payload: TaskContextPayload) -> TaskContext:
    """
    [CREATE] Maps request context into AMES TaskContext.

    Args:
        payload (TaskContextPayload): Context describing the agent task.

    Returns:
        TaskContext: Structured context object for AMES.

    Raises:
        KeyError: When complexity labels are unknown.

    Complexity:
        Time: O(1)
        Space: O(1)

    Side Effects:
        - None

    Design Patterns:
        - Adapter: bridges API payloads and domain models.

    Thread Safety:
        Thread-safe; uses local variables only.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    task_type = TaskType(payload.task_type.value)
    complexity = ComplexityLevel[payload.complexity.value]

    return TaskContext(
        task_type=task_type,
        complexity=complexity,
        language=payload.language,
        lines_of_code=payload.lines_of_code,
        duration_seconds=payload.duration_seconds,
    )


def _record_operation(duration_ms: int, context: Dict[str, Any]) -> None:
    """
    [CREATE] Writes a telemetry operation log for evaluation requests.

    Args:
        duration_ms (int): Request processing time in milliseconds.
        context (dict): Additional metadata for telemetry dashboards.

    Complexity:
        Time: O(1)
        Space: O(1)

    Side Effects:
        - Persists JSON logs under CodeAgents/ID/GPT-5.1-Codex/logs.

    Design Patterns:
        - Facade: encapsulates telemetry implementation details.

    Thread Safety:
        Safe for FastAPI default workers; each call creates its own log object.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    log = OperationLog(
        agent=AGENT_NAME,
        operation="ANALYZE",
        target={"file": "backend/main.py", "function": "create_evaluation"},
        status="SUCCESS",
        duration_ms=duration_ms,
        context=context,
    )
    telemetry_manager.log_operation(log)


@app.get("/")
def read_root() -> Dict[str, Any]:
    """
    [ANALYZE] Returns service metadata for quick smoke checks.

    Returns:
        dict: Basic information about the API instance.

    Complexity:
        Time: O(1)
        Space: O(1)

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    return {
        "message": "Welcome to EudoraX Prototype API",
        "uptime_seconds": (datetime.now(timezone.utc) - APP_START_TIME).total_seconds(),
    }


@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    [ANALYZE] Reports health information for liveness probes.

    Returns:
        dict: Health status indicator.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    return {"status": "healthy"}


@app.post("/evaluation", response_model=EvaluationEnvelope)
async def create_evaluation(payload: EvaluationRequest) -> EvaluationEnvelope:
    """
    [CREATE] Runs the AMES composite scoring pipeline.

    Args:
        payload (EvaluationRequest): Incoming metrics and context.

    Returns:
        EvaluationEnvelope: Identifier, timestamp, and score payload.

    Raises:
        HTTPException: If AMES rejects the provided data.

    Example:
        >>> await create_evaluation(EvaluationRequest(...))

    Complexity:
        Time: O(1)
        Space: O(1)

    Side Effects:
        - Appends to in-memory history.
        - Persists telemetry logs.

    Design Patterns:
        - Service Layer: encapsulates evaluation orchestration.

    Thread Safety:
        Safe under AsyncIO; mutations occur on FastAPI worker event loop.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    start = datetime.now(timezone.utc)

    try:
        scores = _build_metric_scores(payload.metrics)
        context = _build_task_context(payload.context)
        evaluation_result = agent_evaluator.calculate_composite_score(scores, context)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    recorded_at = datetime.now(timezone.utc)
    # Convert EvaluationResult dataclass to dict for Pydantic model
    result_dict = {
        "composite_score": evaluation_result.composite_score,
        "base_score": evaluation_result.base_score,
        "complexity_bonus": evaluation_result.complexity_bonus,
        "language_modifier": evaluation_result.language_modifier,
        "grade": evaluation_result.grade,
        "percentile": evaluation_result.percentile,
        "adjusted_scores": evaluation_result.adjusted_scores,
        "context": evaluation_result.context,
        "breakdown": evaluation_result.breakdown,
    }
    envelope = EvaluationEnvelope(
        evaluation_id=uuid4(),
        recorded_at=recorded_at,
        result=EvaluationResult(**result_dict),
    )
    evaluation_history.append(envelope)

    duration_ms = int((recorded_at - start).total_seconds() * 1000)
    _record_operation(
        duration_ms,
        {
            "task_type": payload.context.task_type.value,
            "complexity": payload.context.complexity.value,
            "language": payload.context.language,
        },
    )

    return envelope


@app.get("/evaluation/history", response_model=List[EvaluationEnvelope])
async def get_evaluation_history(limit: int = 10) -> List[EvaluationEnvelope]:
    """
    [ANALYZE] Returns the most recent evaluation envelopes.

    Args:
        limit (int): Max number of records to return. Defaults to 10.

    Returns:
        list[EvaluationEnvelope]: Chronologically descending history.

    Raises:
        HTTPException: If limit is non-positive.

    Complexity:
        Time: O(n) where n equals the requested limit.
        Space: O(n) because FastAPI serializes the slice.

    Side Effects:
        - None

    Design Patterns:
        - Query Object: exposes read-only API for stored data.

    Thread Safety:
        FastAPI ensures sequential access per request; slicing is safe.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T15:35:00Z
    """

    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be positive")

    history_slice = evaluation_history[-limit:]
    return list(reversed(history_slice))
