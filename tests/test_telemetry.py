
import sys
import os
import json
import shutil
from pathlib import Path
from dataclasses import asdict

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from eudorax.core.telemetry import telemetry, OperationLog, ErrorLog

def test_telemetry_structure():
    print("Testing Telemetry System...")

    # Setup test environment
    test_agent = "TestAgent"
    base_path = Path("CodeAgents")
    logs_dir = base_path / test_agent / "logs"
    errors_dir = base_path / test_agent / "errors"

    # Clean up previous tests
    if logs_dir.exists():
        shutil.rmtree(logs_dir)
    if errors_dir.exists():
        shutil.rmtree(errors_dir)

    # Test Operation Log
    op_log = OperationLog(
        agent=test_agent,
        operation="CREATE",
        target={"file": "test.py"},
        status="SUCCESS",
        context={"test": "true"}
    )

    log_path = telemetry.log_operation(op_log)

    assert log_path.exists(), "Operation log file was not created"
    assert str(logs_dir) in str(log_path), f"Log not in correct directory: {log_path}"

    with open(log_path, 'r') as f:
        data = json.load(f)
        assert data['agent'] == test_agent
        assert data['operation'] == "CREATE"
        assert data['status'] == "SUCCESS"
        print("✅ Operation Log Test Passed")

    # Test Error Log
    error_log = ErrorLog(
        agent=test_agent,
        error_type="ValueError",
        message="Test Error",
        severity="HIGH"
    )

    error_path = telemetry.log_error(error_log)

    assert error_path.exists(), "Error log file was not created"
    assert str(errors_dir) in str(error_path), f"Error log not in correct directory: {error_path}"

    with open(error_path, 'r') as f:
        data = json.load(f)
        assert data['agent'] == test_agent
        assert data['severity'] == "HIGH"
        print("✅ Error Log Test Passed")

    # Cleanup
    if logs_dir.exists():
        shutil.rmtree(logs_dir)
    if errors_dir.exists():
        shutil.rmtree(errors_dir)

    # Remove TestAgent dir if empty
    try:
        (base_path / test_agent).rmdir()
    except:
        pass

if __name__ == "__main__":
    test_telemetry_structure()
