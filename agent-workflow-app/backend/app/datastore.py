"""
Module: app.datastore
Purpose: Provide an in-memory data store seeded from JSON fixtures.

Agent: GPT-5.1-Codex
Created: 2025-12-04T00:00:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DataStore:
    """
    [CREATE] Simple repository backing the API endpoints.

    Attributes:
        data_root (Path): Directory containing seed JSON files.
        workflows (list[dict[str, Any]]): Workflows collection.
        telemetry (list[dict[str, Any]]): Telemetry events collection.

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-04T00:00:00Z
    """

    data_root: Path
    workflows: list[dict[str, Any]] = field(default_factory=list)
    telemetry: list[dict[str, Any]] = field(default_factory=list)

    def load_seed_data(self) -> None:
        """
        [CREATE] Load workflow and telemetry data from JSON seeds.

        Raises:
            FileNotFoundError: When a required JSON file is missing.
        """

        workflow_file = self.data_root / "sample_workflows.json"
        telemetry_file = self.data_root / "sample_telemetry.json"

        self.workflows = self._read_json_file(workflow_file)
        self.telemetry = self._read_json_file(telemetry_file)

    def list_workflows(self) -> list[dict[str, Any]]:
        """Return all workflows."""

        return list(self.workflows)

    def add_workflow(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        [CREATE] Append a workflow to the collection.

        Args:
            payload (dict[str, Any]): Workflow data.

        Returns:
            dict[str, Any]: Stored workflow including generated id.
        """

        workflow = payload.copy()
        workflow.setdefault("id", f"wf-{uuid.uuid4().hex[:8]}")
        workflow.setdefault("status", "planned")
        self.workflows.append(workflow)
        return workflow

    def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """
        [MODIFY] Update an existing workflow.

        Raises:
            KeyError: If the workflow_id is unknown.
        """

        for workflow in self.workflows:
            if workflow["id"] == workflow_id:
                workflow.update(updates)
                return workflow
        raise KeyError(f"Workflow {workflow_id} not found")

    def list_telemetry(self) -> list[dict[str, Any]]:
        """Return telemetry events ordered newest-first."""

        return sorted(self.telemetry, key=lambda event: event["timestamp"], reverse=True)

    def add_telemetry(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        [CREATE] Append telemetry event.

        Args:
            payload (dict[str, Any]): Event details containing timestamp,
                operation, target, and context.
        """

        self.telemetry.append(payload)
        return payload

    def skeleton_summary(self) -> dict[str, Any]:
        """
        [ANALYZE] Derive skeleton completeness metrics.

        Returns:
            dict[str, Any]: Aggregated stats referencing annotation heuristics.
        """

        total = len(self.workflows)
        skeleton_related = [wf for wf in self.workflows if wf.get("category") == "skeleton"]
        completion_ratio = 0.0
        if skeleton_related:
            completion_ratio = sum(
                wf.get("compliance", {}).get("balanced_components", 0.0)
                for wf in skeleton_related
            ) / len(skeleton_related)

        return {
            "total_workflows": total,
            "skeleton_workflows": len(skeleton_related),
            "average_balance": round(completion_ratio, 2),
            "recommendations": [
                "Automate skeleton generation hooks",
                "Attach telemetry events to generator runs",
            ],
        }

    @staticmethod
    def _read_json_file(path: Path) -> list[dict[str, Any]]:
        """Utility reading JSON arrays from disk."""

        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

