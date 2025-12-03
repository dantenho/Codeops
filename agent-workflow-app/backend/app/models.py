"""
Module: app.models
Purpose: Pydantic request/response models shared by API routes.

Agent: GPT-5.1-Codex
Created: 2025-12-04T00:02:00Z
Operation: [CREATE]
"""

from __future__ import annotations

from typing import Literal, Sequence

from pydantic import BaseModel, Field, validator


class WorkflowPayload(BaseModel):
    """
    [CREATE] Request model for workflow creation/update.

    Fields align with the telemetry-derived requirements (category, status,
    compliance metrics, action-to-analysis ratio targets).
    """

    title: str = Field(..., min_length=3)
    owner: str = Field(..., min_length=2)
    category: Literal["telemetry", "skeleton", "rag", "communication"]
    status: Literal["planned", "in_progress", "blocked", "done"] = "planned"
    priority: Literal["low", "medium", "high"] = "medium"
    tags: Sequence[str] = ()
    compliance: dict = Field(default_factory=dict)
    metrics: dict = Field(default_factory=dict)
    next_steps: Sequence[str] = ()
    blockers: Sequence[str] = ()

    @validator("next_steps", "blockers", pre=True)
    def ensure_sequences(cls, value):  # type: ignore[override]
        """Normalize optional arrays."""

        if value is None:
            return ()
        if isinstance(value, list):
            return value
        return (value,)


class TelemetryPayload(BaseModel):
    """
    [CREATE] Payload for telemetry ingestion.
    """

    timestamp: str
    operation: str
    target: str
    status: Literal["SUCCESS", "FAILURE", "PARTIAL"]
    duration_ms: int = Field(..., ge=0)
    context: dict = Field(default_factory=dict)

