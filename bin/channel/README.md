# Suggestion Tunnel System

A critical-only code issue pipeline connecting **Cursor IDE → Antigravity → Claude Code**.

## Architecture

```
┌─────────────┐
│ Cursor IDE  │
│ (Source)    │
└──────┬──────┘
       │
       │ Sends suggestions
       │
       ▼
┌─────────────────────┐
│  Suggestion Tunnel  │
│     (Pipeline)      │
└──────┬──────────────┘
       │
       │ Filters through
       │
       ▼
┌─────────────────────┐
│    Antigravity      │
│  (Critical Filter)  │
│                     │
│ ✓ Security issues   │
│ ✓ Runtime errors    │
│ ✓ Breaking changes  │
│ ✗ Optimizations     │
│ ✗ Style improvements│
└──────┬──────────────┘
       │
       │ Only critical issues pass
       │
       ▼
┌─────────────────────┐
│ Suggestion Bins     │
│  (Organized)        │
└──────┬──────────────┘
       │
       │ Forwarded to
       │
       ▼
┌─────────────────────┐
│   Claude Code       │
│  (Processing)       │
└─────────────────────┘
```

## Core Concepts

### 1. **Suggestion**
A code issue detected by Cursor IDE with:
- Type (bug_fix, security_vulnerability, runtime_error, etc.)
- Severity (critical, high, medium)
- File location and code snippet
- Description and suggested fix

### 2. **Antigravity Filter**
A critical-only filter that:
- ✅ **Allows**: Security vulnerabilities, runtime errors, bugs, breaking changes
- ❌ **Blocks**: Optimizations, style improvements, refactors, performance tweaks

### 3. **Channel**
Communication pathway with filter criteria:
- `cursor-ide-main`: Main channel for all critical suggestions
- `security-alerts`: Security vulnerabilities only
- `runtime-errors`: Runtime and breaking change errors

### 4. **Bin**
Container for grouped suggestions:
- Auto-prioritized by severity
- Tracks processing status
- Organized by channel

### 5. **Tunnel**
The main pipeline orchestrating the flow.

## API Endpoints

### Create a Channel
```bash
POST /tunnel/channels
{
  "name": "my-channel",
  "description": "Channel for critical issues",
  "filter_criteria": {}
}
```

### Ingest Suggestions (Main Endpoint)
```bash
POST /tunnel/ingest
{
  "suggestions": [
    {
      "type": "bug_fix",
      "severity": "critical",
      "file_path": "src/app.py",
      "line_start": 42,
      "code_snippet": "user = None",
      "description": "Null pointer dereference - user is never initialized"
    }
  ],
  "channel_id": "channel-uuid",
  "bin_name": "optional-bin-name"
}
```

### Process Single Suggestion
```bash
POST /tunnel/process-single
{
  "suggestion": { ... },
  "channel_id": "channel-uuid"
}
```

### List Bins
```bash
GET /tunnel/bins
GET /tunnel/bins?channel_id=channel-uuid
```

### Get Bin Details
```bash
GET /tunnel/bins/{bin_id}
```

### Get Statistics
```bash
GET /tunnel/stats
```

## Cursor IDE Integration

### Option 1: Direct API Integration

Create a Cursor IDE extension that sends suggestions:

```typescript
// cursor-extension/src/suggestionTunnel.ts
async function sendToClaude(suggestions: Suggestion[]) {
  const response = await fetch('http://localhost:8000/tunnel/ingest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      suggestions,
      channel_id: 'cursor-main-channel-id'
    })
  });

  const result = await response.json();
  console.log(`Sent ${result.critical_count} critical issues to Claude Code`);
  console.log(`Filtered out ${result.filtered_out} non-critical suggestions`);
}
```

### Option 2: File Watcher

Monitor a suggestions file that Cursor IDE writes to:

```python
# bin/channel/cursor_watcher.py
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CursorSuggestionHandler(FileSystemEventHandler):
    def __init__(self, tunnel, channel_id):
        self.tunnel = tunnel
        self.channel_id = channel_id

    def on_modified(self, event):
        if event.src_path.endswith('cursor_suggestions.json'):
            suggestions = load_suggestions(event.src_path)
            asyncio.run(
                self.tunnel.ingest_from_cursor(
                    suggestions,
                    self.channel_id
                )
            )
```

