"""
[CREATE] Skeleton Finder - Discovery and Analysis Tool

Finds and catalogs all skeleton structures in the database/system.
Part of Composer's analysis toolkit.

Agent: Composer
Timestamp: 2025-12-03T19-06-12Z
Operation: [CREATE]
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("composer.skeleton_finder")


@dataclass
class SkeletonMetadata:
    """
    [CREATE] Metadata about a discovered skeleton structure.

    Captures essential information about skeleton location,
    completeness, and structure metrics.

    Attributes:
        agent_id (str): Agent identifier
        timestamp (str): ISO 8601 timestamp
        path (Path): Full path to skeleton
        completeness_score (float): 0.0-1.0 completeness metric
        directory_count (int): Number of subdirectories
        file_count (int): Number of files
        missing_components (List[str]): List of missing standard components
        size_bytes (int): Total size in bytes

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """

    agent_id: str
    timestamp: str
    path: Path
    completeness_score: float = 0.0
    directory_count: int = 0
    file_count: int = 0
    missing_components: List[str] = field(default_factory=list)
    size_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """
        [CREATE] Convert to dictionary for serialization.

        Returns:
            Dict[str, Any]: Dictionary representation

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        return {
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "path": str(self.path),
            "completeness_score": self.completeness_score,
            "directory_count": self.directory_count,
            "file_count": self.file_count,
            "missing_components": self.missing_components,
            "size_bytes": self.size_bytes
        }


