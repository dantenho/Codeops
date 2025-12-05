import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[3]))

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[3]))

from bin.channel.integration import create_default_channels, setup_tunnel_with_claude
from bin.channel.models import SeverityLevel, Suggestion, SuggestionType
from bin.channel.tunnel import SuggestionTunnel


async def test_tunnel():
    print("Starting Suggestion Tunnel Test...")

    # Initialize
    tunnel = SuggestionTunnel()
    setup_tunnel_with_claude(tunnel)
    channels = create_default_channels(tunnel)

    channel_id = channels["cursor-main"]
    print(f"Tunnel Initialized. Channel ID: {channel_id}")

    # Create a critical suggestion (Should Pass)
    critical_suggestion = Suggestion(
        type=SuggestionType.SECURITY_VULNERABILITY,
        severity=SeverityLevel.CRITICAL,
        file_path="src/auth.py",
        line_start=10,
        code_snippet="password = '123456'",
        description="Hardcoded password detected"
    )

    # Create a non-critical suggestion (Should be Filtered)
    minor_suggestion = Suggestion(
        type=SuggestionType.CRITICAL_REFACTOR,
        severity=SeverityLevel.MEDIUM,
        file_path="src/utils.py",
        line_start=5,
        code_snippet="x = x + 1",
        description="Refactor to use += operator for better style"
    )

    print("\nIngesting suggestions...")
    result = await tunnel.ingest_from_cursor(
        suggestions=[critical_suggestion, minor_suggestion],
        channel_id=channel_id
    )

    print("\nResult:")
    print(f"  - Status: {result['status']}")
    print(f"  - Critical Count (Passed): {result['critical_count']}")
    print(f"  - Filtered Out: {result['filtered_out']}")

    if result['critical_count'] == 1 and result['filtered_out'] == 1:
        print("\nTEST PASSED: Antigravity Filter working correctly.")
    else:
        print("\nTEST FAILED: Incorrect filtering logic.")

if __name__ == "__main__":
    asyncio.run(test_tunnel())
