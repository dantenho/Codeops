import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from training.models.session import SessionStatus, SessionType, TrainingSession
from training.services.config_service import ConfigService
from training.services.threndia_service import ThrendiaService


def _setup_training_base(tmp_path: Path) -> Path:
    base = tmp_path / "CodeAgents" / "Training"
    (base / "config").mkdir(parents=True)
    (base / "ThrendiaData" / "intel").mkdir(parents=True)
    return base


def _write_agent_profile(config_dir: Path) -> None:
    profile = """
agents:
  EudoraX-Pylorix:
    current_level: 2
    roles: [market_analyst]
    intel_sources:
      - name: "Threndia Web Scraper"
        type: web
        endpoint: "https://github.com/Eudora-IA/Threndia"
    telemetry_namespace: mutual_cooperation
    shared_storage_path: "CodeAgents/Training/ThrendiaData"
    threndia:
      api_token_env: "THRENDIA_API_TOKEN"
      scrape_freq_env: "THRENDIA_SCRAPE_FREQ_MINUTES"
      default_session_type: market_analysis
      tagging:
        intel_batch_prefix: "threndia-intel"
        market_focus_topics: ["market_trends"]
"""
    (config_dir / "agent_profiles.yaml").write_text(profile.strip(), encoding="utf-8")


def _write_sample_intel(intel_dir: Path) -> None:
    sample = {
        "title": "Weekly Market Pulse",
        "summary": "Analyze the latest funding rounds and competitive shifts.",
        "source": "https://intel.example.com/report-1",
        "category": "market_trends",
        "risk_level": "low",
        "difficulty": 3,
    }
    (intel_dir / "sample.json").write_text(json.dumps(sample), encoding="utf-8")


@pytest.fixture()
def threndia_env(tmp_path, monkeypatch) -> ThrendiaService:
    base = _setup_training_base(tmp_path)
    _write_agent_profile(base / "config")
    _write_sample_intel(base / "ThrendiaData" / "intel")

    monkeypatch.setenv("THRENDIA_API_TOKEN", "demo-token")
    monkeypatch.setenv("THRENDIA_SCRAPE_FREQ_MINUTES", "45")

    config_service = ConfigService(base / "config")
    return ThrendiaService(base, config_service)


def test_generate_market_activities_returns_research_tasks(threndia_env):
    activities, metadata = threndia_env.generate_market_activities("EudoraX-Pylorix", limit=2)

    assert activities, "Expected at least one generated activity"
    assert activities[0].activity_type.value == "research"
    assert metadata["intel_batch_id"].startswith("threndia-intel")


def test_sync_intel_creates_log_file(threndia_env):
    summary = threndia_env.sync_intel("EudoraX-Pylorix", dry_run=False)

    logs_dir = threndia_env.base_path.parent / "EudoraX-Pylorix" / "logs"
    log_files = list(logs_dir.glob("log_*.json"))
    assert log_files, "Expected telemetry log to be written"

    with open(log_files[-1], "r", encoding="utf-8") as handle:
        log_data = json.load(handle)

    assert log_data["operation"] == "threndia_sync"
    assert log_data["intel_batch_id"] == summary["intel_batch_id"]


def test_record_market_session_logs_session(threndia_env):
    session = TrainingSession(
        session_id="session-123",
        agent_id="EudoraX-Pylorix",
        session_type=SessionType.MARKET_ANALYSIS,
        scheduled_for=datetime.now(timezone.utc),
        status=SessionStatus.IN_PROGRESS,
        activities=[],
    )
    session.complete()

    metadata = {"intel_batch_id": "threndia-intel-test", "sources": ["threndia-placeholder"]}
    log_path = threndia_env.record_market_session(session, metadata)

    assert log_path and log_path.exists()
    payload = json.loads(log_path.read_text(encoding="utf-8"))
    assert payload["operation"] == "market_analysis_session"
    assert payload["intel_batch_id"] == metadata["intel_batch_id"]
