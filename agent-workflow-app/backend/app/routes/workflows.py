"""
Workflow routes module.

Agent: GPT-5.1-Codex
Created: 2025-12-04T00:03:00Z
Operation: [CREATE]
"""

from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

from ..datastore import DataStore
from ..models import WorkflowPayload

workflows_bp = Blueprint("workflows", __name__)


def _store() -> DataStore:
    """Retrieve the shared datastore from app config."""

    return current_app.config["DATASTORE"]


@workflows_bp.get("/workflows")
def list_workflows():
    """
    [ANALYZE] Return all workflows with computed action/analysis ratio flag.
    """

    workflows = _store().list_workflows()
    for wf in workflows:
        metrics = wf.setdefault("metrics", {})
        action = metrics.get("action_count", 0) or 0.0001
        analysis = metrics.get("analysis_count", 0)
        metrics["action_analysis_ratio"] = round(action / max(analysis, 1), 2)
    return jsonify(workflows)


@workflows_bp.post("/workflows")
def create_workflow():
    """
    [CREATE] Add a workflow derived from telemetry recommendations.
    """

    payload = WorkflowPayload(**request.json)
    workflow = _store().add_workflow(payload.dict())
    workflow["created_at"] = datetime.now(timezone.utc).isoformat()
    return jsonify(workflow), 201


@workflows_bp.patch("/workflows/<workflow_id>")
def update_workflow(workflow_id: str):
    """
    [MODIFY] Update workflow status or metadata.
    """

    payload = request.json or {}
    try:
        workflow = _store().update_workflow(workflow_id, payload)
    except KeyError as err:
        return jsonify({"error": str(err)}), 404
    return jsonify(workflow)

