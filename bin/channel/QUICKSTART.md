# Suggestion Tunnel - Quick Start

Get the tunnel running in 5 minutes.

## Installation

```bash
# Navigate to project root
cd CodeAgents

# Install dependencies (if not already installed)
pip install fastapi uvicorn pydantic aiohttp watchdog
```

## Start the Tunnel

```bash
# Start the FastAPI server (includes tunnel endpoints)
cd packages/api
uvicorn codeops.api.main:app --reload --port 8000
```

The tunnel is now running at `http://localhost:8000/tunnel`

## Test the Tunnel

```bash
# Health check
curl http://localhost:8000/tunnel/health

# Get statistics
curl http://localhost:8000/tunnel/stats

# List channels (3 default channels created on startup)
curl http://localhost:8000/tunnel/channels
```

## Send Your First Suggestion

### Option 1: Using curl

```bash
# First, get a channel ID
CHANNEL_ID=$(curl -s http://localhost:8000/tunnel/channels | jq -r '.[0].id')

# Send a critical security issue
curl -X POST http://localhost:8000/tunnel/ingest \
  -H "Content-Type: application/json" \
  -d "{
    \"channel_id\": \"$CHANNEL_ID\",
    \"suggestions\": [
      {
        \"type\": \"security_vulnerability\",
        \"severity\": \"critical\",
        \"file_path\": \"src/auth.py\",
        \"line_start\": 42,
        \"code_snippet\": \"password = request.args.get('password')\",
        \"description\": \"Password exposed in URL parameters - critical security issue\"
      }
    ]
  }"
```

### Option 2: Using Python

```python
import asyncio
from bin.channel.examples.cursor_integration import CursorTunnelClient

async def test():
    # Initialize client
    client = CursorTunnelClient(
        base_url="http://localhost:8000",
        channel_id="your-channel-id"  # Get from /tunnel/channels
    )

    # Send a critical issue
    result = await client.send_suggestions([
        {
            "type": "bug_fix",
            "severity": "critical",
            "file_path": "src/app.py",
            "line_start": 10,
            "code_snippet": "user = None",
            "description": "Null pointer dereference - user never initialized"
        }
    ])

    print(f"Critical issues sent: {result['critical_count']}")
    print(f"Filtered out: {result['filtered_out']}")

asyncio.run(test())
```

## Understanding the Flow

```
Your Cursor IDE
      ↓
   [Send suggestion via API]
      ↓
  Suggestion Tunnel
      ↓
  Antigravity Filter ← (Blocks non-critical issues)
      ↓
  Suggestion Bin
      ↓
   Claude Code
```

## What Gets Through Antigravity?

✅ **Allowed (Critical)**
- Security vulnerabilities
- Runtime errors
- Breaking changes
- Logic errors
- Bugs causing data corruption

❌ **Blocked (Non-Critical)**
- Performance optimizations
- Code style improvements
- Refactoring suggestions
- Best practices
- Formatting

## Test Antigravity Filtering

```bash
# This will be BLOCKED (optimization)
curl -X POST http://localhost:8000/tunnel/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "your-channel-id",
    "suggestions": [{
      "type": "critical_refactor",
      "severity": "medium",
      "file_path": "src/utils.py",
      "line_start": 5,
      "code_snippet": "for i in range(len(arr)):",
      "description": "Use enumerate for better performance and readability"
    }]
  }'

# Response: {"status": "no_critical_issues", "filtered_out": 1}
```

```bash
# This will PASS (critical bug)
curl -X POST http://localhost:8000/tunnel/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "your-channel-id",
    "suggestions": [{
      "type": "bug_fix",
      "severity": "critical",
      "file_path": "src/payment.py",
      "line_start": 42,
      "code_snippet": "total = price * quantity",
      "description": "Integer overflow possible with large values causing payment calculation error"
    }]
  }'

# Response: {"status": "success", "critical_count": 1}
```

## View Results

```bash
# List all bins with critical issues
curl http://localhost:8000/tunnel/bins

# Get details of a specific bin
curl http://localhost:8000/tunnel/bins/{bin_id}

# Check tunnel statistics
curl http://localhost:8000/tunnel/stats
```

## Next Steps

1. **Integrate with Cursor IDE**
   - See [README.md](README.md#cursor-ide-integration) for integration options
   - Use file watcher, webhook, or direct API

2. **Configure Exclusions**
   - Edit [config.py](config.py) to exclude test files, build artifacts, etc.

3. **Customize Channels**
   - Create specialized channels for different issue types
   - Set up routing rules

4. **Connect to Claude Code**
   - Implement the Claude Code handler in [integration.py](integration.py)
   - Configure callbacks for your specific setup

## Troubleshooting

### Tunnel not loading
```bash
# Check if the router is imported correctly
tail -f logs/api.log | grep "Suggestion Tunnel"
```

### No issues passing through
- Check severity levels (must be HIGH or CRITICAL)
- Check suggestion type (must be critical type)
- Review Antigravity filter rules in [antigravity.py](antigravity.py)

### Channel not found
```bash
# List all channels to get valid IDs
curl http://localhost:8000/tunnel/channels
```

## Configuration

Edit `bin/channel/config.py` or set environment variables:

```bash
# Example .env file
TUNNEL_ENABLED=true
TUNNEL_LOG_LEVEL=INFO
ANTIGRAVITY_STRICT_MODE=true
ANTIGRAVITY_MIN_SEVERITY=HIGH
MAX_BIN_SIZE=100
```

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Look for the `suggestion-tunnel` tag.

## Support

See full documentation in [README.md](README.md)
