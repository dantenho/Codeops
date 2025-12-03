"""
High-level orchestration service for GitHub optimization workflows.

Wires together the comment processor, detector, catalog, and optional
memory service so PR feedback can automatically become reusable patterns.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import yaml

from .comment_processor import CommentProcessor, OptimizationComment
from .optimization_catalog import CatalogEntry, OptimizationCatalog
from .optimization_detector import DetectedOptimization, OptimizationDetector

try:  # Memory service is optional – only available in training package.
    from CodeAgents.Training.src.training.services.memory_service import MemoryService  # type: ignore
except Exception:  # pragma: no cover - fallback for environments without training pkg
    MemoryService = None  # type: ignore


class OptimizationService:
    """
    Orchestrates the GitHub optimization learning loop.

    Responsibilities:
        * Parse PR feedback via CommentProcessor.
        * Detect optimization patterns via OptimizationDetector.
        * Persist catalog entries and training materials via OptimizationCatalog.
        * Emit lightweight telemetry so Agents.MD compliance tooling can trace runs.
    """

    DEFAULT_CONFIG_PATH = Path("config/optimization_patterns.yaml")

    def __init__(
        self,
        config_path: Optional[Path | str] = None,
        *,
        catalog_path: Optional[Path | str] = None,
        memory_db_path: Optional[Path | str] = None,
        telemetry_path: Optional[Path | str] = None,
    ) -> None:
        self.comment_processor = CommentProcessor()
        self.detector = OptimizationDetector()

        self.config = self._load_config(config_path)

        catalog_path = Path(
            catalog_path
            or self.config.get("service", {}).get("catalog_path", "data/optimizations")
        )
        memory_db_path = Path(
            memory_db_path
            or self.config.get("service", {}).get("memory_db_path", "CodeAgents/Training/chroma_db")
        )
        telemetry_path = Path(
            telemetry_path
            or self.config.get("service", {}).get(
                "telemetry_path", "CodeAgents/ID/Optimization/logs"
            )
        )

        self.telemetry_path = telemetry_path
        self.telemetry_path.mkdir(parents=True, exist_ok=True)

        self.memory_service = self._maybe_create_memory_service(memory_db_path)
        self.catalog = OptimizationCatalog(
            catalog_path,
            memory_service=self.memory_service,
        )

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def process_pull_request(self, pr_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a GitHub pull request payload and update the optimization catalog.

        Args:
            pr_payload: GitHub API payload containing `comments` or review comment arrays.

        Returns:
            Summary dictionary with counts and identifiers for telemetry/reporting.
        """
        processed_comments = self.comment_processor.process_pr_comments(pr_payload)
        detected: List[DetectedOptimization] = []

        for comment in processed_comments:
            detected.extend(self.detector.analyze_comment(comment))

        catalog_entries = self._persist_optimizations(detected, processed_comments)
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_comments": len(processed_comments),
            "detected_optimizations": len(detected),
            "catalog_entries_created": len(catalog_entries),
            "catalog_path": str(self.catalog.catalog_path),
        }
        self._write_telemetry("process_pull_request", summary)
        return summary

    def process_comments(self, comments: Sequence[str]) -> Dict[str, Any]:
        """
        Convenience helper for CLI pipelines that only supply raw comment strings.
        """
        payload = {"comments": [{"id": idx, "body": body} for idx, body in enumerate(comments)]}
        return self.process_pull_request(payload)

    def recommend_for_code(
        self,
        code: str,
        *,
        language: str = "python",
        limit: int = 5,
    ) -> List[CatalogEntry]:
        """
        Return top catalog recommendations for the provided code snippet.
        """
        return self.catalog.get_recommendations(code, language=language, limit=limit)

    def export_catalog(self, output_path: Path | str) -> Path:
        """
        Export the optimization catalog to a YAML file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.catalog.export_to_yaml(output_path)
        self._write_telemetry(
            "export_catalog",
            {
                "output_path": str(output_path),
                "total_patterns": len(self.catalog.entries),
            },
        )
        return output_path

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _persist_optimizations(
        self,
        optimizations: Sequence[DetectedOptimization],
        comments: Sequence[OptimizationComment],
    ) -> List[CatalogEntry]:
        entries: List[CatalogEntry] = []

        tags_by_comment: Dict[str, List[str]] = {
            comment.comment_id: comment.tags or [] for comment in comments
        }

        for optimization in optimizations:
            comment_tags: List[str] = []
            for comment_id in optimization.related_comment_ids:
                comment_tags.extend(tags_by_comment.get(comment_id, []))

            entry = self.catalog.add_optimization(
                optimization,
                tags=list(set(comment_tags)),
                create_training_material=bool(self.memory_service),
            )
            entries.append(entry)

        return entries

    def _load_config(self, config_path: Optional[Path | str]) -> Dict[str, Any]:
        candidate = Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        if not candidate.exists():
            return {}

        with open(candidate, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _maybe_create_memory_service(
        self,
        memory_db_path: Path,
    ) -> Optional["MemoryService"]:
        if MemoryService is None:
            return None

        try:
            memory_db_path.parent.mkdir(parents=True, exist_ok=True)
            return MemoryService(str(memory_db_path))
        except Exception:
            return None

    def _write_telemetry(self, operation: str, payload: Dict[str, Any]) -> None:
        """
        Persist a JSON telemetry log for compliance with Agents.MD.
        """
        telemetry = {
            "agent": os.getenv("OPTIMIZATION_AGENT", "OptimizationService"),
            "operation": operation,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }

        log_name = f"log_{telemetry['timestamp'].replace(':', '-').replace('.', '-')}.json"
        try:
            with open(self.telemetry_path / log_name, "w", encoding="utf-8") as handle:
                json.dump(telemetry, handle, indent=2)
        except Exception:
            # Telemetry failures should never block the main workflow.
            pass
