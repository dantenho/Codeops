"""
[CREATE] Run Complete Skeleton Analysis

Orchestrates the complete analysis pipeline:
1. Finder - Discover skeletons
2. Philosopher - Critical analysis
3. Michelangelo - Mathematical analysis

Agent: Composer
Timestamp: 2025-12-03T19-06-12Z
Operation: [CREATE]
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from skeleton_finder import SkeletonFinder, create_skeleton_finder
from philosopher_analysis import Philosopher, create_philosopher
from michelangelo_analysis import Michelangelo, create_michelangelo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("composer.run_analysis")


def main() -> None:
    """
    [CREATE] Run complete skeleton analysis pipeline.

    Agent: Composer
    Timestamp: 2025-12-03T19-06-12Z
    """
    logger.info("=" * 80)
    logger.info("COMPOSER SKELETON ANALYSIS - Complete Pipeline")
    logger.info("=" * 80)

    # Initialize components
    finder = create_skeleton_finder()
    philosopher = create_philosopher()
    michelangelo = create_michelangelo()

    # Task 2: Find all skeletons
    logger.info("\n[TASK 2] FINDER - Discovering skeletons...")
    skeletons = finder.find_all_skeletons()
    logger.info(f"Found {len(skeletons)} skeleton structures")

    # Export skeleton discovery
    discovery_output = Path(__file__).parent / "skeleton_discovery.json"
    finder.export_analysis(skeletons, discovery_output)
    logger.info(f"Discovery results exported to {discovery_output}")

    # Task 3: Philosophical analysis
    logger.info("\n[TASK 3] PHILOSOPHER - Critical analysis...")
    philosophical_analyses = []

    for skeleton in skeletons:
        analysis = philosopher.analyze_skeleton(skeleton)
        philosophical_analyses.append(analysis)
        logger.info(f"  {skeleton.agent_id}: Score {analysis.overall_score:.2f}/100")

    # Export philosophical analysis
    philosopher_output = Path(__file__).parent / "philosophical_analysis.json"
    with open(philosopher_output, "w", encoding="utf-8") as f:
        json.dump(
            {
                "analyses": [a.to_dict() for a in philosophical_analyses],
                "summary": {
                    "total_analyzed": len(philosophical_analyses),
                    "average_score": sum(a.overall_score for a in philosophical_analyses) / len(philosophical_analyses) if philosophical_analyses else 0.0,
                    "highest_score": max((a.overall_score for a in philosophical_analyses), default=0.0),
                    "lowest_score": min((a.overall_score for a in philosophical_analyses), default=0.0)
                }
            },
            f,
            indent=2
        )
    logger.info(f"Philosophical analysis exported to {philosopher_output}")

    # Task 4: Mathematical analysis
    logger.info("\n[TASK 4] MICHELANGELO - Mathematical structure analysis...")

    mathematical_analyses = []
    for skeleton in skeletons:
        metrics = michelangelo.analyze_structure(skeleton)
        mathematical_analyses.append({
            "skeleton_id": f"{skeleton.agent_id}_{skeleton.timestamp}",
            "metrics": metrics.to_dict()
        })
        logger.info(f"  {skeleton.agent_id}: Optimality {metrics.optimality_score:.2f}")

    # Predict optimal structure
    logger.info("\nPredicting optimal structure configuration...")
    optimal_prediction = michelangelo.predict_optimal_structure(skeletons)
    logger.info(f"  Confidence: {optimal_prediction.confidence_level:.2f}")
    logger.info(f"  Predicted Completeness: {optimal_prediction.predicted_completeness:.2f}")
    logger.info(f"  Recommended Components: {', '.join(optimal_prediction.recommended_components)}")

    # Export mathematical analysis
    michelangelo_output = Path(__file__).parent / "mathematical_analysis.json"
    michelangelo.export_analysis(michelangelo_output)
    logger.info(f"Mathematical analysis exported to {michelangelo_output}")

    # Create comprehensive report
    logger.info("\n[REPORT] Generating comprehensive analysis report...")
    report_output = Path(__file__).parent / "comprehensive_analysis_report.json"

    report = {
        "report_timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "Composer",
        "summary": {
            "skeletons_discovered": len(skeletons),
            "average_philosophical_score": sum(a.overall_score for a in philosophical_analyses) / len(philosophical_analyses) if philosophical_analyses else 0.0,
            "average_mathematical_optimality": sum(m["metrics"]["optimality_score"] for m in mathematical_analyses) / len(mathematical_analyses) if mathematical_analyses else 0.0,
            "optimal_structure_confidence": optimal_prediction.confidence_level
        },
        "skeleton_details": [
            {
                "agent_id": s.agent_id,
                "timestamp": s.timestamp,
                "completeness": s.completeness_score,
                "philosophical_score": ph.overall_score,
                "mathematical_optimality": math_an["metrics"]["optimality_score"]
            }
            for s, ph, math_an in zip(skeletons, philosophical_analyses, mathematical_analyses)
        ],
        "optimal_structure_prediction": optimal_prediction.to_dict(),
        "recommendations": [
            "Maintain standard 6-component structure (training/rules/methods/files/database/memory)",
            f"Target completeness score: {optimal_prediction.predicted_completeness:.2f}",
            f"Aim for optimality score: {sum(m['metrics']['optimality_score'] for m in mathematical_analyses) / len(mathematical_analyses) if mathematical_analyses else 75.0:.2f}",
            "Ensure all components have at least minimal file presence",
            "Maintain consistent timestamp format (ISO 8601)"
        ]
    }

    with open(report_output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Comprehensive report exported to {report_output}")

    logger.info("\n" + "=" * 80)
    logger.info("ANALYSIS COMPLETE")
    logger.info("=" * 80)
    logger.info(f"  Skeletons analyzed: {len(skeletons)}")
    logger.info(f"  Average score: {report['summary']['average_philosophical_score']:.2f}/100")
    logger.info(f"  Optimality: {report['summary']['average_mathematical_optimality']:.2f}/100")
    logger.info(f"  Confidence: {optimal_prediction.confidence_level:.2f}")


if __name__ == "__main__":
    main()
