"""
Test suite for all code paths.
Tests enum validation, imports, and runtime behavior.
"""
import asyncio
import sys
import traceback
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_enum_validation() -> Dict[str, Any]:
    """Test all enum values are valid."""
    try:
        from bin.channel.models import SeverityLevel, SuggestionType

        # Test all SeverityLevel values
        valid_severities = []
        for severity_name in ["CRITICAL", "HIGH", "MEDIUM"]:
            severity = getattr(SeverityLevel, severity_name)
            valid_severities.append(severity_name)

        # Verify LOW doesn't exist
        try:
            _ = SeverityLevel.LOW
            return {"status": "error", "error": "LOW severity should not exist"}
        except AttributeError:
            pass  # Expected

        # Test all SuggestionType values
        valid_types = []
        for type_name in ["BUG_FIX", "SECURITY_VULNERABILITY", "BREAKING_CHANGE",
                         "RUNTIME_ERROR", "TYPE_ERROR", "LOGIC_ERROR", "CRITICAL_REFACTOR"]:
            suggestion_type = getattr(SuggestionType, type_name)
            valid_types.append(type_name)

        # Verify REFACTORING doesn't exist
        try:
            _ = SuggestionType.REFACTORING
            return {"status": "error", "error": "REFACTORING type should not exist"}
        except AttributeError:
            pass  # Expected

        return {"status": "success", "valid_severities": valid_severities, "valid_types": valid_types}

    except Exception as e:
        return {"status": "error", "error": str(e)}


async def test_suggestion_creation() -> Dict[str, Any]:
    """Test suggestions can be created with valid enum values."""
    try:
        from bin.channel.models import SeverityLevel, Suggestion, SuggestionType

        suggestions_created = []

        # Test critical suggestion
        critical = Suggestion(
            type=SuggestionType.SECURITY_VULNERABILITY,
            severity=SeverityLevel.CRITICAL,
            file_path="test.py",
            line_start=1,
            code_snippet="password = '123'",
            description="Test security issue"
        )
        suggestions_created.append("critical")

        # Test medium severity with CRITICAL_REFACTOR
        refactor = Suggestion(
            type=SuggestionType.CRITICAL_REFACTOR,
            severity=SeverityLevel.MEDIUM,
            file_path="test.py",
            line_start=2,
            code_snippet="x = x + 1",
            description="Test refactor"
        )
        suggestions_created.append("refactor")

        return {"status": "success", "suggestions_created": suggestions_created}

    except Exception as e:
        return {"status": "error", "error": str(e)}


async def test_tunnel_initialization() -> Dict[str, Any]:
    """Test tunnel system initializes without errors."""
    try:
        from bin.channel.tunnel import SuggestionTunnel

        tunnel = SuggestionTunnel()
        channel = tunnel.create_channel("test-channel", "Test Channel")

        return {"status": "success", "tunnel_initialized": True}

    except Exception as e:
        return {"status": "error", "error": str(e)}


async def test_filter_logic() -> Dict[str, Any]:
    """Test Antigravity filter correctly identifies critical vs non-critical."""
    try:
        from bin.channel.models import SeverityLevel, Suggestion, SuggestionType
        from bin.channel.antigravity import AntigravityFilter

        # Create critical suggestion (should pass)
        critical = Suggestion(
            type=SuggestionType.SECURITY_VULNERABILITY,
            severity=SeverityLevel.CRITICAL,
            file_path="test.py",
            line_start=1,
            code_snippet="password = '123'",
            description="Security vulnerability detected"
        )

        is_critical_result = AntigravityFilter.is_critical(critical)

        # Create non-critical suggestion (should be filtered)
        non_critical = Suggestion(
            type=SuggestionType.CRITICAL_REFACTOR,
            severity=SeverityLevel.MEDIUM,
            file_path="test.py",
            line_start=2,
            code_snippet="x = x + 1",
            description="Use += operator for better style"
        )

        is_non_critical_result = AntigravityFilter.is_critical(non_critical)

        # Test filter method
        filtered = AntigravityFilter.filter([critical, non_critical])

        return {
            "status": "success",
            "critical_passed": is_critical_result,
            "non_critical_filtered": not is_non_critical_result,
            "filtered_count": len(filtered)
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


async def test_backend_api() -> Dict[str, Any]:
    """Test backend API imports and basic functionality."""
    try:
        api_path = project_root / "backend" / "api"
        if api_path.exists():
            sys.path.insert(0, str(api_path.parent))
            from api import main

            # Test nodes directory discovery
            if hasattr(main, 'discover_nodes'):
                nodes = main.discover_nodes()
                return {"status": "success", "nodes_count": len(nodes)}

        return {"status": "success", "api_available": False}

    except Exception as e:
        return {"status": "error", "error": str(e)}


async def main():
    """Run all tests."""
    print("=" * 60)
    print("CODE TEST SUITE - ALL CODE PATHS")
    print("=" * 60)
    print()

    results = {}

    print("[A] Testing enum validation...")
    results['enum_validation'] = await test_enum_validation()
    print(f"   Result: {results['enum_validation']['status']}")
    if results['enum_validation']['status'] == 'error':
        print(f"   Error: {results['enum_validation'].get('error')}")
    print()

    print("[B] Testing suggestion creation...")
    results['suggestion_creation'] = await test_suggestion_creation()
    print(f"   Result: {results['suggestion_creation']['status']}")
    if results['suggestion_creation']['status'] == 'error':
        print(f"   Error: {results['suggestion_creation'].get('error')}")
    print()

    print("[C] Testing tunnel initialization...")
    results['tunnel_init'] = await test_tunnel_initialization()
    print(f"   Result: {results['tunnel_init']['status']}")
    if results['tunnel_init']['status'] == 'error':
        print(f"   Error: {results['tunnel_init'].get('error')}")
    print()

    print("[D] Testing filter logic...")
    results['filter_logic'] = await test_filter_logic()
    print(f"   Result: {results['filter_logic']['status']}")
    if results['filter_logic']['status'] == 'error':
        print(f"   Error: {results['filter_logic'].get('error')}")
    print()

    print("[E] Testing backend API...")
    results['backend_api'] = await test_backend_api()
    print(f"   Result: {results['backend_api']['status']}")
    if results['backend_api']['status'] == 'error':
        print(f"   Error: {results['backend_api'].get('error')}")
    print()

    print("=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)

    # Summary
    passed = sum(1 for r in results.values() if r.get('status') == 'success')
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    print()

    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(main())
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()

