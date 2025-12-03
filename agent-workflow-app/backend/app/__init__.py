"""
Module: app.__init__.py
Purpose: Application factory for the Agent Workflow backend.

Creates and configures the Flask application, registers API blueprints, and
injects in-memory data stores seeded from the shared `data/` directory.

Agent: GPT-5.1-Codex
Created: 2025-12-03T23:58:00Z
Operation: [CREATE]
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask
from flask_cors import CORS

from .config import AppConfig
from .datastore import DataStore
from .routes.skeleton import skeleton_bp
from .routes.telemetry import telemetry_bp
from .routes.workflows import workflows_bp


def create_app(config: AppConfig | None = None) -> Flask:
    """
    [CREATE] Build and configure the Flask application.

    Args:
        config (AppConfig | None): Optional explicit configuration. When not
            provided, values are loaded from environment variables.

    Returns:
        Flask: Configured application instance with registered blueprints.

    Example:
        >>> app = create_app()
        >>> client = app.test_client()
        >>> resp = client.get(\"/api/workflows\")
        >>> resp.status_code
        200

    Agent: GPT-5.1-Codex
    Timestamp: 2025-12-03T23:58:00Z
    """

    app = Flask(__name__)
    cfg = config or AppConfig.from_env()

    data_root = Path(cfg.data_dir).resolve()
    datastore = DataStore(data_root=data_root)
    datastore.load_seed_data()

    app.config["DATASTORE"] = datastore
    CORS(app, resources={r"/api/*": {"origins": cfg.allow_origins}})

    app.register_blueprint(workflows_bp, url_prefix="/api")
    app.register_blueprint(telemetry_bp, url_prefix="/api")
    app.register_blueprint(skeleton_bp, url_prefix="/api")

    @app.get("/health")
    def health_check() -> dict[str, str]:
        """Simple health endpoint for uptime checks."""

        return {"status": "ok"}

    return app


__all__ = ["create_app"]

