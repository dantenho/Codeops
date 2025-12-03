"""
[CREATE] Training System Bootstrap & Orchestrator

Initializes and orchestrates the training system for all agents.
Provides a unified entry point for system initialization and health checks.

Agent: Composer
Timestamp: 2025-12-03T14:30:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from .models.progress import AgentProgress
from .models.session import SessionType
from .services.training_manager import TrainingManager
from .services.memory_service import MemoryService
from .services.token_tracker import TokenTracker
from .services.reflex_service import ReflexService
from .services.config_service import ConfigService

# Import skeleton generator (handle import path)
import sys
from pathlib import Path
_core_path = Path(__file__).parent.parent.parent.parent / "core"
if _core_path.exists():
    sys.path.insert(0, str(_core_path.parent))
    from core.skeleton_generator import SkeletonGenerator, create_skeleton_generator
else:
    # Fallback: try relative import
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "skeleton_generator",
            Path(__file__).parent.parent.parent.parent / "core" / "skeleton_generator.py"
        )
        if spec and spec.loader:
            skeleton_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(skeleton_module)
            SkeletonGenerator = skeleton_module.SkeletonGenerator
            create_skeleton_generator = skeleton_module.create_skeleton_generator
        else:
            SkeletonGenerator = None
            create_skeleton_generator = None
    except Exception:
        SkeletonGenerator = None
        create_skeleton_generator = None


class TrainingSystemBootstrap:
    """
    [CREATE] Bootstrap and orchestration service for the training system.

    Provides system initialization, health checks, and multi-agent
    orchestration capabilities.

    Attributes:
        base_path (Path): Base path for training system
        training_manager (TrainingManager): Core training manager
        memory_service (MemoryService): Memory/ChromaDB service
        token_tracker (TokenTracker): Token usage tracker
        reflex_service (ReflexService): Reflection service
        config_service (ConfigService): Configuration service
        logger (logging.Logger): System logger

    Example:
        >>> bootstrap = TrainingSystemBootstrap(Path("CodeAgents/Training"))
        >>> bootstrap.initialize_system()
        >>> health = bootstrap.check_system_health()
        >>> if health["status"] == "healthy":
        ...     bootstrap.initialize_all_agents()

    Complexity:
        Time: O(n) where n is number of agents
        Space: O(1) constant memory usage

    Agent: Composer
    Timestamp: 2025-12-03T14:30:00Z
    """

    def __init__(self, base_path: Path, project_root: Optional[Path] = None):
        """
        [CREATE] Initialize the training system bootstrap.

        Args:
            base_path (Path): Base path for training system.
                Must exist and be readable.
            project_root (Optional[Path]): Project root directory.
                Default: None (auto-detect from base_path).

        Raises:
            FileNotFoundError: If base_path doesn't exist
            PermissionError: If base_path is not readable

        Agent: Composer
        Timestamp: 2025-12-03T14:30:00Z
        """
        if not base_path.exists():
            raise FileNotFoundError(f"Training system path not found: {base_path}")

        self.base_path = base_path
        self.project_root = project_root or base_path.parent.parent

        # Initialize logging
        self.logger = logging.getLogger("training.bootstrap")
        self.logger.setLevel(logging.INFO)

        # Initialize services
        self.config_service = ConfigService(base_path / "config")
        self.training_manager = TrainingManager(base_path)
        self.memory_service = MemoryService()
        self.token_tracker = TokenTracker(self.project_root / "token_metrics")
        self.reflex_service = ReflexService(base_path)

        # Initialize skeleton generator if available
        try:
            if create_skeleton_generator is not None:
                skeleton_base = self.project_root / "CodeAgents"
                self.skeleton_generator = create_skeleton_generator(skeleton_base)
                self.logger.info("Skeleton generator initialized")
            else:
                self.skeleton_generator = None
                self.logger.warning("Skeleton generator not available")
        except Exception as e:
            self.skeleton_generator = None
            self.logger.warning(f"Skeleton generator not available: {e}")

        self.logger.info(f"Training system bootstrap initialized at {base_path}")

    def initialize_system(self) -> Dict[str, Any]:
        """
        [CREATE] Initialize the entire training system.

        Performs system-wide initialization including:
        - Configuration validation
        - Directory structure creation
        - Service health checks
        - Database connection verification

        Returns:
            Dict[str, Any]: Initialization results with status and details.

        Raises:
            RuntimeError: If critical initialization fails

        Example:
            >>> result = bootstrap.initialize_system()
            >>> print(result["status"])
            initialized

        Complexity:
            Time: O(1) - initialization operations
            Space: O(1)

        Agent: Composer
        Timestamp: 2025-12-03T14:30:00Z
        """
        results = {
            "status": "initializing",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {},
            "errors": []
        }

        try:
            # Check configuration
            try:
                agent_profiles = self.config_service.get_agent_profile("Composer")
                results["checks"]["config"] = "valid"
            except Exception as e:
                results["checks"]["config"] = f"error: {e}"
                results["errors"].append(f"Config check failed: {e}")

            # Check directory structure
            required_dirs = [
                self.base_path / "data",
                self.base_path / "data" / "progress",
                self.base_path / "data" / "reflections",
                self.base_path / "Flashcards" / "decks",
            ]

            for dir_path in required_dirs:
                dir_path.mkdir(parents=True, exist_ok=True)
            results["checks"]["directories"] = "created"

            # Check memory service
            try:
                metrics = self.memory_service.get_collection_metrics()
                results["checks"]["memory_service"] = f"connected ({sum(metrics.values())} documents)"
            except Exception as e:
                results["checks"]["memory_service"] = f"error: {e}"
                results["errors"].append(f"Memory service check failed: {e}")

            # Check token tracker
            try:
                stats = self.token_tracker.get_agent_stats("Composer", days=1)
                results["checks"]["token_tracker"] = "operational"
            except Exception as e:
                results["checks"]["token_tracker"] = f"error: {e}"
                results["errors"].append(f"Token tracker check failed: {e}")

            if results["errors"]:
                results["status"] = "partial"
            else:
                results["status"] = "initialized"

            self.logger.info(f"System initialization complete: {results['status']}")

        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(f"Initialization failed: {e}")
            self.logger.error(f"System initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize training system: {e}") from e

        return results

    def create_agent_skeleton(
        self,
        agent_id: str,
        timestamp: Optional[str] = None
    ) -> Optional[Path]:
        """
        [CREATE] Create skeleton structure for an agent.

        Args:
            agent_id (str): Agent identifier.
            timestamp (Optional[str]): ISO 8601 timestamp string.
                Default: None (auto-generate).

        Returns:
            Optional[Path]: Path to created structure, or None if generator unavailable.

        Agent: Composer
        Timestamp: 2025-12-03T15:00:00Z
        """
        if self.skeleton_generator is None:
            self.logger.warning("Skeleton generator not available")
            return None

        try:
            path = self.skeleton_generator.create_agent_skeleton(agent_id, timestamp)
            self.logger.info(f"Created skeleton structure for {agent_id} at {path}")
            return path
        except Exception as e:
            self.logger.error(f"Failed to create skeleton for {agent_id}: {e}")
            return None

    def initialize_all_agents(
        self,
        agent_ids: Optional[List[str]] = None,
        create_skeletons: bool = True
    ) -> Dict[str, Any]:
        """
        [CREATE] Initialize training profiles for all agents.

        Creates or updates agent progress records for all configured agents.
        Optionally creates skeleton structures.

        Args:
            agent_ids (Optional[List[str]]): Specific agents to initialize.
                Default: None (initialize all configured agents).
            create_skeletons (bool): Whether to create skeleton structures.
                Default: True.

        Returns:
            Dict[str, Any]: Initialization results per agent.

        Example:
            >>> results = bootstrap.initialize_all_agents()
            >>> for agent, status in results["agents"].items():
            ...     print(f"{agent}: {status}")

        Complexity:
            Time: O(n) where n is number of agents
            Space: O(n)

        Agent: Composer
        Timestamp: 2025-12-03T15:00:00Z
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents": {},
            "errors": []
        }

        # Get agent list from config if not provided
        if agent_ids is None:
            agent_ids = self._get_configured_agents()

        for agent_id in agent_ids:
            try:
                # Create skeleton structure if requested
                skeleton_path = None
                if create_skeletons:
                    skeleton_path = self.create_agent_skeleton(agent_id)

                # Initialize agent progress
                progress = self.training_manager.initialize_agent(agent_id)
                results["agents"][agent_id] = {
                    "status": "initialized",
                    "level": progress.current_level,
                    "xp": progress.xp.total,
                    "skeleton_created": skeleton_path is not None,
                    "skeleton_path": str(skeleton_path) if skeleton_path else None
                }
                self.logger.info(f"Initialized agent: {agent_id} (level {progress.current_level})")
            except Exception as e:
                results["agents"][agent_id] = {
                    "status": "failed",
                    "error": str(e)
                }
                results["errors"].append(f"{agent_id}: {e}")
                self.logger.error(f"Failed to initialize agent {agent_id}: {e}")

        return results

    def check_system_health(self) -> Dict[str, Any]:
        """
        [CREATE] Perform comprehensive system health check.

        Checks all services, storage, and configurations for issues.

        Returns:
            Dict[str, Any]: Health status with detailed checks.

        Example:
            >>> health = bootstrap.check_system_health()
            >>> if health["status"] == "healthy":
            ...     print("All systems operational")

        Complexity:
            Time: O(1) - health checks are quick
            Space: O(1)

        Agent: Composer
        Timestamp: 2025-12-03T14:30:00Z
        """
        health = {
            "status": "checking",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {},
            "warnings": [],
            "errors": []
        }

        # Check services
        try:
            metrics = self.memory_service.get_collection_metrics()
            health["checks"]["memory_service"] = {
                "status": "healthy",
                "collections": metrics
            }
        except Exception as e:
            health["checks"]["memory_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health["errors"].append(f"Memory service: {e}")

        # Check token tracker
        try:
            stats = self.token_tracker.get_agent_stats("Composer", days=1)
            health["checks"]["token_tracker"] = {
                "status": "healthy",
                "sessions": stats.total_sessions
            }
        except Exception as e:
            health["checks"]["token_tracker"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health["errors"].append(f"Token tracker: {e}")

        # Check training manager
        try:
            progress = self.training_manager.get_progress("Composer")
            health["checks"]["training_manager"] = {
                "status": "healthy",
                "has_progress": progress is not None
            }
        except Exception as e:
            health["checks"]["training_manager"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health["errors"].append(f"Training manager: {e}")

        # Determine overall status
        if health["errors"]:
            health["status"] = "unhealthy"
        elif health["warnings"]:
            health["status"] = "degraded"
        else:
            health["status"] = "healthy"

        return health

    def get_system_statistics(self) -> Dict[str, Any]:
        """
        [CREATE] Get comprehensive system statistics.

        Aggregates statistics from all services and agents.

        Returns:
            Dict[str, Any]: System-wide statistics.

        Example:
            >>> stats = bootstrap.get_system_statistics()
            >>> print(f"Total agents: {stats['agents']['total']}")

        Complexity:
            Time: O(n) where n is number of agents
            Space: O(n)

        Agent: Composer
        Timestamp: 2025-12-03T14:30:00Z
        """
        stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents": {},
            "memory": {},
            "tokens": {},
            "sessions": {}
        }

        # Agent statistics
        agent_ids = self._get_configured_agents()
        agent_stats = {}
        total_xp = 0
        total_sessions = 0

        for agent_id in agent_ids:
            try:
                progress = self.training_manager.get_progress(agent_id)
                if progress:
                    agent_stats[agent_id] = {
                        "level": progress.current_level,
                        "xp": progress.xp.total,
                        "streak": progress.daily_streak.current,
                        "sessions": progress.completions.sessions_completed
                    }
                    total_xp += progress.xp.total
                    total_sessions += progress.completions.sessions_completed
            except Exception:
                pass

        stats["agents"] = {
            "total": len(agent_ids),
            "initialized": len(agent_stats),
            "total_xp": total_xp,
            "total_sessions": total_sessions,
            "by_agent": agent_stats
        }

        # Memory statistics
        try:
            memory_metrics = self.memory_service.get_collection_metrics()
            stats["memory"] = memory_metrics
        except Exception:
            stats["memory"] = {"error": "unavailable"}

        # Token statistics (aggregate across agents)
        token_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "by_agent": {}
        }

        for agent_id in agent_ids:
            try:
                agent_token_stats = self.token_tracker.get_agent_stats(agent_id, days=30)
                token_stats["total_tokens"] += agent_token_stats.lifetime_tokens
                token_stats["total_cost"] += agent_token_stats.lifetime_cost_usd
                token_stats["by_agent"][agent_id] = {
                    "tokens": agent_token_stats.lifetime_tokens,
                    "cost": agent_token_stats.lifetime_cost_usd,
                    "sessions": agent_token_stats.total_sessions
                }
            except Exception:
                pass

        stats["tokens"] = token_stats

        return stats

    def _get_configured_agents(self) -> List[str]:
        """
        [CREATE] Get list of configured agent IDs from config.

        Returns:
            List[str]: Agent IDs from configuration.

        Complexity:
            Time: O(1)
            Space: O(n) where n is number of agents

        Agent: Composer
        Timestamp: 2025-12-03T14:30:00Z
        """
        # Default agent list from Agents.MD
        default_agents = [
            "GrokIA",
            "GeminiFlash25",
            "GeminiPro25",
            "GeminiPro30",
            "Jules",
            "ClaudeCode",
            "Composer"
        ]

        try:
            # Try to load from config
            config = self.config_service.load_config("agent_profiles.yaml")
            if config and "agents" in config:
                return list(config["agents"].keys())
        except Exception:
            pass

        return default_agents


def create_bootstrap(base_path: Optional[Path] = None) -> TrainingSystemBootstrap:
    """
    [CREATE] Factory function to create a configured bootstrap instance.

    Args:
        base_path (Optional[Path]): Base path for training system.
            Default: None (auto-detect).

    Returns:
        TrainingSystemBootstrap: Configured bootstrap instance.

    Example:
        >>> bootstrap = create_bootstrap()
        >>> bootstrap.initialize_system()

    Agent: Composer
    Timestamp: 2025-12-03T14:30:00Z
    """
    if base_path is None:
        # Auto-detect from current file location
        current_file = Path(__file__)
        base_path = current_file.parent.parent.parent

    return TrainingSystemBootstrap(base_path)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    bootstrap = create_bootstrap()
    init_result = bootstrap.initialize_system()
    print(f"System Status: {init_result['status']}")

    health = bootstrap.check_system_health()
    print(f"Health Status: {health['status']}")

    stats = bootstrap.get_system_statistics()
    print(f"Total Agents: {stats['agents']['total']}")
