"""
# [CREATE] Test execution runner for CodeAgents training tests
#
# Executes test_models.py and test_spaced_repetition.py, captures results,
# handles import errors, and generates structured reports.
#
# Agent: GrokIA
# Created: 2025-12-04T00:00:00Z
# Operation: [CREATE]

import os
import sys
import json
import subprocess
import tempfile
import shutil
import time
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestRunner:
    """Main test execution runner."""

    def __init__(self, test_dir: Path = Path("CodeAgents/Training/tests")):
        self.test_dir = test_dir
        self.test_files = [
            "test_models.py",
            "test_spaced_repetition.py"
        ]
        self.results_dir = Path("test_analysis/execution")
        self.results_dir.mkdir(exist_ok=True)

    def check_environment(self) -> dict:
        """Check Python environment and dependencies."""
        env_check = {
            "python_version": sys.version,
            "working_directory": str(Path.cwd()),
            "test_directory": str(self.test_dir),
            "pytest_available": self._check_pytest(),
            "dependencies_installed": self._check_dependencies()
        }
        logger.info(f"Environment check: {env_check}")
        return env_check

    def _check_pytest(self) -> bool:
        """Check if pytest is available."""
        try:
            import pytest
            return True
        except ImportError:
            return False

    def _check_dependencies(self) -> dict:
        """Check if test dependencies are available."""
        deps = {}
        try:
            import pytest
            deps["pytest"] = "available"
        except ImportError:
            deps["pytest"] = "missing - install with: pip install pytest"

        try:
            from training.models import Flashcard
            deps["training.models"] = "available"
        except ImportError as e:
            deps["training.models"] = f"import error: {str(e)}"

        try:
            from training.services.spaced_repetition import SM2SpacedRepetition
            deps["training.services"] = "available"
        except ImportError as e:
            deps["training.services"] = f"import error: {str(e)}"

        return deps

    def run_single_test_file(self, test_file: str) -> dict:
        """Run a single test file and capture results."""
        test_path = self.test_dir / test_file

        if not test_path.exists():
            return {
                "test_file": test_file,
                "status": "error",
                "error": f"Test file not found: {test_path}",
                "duration": 0,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "output": ""
            }

        start_time = time.time()
        result = {
            "test_file": test_file,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "duration": 0,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "output": "",
            "errors": []
        }

        try:
            # Create temporary environment for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy test file to temp directory
                temp_test_path = Path(temp_dir) / test_file
                shutil.copy2(test_path, temp_test_path)

                # Set PYTHONPATH to include src directory
                env = os.environ.copy()
                src_path = Path.cwd() / "CodeAgents/Training/src"
                env["PYTHONPATH"] = f"{src_path}:{env.get('PYTHONPATH', '')}"

                # Try to run with pytest
                cmd = ["pytest", str(temp_test_path), "-v", "--tb=short"]
                process = subprocess.Popen(
                    cmd,
                    cwd=temp_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True
                )

                stdout, stderr = process.communicate()
                return_code = process.returncode

                end_time = time.time()
                result["duration"] = end_time - start_time

                if return_code == 0:
                    result["status"] = "success"
                    # Parse pytest output for counts
                    output = stdout + stderr
                    result["output"] = output

                    # Simple parsing for test counts
                    if "collected 0 items" in output:
                        result["tests_run"] = 0
                        result["errors"].append("No tests collected - likely import errors")
                    else:
                        # Look for summary line
                        summary_line = None
                        for line in output.splitlines():
                            if line.strip().startswith("=== ") or " passed" in line:
                                summary_line = line
                                break

                        if summary_line:
                            # Extract numbers (basic parsing)
                            import re
                            numbers = re.findall(r'\d+', summary_line)
                            if len(numbers) >= 2:
                                result["tests_run"] = int(numbers[0])
                                result["tests_passed"] = int(numbers[1])
                                result["tests_failed"] = result["tests_run"] - result["tests_passed"]
                else:
                    result["status"] = "failed"
                    result["output"] = f"Return code: {return_code}\n{stdout}\n{stderr}"
                    result["errors"].append(f"Pytest failed with return code {return_code}")

        except Exception as e:
            end_time = time.time()
            result["duration"] = end_time - start_time
            result["status"] = "error"
            result["output"] = f"Exception during execution: {str(e)}"
            result["errors"].append(str(e))

        return result

    def run_all_tests(self) -> dict:
        """Run all test files and return combined results."""
        all_results = {
            "timestamp": datetime.now().isoformat(),
            "environment": self.check_environment(),
            "individual_results": {},
            "summary": {
                "total_tests_run": 0,
                "total_tests_passed": 0,
                "total_tests_failed": 0,
                "total_duration": 0,
                "overall_status": "success"
            }
        }

        for test_file in self.test_files:
            result = self.run_single_test_file(test_file)
            all_results["individual_results"][test_file] = result

            # Update summary
            all_results["summary"]["total_tests_run"] += result["tests_run"]
            all_results["summary"]["total_tests_passed"] += result["tests_passed"]
            all_results["summary"]["total_tests_failed"] += result["tests_failed"]
            all_results["summary"]["total_duration"] += result["duration"]

            if result["status"] != "success":
                all_results["summary"]["overall_status"] = "failed"

        return all_results

    def save_results(self, results: dict, filename: str = None) -> Path:
        """Save test results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"

        filepath = self.results_dir / filename
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Results saved to: {filepath}")
        return filepath

    def generate_summary_report(self, results: dict) -> Path:
        """Generate markdown summary report."""
        summary = results["summary"]
        individual = results["individual_results"]

        report_content = f"""# Test Execution Summary
Generated: {datetime.now().isoformat()}

## Environment
{json.dumps(results['environment'], indent=2)}

## Overall Results
- **Total Tests Run:** {summary['total_tests_run']}
- **Tests Passed:** {summary['total_tests_passed']}
- **Tests Failed:** {summary['total_tests_failed']}
- **Overall Status:** {summary['overall_status'].upper()}
- **Total Duration:** {summary['total_duration']:.2f} seconds

## Individual Test Files

"""

        for test_file, result in individual.items():
            report_content += f"""
### {test_file}
- **Status:** {result['status'].upper()}
- **Tests Run:** {result['tests_run']}
- **Duration:** {result['duration']:.2f} seconds
- **Errors:** {len(result['errors'])}
"""

            if result['errors']:
                report_content += "\n**Errors:**\n"
                for error in result['errors']:
                    report_content += f"- {error}\n"

            if result['status'] == 'failed':
                report_content += f"\n**Output:**\n```\n{result['output'][:500]}...\n```\n"

        report_path = self.results_dir / "execution_summary.md"
        with open(report_path, "w") as f:
            f.write(report_content)

        logger.info(f"Summary report generated: {report_path}")
        return report_path

def main():
    """Main execution function."""
    print("CodeAgents Test Runner")
    print("=" * 50)

    runner = TestRunner()

    print("1. Checking environment...")
    env = runner.check_environment()

    print("\n2. Running tests...")
    results = runner.run_all_tests()

    print("\n3. Saving results...")
    json_path = runner.save_results(results)

    print("\n4. Generating summary report...")
    md_path = runner.generate_summary_report(results)

    print(f"\n✅ Execution complete!")
    print(f"📊 Results: {json_path}")
    print(f"📋 Summary: {md_path}")

    # Print summary
    summary = results["summary"]
    print(f"\n📈 SUMMARY:")
    print(f"   Tests Run: {summary['total_tests_run']}")
    print(f"   Passed: {summary['total_tests_passed']}")
    print(f"   Failed: {summary['total_tests_failed']}")
    print(f"   Status: {summary['overall_status'].upper()}")
    print(f"   Duration: {summary['total_duration']:.2f}s")

if __name__ == "__main__":
    main()

