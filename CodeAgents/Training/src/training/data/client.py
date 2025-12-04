"""
Module: client.py
Purpose: Hierarchical wrapper around ChromaDB collections.

Establishes a single point of entry for the training datastore so that other
modules interact with a structured interface instead of bare global
collections.

Agent: GPT-5.1 Codex
Created: 2025-12-03T07:10:00Z
Operation: [CREATE]
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.api.models.Collection import Collection


DEFAULT_DB_PATH = Path("chroma_db")


@dataclass(frozen=True)
class CollectionSet:
    """Typed container for the four ATS data collections."""

    training: Collection
    scores: Collection
    errors: Collection
    daily_logs: Collection


class ChromaDatabase:
    """
    [CREATE] Facade that exposes typed access to ChromaDB collections.

    Design Pattern:
        Facade + Repository seed. Callers access domain-specific repositories
        rather than global module-level state.

    Thread Safety:
        Not thread-safe. Instantiate per-process.
    """

    def __init__(self, path: Optional[str | Path] = None):
        resolved_path = Path(path) if path else DEFAULT_DB_PATH
        resolved_path.mkdir(parents=True, exist_ok=True)
        self.path = resolved_path
        self.client = chromadb.PersistentClient(path=str(self.path))
        self.collections = CollectionSet(
            training=self.client.get_or_create_collection("training_data"),
            scores=self.client.get_or_create_collection("score_data"),
            errors=self.client.get_or_create_collection("error_data"),
            daily_logs=self.client.get_or_create_collection("daily_log_data"),
        )

    def stats(self) -> dict[str, int]:
        """Return document counts for each collection."""
        return {
            "training": self.collections.training.count(),
            "scores": self.collections.scores.count(),
            "errors": self.collections.errors.count(),
            "daily_logs": self.collections.daily_logs.count(),
        }

    def close(self) -> None:
        """Placeholder to support future resource cleanup."""
        # chromadb PersistentClient does not yet expose close semantics.
        return
