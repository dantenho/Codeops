"""
[CREATE] Run Complete Analysis - Finder, Philosopher, Michelangelo

Orchestrates the complete analysis workflow combining all three analysis
frameworks to generate comprehensive skeleton analysis reports.

Agent: Composer
Timestamp: 2025-12-03T19:25:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import sys
from pathlib import Path

# Add methods directory to path
methods_dir = Path(__file__).parent
sys.path.insert(0, str(methods_dir))

from michelangelo_analyzer import create_michelangelo_analyzer
from philosopher_analyzer import create_philosopher_analyzer
from skeleton_finder import create_skeleton_finder

logger = logging.getLogger("composer.run_analysis")


def run_complete_analysis(output_path: Path) -> Dict[str, Any]:
    """
    [CREATE] Run complete analysis workflow.

    Combines Finder, Philosopher, and Michelangelo analyses to generate
    comprehensive skeleton analysis report.

    Args:
        output_path (Path): Path to save analysis report JSON.

    Returns:
        Dict[str, Any]: Complete analysis report.

    Algorithm:
        1. Finder: Locate all skeletons
        2. Philosopher: Critical analysis of each skeleton
        3. Michelangelo: Mathematical analysis of each skeleton
        4. Combine results into comprehensive report

    Agent: Composer
    Timestamp: 2025-12-03T19:25:00Z
    """
    logger.info("Starting complete skeleton analysis workflow...")

    # Step 1: Finder - Locate all skeletons
    finder = create_skeleton_finder()
    finder_report = finder.generate_finder_report()
    logger.info(f"Found {finder_report['metadata']['total_skeletons']} skeletons")

    # Step 2 & 3: Analyze each skeleton
    philosopher = create_philosopher_analyzer()
    michelangelo = create_michelangelo_analyzer()

    analyzed_skeletons = []
    for agent_id, skeletons in finder_report["skeletons_by_agent"].items():
        for skeleton_data in skeletons:
            # Philosopher analysis
            critical_analysis = philosopher.analyze_skeleton(skeleton_data)

            # Michelangelo analysis
            math_analysis = michelangelo.analyze_structure(skeleton_data)

            analyzed_skeletons.append({
                "skeleton_data": skeleton_data,
                "philosopher_analysis": {
                    "overall_score": critical_analysis.overall_score,
                    "quality_level": critical_analysis.quality_level.name,
                    "strengths": critical_analysis.strengths,
                    "weaknesses": critical_analysis.weaknesses,
                    "improvements": critical_analysis.improvements,
                    "annotations": critical_analysis.annotations,
                    "philosophical_reflection": critical_analysis.philosophical_reflection,
                },
                "michelangelo_analysis": {
                    "metrics": {
                        "completeness_ratio": math_analysis.metrics.completeness_ratio,
                        "file_density": math_analysis.metrics.file_density,
                        "structural_entropy": math_analysis.metrics.structural_entropy,
                        "balance_index": math_analysis.metrics.balance_index,
                        "growth_potential": math_analysis.metrics.growth_potential,
                        "structural_integrity": math_analysis.metrics.structural_integrity,
                        "accuracy_estimate": math_analysis.metrics.accuracy_estimate,
                    },
                    "equations_used": math_analysis.equations_used,
                    "predictions": math_analysis.predictions,
                    "optimization_suggestions": math_analysis.optimization_suggestions,
                },
            })

    # Generate comprehensive report
    report = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "analyzer": "Composer",
            "analysis_frameworks": ["Finder", "Philosopher", "Michelangelo"],
        },
        "finder_report": finder_report,
        "analyzed_skeletons": analyzed_skeletons,
        "summary": {
            "total_skeletons_analyzed": len(analyzed_skeletons),
            "average_philosopher_score": sum(
                s["philosopher_analysis"]["overall_score"]
                for s in analyzed_skeletons
            ) / len(analyzed_skeletons) if analyzed_skeletons else 0,
            "average_structural_integrity": sum(
                s["michelangelo_analysis"]["metrics"]["structural_integrity"]
                for s in analyzed_skeletons
            ) / len(analyzed_skeletons) if analyzed_skeletons else 0,
        },
    }

    # Save report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"Analysis complete. Report saved to {output_path}")
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    output_path = Path(__file__).parent.parent / "analysis_report.json"
    report = run_complete_analysis(output_path)
    print(f"Analysis complete. Analyzed {len(report['analyzed_skeletons'])} skeletons.")
