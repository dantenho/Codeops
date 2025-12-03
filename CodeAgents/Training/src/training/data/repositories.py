"""
Module: repositories.py
Purpose: Repository objects for ATS collections.

Encapsulates CRUD and utility helpers (e.g., duplicate detection) for each
collection so that higher-level services have a clean, hierarchical API.

Agent: GPT-5.1 Codex
Created: 2025-12-03T07:10:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from chromadb.api.types import Collection

from .client import ChromaDatabase


def _hash_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class BaseRepository:
    """Common helpers shared across repositories."""

    def __init__(self, collection: Collection):
        self.collection = collection

    def count(self) -> int:
        return self.collection.count()

    def _delete_ids(self, ids: Sequence[str]) -> int:
        if not ids:
            return 0
        self.collection.delete(ids=list(ids))
        return len(ids)


class TrainingMaterialRepository(BaseRepository):
    """CRUD helpers for training materials stored in Chroma."""

    def add_material(
        self,
        topic: str,
        document: str,
        agent_id: str,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        file_hash = _hash_text(document)
        metadatas = {
            "topic": topic,
            "agent_id": agent_id,
            "timestamp": _timestamp(),
            "file_name": file_name or "unknown",
            "content_hash": file_hash,
        }
        if metadata:
            metadatas.update(metadata)

        self.collection.add(
            documents=[document],
            metadatas=[metadatas],
            ids=[f"{file_hash}_{_timestamp()}"],
        )

    def query(self, topic: str, limit: int, agent_id: Optional[str] = None):
        where_clause: Optional[Dict[str, Any]] = None
        if agent_id:
            where_clause = {"agent_id": agent_id}

        return self.collection.query(
            query_texts=[topic],
            n_results=limit,
            where=where_clause,
        )

    def remove_duplicate_documents(self) -> int:
        """
        Remove duplicate documents based on (agent_id, file_name, content_hash).
        """
        dataset = self.collection.get(include=["metadatas", "ids"])
        metadatas: List[Dict[str, Any]] = dataset.get("metadatas") or []
        ids: List[str] = dataset.get("ids") or []

        observed: dict[tuple[Any, ...], str] = {}
        duplicates: list[str] = []

        for metadata, doc_id in zip(metadatas, ids):
            key = (
                metadata.get("agent_id"),
                metadata.get("file_name"),
                metadata.get("content_hash"),
            )
            if key in observed:
                duplicates.append(doc_id)
            else:
                observed[key] = doc_id

        return self._delete_ids(duplicates)


class ScoreRepository(BaseRepository):
    """Repository for score collection documents."""

    def add_score(
        self,
        topic: str,
        score: float,
        time_taken: float,
        agent_id: str,
        metrics: Dict[str, Any],
    ) -> None:
        metadata = {
            "topic": topic,
            "score": score,
            "time_taken": time_taken,
            "agent_id": agent_id,
            "timestamp": _timestamp(),
            **metrics,
        }
        self.collection.add(
            documents=[f"Topic: {topic}, Score: {score}, Time: {time_taken}"],
            metadatas=[metadata],
            ids=[f"score_{agent_id}_{_timestamp()}"],
        )

    def fetch_scores(
        self,
        agent_id: str,
        topic: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        if limit <= 0:
            return []

        if topic:
            where_clause: Dict[str, Any] = {"$and": [{"agent_id": agent_id}, {"topic": topic}]}
        else:
            where_clause = {"agent_id": agent_id}

        payload = self.collection.get(where=where_clause, limit=limit, include=["metadatas"])
        return payload.get("metadatas") or []


class ErrorRepository(BaseRepository):
    """Repository for error collection."""

    def add_error(self, message: str, context: str, agent_id: str) -> None:
        severity = "high" if "critical" in message.lower() else "medium"
        metadata = {
            "context": context,
            "agent_id": agent_id,
            "timestamp": _timestamp(),
            "severity": severity,
        }
        self.collection.add(
            documents=[message],
            metadatas=[metadata],
            ids=[f"error_{agent_id}_{_timestamp()}"],
        )

    def recent_errors(self, agent_id: Optional[str], limit: int) -> Dict[str, Any]:
        where_clause = {"agent_id": agent_id} if agent_id else None
        return self.collection.get(where=where_clause, limit=limit, include=["metadatas", "documents", "ids"])


class DailyLogRepository(BaseRepository):
    """Repository for daily logs."""

    def add_log(self, agent_id: str, activity_type: str, details: Dict[str, Any]):
        metadata = {
            "agent_id": agent_id,
            "activity_type": activity_type,
            "timestamp": _timestamp(),
            **{k: str(v) for k, v in details.items()},
        }
        self.collection.add(
            documents=[f"Activity: {activity_type} - {metadata['timestamp']}"],
            metadatas=[metadata],
            ids=[f"log_{agent_id}_{_timestamp()}"],
        )

    def get_recent(self, agent_id: str, limit: int = 100):
        return self.collection.get(where={"agent_id": agent_id}, limit=limit)


class RepositoryRegistry:
    """Factory/registry that exposes strongly-typed repositories."""

    def __init__(self, database: Optional[ChromaDatabase] = None):
        self.database = database or ChromaDatabase()
        self.training_materials = TrainingMaterialRepository(self.database.collections.training)
        self.scores = ScoreRepository(self.database.collections.scores)
        self.errors = ErrorRepository(self.database.collections.errors)
        self.daily_logs = DailyLogRepository(self.database.collections.daily_logs)

    def stats(self) -> dict[str, int]:
        return self.database.stats()
