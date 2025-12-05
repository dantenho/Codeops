"""
Agent Simulation Runner - Windows Compatible
Runs integration simulations without emoji encoding issues
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_integration_simulations import run_all_simulations

if __name__ == "__main__":
    try:
        results = run_all_simulations()

        # Print simple summary
        print("\n" + "="*70)
        print("FINAL RESULTS")
        print("="*70)

        passed = sum(1 for r in results if r.get("success", False))
        total = len(results)

        print(f"\nTotal Simulations: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")

        sys.exit(0 if passed == total else 1)

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
