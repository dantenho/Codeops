"""
CLI regression tests for the Agent Training System.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from CodeAgents.Training.src.training import cli as training_cli
from CodeAgents.Training.src.training.data.progress_repository import ProgressRepository
from CodeAgents.Training.src.training.services.token_tracker import TokenTracker


class _MemoryStub:
    """Minimal stand-in for MemoryService used in tests."""

    def __init__(self) -> None:
        self.training_materials = []
        self.scores = []
        self.logs = []
        self.errors = []

    def add_training_material(self, *args, **kwargs):
        self.training_materials.append((args, kwargs))

    def add_score(self, *args, **kwargs):
        self.scores.append((args, kwargs))

    def log_daily_activity(self, *args, **kwargs):
        self.logs.append((args, kwargs))

    def add_error(self, *args, **kwargs):
        self.errors.append((args, kwargs))


@pytest.fixture()
def cli_env(monkeypatch, tmp_path: Path):
    repo = ProgressRepository(tmp_path / "progress")
    monkeypatch.setattr(training_cli.training_manager, "progress_repo", repo)
    tracker = TokenTracker(tmp_path / "tokens")
    monkeypatch.setattr(training_cli, "token_tracker", tracker)
    monkeypatch.setattr(training_cli, "memory_service", _MemoryStub())
    training_cli.training_manager._threndia_cache.clear()
    return {"runner": CliRunner(), "tracker": tracker, "repo": repo}


def test_init_and_progress(cli_env):
    runner = cli_env["runner"]
    result = runner.invoke(training_cli.app, ["init", "ClaudeCode", "--force"])
    assert result.exit_code == 0, result.output

    result = runner.invoke(training_cli.app, ["progress", "ClaudeCode"])
    assert result.exit_code == 0, result.output
    assert "Level" in result.stdout


def test_start_session_records_tokens(cli_env):
    runner = cli_env["runner"]
    runner.invoke(training_cli.app, ["init", "ClaudeCode", "--force"])

    result = runner.invoke(training_cli.app, ["start", "ClaudeCode", "--type", "daily"])
    assert result.exit_code == 0, result.output

    stats = cli_env["tracker"].get_agent_stats("ClaudeCode")
    assert stats.total_operations > 0
    assert stats.lifetime_tokens > 0


def test_simulation_generates_token_summary(cli_env):
    runner = cli_env["runner"]
    runner.invoke(training_cli.app, ["init", "ClaudeCode", "--force"])

    result = runner.invoke(
        training_cli.app, ["simulate", "ClaudeCode", "--iterations", "2", "--topic", "dsa"]
    )
    assert result.exit_code == 0, result.output

    stats = cli_env["tracker"].get_agent_stats("ClaudeCode")
    assert stats.total_operations > 0
