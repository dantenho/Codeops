"""
Wait for response from Gemini via tunnel.

Agent: Antigravity
Created: 2025-12-05T09:05:00Z
Operation: [CREATE]
"""
import time
from datetime import datetime, timezone
from tunnel import Tunnel, MessageType

def wait_for_gemini_response(check_interval: int = 5, max_wait: int = 300):
    """
    [CREATE] Waits for response from Gemini, checking inbox periodically.

    Args:
        check_interval (int): Seconds between checks. Default: 5.
        max_wait (int): Maximum seconds to wait. Default: 300 (5 minutes).

    Returns:
        List[TunnelMessage]: Messages from Gemini, empty if timeout.

    Agent: Antigravity
    Timestamp: 2025-12-05T09:05:00Z
    """
    tunnel = Tunnel("antigravity")
    start_time = time.time()
    check_count = 0

    print("=" * 60)
    print("🔍 Waiting for Gemini's response...")
    print("=" * 60)
    print(f"📬 Checking inbox every {check_interval} seconds")
    print(f"⏱️  Maximum wait time: {max_wait} seconds")
    print(f"📅 Started at: {datetime.now(timezone.utc).isoformat()}")
    print()

    while (time.time() - start_time) < max_wait:
        check_count += 1
        messages = tunnel.receive(mark_read=False)

        # Filter messages from Gemini
        gemini_messages = [msg for msg in messages if msg.sender.lower() == "gemini"]

        if gemini_messages:
            print(f"\n✅ Received {len(gemini_messages)} message(s) from Gemini!")
            print("-" * 60)
            for msg in gemini_messages:
                print(f"📨 Message ID: {msg.id}")
                print(f"   Type: {msg.message_type}")
                print(f"   Timestamp: {msg.timestamp}")
                print(f"   Payload:")
                import json
                print(json.dumps(msg.payload, indent=6))
                print()

            # Mark as read
            tunnel.receive(mark_read=True)
            return gemini_messages

        elapsed = int(time.time() - start_time)
        print(f"⏳ Check #{check_count} - No messages yet (elapsed: {elapsed}s)", end="\r")
        time.sleep(check_interval)

    print(f"\n\n⏰ Timeout after {max_wait} seconds")
    print("   No response from Gemini received")
    return []

if __name__ == "__main__":
    # Wait for response (check every 5 seconds, max 5 minutes)
    messages = wait_for_gemini_response(check_interval=5, max_wait=300)

    if not messages:
        print("\n💡 Tips:")
        print("   - Gemini might be processing the message")
        print("   - Check .tunnel/gemini_inbox.jsonl manually")
        print("   - Verify Gemini's heartbeat is active")
        print("   - Try sending another message if needed")
