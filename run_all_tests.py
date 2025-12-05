#!/usr/bin/env python
"""
Comprehensive Test Runner with Bug Detection.

Runs all tests, identifies bugs, and provides detailed reports.
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


# Colors for output
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Color.BOLD}{Color.BLUE}{'=' * 70}")
    print(f" {text}")
    print(f"{'=' * 70}{Color.RESET}\n")


def run_test_suite(name, command, timeout=60):
    """Run a test suite and return results."""
    print(f"{Color.BOLD}{name}...{Color.RESET}")
    start = time.time()

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )

        duration = time.time() - start
        success = result.returncode == 0

        # Parse output for details
        output = result.stdout + result.stderr

        return {
            "name": name,
            "success": success,
            "duration": duration,
            "exit_code": result.returncode,
            "stdout": result.stdout[-500:] if result.stdout else "",
            "stderr": result.stderr[-500:] if result.stderr else "",
            "output": output
        }

    except subprocess.TimeoutExpired:
        return {
            "name": name,
            "success": False,
            "duration": timeout,
            "exit_code": -1,
            "error": "TIMEOUT",
            "output": ""
        }

    except Exception as e:
        return {
            "name": name,
            "success": False,
            "duration": 0,
            "exit_code": -1,
            "error": str(e),
            "output": ""
        }


def check_imports():
    """Check if all required imports work."""
    print_header("CHECKING DEPENDENCIES")

    imports_to_check = [
        ("packages.telemetry", "TelemetryLogger"),
        ("packages.integration.local_tools", "tools"),
        ("chromadb", None),
        ("numpy", None),
        ("playwright.async_api", None),
        ("google.generativeai", None),
    ]

    results = []

    for module_name, attr in imports_to_check:
        try:
            if attr:
                exec(f"from {module_name} import {attr}")
            else:
                exec(f"import {module_name}")
            results.append((module_name, True, None))
            print(f"  {Color.GREEN}✅{Color.RESET} {module_name}")
        except Exception as e:
            results.append((module_name, False, str(e)))
            print(f"  {Color.YELLOW}⚠️{Color.RESET} {module_name}: {str(e)[:50]}")

    return results


def main():
    """Run all tests and generate report."""
    print_header("COMPREHENSIVE TEST SUITE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Working Directory: {os.getcwd()}")

    # Check dependencies first
    import_results = check_imports()

    # Test suites to run
    test_suites = [
        {
            "name": "Unit Tests (Nodes)",
            "command": "python -m pytest tests/test_nodes.py -v --tb=short",
            "timeout": 30
        },
        {
            "name": "Integration Simulations (Mock)",
            "command": "python tests/test_integration_simulations.py",
            "timeout": 45
        },
        {
            "name": "Real Simulations",
            "command": "python tests/test_real_simulations.py",
            "timeout": 60
        },
    ]

    # Run all tests
    print_header("RUNNING TEST SUITES")

    results = []
    for suite in test_suites:
        result = run_test_suite(
            suite["name"],
            suite["command"],
            suite.get("timeout", 60)
        )
        results.append(result)

        # Print immediate result
        if result["success"]:
            print(f"  {Color.GREEN}✅ PASSED{Color.RESET} ({result['duration']:.2f}s)")
        else:
            print(f"  {Color.RED}❌ FAILED{Color.RESET} (exit code: {result.get('exit_code', 'N/A')})")
            if "error" in result:
                print(f"     Error: {result['error']}")
        print()

    # Summary
    print_header("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for r in results if r["success"])
    failed = total - passed

    print(f"Total Test Suites: {total}")
    print(f"{Color.GREEN}Passed: {passed}{Color.RESET}")
    print(f"{Color.RED}Failed: {failed}{Color.RESET}")
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if failed == 0 else '❌ SOME TESTS FAILED'}")

    # Detailed failure report
    if failed > 0:
        print_header("FAILURE DETAILS")

        for result in results:
            if not result["success"]:
                print(f"\n{Color.RED}❌ {result['name']}{Color.RESET}")
                print(f"   Exit Code: {result.get('exit_code', 'N/A')}")

                if "error" in result:
                    print(f"   Error: {result['error']}")

                if result.get("stderr"):
                    print("\n   Last stderr output:")
                    print("   " + "\n   ".join(result["stderr"].split("\n")[:10]))

    # Dependency warnings
    failed_imports = [i for i in import_results if not i[1]]
    if failed_imports:
        print_header("MISSING DEPENDENCIES")
        for module, success, error in failed_imports:
            print(f"  {Color.YELLOW}⚠️{Color.RESET} {module}")
            print(f"     Install: pip install {module.split('.')[0]}")

    # Save report
    report_file = Path("test_report.txt")
    with open(report_file, "w") as f:
        f.write(f"Test Report - {datetime.now().isoformat()}\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Total: {total}, Passed: {passed}, Failed: {failed}\n\n")

        for result in results:
            f.write(f"\n{result['name']}: {'PASS' if result['success'] else 'FAIL'}\n")
            f.write(f"Duration: {result['duration']:.2f}s\n")
            if not result["success"] and "error" in result:
                f.write(f"Error: {result['error']}\n")

    print(f"\n{Color.BLUE}Report saved to: {report_file}{Color.RESET}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