### Option 3: WebSocket Integration

For real-time suggestions:

```python
# Add to api.py
@router.websocket("/ws/suggestions")
async def websocket_endpoint(websocket: WebSocket, channel_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        suggestion = Suggestion(**data)
        result = await tunnel.process_suggestion_sync(
            suggestion,
            channel_id
        )
        await websocket.send_json(result)
```

## Antigravity Filter Rules

### ✅ **Passes Through** (Critical)
- Security vulnerabilities (SQL injection, XSS, etc.)
- Runtime errors (null pointer, type errors)
- Breaking changes
- Logic errors causing incorrect behavior
- Bugs with data corruption risk

### ❌ **Filtered Out** (Non-Critical)
- Performance optimizations
- Code style improvements
- Refactoring suggestions
- Best practice recommendations
- Formatting issues
- Convention updates

## Usage Example

```python
from bin.channel import SuggestionTunnel, Suggestion, SuggestionType, SeverityLevel

# Initialize tunnel
tunnel = SuggestionTunnel()

# Create channel
channel = tunnel.create_channel(
    name="cursor-main",
    description="Main channel for Cursor IDE"
)

# Register Claude Code callback
async def send_to_claude(bin):
    print(f"Sending {len(bin.suggestions)} critical issues to Claude Code")
    # Your Claude Code integration here

tunnel.register_claude_callback(send_to_claude)

# Ingest suggestions
suggestions = [
    Suggestion(
        type=SuggestionType.SECURITY_VULNERABILITY,
        severity=SeverityLevel.CRITICAL,
        file_path="app.py",
        line_start=42,
        code_snippet="sql = f'SELECT * FROM users WHERE id={user_id}'",
        description="SQL injection vulnerability detected"
    ),
    Suggestion(
        type=SuggestionType.BUG_FIX,
        severity=SeverityLevel.HIGH,
        file_path="utils.py",
        line_start=15,
        code_snippet="return data[index]",
        description="Potential index out of bounds error"
    )
]

result = await tunnel.ingest_from_cursor(suggestions, channel.id)
print(result)
# Output: {"status": "success", "critical_count": 2, ...}
```

## File Exclusions

To exclude files from the tunnel, add to channel filter criteria:

```python
channel = tunnel.create_channel(
    name="filtered-channel",
    description="Channel with exclusions",
    filter_criteria={
        "exclude_paths": [
            "tests/**",
            "**/*.test.py",
            "node_modules/**",
            "build/**",
            "dist/**"
        ]
    }
)
```

Or filter in the suggestion itself:

```python
suggestion = Suggestion(
    ...,
    metadata={
        "exclude": False,
        "tags": ["production-code"]
    }
)
```

## Integration with CodeAgents

The tunnel integrates with the existing CodeAgents infrastructure:

1. **FastAPI Router**: [packages/api/src/codeops/api/routers/tunnel.py](../../packages/api/src/codeops/api/routers/tunnel.py)
2. **Main API**: [packages/api/src/codeops/api/main.py](../../packages/api/src/codeops/api/main.py)
3. **Celery Tasks**: Can trigger async processing via existing worker
4. **Vector DB**: Can store suggestion history in Chroma DB

## Starting the Tunnel

```bash
# Start the FastAPI server (includes tunnel endpoints)
cd packages/api
uvicorn codeops.api.main:app --reload --port 8000

# Test the tunnel
curl http://localhost:8000/tunnel/health
```

## Default Channels

On startup, three default channels are created:

1. **cursor-ide-main**: Main channel for all critical suggestions
2. **security-alerts**: Security vulnerabilities only
3. **runtime-errors**: Runtime and breaking change errors

## Statistics

Get real-time tunnel statistics:

```bash
GET /tunnel/stats

Response:
{
  "channels": 3,
  "bins": 15,
  "active_bins": 8,
  "total_suggestions": 127,
  "critical_suggestions": 43,
  "is_active": true
}
```

## License

Part of the CodeAgents project.
