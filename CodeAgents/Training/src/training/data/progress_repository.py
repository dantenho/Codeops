"""
Progress persistence repository for agent training data.

Provides JSON-based storage for AgentProgress with atomic writes,
history tracking, and backup capabilities.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from filelock import FileLock

from ..models.progress import AgentProgress


class ProgressRepository:
    """
    Repository for persisting and retrieving agent progress data.

    Uses JSON files with atomic writes to ensure data integrity.
    Maintains progress history for rollback and analysis.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize progress repository.

        Args:
            data_dir: Directory for storing progress files (default: ./progress_data)
        """
        self.data_dir = Path(data_dir or "progress_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories
        self.current_dir = self.data_dir / "current"
        self.history_dir = self.data_dir / "history"
        self.backups_dir = self.data_dir / "backups"

        self.current_dir.mkdir(exist_ok=True)
        self.history_dir.mkdir(exist_ok=True)
        self.backups_dir.mkdir(exist_ok=True)

    def save(
        self,
        progress: AgentProgress,
        create_snapshot: bool = False
    ) -> bool:
        """
        Save agent progress to disk with atomic write.

        Args:
            progress: AgentProgress object to save
            create_snapshot: Whether to create a historical snapshot

        Returns:
            True if save successful, False otherwise
        """
        file_path = self.current_dir / f"{progress.agent_id}.json"
        temp_path = file_path.with_suffix(".tmp")
        lock_path = file_path.with_suffix(".lock")

        try:
            # Use file lock to prevent concurrent writes
            with FileLock(str(lock_path), timeout=10):
                # Write to temporary file
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(
                        progress.model_dump(),
                        f,
                        indent=2,
                        default=str,
                        ensure_ascii=False
                    )

                # Atomic rename (on POSIX) or copy (on Windows)
                if file_path.exists():
                    # Backup existing file
                    backup_path = self.backups_dir / f"{progress.agent_id}_last.json"
                    shutil.copy2(file_path, backup_path)

                # Replace old file with new one
                temp_path.replace(file_path)

                # Create historical snapshot if requested
                if create_snapshot:
                    self._create_snapshot(progress)

                return True

        except Exception as e:
            print(f"Error saving progress for {progress.agent_id}: {e}")
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            return False

        finally:
            # Clean up lock file
            if lock_path.exists():
                try:
                    lock_path.unlink()
                except Exception:
                    pass

    def load(self, agent_id: str) -> Optional[AgentProgress]:
        """
        Load agent progress from disk.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentProgress object or None if not found
        """
        file_path = self.current_dir / f"{agent_id}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AgentProgress(**data)

        except Exception as e:
            print(f"Error loading progress for {agent_id}: {e}")

            # Try loading from backup
            backup_path = self.backups_dir / f"{agent_id}_last.json"
            if backup_path.exists():
                print(f"Attempting to restore from backup...")
                try:
                    with open(backup_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return AgentProgress(**data)
                except Exception as backup_error:
                    print(f"Backup restore failed: {backup_error}")

            return None

    def exists(self, agent_id: str) -> bool:
        """
        Check if progress file exists for agent.

        Args:
            agent_id: Agent identifier

        Returns:
            True if progress file exists
        """
        file_path = self.current_dir / f"{agent_id}.json"
        return file_path.exists()

    def delete(self, agent_id: str) -> bool:
        """
        Delete agent progress (moves to backups first).

        Args:
            agent_id: Agent identifier

        Returns:
            True if deletion successful
        """
        file_path = self.current_dir / f"{agent_id}.json"

        if not file_path.exists():
            return False

        try:
            # Backup before deletion
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backups_dir / f"{agent_id}_deleted_{timestamp}.json"
            shutil.copy2(file_path, backup_path)

            # Delete current file
            file_path.unlink()
            return True

        except Exception as e:
            print(f"Error deleting progress for {agent_id}: {e}")
            return False

    def list_all(self) -> List[str]:
        """
        List all agent IDs with saved progress.

        Returns:
            List of agent IDs
        """
        agent_ids = []

        for file_path in self.current_dir.glob("*.json"):
            agent_ids.append(file_path.stem)

        return sorted(agent_ids)

    def load_all(self) -> Dict[str, AgentProgress]:
        """
        Load progress for all agents.

        Returns:
            Dictionary mapping agent_id to AgentProgress
        """
        progress_dict = {}

        for agent_id in self.list_all():
            progress = self.load(agent_id)
            if progress:
                progress_dict[agent_id] = progress

        return progress_dict

    def get_history(
        self,
        agent_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get historical snapshots for an agent.

        Args:
            agent_id: Agent identifier
            limit: Maximum number of snapshots to return (most recent first)

        Returns:
            List of snapshot dictionaries with metadata
        """
        history = []
        agent_history_dir = self.history_dir / agent_id

        if not agent_history_dir.exists():
            return history

        # Collect all snapshot files
        snapshot_files = sorted(
            agent_history_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if limit:
            snapshot_files = snapshot_files[:limit]

        for snapshot_file in snapshot_files:
            try:
                with open(snapshot_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    history.append({
                        "timestamp": snapshot_file.stem,
                        "file_path": str(snapshot_file),
                        "data": data,
                    })
            except Exception as e:
                print(f"Error loading snapshot {snapshot_file}: {e}")

        return history

    def restore_from_snapshot(
        self,
        agent_id: str,
        timestamp: str
    ) -> Optional[AgentProgress]:
        """
        Restore agent progress from a historical snapshot.

        Args:
            agent_id: Agent identifier
            timestamp: Snapshot timestamp to restore from

        Returns:
            Restored AgentProgress or None if failed
        """
        snapshot_path = self.history_dir / agent_id / f"{timestamp}.json"

        if not snapshot_path.exists():
            print(f"Snapshot not found: {snapshot_path}")
            return None

        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                progress = AgentProgress(**data)

                # Save as current
                self.save(progress, create_snapshot=False)

                return progress

        except Exception as e:
            print(f"Error restoring snapshot for {agent_id}: {e}")
            return None

    def _create_snapshot(self, progress: AgentProgress):
        """
        Create a historical snapshot of agent progress.

        Args:
            progress: AgentProgress to snapshot
        """
        agent_history_dir = self.history_dir / progress.agent_id
        agent_history_dir.mkdir(exist_ok=True)

        # Use timestamp as filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        snapshot_path = agent_history_dir / f"{timestamp}.json"

        try:
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(
                    progress.model_dump(),
                    f,
                    indent=2,
                    default=str,
                    ensure_ascii=False
                )

            # Clean up old snapshots (keep last 50)
            self._cleanup_old_snapshots(agent_history_dir, keep=50)

        except Exception as e:
            print(f"Error creating snapshot for {progress.agent_id}: {e}")

    def _cleanup_old_snapshots(self, directory: Path, keep: int = 50):
        """
        Remove old snapshots, keeping only the most recent N.

        Args:
            directory: Directory containing snapshots
            keep: Number of recent snapshots to retain
        """
        snapshot_files = sorted(
            directory.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Delete old snapshots beyond the keep limit
        for old_snapshot in snapshot_files[keep:]:
            try:
                old_snapshot.unlink()
            except Exception as e:
                print(f"Error deleting old snapshot {old_snapshot}: {e}")

    def get_stats(self) -> Dict:
        """
        Get repository statistics.

        Returns:
            Dictionary with repository stats
        """
        stats = {
            "total_agents": len(self.list_all()),
            "total_history_snapshots": 0,
            "total_backups": 0,
            "disk_usage_mb": 0,
        }

        # Count history snapshots
        if self.history_dir.exists():
            stats["total_history_snapshots"] = len(list(self.history_dir.rglob("*.json")))

        # Count backups
        if self.backups_dir.exists():
            stats["total_backups"] = len(list(self.backups_dir.glob("*.json")))

        # Calculate disk usage
        total_size = 0
        for file_path in self.data_dir.rglob("*.json"):
            total_size += file_path.stat().st_size
        stats["disk_usage_mb"] = round(total_size / (1024 * 1024), 2)

        return stats


# Singleton instance
_repository_instance: Optional[ProgressRepository] = None


def get_progress_repository(data_dir: Optional[Path] = None) -> ProgressRepository:
    """
    Get the singleton ProgressRepository instance.

    Args:
        data_dir: Directory for storing progress files

    Returns:
        ProgressRepository instance
    """
    global _repository_instance

    if _repository_instance is None:
        _repository_instance = ProgressRepository(data_dir)

    return _repository_instance
