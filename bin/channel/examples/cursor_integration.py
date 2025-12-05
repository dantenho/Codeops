"""
Example integration scripts for Cursor IDE.
"""
import asyncio
import aiohttp
from typing import List, Dict, Any


class CursorTunnelClient:
    """Client for sending Cursor IDE suggestions to the tunnel."""

    def __init__(self, base_url: str = "http://localhost:8000", channel_id: str = None):
        self.base_url = base_url
        self.channel_id = channel_id

    async def send_suggestions(
        self,
        suggestions: List[Dict[str, Any]],
        bin_name: str = None
    ) -> Dict[str, Any]:
        """Send a batch of suggestions to the tunnel."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tunnel/ingest",
                json={
                    "suggestions": suggestions,
                    "channel_id": self.channel_id,
                    "bin_name": bin_name
                }
            ) as response:
                return await response.json()

    async def send_single_suggestion(
        self,
        suggestion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a single suggestion in real-time."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tunnel/process-single",
                json={
                    "suggestion": suggestion,
                    "channel_id": self.channel_id
                }
            ) as response:
                return await response.json()

    async def get_stats(self) -> Dict[str, Any]:
        """Get tunnel statistics."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/tunnel/stats"
            ) as response:
                return await response.json()


# Example 1: Send a batch of critical issues
async def example_batch_send():
    """Example: Send multiple suggestions at once."""
    client = CursorTunnelClient(channel_id="your-channel-id")

    suggestions = [
        {
            "type": "security_vulnerability",
            "severity": "critical",
            "file_path": "src/auth.py",
            "line_start": 42,
            "code_snippet": "password = request.GET['password']",
            "description": "Password transmitted in URL - use POST instead",
            "suggested_fix": "password = request.POST.get('password')"
        },
        {
            "type": "runtime_error",
            "severity": "high",
            "file_path": "src/utils.py",
            "line_start": 15,
            "code_snippet": "return data[index]",
            "description": "Potential IndexError - no bounds checking",
            "suggested_fix": "return data[index] if index < len(data) else None"
        }
    ]

    result = await client.send_suggestions(suggestions, bin_name="cursor_batch_001")
    print(f"✓ Sent {result['critical_count']} critical issues to Claude Code")
    print(f"✗ Filtered out {result['filtered_out']} non-critical suggestions")


# Example 2: Real-time suggestion streaming
async def example_realtime_stream():
    """Example: Stream suggestions as they're detected."""
    client = CursorTunnelClient(channel_id="your-channel-id")

    # Simulate Cursor detecting issues in real-time
    suggestion = {
        "type": "bug_fix",
        "severity": "critical",
        "file_path": "src/payment.py",
        "line_start": 108,
        "code_snippet": "total = price * quantity",
        "description": "Integer overflow risk with large quantities",
        "suggested_fix": "total = Decimal(price) * Decimal(quantity)"
    }

    result = await client.send_single_suggestion(suggestion)
    if result["status"] == "success":
        print(f"✓ Critical issue sent to Claude Code (bin: {result['bin_id']})")
    else:
        print("✗ No critical issues detected")


# Example 3: File watcher integration
async def example_file_watcher():
    """Example: Watch a file for Cursor IDE suggestions."""
    import json
    from pathlib import Path
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class SuggestionFileHandler(FileSystemEventHandler):
        def __init__(self, client: CursorTunnelClient):
            self.client = client

        def on_modified(self, event):
            if event.src_path.endswith('cursor_suggestions.json'):
                with open(event.src_path, 'r') as f:
                    suggestions = json.load(f)

                # Send to tunnel
                result = asyncio.run(
                    self.client.send_suggestions(suggestions)
                )
                print(f"Processed {len(suggestions)} suggestions")
                print(f"Critical: {result['critical_count']}")

    client = CursorTunnelClient(channel_id="your-channel-id")
    event_handler = SuggestionFileHandler(client)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    print("Watching for Cursor IDE suggestions...")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Example 4: Check tunnel statistics
async def example_check_stats():
    """Example: Monitor tunnel statistics."""
    client = CursorTunnelClient()
    stats = await client.get_stats()

    print("=== Tunnel Statistics ===")
    print(f"Channels: {stats['channels']}")
    print(f"Active bins: {stats['active_bins']}")
    print(f"Total suggestions: {stats['total_suggestions']}")
    print(f"Critical suggestions: {stats['critical_suggestions']}")


if __name__ == "__main__":
    # Run an example
    print("Running batch send example...")
    asyncio.run(example_batch_send())

    print("\nRunning real-time stream example...")
    asyncio.run(example_realtime_stream())

    print("\nChecking tunnel statistics...")
    asyncio.run(example_check_stats())
