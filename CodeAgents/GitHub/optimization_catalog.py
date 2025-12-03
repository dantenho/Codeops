"""
Optimization Catalog - Centralized optimization pattern repository.

Manages a catalog of optimization patterns with learning integration.
Tracks effectiveness and creates training materials automatically.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

from .optimization_detector import DetectedOptimization, OptimizationCategory, OptimizationImpact


class CatalogEntry(BaseModel):
    """Entry in the optimization catalog."""
    entry_id: str
    optimization: DetectedOptimization
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    times_applied: int = 0
    times_successful: int = 0
    quality_improvements: List[float] = Field(default_factory=list)
    training_material_path: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class OptimizationCatalog:
    """
    Centralized catalog of optimization patterns.

    Integrates with memory service to create training materials
    and tracks pattern effectiveness over time.
    """

    def __init__(
        self,
        catalog_path: Path,
        memory_service=None,
    ):
        """
        Initialize optimization catalog.

        Args:
            catalog_path: Path to catalog storage
            memory_service: Optional memory service for training materials
        """
        self.catalog_path = catalog_path
        self.memory_service = memory_service

        # Ensure catalog directory exists
        self.catalog_path.mkdir(parents=True, exist_ok=True)

        # Catalog entries
        self.entries: Dict[str, CatalogEntry] = {}

        # Load existing catalog
        self._load_catalog()

    def add_optimization(
        self,
        optimization: DetectedOptimization,
        tags: Optional[List[str]] = None,
        create_training_material: bool = True,
    ) -> CatalogEntry:
        """
        Add optimization to catalog.

        Args:
            optimization: Optimization to add
            tags: Optional tags for categorization
            create_training_material: Whether to create training material

        Returns:
            Created catalog entry
        """
        entry_id = optimization.optimization_id

        # Check if already exists
        if entry_id in self.entries:
            # Update existing entry
            entry = self.entries[entry_id]
            entry.optimization = optimization
            entry.updated_at = datetime.now(timezone.utc)

            if tags:
                entry.tags = list(set(entry.tags + tags))
        else:
            # Create new entry
            entry = CatalogEntry(
                entry_id=entry_id,
                optimization=optimization,
                tags=tags or [],
            )

            self.entries[entry_id] = entry

        # Create training material if requested
        if create_training_material and self.memory_service:
            self._create_training_material(entry)

        # Save catalog
        self._save_catalog()

        return entry

    def record_application(
        self,
        entry_id: str,
        success: bool,
        quality_improvement: Optional[float] = None,
    ):
        """
        Record an application of an optimization.

        Args:
            entry_id: Catalog entry ID
            success: Whether application was successful
            quality_improvement: Quality score improvement (if any)
        """
        if entry_id not in self.entries:
            return

        entry = self.entries[entry_id]
        entry.times_applied += 1

        if success:
            entry.times_successful += 1

        if quality_improvement is not None:
            entry.quality_improvements.append(quality_improvement)

        # Update optimization stats
        entry.optimization.occurrence_count += 1
        entry.optimization.success_rate = (
            entry.times_successful / entry.times_applied
            if entry.times_applied > 0 else 0.0
        )

        if entry.quality_improvements:
            entry.optimization.avg_improvement = (
                sum(entry.quality_improvements) / len(entry.quality_improvements)
            )

        entry.updated_at = datetime.now(timezone.utc)

        # Save catalog
        self._save_catalog()

    def search(
        self,
        query: str,
        category: Optional[OptimizationCategory] = None,
        impact: Optional[OptimizationImpact] = None,
        tags: Optional[List[str]] = None,
        min_success_rate: float = 0.0,
    ) -> List[CatalogEntry]:
        """
        Search catalog for optimizations.

        Args:
            query: Search query
            category: Filter by category
            impact: Filter by impact
            tags: Filter by tags
            min_success_rate: Minimum success rate

        Returns:
            List of matching catalog entries
        """
        results = []
        query_lower = query.lower()

        for entry in self.entries.values():
            opt = entry.optimization

            # Filter by category
            if category and opt.category != category:
                continue

            # Filter by impact
            if impact and opt.impact != impact:
                continue

            # Filter by tags
            if tags and not any(tag in entry.tags for tag in tags):
                continue

            # Filter by success rate
            if opt.success_rate < min_success_rate:
                continue

            # Match query
            if (query_lower in opt.title.lower() or
                query_lower in opt.description.lower() or
                query_lower in opt.pattern_before.lower() or
                query_lower in opt.pattern_after.lower()):
                results.append(entry)

        # Sort by relevance (success rate * occurrence count)
        results.sort(
            key=lambda e: e.optimization.success_rate * e.optimization.occurrence_count,
            reverse=True
        )

        return results

    def get_recommendations(
        self,
        code: str,
        language: str = "python",
        limit: int = 5,
    ) -> List[CatalogEntry]:
        """
        Get optimization recommendations for code.

        Args:
            code: Code to analyze
            language: Programming language
            limit: Maximum recommendations

        Returns:
            List of recommended optimizations
        """
        import re

        recommendations = []
        code_lower = code.lower()

        for entry in self.entries.values():
            opt = entry.optimization

            # Match language
            if opt.language != language:
                continue

            # Try to match pattern_before in code
            try:
                if re.search(opt.pattern_before, code, re.IGNORECASE | re.DOTALL):
                    recommendations.append(entry)
            except re.error:
                # Pattern might not be a valid regex, try simple substring match
                if opt.pattern_before.lower() in code_lower:
                    recommendations.append(entry)

        # Sort by effectiveness
        recommendations.sort(
            key=lambda e: (
                e.optimization.impact.value,  # Higher impact first
                e.optimization.success_rate,  # Higher success rate
                -e.optimization.occurrence_count  # More common patterns
            ),
            reverse=True
        )

        return recommendations[:limit]

    def get_top_patterns(
        self,
        limit: int = 10,
        by: str = "success_rate",
    ) -> List[CatalogEntry]:
        """
        Get top optimization patterns.

        Args:
            limit: Maximum number to return
            by: Sort criterion ("success_rate", "occurrence", "improvement")

        Returns:
            List of top patterns
        """
        entries = list(self.entries.values())

        if by == "success_rate":
            entries.sort(
                key=lambda e: e.optimization.success_rate,
                reverse=True
            )
        elif by == "occurrence":
            entries.sort(
                key=lambda e: e.optimization.occurrence_count,
                reverse=True
            )
        elif by == "improvement":
            entries.sort(
                key=lambda e: e.optimization.avg_improvement,
                reverse=True
            )

        return entries[:limit]

    def export_to_yaml(self, output_path: Path):
        """
        Export catalog to YAML file.

        Args:
            output_path: Output file path
        """
        export_data = {
            "version": "1.0.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_patterns": len(self.entries),
            "patterns": []
        }

        for entry in self.entries.values():
            opt = entry.optimization

            pattern_data = {
                "id": entry.entry_id,
                "title": opt.title,
                "category": opt.category.value,
                "impact": opt.impact.value,
                "language": opt.language,
                "description": opt.description,
                "pattern_before": opt.pattern_before,
                "pattern_after": opt.pattern_after,
                "explanation": opt.explanation,
                "stats": {
                    "occurrence_count": opt.occurrence_count,
                    "success_rate": opt.success_rate,
                    "avg_improvement": opt.avg_improvement,
                    "times_applied": entry.times_applied,
                    "times_successful": entry.times_successful,
                },
                "tags": entry.tags,
            }

            export_data["patterns"].append(pattern_data)

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(export_data, f, default_flow_style=False, sort_keys=False)

    def import_from_yaml(self, input_path: Path):
        """
        Import patterns from YAML file.

        Args:
            input_path: Input file path
        """
        with open(input_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for pattern_data in data.get("patterns", []):
            # Create optimization
            optimization = DetectedOptimization(
                optimization_id=pattern_data["id"],
                category=OptimizationCategory(pattern_data["category"]),
                impact=OptimizationImpact(pattern_data["impact"]),
                title=pattern_data["title"],
                description=pattern_data["description"],
                pattern_before=pattern_data["pattern_before"],
                pattern_after=pattern_data["pattern_after"],
                language=pattern_data.get("language", "python"),
                explanation=pattern_data.get("explanation", ""),
                occurrence_count=pattern_data.get("stats", {}).get("occurrence_count", 0),
                success_rate=pattern_data.get("stats", {}).get("success_rate", 0.0),
                avg_improvement=pattern_data.get("stats", {}).get("avg_improvement", 0.0),
            )

            # Add to catalog
            self.add_optimization(
                optimization=optimization,
                tags=pattern_data.get("tags", []),
                create_training_material=False,  # Don't recreate for imports
            )

    def get_stats(self) -> Dict:
        """Get catalog statistics."""
        if not self.entries:
            return {
                "total_patterns": 0,
                "by_category": {},
                "by_impact": {},
                "avg_success_rate": 0.0,
                "total_applications": 0,
            }

        return {
            "total_patterns": len(self.entries),
            "by_category": {
                category.value: len([
                    e for e in self.entries.values()
                    if e.optimization.category == category
                ])
                for category in OptimizationCategory
            },
            "by_impact": {
                impact.value: len([
                    e for e in self.entries.values()
                    if e.optimization.impact == impact
                ])
                for impact in OptimizationImpact
            },
            "avg_success_rate": sum(
                e.optimization.success_rate for e in self.entries.values()
            ) / len(self.entries),
            "total_applications": sum(
                e.times_applied for e in self.entries.values()
            ),
            "total_improvements": sum(
                len(e.quality_improvements) for e in self.entries.values()
            ),
        }

    def _create_training_material(self, entry: CatalogEntry):
        """Create training material for catalog entry."""
        if not self.memory_service:
            return

        from .optimization_detector import OptimizationDetector

        # Generate material content
        detector = OptimizationDetector()
        content = detector.create_training_material(entry.optimization)

        try:
            # Add to memory service
            topic = f"optimization_{entry.optimization.category.value}"
            file_name = f"{entry.entry_id}.md"

            self.memory_service.add_training_material(
                topic=topic,
                file_name=file_name,
                content=content,
                agent_id="system",  # System-generated material
            )

            # Store path
            entry.training_material_path = f"{topic}/{file_name}"

        except Exception as e:
            # Don't fail if training material creation fails
            pass

    def _load_catalog(self):
        """Load catalog from disk."""
        catalog_file = self.catalog_path / "catalog.json"

        if not catalog_file.exists():
            return

        try:
            with open(catalog_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for entry_data in data.get("entries", []):
                entry = CatalogEntry(**entry_data)
                self.entries[entry.entry_id] = entry

        except Exception as e:
            print(f"Warning: Failed to load catalog: {e}")

    def _save_catalog(self):
        """Save catalog to disk."""
        catalog_file = self.catalog_path / "catalog.json"

        try:
            data = {
                "version": "1.0.0",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "entries": [
                    entry.model_dump(mode='json')
                    for entry in self.entries.values()
                ]
            }

            with open(catalog_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            print(f"Warning: Failed to save catalog: {e}")
