"""
Unit tests for the OptimizationService orchestration layer.
"""

from __future__ import annotations

from pathlib import Path

from CodeAgents.GitHub.optimization_service import OptimizationService


def _make_service(tmp_path: Path) -> OptimizationService:
    catalog_dir = tmp_path / "catalog"
    telemetry_dir = tmp_path / "telemetry"
    memory_dir = tmp_path / "memory"
    return OptimizationService(
        catalog_path=catalog_dir,
        telemetry_path=telemetry_dir,
        memory_db_path=memory_dir,
        config_path=None,
    )


def test_process_pull_request_creates_catalog_entries(tmp_path):
    service = _make_service(tmp_path)
    payload = {
        "comments": [
            {
                "id": "1",
                "body": "Consider using a list comprehension for better performance.",
                "user": {"login": "reviewer"},
                "created_at": "2025-12-03T00:00:00Z",
                "path": "src/example.py",
                "line": 10,
            }
        ]
    }

    summary = service.process_pull_request(payload)

    assert summary["total_comments"] == 1
    assert summary["detected_optimizations"] >= 1
    assert summary["catalog_entries_created"] >= 1
    assert (service.catalog.catalog_path / "catalog.json").exists()


def test_recommend_for_code_returns_matches(tmp_path):
    service = _make_service(tmp_path)
    payload = {
        "comments": [
            {
                "id": "99",
                "body": "This could be optimized with a list comprehension.",
            }
        ]
    }
    service.process_pull_request(payload)

    code = """
result = []
for item in items:
    result.append(item * 2)
"""
    recommendations = service.recommend_for_code(code, language="python", limit=3)

    assert recommendations, "Expected at least one recommendation"
    assert "list" in recommendations[0].optimization.title.lower()


def test_export_catalog_writes_yaml(tmp_path):
    service = _make_service(tmp_path)
    payload = {
        "comments": [
            {
                "id": "100",
                "body": "Use dict.get() instead of manual checks.",
            }
        ]
    }
    service.process_pull_request(payload)

    output_path = tmp_path / "catalog.yaml"
    service.export_catalog(output_path)

    assert output_path.exists()
    contents = output_path.read_text(encoding="utf-8")
    assert "patterns" in contents
    assert "dict_get" in contents