class SkeletonFinder:
    """
    [CREATE] Finds and analyzes skeleton structures.

    Scans the CodeAgents/ID directory structure to discover
    all agent skeletons and analyze their completeness.

    Attributes:
        base_path (Path): Base path for CodeAgents directory
        required_components (List[str]): Standard skeleton components

    Example:
        >>> finder = SkeletonFinder()
        >>> skeletons = finder.find_all_skeletons()
        >>> for skeleton in skeletons:
        ...     print(f"{skeleton.agent_id}: {skeleton.completeness_score}")

    Complexity:
        Time: O(n*m) where n is agents, m is files per skeleton
        Space: O(n) for skeleton metadata storage

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """

    def __init__(self, base_path: Optional[Path] = None) -> None:
        """
        [CREATE] Initialize skeleton finder.

        Args:
            base_path (Optional[Path]): Base path for CodeAgents.
                Default: None (auto-detect).

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        if base_path is None:
            current_file = Path(__file__)
            self.base_path = current_file.parent.parent.parent
        else:
            self.base_path = Path(base_path)

        self.agent_base_path = self.base_path / "ID"
        self.structures_base_path = self.base_path.parent / "Structures"

        # Standard skeleton components
        self.required_components = [
            "training",
            "rules",
            "methods",
            "files",
            "database",
            "memory"
        ]

        logger.info(f"Skeleton finder initialized at {self.base_path}")

    def find_all_skeletons(self) -> List[SkeletonMetadata]:
        """
        [CREATE] Find all skeleton structures in the system.

        Scans both CodeAgents/ID and Structures directories
        to discover all agent skeletons.

        Returns:
            List[SkeletonMetadata]: List of discovered skeletons

        Example:
            >>> finder = SkeletonFinder()
            >>> skeletons = finder.find_all_skeletons()
            >>> print(f"Found {len(skeletons)} skeletons")

        Complexity:
            Time: O(n*m) where n is agents, m is directories per agent
            Space: O(n) for results

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        skeletons: List[SkeletonMetadata] = []

        # Scan CodeAgents/ID
        if self.agent_base_path.exists():
            for agent_dir in self.agent_base_path.iterdir():
                if agent_dir.is_dir() and not agent_dir.name.startswith("."):
                    agent_skeletons = self._scan_agent_directory(agent_dir)
                    skeletons.extend(agent_skeletons)

        # Scan Structures
        if self.structures_base_path.exists():
            for structure_dir in self.structures_base_path.iterdir():
                if structure_dir.is_dir() and not structure_dir.name.startswith("."):
                    template_skeletons = self._scan_template_directory(structure_dir)
                    skeletons.extend(template_skeletons)

        logger.info(f"Found {len(skeletons)} skeleton structures")
        return skeletons

    def _scan_agent_directory(self, agent_dir: Path) -> List[SkeletonMetadata]:
        """
        [CREATE] Scan agent directory for timestamped skeletons.

        Args:
            agent_dir (Path): Agent directory path

        Returns:
            List[SkeletonMetadata]: Discovered skeletons

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        skeletons: List[SkeletonMetadata] = []

        for item in agent_dir.iterdir():
            if item.is_dir():
                # Check if it's a timestamped directory (format: YYYY-MM-DDTHH-MM-SSZ)
                if self._is_timestamp_directory(item.name):
                    metadata = self._analyze_skeleton(
                        agent_id=agent_dir.name,
                        timestamp=item.name,
                        skeleton_path=item
                    )
                    skeletons.append(metadata)

        return skeletons

    def _scan_template_directory(self, template_dir: Path) -> List[SkeletonMetadata]:
        """
        [CREATE] Scan template directory for skeletons.

        Args:
            template_dir (Path): Template directory path

        Returns:
            List[SkeletonMetadata]: Discovered template skeletons

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        skeletons: List[SkeletonMetadata] = []

        for item in template_dir.iterdir():
            if item.is_dir() and self._is_timestamp_directory(item.name):
                metadata = self._analyze_skeleton(
                    agent_id=template_dir.name,
                    timestamp=item.name,
                    skeleton_path=item
                )
                skeletons.append(metadata)

        return skeletons

    def _is_timestamp_directory(self, name: str) -> bool:
        """
        [CREATE] Check if directory name matches timestamp format.

        Args:
            name (str): Directory name

        Returns:
            bool: True if matches timestamp format

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        # Format: YYYY-MM-DDTHH-MM-SSZ or YYYY-MM-DDTHHMMSSZ
        if "T" not in name or "Z" not in name:
            return False

        parts = name.split("T")
        if len(parts) != 2:
            return False

        date_part = parts[0]
        time_part = parts[1].rstrip("Z")

        # Check date format (YYYY-MM-DD)
        try:
            year, month, day = date_part.split("-")
            if len(year) == 4 and len(month) == 2 and len(day) == 2:
                return True
        except ValueError:
            return False

        return False

    def _analyze_skeleton(
        self,
        agent_id: str,
        timestamp: str,
        skeleton_path: Path
    ) -> SkeletonMetadata:
        """
        [CREATE] Analyze a skeleton structure for completeness.

        Args:
            agent_id (str): Agent identifier
            timestamp (str): Timestamp string
            skeleton_path (Path): Path to skeleton directory

        Returns:
            SkeletonMetadata: Analyzed skeleton metadata

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        metadata = SkeletonMetadata(
            agent_id=agent_id,
            timestamp=timestamp,
            path=skeleton_path
        )

        # Count directories and files
        dirs_found = set()
        files_found = []
        total_size = 0

        for item in skeleton_path.rglob("*"):
            if item.is_dir():
                # Get relative component name
                rel_path = item.relative_to(skeleton_path)
                if rel_path.parts:
                    component = rel_path.parts[0]
                    dirs_found.add(component)
            elif item.is_file():
                files_found.append(item)
                try:
                    total_size += item.stat().st_size
                except OSError:
                    pass

        metadata.directory_count = len(dirs_found)
        metadata.file_count = len(files_found)
        metadata.size_bytes = total_size

        # Check for missing components
        found_components = dirs_found & set(self.required_components)
        missing = set(self.required_components) - found_components
        metadata.missing_components = sorted(list(missing))

        # Calculate completeness score
        # Base score: percentage of required components present
        component_score = len(found_components) / len(self.required_components)

        # Bonus: if has files (not just empty structure)
        file_bonus = min(0.2, metadata.file_count * 0.01)

        metadata.completeness_score = min(1.0, component_score + file_bonus)

        return metadata

    def export_analysis(self, skeletons: List[SkeletonMetadata], output_path: Path) -> None:
        """
        [CREATE] Export skeleton analysis to JSON file.

        Args:
            skeletons (List[SkeletonMetadata]): Skeleton metadata list
            output_path (Path): Output file path

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        data = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_skeletons": len(skeletons),
            "skeletons": [s.to_dict() for s in skeletons],
            "summary": {
                "avg_completeness": sum(s.completeness_score for s in skeletons) / len(skeletons) if skeletons else 0.0,
                "total_files": sum(s.file_count for s in skeletons),
                "total_size_bytes": sum(s.size_bytes for s in skeletons)
            }
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported analysis to {output_path}")


def create_skeleton_finder(base_path: Optional[Path] = None) -> SkeletonFinder:
    """
    [CREATE] Factory function to create skeleton finder.

    Args:
        base_path (Optional[Path]): Base path for CodeAgents.
            Default: None (auto-detect).

    Returns:
        SkeletonFinder: Configured finder instance

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """
    return SkeletonFinder(base_path)
