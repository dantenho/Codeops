"""
[CREATE] Antigravity Core Methods

Structural validation and optimization methods for the EudoraX agent system.

Agent: Antigravity
Timestamp: 2025-12-03T16:27:00-03:00
Operation: [CREATE]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StructureMetrics:
    """Metrics for agent structure evaluation."""
    completeness_ratio: float
    content_density: float
    entropy: float
    interconnectivity: float
    accuracy: float


def calculate_structure_metrics(agent_path: Path) -> StructureMetrics:
    """
    Calculate mathematical metrics for an agent structure.

    Args:
        agent_path: Path to agent directory

    Returns:
        StructureMetrics with calculated values
    """
    required = {'training', 'rules', 'methods', 'files', 'database', 'memory', 'logs', 'analysis'}

    if not agent_path.exists():
        return StructureMetrics(0, 0, 0, 0, 0)

    # Completeness
    present = {d.name for d in agent_path.iterdir() if d.is_dir()}
    completeness = len(present & required) / len(required)

    # Content density
    files = list(agent_path.rglob('*'))
    total_files = len([f for f in files if f.is_file()])
    content_files = len([f for f in files if f.is_file() and f.stat().st_size > 100])
    density = content_files / total_files if total_files > 0 else 0

    # Simple entropy (uniformity of directory sizes)
    import math
    sizes = [len(list(d.rglob('*'))) for d in agent_path.iterdir() if d.is_dir()]
    total = sum(sizes)
    if total > 0:
        probs = [s/total for s in sizes]
        entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in probs)
        max_entropy = math.log2(len(probs)) if probs else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    else:
        normalized_entropy = 0

    # Interconnectivity (heuristic)
    interconnectivity = min(0.6 + (completeness * 0.2), 1.0)

    # Overall accuracy
    accuracy = 0.4 * completeness + 0.3 * (1 - normalized_entropy) + 0.3 * interconnectivity

    return StructureMetrics(
        completeness_ratio=completeness,
        content_density=density,
        entropy=normalized_entropy,
        interconnectivity=interconnectivity,
        accuracy=accuracy
    )


def validate_skeleton(agent_id: str, base_path: str = "CodeAgents") -> Tuple[bool, List[str]]:
    """
    Validate an agent skeleton structure.

    Args:
        agent_id: Agent identifier
        base_path: Base path for agents

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    agent_path = Path(base_path) / agent_id
    issues = []

    if not agent_path.exists():
        return False, [f"Agent path does not exist: {agent_path}"]

    required_dirs = ['training', 'rules', 'methods', 'files', 'database', 'memory']
    for req_dir in required_dirs:
        if not (agent_path / req_dir).exists():
            issues.append(f"Missing required directory: {req_dir}")

    # Check for essential files
    if (agent_path / 'training').exists():
        if not (agent_path / 'training' / 'progress.json').exists():
            issues.append("Missing training/progress.json")

    return len(issues) == 0, issues


def generate_improvement_plan(metrics: StructureMetrics) -> List[str]:
    """
    Generate actionable improvement recommendations.

    Args:
        metrics: Current structure metrics

    Returns:
        List of recommended actions
    """
    recommendations = []

    if metrics.completeness_ratio < 0.75:
        recommendations.append("Add missing required directories to reach 75% completeness")

    if metrics.content_density < 0.60:
        recommendations.append("Populate existing structures with meaningful content")

    if metrics.accuracy < 0.75:
        recommendations.append("Focus on balanced development across all components")

    if not recommendations:
        recommendations.append("Structure is optimal - maintain and iterate")

    return recommendations
