"""
[CREATE] Skeleton Finder - Discovery and Analysis System

Comprehensive system for locating, cataloging, and analyzing all skeleton
structures in the codebase. Implements systematic search across multiple
storage locations and databases.

Agent: Composer
Timestamp: 2025-12-03T19:10:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import json
import logging
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("composer.skeleton_finder")


class SkeletonFinder:
    """
    [CREATE] Finds and catalogs all skeleton structures in the system.

    Searches across multiple locations:
    - CodeAgents/ID/{AgentID}/{Timestamp}/
    - Structures/{AgentID}/{Timestamp}/
    - ChromaDB vector database
    - Structure report JSON files

    Attributes:
        base_path (Path): Base path for CodeAgents directory
        structures_path (Path): Path to Structures directory
        chroma_db_path (Path): Path to ChromaDB database
        found_skeletons (Dict[str, List[Dict[str, Any]]]): Catalog of found skeletons

    Example:
        >>> finder = SkeletonFinder()
        >>> skeletons = finder.find_all_skeletons()
        >>> finder.analyze_skeleton_structure("Composer", "2025-12-03T18-49-33Z")

    Complexity:
        Time: O(n * m) where n is agents, m is timestamps per agent
        Space: O(n * m) for skeleton catalog

    Agent: Composer
    Timestamp: 2025-12-03T19:10:00Z
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        [CREATE] Initialize skeleton finder.

        Args:
            base_path (Optional[Path]): Base path for CodeAgents directory.
                Default: None (auto-detect).

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        if base_path is None:
            current_file = Path(__file__)
            self.base_path = current_file.parent.parent.parent.parent
        else:
            self.base_path = Path(base_path)

        self.agent_base_path = self.base_path / "ID"
        self.structures_path = self.base_path.parent / "Structures"
        self.chroma_db_path = self.base_path / "Training" / "chroma_db" / "chroma.sqlite3"
        self.structure_report_path = self.base_path / "Training" / "structure_report.json"

        self.found_skeletons: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        logger.info(f"Skeleton finder initialized at {self.base_path}")

    def find_all_skeletons(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        [CREATE] Find all skeleton structures in the system.

        Searches all known locations and catalogs findings.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Catalog of skeletons by agent ID.
                Each skeleton entry contains: agent_id, timestamp, path, components, metadata

        Example:
            >>> finder = SkeletonFinder()
            >>> catalog = finder.find_all_skeletons()
            >>> print(f"Found {len(catalog)} agents with skeletons")

        Algorithm:
            1. Scan CodeAgents/ID/ for agent directories
            2. Scan Structures/ for template skeletons
            3. Query ChromaDB for skeleton-related data
            4. Parse structure_report.json
            5. Merge and deduplicate findings

        Complexity:
            Time: O(n * m * k) where n=agents, m=timestamps, k=components
            Space: O(n * m)

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        logger.info("Starting comprehensive skeleton search...")

        # Search CodeAgents/ID/
        self._scan_agent_directories()

        # Search Structures/
        self._scan_structures_directory()

        # Query ChromaDB
        self._query_chromadb()

        # Parse structure report
        self._parse_structure_report()

        logger.info(f"Found skeletons for {len(self.found_skeletons)} agents")
        return dict(self.found_skeletons)

    def _scan_agent_directories(self) -> None:
        """
        [CREATE] Scan CodeAgents/ID/ for skeleton structures.

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        if not self.agent_base_path.exists():
            logger.warning(f"Agent base path does not exist: {self.agent_base_path}")
            return

        for agent_dir in self.agent_base_path.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith("."):
                continue

            agent_id = agent_dir.name
            logger.debug(f"Scanning agent directory: {agent_id}")

            # Look for timestamped directories
            for timestamp_dir in agent_dir.iterdir():
                if not timestamp_dir.is_dir():
                    continue

                timestamp = timestamp_dir.name
                skeleton_info = self._analyze_skeleton_structure(agent_id, timestamp, timestamp_dir)
                if skeleton_info:
                    self.found_skeletons[agent_id].append(skeleton_info)

    def _scan_structures_directory(self) -> None:
        """
        [CREATE] Scan Structures/ directory for template skeletons.

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        if not self.structures_path.exists():
            logger.warning(f"Structures path does not exist: {self.structures_path}")
            return

        for agent_dir in self.structures_path.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith("."):
                continue

            agent_id = agent_dir.name
            logger.debug(f"Scanning structures directory: {agent_id}")

            for timestamp_dir in agent_dir.iterdir():
                if not timestamp_dir.is_dir():
                    continue

                timestamp = timestamp_dir.name
                skeleton_info = self._analyze_skeleton_structure(
                    agent_id, timestamp, timestamp_dir, is_template=True
                )
                if skeleton_info:
                    self.found_skeletons[agent_id].append(skeleton_info)

    def _analyze_skeleton_structure(
        self,
        agent_id: str,
        timestamp: str,
        skeleton_path: Path,
        is_template: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        [CREATE] Analyze a skeleton structure and extract metadata.

        Args:
            agent_id (str): Agent identifier.
            timestamp (str): Timestamp string.
            skeleton_path (Path): Path to skeleton directory.
            is_template (bool): Whether this is a template skeleton.
                Default: False.

        Returns:
            Optional[Dict[str, Any]]: Skeleton information dict, or None if invalid.

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        if not skeleton_path.exists() or not skeleton_path.is_dir():
            return None

        components = {
            "training": self._check_component(skeleton_path / "training"),
            "rules": self._check_component(skeleton_path / "rules"),
            "methods": self._check_component(skeleton_path / "methods"),
            "files": self._check_component(skeleton_path / "files"),
            "database": self._check_component(skeleton_path / "database"),
            "memory": self._check_component(skeleton_path / "memory"),
        }

        # Count files in each component
        file_counts = {
            comp: self._count_files(skeleton_path / comp) if exists else 0
            for comp, exists in components.items()
        }

        # Check for key files
        key_files = {
            "progress_json": (skeleton_path / "training" / "progress.json").exists(),
            "protocols_md": (skeleton_path / "rules" / "protocols.md").exists(),
            "schema_sql": (skeleton_path / "database" / "schema.sql").exists(),
        }

        return {
            "agent_id": agent_id,
            "timestamp": timestamp,
            "path": str(skeleton_path),
            "is_template": is_template,
            "components": components,
            "file_counts": file_counts,
            "key_files": key_files,
            "total_files": sum(file_counts.values()),
            "discovered_at": datetime.now(timezone.utc).isoformat(),
        }

    def _check_component(self, path: Path) -> bool:
        """
        [CREATE] Check if a component directory exists.

        Args:
            path (Path): Path to check.

        Returns:
            bool: True if directory exists.

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        return path.exists() and path.is_dir()

    def _count_files(self, path: Path) -> int:
        """
        [CREATE] Count files recursively in a directory.

        Args:
            path (Path): Directory path.

        Returns:
            int: Number of files found.

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        if not path.exists():
            return 0

        count = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    count += 1
        except PermissionError:
            logger.warning(f"Permission denied accessing {path}")
        return count

    def _query_chromadb(self) -> None:
        """
        [CREATE] Query ChromaDB for skeleton-related data.

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        if not self.chroma_db_path.exists():
            logger.warning(f"ChromaDB not found at {self.chroma_db_path}")
            return

        try:
            conn = sqlite3.connect(self.chroma_db_path)
            cursor = conn.cursor()

            # Query for collections (ChromaDB stores collections in SQLite)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            logger.debug(f"Found {len(tables)} tables in ChromaDB")

            # Look for skeleton-related collections
            for table in tables:
                table_name = table[0]
                if "skeleton" in table_name.lower() or "agent" in table_name.lower():
                    logger.info(f"Found skeleton-related table: {table_name}")

            conn.close()
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")

    def _parse_structure_report(self) -> None:
        """
        [CREATE] Parse structure_report.json for skeleton metadata.

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        if not self.structure_report_path.exists():
            logger.warning(f"Structure report not found: {self.structure_report_path}")
            return

        try:
            with open(self.structure_report_path, "r", encoding="utf-8") as f:
                report = json.load(f)

            # Extract agent information
            if "configs" in report and "agent_profiles" in report["configs"]:
                agents = report["configs"]["agent_profiles"].get("agents", {})
                for agent_id, agent_data in agents.items():
                    if agent_id not in self.found_skeletons:
                        # Agent exists in report but no skeleton found yet
                        logger.debug(f"Agent {agent_id} in report but no skeleton directory found")

        except Exception as e:
            logger.error(f"Error parsing structure report: {e}")

    def generate_finder_report(self) -> Dict[str, Any]:
        """
        [CREATE] Generate comprehensive finder report.

        Returns:
            Dict[str, Any]: Complete finder analysis report.

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        skeletons = self.find_all_skeletons()

        report = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "finder": "Composer",
                "total_agents": len(skeletons),
                "total_skeletons": sum(len(skeletons) for skeletons in skeletons.values()),
            },
            "skeletons_by_agent": skeletons,
            "statistics": self._calculate_statistics(skeletons),
            "findings": self._generate_findings(skeletons),
        }

        return report

    def _calculate_statistics(self, skeletons: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        [CREATE] Calculate statistics about found skeletons.

        Args:
            skeletons (Dict[str, List[Dict[str, Any]]]): Skeleton catalog.

        Returns:
            Dict[str, Any]: Statistics dictionary.

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        total_skeletons = sum(len(skeletons) for skeletons in skeletons.values())
        total_files = sum(
            skeleton.get("total_files", 0)
            for skeletons in skeletons.values()
            for skeleton in skeletons
        )

        component_completeness = defaultdict(int)
        for skeletons in skeletons.values():
            for skeleton in skeletons:
                components = skeleton.get("components", {})
                for comp, exists in components.items():
                    if exists:
                        component_completeness[comp] += 1

        return {
            "total_skeletons": total_skeletons,
            "total_files": total_files,
            "average_files_per_skeleton": total_files / total_skeletons if total_skeletons > 0 else 0,
            "component_completeness": dict(component_completeness),
            "agents_with_skeletons": len(skeletons),
        }

    def _generate_findings(self, skeletons: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """
        [CREATE] Generate findings and observations.

        Args:
            skeletons (Dict[str, List[Dict[str, Any]]]): Skeleton catalog.

        Returns:
            List[str]: List of findings.

        Agent: Composer
        Timestamp: 2025-12-03T19:10:00Z
        """
        findings = []

        if not skeletons:
            findings.append("No skeletons found in the system")
            return findings

        findings.append(f"Found {len(skeletons)} agents with skeleton structures")

        # Find agents with most skeletons
        agent_counts = {agent: len(skeletons) for agent, skeletons in skeletons.items()}
        if agent_counts:
            max_agent = max(agent_counts.items(), key=lambda x: x[1])
            findings.append(f"Agent '{max_agent[0]}' has the most skeletons: {max_agent[1]}")

        # Check for incomplete skeletons
        incomplete_count = 0
        for skeletons in skeletons.values():
            for skeleton in skeletons:
                components = skeleton.get("components", {})
                if not all(components.values()):
                    incomplete_count += 1

        if incomplete_count > 0:
            findings.append(f"Found {incomplete_count} incomplete skeletons")

        return findings


def create_skeleton_finder(base_path: Optional[Path] = None) -> SkeletonFinder:
    """
    [CREATE] Factory function to create skeleton finder instance.

    Args:
        base_path (Optional[Path]): Base path for CodeAgents directory.
            Default: None (auto-detect).

    Returns:
        SkeletonFinder: Configured finder instance.

    Example:
        >>> finder = create_skeleton_finder()
        >>> report = finder.generate_finder_report()

    Agent: Composer
    Timestamp: 2025-12-03T19:10:00Z
    """
    return SkeletonFinder(base_path)
