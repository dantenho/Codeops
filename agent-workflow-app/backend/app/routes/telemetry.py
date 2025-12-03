"""
Telemetry routes.

Agent: GPT-5.1-Codex
Created: 2025-12-04T00:04:00Z
Operation: [CREATE]
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..datastore import DataStore
from ..models import TelemetryPayload

telemetry_bp = Blueprint("telemetry", __name__)


def _store() -> DataStore:
    return current_app.config["DATASTORE"]


@telemetry_bp.get("/telemetry")
def list_telemetry():
    """Return recent telemetry events."""

    return jsonify(_store().list_telemetry())


@telemetry_bp.post("/telemetry")
def create_telemetry():
    """
    [CREATE] Store a telemetry event in the in-memory buffer.
    """

    payload = TelemetryPayload(**request.json)
    record = _store().add_telemetry(payload.dict())
    return jsonify(record), 201

