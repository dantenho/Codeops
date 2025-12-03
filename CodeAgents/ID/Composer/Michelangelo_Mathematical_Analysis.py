"""
[CREATE] Michelangelo - Mathematical Analysis of Skeleton Structures

Uses mathematical equations and accuracy metrics to estimate optimal structure.

Agent: Composer
Timestamp: 2025-12-03T19-06-12Z
Operation: [ANALYZE]
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Tuple

@dataclass
class SkeletonMetrics:
    """
    [CREATE] Mathematical metrics for skeleton analysis.

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """
    agent_id: str
    timestamp: str
    completeness: float
    component_count: int
    file_count: int
    dir_count: int
    depth: int
    entropy: float
    structural_score: float = 0.0

@dataclass
class StructureOptimization:
    """
    [CREATE] Optimization recommendations based on mathematical analysis.

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """
    current_score: float
    optimal_score: float
    improvement_potential: float
    recommendations: List[str] = field(default_factory=list)
    predicted_completeness: float = 0.0
    accuracy_estimate: float = 0.0

class SkeletonMathematicalAnalyzer:
    """
    [CREATE] Mathematical analyzer for skeleton structures.

    Implements various mathematical models to evaluate and optimize
    skeleton structures.

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """

    def __init__(self):
        """Initialize the analyzer."""
        self.optimal_completeness = 1.0
        self.optimal_depth = 3.5  # Between 3 and 4 levels
        self.optimal_file_distribution = {
            'training': 3,
            'rules': 3,
            'methods': 3,
            'files': 0,  # Subdirectories only
            'database': 3,
            'memory': 0  # Subdirectories only
        }

    def calculate_completeness(self, skeleton_data: Dict[str, Any]) -> float:
        """
        [CREATE] Calculate structure completeness metric.

        Formula: C = (Σ(components_present) / total_components) × 100

        Args:
            skeleton_data: Skeleton analysis data

        Returns:
            float: Completeness score (0.0 to 1.0)

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        components = skeleton_data.get('components', {})
        total_components = len(components)

        if total_components == 0:
            return 0.0

        present_count = sum(1 for c in components.values() if c.get('exists', False))
        completeness = present_count / total_components

        # Weight by component completeness
        weighted_sum = sum(
            c.get('completeness', 0.0)
            for c in components.values()
            if c.get('exists', False)
        )

        if present_count > 0:
            completeness = (completeness + weighted_sum / present_count) / 2

        return completeness

    def calculate_depth_metric(self, skeleton_data: Dict[str, Any]) -> float:
        """
        [CREATE] Calculate directory depth metric.

        Formula: D = Σ(depth_i × weight_i) / Σ(weight_i)
        Optimal depth: 3-4 levels

        Args:
            skeleton_data: Skeleton analysis data

        Returns:
            float: Depth score (0.0 to 1.0, higher is better if optimal)

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        components = skeleton_data.get('components', {})
        depths = []

        for component_name, component_data in components.items():
            if component_data.get('exists', False):
                # Base depth: 2 (agent/timestamp/component)
                base_depth = 2
                # Add subdirectory depth
                subdirs = component_data.get('subdirs', [])
                if subdirs:
                    base_depth += 1
                depths.append(base_depth)

        if not depths:
            return 0.0

        avg_depth = sum(depths) / len(depths)

        # Score based on proximity to optimal depth (3.5)
        depth_score = 1.0 - abs(avg_depth - self.optimal_depth) / self.optimal_depth
        return max(0.0, depth_score)

    def calculate_entropy(self, skeleton_data: Dict[str, Any]) -> float:
        """
        [CREATE] Calculate file distribution entropy.

        Formula: H = -Σ(p_i × log2(p_i))
        Higher entropy = better distribution

        Args:
            skeleton_data: Skeleton analysis data

        Returns:
            float: Entropy score (0.0 to 1.0)

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        components = skeleton_data.get('components', {})
        total_files = skeleton_data.get('total_files', 0)

        if total_files == 0:
            return 0.0

        # Calculate file distribution probabilities
        probabilities = []
        for component_data in components.values():
            file_count = len(component_data.get('files', []))
            if file_count > 0:
                prob = file_count / total_files
                probabilities.append(prob)

        if not probabilities:
            return 0.0

        # Calculate entropy
        entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)

        # Normalize to 0-1 scale (max entropy for uniform distribution)
        max_entropy = math.log2(len(probabilities))
        if max_entropy == 0:
            return 0.0

        normalized_entropy = entropy / max_entropy
        return normalized_entropy

    def calculate_temporal_density(self, skeletons: List[Dict[str, Any]]) -> float:
        """
        [CREATE] Calculate temporal density metric.

        Formula: TD = skeletons_count / time_span_days
        Measures skeleton creation frequency

        Args:
            skeletons: List of skeleton data

        Returns:
            float: Temporal density score

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        if len(skeletons) < 2:
            return 0.5  # Neutral score for single skeleton

        # Parse timestamps and calculate time span
        timestamps = []
        for skeleton in skeletons:
            try:
                ts_str = skeleton.get('timestamp', '')
                # Convert YYYY-MM-DDTHH-MM-SSZ to datetime
                dt = datetime.strptime(ts_str, '%Y-%m-%dT%H-%M-%SZ')
                timestamps.append(dt.replace(tzinfo=timezone.utc))
            except (ValueError, KeyError):
                continue

        if len(timestamps) < 2:
            return 0.5

        timestamps.sort()
        time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 86400  # days

        if time_span == 0:
            return 1.0  # All created at once

        density = len(skeletons) / time_span

        # Normalize (assume optimal is 1 skeleton per day)
        optimal_density = 1.0
        score = min(1.0, density / optimal_density)

        return score

    def calculate_structural_score(
        self,
        completeness: float,
        depth_score: float,
        entropy: float,
        temporal_density: float = 0.5
    ) -> float:
        """
        [CREATE] Calculate overall structural quality score.

        Formula: Q = α×C + β×D + γ×H + δ×TD
        Where α+β+γ+δ = 1

        Args:
            completeness: Completeness score
            depth_score: Depth metric score
            entropy: Entropy score
            temporal_density: Temporal density score

        Returns:
            float: Overall structural score (0.0 to 1.0)

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        # Weighted combination
        alpha = 0.40  # Completeness is most important
        beta = 0.20   # Depth matters for usability
        gamma = 0.25  # Entropy indicates good distribution
        delta = 0.15  # Temporal density less critical

        score = (
            alpha * completeness +
            beta * depth_score +
            gamma * entropy +
            delta * temporal_density
        )

        return score

    def predict_optimal_structure(
        self,
        agent_id: str,
        current_skeleton: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        [CREATE] Predict optimal structure based on agent type and current state.

        Uses regression-like approach to estimate optimal configuration.

        Args:
            agent_id: Agent identifier
            current_skeleton: Current skeleton data

        Returns:
            Dict with predicted optimal structure

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        # Base prediction on agent type and current state
        current_completeness = current_skeleton.get('completeness_score', 0.0)

        # Predict optimal completeness (should be 1.0)
        predicted_completeness = 1.0

        # Predict optimal file distribution
        predicted_files = {
            'training': 3,  # progress.json + 2 subdirs
            'rules': 3,     # protocols.md, constraints.yaml, guidelines.json
            'methods': 3,  # __init__.py, core_methods.py, utilities.py
            'files': 0,     # Only subdirectories
            'database': 3,  # schema.sql + 2 subdirs
            'memory': 0     # Only subdirectories
        }

        # Calculate accuracy estimate
        current_files = sum(len(c.get('files', [])) for c in current_skeleton.get('components', {}).values())
        predicted_total_files = sum(predicted_files.values())

        if predicted_total_files > 0:
            accuracy = 1.0 - abs(current_files - predicted_total_files) / predicted_total_files
        else:
            accuracy = 0.0

        return {
            'predicted_completeness': predicted_completeness,
            'predicted_file_distribution': predicted_files,
            'predicted_total_files': predicted_total_files,
            'accuracy_estimate': max(0.0, accuracy),
            'improvement_potential': predicted_completeness - current_completeness
        }

    def estimate_accuracy(
        self,
        actual: Dict[str, Any],
        predicted: Dict[str, Any]
    ) -> float:
        """
        [CREATE] Estimate accuracy of predictions.

        Formula: A = 1 - (|actual - predicted| / predicted)

        Args:
            actual: Actual skeleton metrics
            predicted: Predicted metrics

        Returns:
            float: Accuracy score (0.0 to 1.0)

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        actual_completeness = actual.get('completeness_score', 0.0)
        predicted_completeness = predicted.get('predicted_completeness', 1.0)

        if predicted_completeness == 0:
            return 0.0

        accuracy = 1.0 - abs(actual_completeness - predicted_completeness) / predicted_completeness
        return max(0.0, min(1.0, accuracy))

    def analyze_skeleton(self, skeleton_data: Dict[str, Any]) -> SkeletonMetrics:
        """
        [CREATE] Perform comprehensive mathematical analysis of a skeleton.

        Args:
            skeleton_data: Skeleton analysis data

        Returns:
            SkeletonMetrics: Calculated metrics

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        completeness = self.calculate_completeness(skeleton_data)
        depth_score = self.calculate_depth_metric(skeleton_data)
        entropy = self.calculate_entropy(skeleton_data)

        structural_score = self.calculate_structural_score(
            completeness, depth_score, entropy
        )

        return SkeletonMetrics(
            agent_id=skeleton_data.get('agent_id', ''),
            timestamp=skeleton_data.get('timestamp', ''),
            completeness=completeness,
            component_count=len(skeleton_data.get('components', {})),
            file_count=skeleton_data.get('total_files', 0),
            dir_count=skeleton_data.get('total_dirs', 0),
            depth=int(sum(
                len(c.get('subdirs', [])) + 1
                for c in skeleton_data.get('components', {}).values()
                if c.get('exists', False)
            ) / max(1, len([c for c in skeleton_data.get('components', {}).values() if c.get('exists', False)]))),
            entropy=entropy,
            structural_score=structural_score
        )

    def optimize_structure(
        self,
        skeleton_data: Dict[str, Any],
        all_skeletons: List[Dict[str, Any]]
    ) -> StructureOptimization:
        """
        [CREATE] Generate optimization recommendations.

        Args:
            skeleton_data: Current skeleton data
            all_skeletons: All skeletons for context

        Returns:
            StructureOptimization: Optimization recommendations

        Agent: Composer
        Timestamp: 2025-12-03T19-06-12Z
        """
        metrics = self.analyze_skeleton(skeleton_data)
        prediction = self.predict_optimal_structure(
            skeleton_data.get('agent_id', ''),
            skeleton_data
        )

        current_score = metrics.structural_score
        optimal_score = 1.0  # Perfect structure
        improvement_potential = optimal_score - current_score

        recommendations = []

        # Generate recommendations based on analysis
        if metrics.completeness < 0.9:
            recommendations.append(
                f"Improve completeness from {metrics.completeness:.1%} to 100%"
            )

        if metrics.entropy < 0.5:
            recommendations.append(
                f"Improve file distribution entropy from {metrics.entropy:.2f} to >0.7"
            )

        missing_components = skeleton_data.get('missing_components', [])
        if missing_components:
            recommendations.append(
                f"Add missing components: {', '.join(missing_components)}"
            )

        accuracy = self.estimate_accuracy(skeleton_data, prediction)

        return StructureOptimization(
            current_score=current_score,
            optimal_score=optimal_score,
            improvement_potential=improvement_potential,
            recommendations=recommendations,
            predicted_completeness=prediction['predicted_completeness'],
            accuracy_estimate=accuracy
        )


def main():
    """Main execution function."""
    # Load skeleton inventory
    inventory_file = Path(__file__).parent / "skeleton_inventory.json"

    if not inventory_file.exists():
        print("Error: skeleton_inventory.json not found. Run skeleton_finder.py first.")
        return

    with open(inventory_file, 'r', encoding='utf-8') as f:
        inventory = json.load(f)

    analyzer = SkeletonMathematicalAnalyzer()

    # Analyze each skeleton
    results = []
    for agent_id, skeletons in inventory['skeletons'].items():
        for skeleton in skeletons:
            metrics = analyzer.analyze_skeleton(skeleton)
            optimization = analyzer.optimize_structure(skeleton, skeletons)

            results.append({
                'agent_id': agent_id,
                'timestamp': skeleton['timestamp'],
                'metrics': {
                    'completeness': metrics.completeness,
                    'structural_score': metrics.structural_score,
                    'entropy': metrics.entropy,
                    'file_count': metrics.file_count,
                    'dir_count': metrics.dir_count
                },
                'optimization': {
                    'current_score': optimization.current_score,
                    'optimal_score': optimization.optimal_score,
                    'improvement_potential': optimization.improvement_potential,
                    'accuracy_estimate': optimization.accuracy_estimate,
                    'recommendations': optimization.recommendations
                }
            })

    # Generate report
    report_file = Path(__file__).parent / "mathematical_analysis_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'agent': 'Composer',
                'analyzer_version': '1.0.0'
            },
            'results': results
        }, f, indent=2)

    # Print summary
    print("=" * 80)
    print("MICHELANGELO MATHEMATICAL ANALYSIS REPORT")
    print("=" * 80)
    print()

    for result in results:
        print(f"Agent: {result['agent_id']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"  Completeness: {result['metrics']['completeness']:.1%}")
        print(f"  Structural Score: {result['metrics']['structural_score']:.2f}/1.00")
        print(f"  Entropy: {result['metrics']['entropy']:.2f}")
        print(f"  Accuracy Estimate: {result['optimization']['accuracy_estimate']:.1%}")
        print(f"  Improvement Potential: {result['optimization']['improvement_potential']:.1%}")
        print()
        print("  Recommendations:")
        for rec in result['optimization']['recommendations']:
            print(f"    - {rec}")
        print()

    print(f"Full report saved to: {report_file}")


if __name__ == "__main__":
    main()
