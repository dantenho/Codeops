"""
Memory Service for the Agent Training System.
"""

from typing import Dict, Any, List, Optional

from ..data.client import ChromaDatabase
from ..data.repositories import RepositoryRegistry


class MemoryService:
    def __init__(self, db_path: Optional[str] = None):
        database = ChromaDatabase(db_path) if db_path else None
        self.registry = RepositoryRegistry(database)

    def add_training_material(self, topic: str, file_name: str, content: str, agent_id: str = "system"):
        """Adds training material to the memory."""
        self.registry.training_materials.add_material(
            topic=topic,
            document=content,
            agent_id=agent_id,
            file_name=file_name,
        )

    def recall_training_material(self, topic: str, limit: int = 5, agent_id: Optional[str] = None):
        """
        [REFACTOR] Retrieve training materials related to a topic (optionally agent filtered).

        Purpose:
            Surfaces the content previously embedded into Chroma so agents can refresh knowledge.

        Parameters:
            topic (str): Semantic search seed used to locate relevant documents. Must be non-empty.
            limit (int): Maximum number of documents to return. Must be positive.
            agent_id (Optional[str]): Optional filter to restrict documents to a specific agent context.

        Returns:
            Dict[str, Any]: Raw Chroma query response including documents, ids, and metadata.

        Raises:
            ValueError: If limit <= 0 or topic is empty.

        Example:
            >>> MemoryService().recall_training_material("dsa", limit=3, agent_id="ClaudeCode")

        Complexity:
            Time: O(k) where k == limit
            Space: O(k)

        Side Effects:
            - Issues a read operation against the persistent Chroma collection.

        Design Patterns:
            None. Direct gateway to the vector store.

        Thread Safety:
            Not thread-safe because Chroma clients are shared.

        Agent: GPT-5.1 Codex
        Timestamp: 2025-12-03T00:00:00Z
        """
        if not topic:
            raise ValueError("topic is required for recall operations.")
        if limit <= 0:
            raise ValueError("limit must be greater than zero.")

        return self.registry.training_materials.query(topic, limit, agent_id=agent_id)

    def summarize_agent_performance(
        self,
        agent_id: str,
        topic: Optional[str] = None,
        limit: int = 25,
    ) -> Dict[str, Any]:
        """
        [CREATE] Aggregate score/time metrics for an agent (optionally by topic).

        Purpose:
            Provides fast visibility into how an agent performs over time leveraging Chroma score
            entries. Outputs both the raw entries and useful summary statistics that can power CLI
            dashboards or automated recommendations.

        Parameters:
            agent_id (str): Unique agent identifier used throughout the training system.
            topic (Optional[str]): When provided, only include results for that topic.
            limit (int): Maximum number of score entries to inspect. Must be positive.

        Returns:
            Dict[str, Any]: {
                "agent_id": str,
                "topic": Optional[str],
                "entries": List[Dict[str, Any]],
                "summary": Dict[str, float]
            }

        Raises:
            ValueError: If limit <= 0 or agent_id is empty.

        Example:
            >>> MemoryService().summarize_agent_performance("ClaudeCode", limit=10)

        Complexity:
            Time: O(n) where n == number of retrieved score records.
            Space: O(n) for the materialized summary list.

        Side Effects:
            - Executes read queries against Chroma score collection.

        Design Patterns:
            Repository-style data access for summarizing records.

        Thread Safety:
            Not thread-safe; relies on shared mutable Chroma client state.

        Agent: GPT-5.1 Codex
        Timestamp: 2025-12-03T00:00:00Z
        """
        if not agent_id:
            raise ValueError("agent_id is required to summarize performance.")
        if limit <= 0:
            raise ValueError("limit must be greater than zero.")

        metadatas = self.registry.scores.fetch_scores(agent_id, topic, limit)

        def _as_float(value: Any) -> float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        entries: List[Dict[str, Any]] = []
        for metadata in metadatas:
            score = _as_float(metadata.get("score"))
            time_taken = _as_float(metadata.get("time_taken"))
            score_per_minute = (score / time_taken * 60) if time_taken > 0 else 0.0
            tokens_processed = _as_float(metadata.get("tokens_processed"))
            tokens_per_second = _as_float(metadata.get("tokens_per_second"))
            score_per_token = _as_float(metadata.get("score_per_token"))
            gpu_utilization = _as_float(metadata.get("gpu_utilization_avg"))
            gpu_memory = _as_float(metadata.get("gpu_memory_used_mb"))

            entries.append(
                {
                    "topic": metadata.get("topic", topic or "unknown"),
                    "score": score,
                    "time_taken": time_taken,
                    "score_per_minute": score_per_minute,
                    "tokens_processed": tokens_processed,
                    "tokens_per_second": tokens_per_second,
                    "score_per_token": score_per_token,
                    "gpu_utilization_avg": gpu_utilization,
                    "gpu_memory_used_mb": gpu_memory,
                    "timestamp": metadata.get("timestamp"),
                    "fatigue_level": metadata.get("fatigue_level"),
                    "files_processed": metadata.get("files_processed"),
                    "session_type": metadata.get("session_type"),
                }
            )

        if not entries:
            return {
                "agent_id": agent_id,
                "topic": topic,
                "entries": [],
                "summary": {
                    "sample_size": 0,
                    "average_score": 0.0,
                    "average_time_seconds": 0.0,
                    "average_score_per_minute": 0.0,
                },
            }

        sample_size = len(entries)
        average_score = sum(entry["score"] for entry in entries) / sample_size
        average_time = sum(entry["time_taken"] for entry in entries) / sample_size
        average_score_per_minute = (
            sum(entry["score_per_minute"] for entry in entries) / sample_size
        )
        average_tokens = sum(entry["tokens_processed"] for entry in entries) / sample_size
        average_tokens_per_second = (
            sum(entry["tokens_per_second"] for entry in entries) / sample_size
        )
        average_score_per_token = (
            sum(entry["score_per_token"] for entry in entries) / sample_size
        )
        average_gpu_utilization = (
            sum(entry["gpu_utilization_avg"] for entry in entries) / sample_size
        )
        average_gpu_memory = (
            sum(entry["gpu_memory_used_mb"] for entry in entries) / sample_size
        )

        return {
            "agent_id": agent_id,
            "topic": topic,
            "entries": entries,
            "summary": {
                "sample_size": sample_size,
                "average_score": average_score,
                "average_time_seconds": average_time,
                "average_score_per_minute": average_score_per_minute,
                "average_tokens_processed": average_tokens,
                "average_tokens_per_second": average_tokens_per_second,
                "average_score_per_token": average_score_per_token,
                "average_gpu_utilization": average_gpu_utilization,
                "average_gpu_memory_used_mb": average_gpu_memory,
            },
        }

    def get_recent_errors(self, agent_id: Optional[str], limit: int = 5) -> Dict[str, Any]:
        """
        [CREATE] Retrieve the most recent error logs for an agent.

        Purpose:
            Surfaces failure contexts so the CLI can display actionable error-handling data.

        Parameters:
            agent_id (str): Agent identifier scoped within the training system.
            limit (int): Number of error records to return. Must be positive.

        Returns:
            Dict[str, Any]: {
                "agent_id": str,
                "entries": List[Dict[str, Any]]
            }

        Raises:
            ValueError: If agent_id is empty or limit <= 0.

        Example:
            >>> MemoryService().get_recent_errors("ClaudeCode", limit=3)

        Complexity:
            Time: O(k) where k == limit
            Space: O(k)

        Side Effects:
            - Executes read operations against the Chroma error collection.

        Design Patterns:
            Repository pattern applied to error records.

        Thread Safety:
            Not thread-safe; expect external synchronization if used concurrently.

        Agent: GPT-5.1 Codex
        Timestamp: 2025-12-03T00:00:00Z
        """
        if limit <= 0:
            raise ValueError("limit must be greater than zero.")

        raw_errors = self.registry.errors.recent_errors(agent_id=agent_id, limit=limit)
        documents: List[str] = raw_errors.get("documents") or []
        metadatas: List[Dict[str, Any]] = raw_errors.get("metadatas") or []

        entries: List[Dict[str, Any]] = []
        for message, metadata in zip(documents, metadatas):
            entries.append(
                {
                    "message": message,
                    "context": metadata.get("context"),
                    "timestamp": metadata.get("timestamp"),
                    "severity": metadata.get("severity", "unknown"),
                    "agent_id": metadata.get("agent_id", agent_id),
                }
            )

        return {"agent_id": agent_id, "entries": entries}

    def add_error(self, error_message: str, context: str, agent_id: str = "system"):
        """Adds an error to the memory."""
        self.registry.errors.add_error(error_message, context, agent_id)

    def add_score(
        self,
        topic: str,
        score: float,
        time_taken: float,
        agent_id: str = "system",
        metrics: Optional[Dict[str, Any]] = None,
    ):
        """Adds a score to the memory with detailed metrics."""
        if metrics is None:
            metrics = {}

        metadata = metrics or {}
        self.registry.scores.add_score(topic, score, time_taken, agent_id, metadata)

    def log_daily_activity(self, agent_id: str, activity_type: str, details: Dict[str, Any]):
        """Logs daily activity for reflection."""
        self.registry.daily_logs.add_log(agent_id, activity_type, details)

    def get_daily_logs(self, agent_id: str, date_str: Optional[str] = None):
        """Retrieves logs for a specific day (or all if None)."""
        # Note: Chroma filtering by date string is basic.
        # For a real app, we'd query by timestamp range.
        # Here we just return recent logs.
        return self.registry.daily_logs.get_recent(agent_id, limit=100)

    def get_collection_metrics(self) -> Dict[str, int]:
        """Return counts for each collection."""
        return self.registry.stats()

    def dedupe_training_materials(self) -> int:
        """Remove duplicate training documents."""
        return self.registry.training_materials.remove_duplicate_documents()
