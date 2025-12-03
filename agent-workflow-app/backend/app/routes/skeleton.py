"""
Skeleton readiness routes.

Agent: GPT-5.1-Codex
Created: 2025-12-04T00:05:00Z
Operation: [CREATE]
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from ..datastore import DataStore

skeleton_bp = Blueprint("skeleton", __name__)


def _store() -> DataStore:
    return current_app.config["DATASTORE"]


@skeleton_bp.get("/skeleton/summary")
def skeleton_summary():
    """
    [ANALYZE] Provide aggregate skeleton validation metrics.
    """

    return jsonify(_store().skeleton_summary())

