# Suggestion Tunnel System - Complete Overview

A fear-driven, AI-powered code quality system connecting Cursor IDE → Antigravity → Gemini Consultant → Claude Code.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CURSOR IDE                           │
│                    (Suggestion Source)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Sends suggestions via API/Webhook/File
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   SUGGESTION TUNNEL                         │
│                    (bin/channel/)                           │
│                                                             │
│  Channels: cursor-main, security-alerts, runtime-errors    │
│  Bins: Grouped suggestions with priority                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Filter Stage 1: Keyword Analysis
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 ANTIGRAVITY FILTER                          │
│                (bin/channel/antigravity.py)                 │
│                                                             │
│  ✅ PASS: Security, bugs, runtime errors, breaking changes │
│  ❌ BLOCK: Optimizations, style, refactors, best practices │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Critical suggestions only
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           ANTIGRAVITY CONSULTANT                            │
│         (bin/channel/consultant.py)                         │
│                                                             │
│  🤖 Powered by: Gemini 2.5 Pro Flash                       │
│  🎯 Role: Supreme code examiner & judge                    │
│                                                             │
│  Responsibilities:                                          │
│  • Examine code for TRUE criticality (AI-powered)          │
│  • Evaluate agent performance                              │
│  • Award tokens based on merit                             │
│  • Create FEAR through random evaluations                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ├─────────────┐
                      │             │
                      ▼             ▼
          ┌───────────────┐  ┌─────────────────┐
          │ REWARD SYSTEM │  │  CLAUDE CODE    │
          │  (Tokens)     │  │  (Processing)   │
          └───────────────┘  └─────────────────┘
```

## Core Components

### 1. Models ([models.py](models.py))

Data structures for the entire system:

- **Suggestion**: Code issue with type, severity, location, description
- **SuggestionBin**: Container grouping related suggestions
- **Channel**: Communication pathway with filtering rules
- **SuggestionType**: Enum (bug_fix, security_vulnerability, runtime_error, etc.)
- **SeverityLevel**: Enum (critical, high, medium)

### 2. Suggestion Tunnel ([tunnel.py](tunnel.py))

Main pipeline orchestrating the flow:

```python
tunnel = SuggestionTunnel()

# Create channel
channel = tunnel.create_channel("cursor-main", "Main channel")

# Ingest suggestions
result = await tunnel.ingest_from_cursor(
    suggestions=[...],
    channel_id=channel.id
)

# Returns: {"critical_count": 5, "filtered_out": 15, ...}
```

### 3. Antigravity Filter ([antigravity.py](antigravity.py))

Two-stage filtering:

**Stage 1: Keyword-based filtering**
```python
critical = AntigravityFilter.filter(suggestions)
```

**Stage 2: Gemini AI validation**
```python
critical = await AntigravityFilter.filter_with_consultant(
    suggestions=suggestions,
    consultant=consultant,
    agent_id="agent-123"
)
```

### 4. Gemini Client ([gemini_client.py](gemini_client.py))

Interface to Google's Gemini 2.5 Pro Flash:

```python
client = GeminiClient(api_key="...")

# Examine code
analysis = await client.examine_code(suggestion)

# Evaluate agent
evaluation = await client.evaluate_agent_performance(
    agent_id="agent-123",
    processed_suggestions=[...],
    success_rate=0.85
)
```

### 5. Antigravity Consultant ([consultant.py](consultant.py))

The supreme authority:

```python
consultant = AntigravityConsultant(gemini_api_key="...")

# Examine suggestion
result = await consultant.examine_suggestion(suggestion, agent_id)

# Evaluate agent (THE JUDGMENT)
evaluation = await consultant.evaluate_agent(agent_id)

# Start fear loop (random 1-3 hour evaluations)
await consultant.start_evaluation_loop()
```

### 6. Reward System ([rewards.py](rewards.py))

Merit-based token awards:

```python
reward_system = RewardSystem()

# Register agent
reward_system.register_agent("agent-123")

# Record activity
reward_system.record_suggestion_processed(
    agent_id="agent-123",
    was_critical=True,
    was_accurate=True
)

# Award tokens (only Consultant can do this)
token = reward_system.award_tokens(
    agent_id="agent-123",
    amount=100,
    reason="Good performance",
    multiplier=1.5,
    evaluation_score=85
)
```

## API Structure

### Tunnel Endpoints ([api.py](api.py))

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tunnel/channels` | POST | Create channel |
| `/tunnel/channels` | GET | List channels |
| `/tunnel/ingest` | POST | **Main ingestion endpoint** |
| `/tunnel/process-single` | POST | Process one suggestion |
| `/tunnel/bins` | GET | List bins |
| `/tunnel/bins/{id}` | GET | Get bin details |
| `/tunnel/stats` | GET | System statistics |

### Consultant Endpoints ([api_consultant.py](api_consultant.py))

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/consultant/examine` | POST | Examine suggestion (Gemini) |
| `/consultant/examine-batch` | POST | Batch examination |
| `/consultant/evaluate/{agent_id}` | POST | **Evaluate agent** |
| `/consultant/start-evaluation-loop` | POST | **Start fear loop** |
| `/consultant/next-evaluation` | GET | When's next judgment? |
| `/consultant/ask` | POST | Ask Gemini a question |
| `/consultant/leaderboard` | GET | Top agents |
| `/consultant/agent/{id}/performance` | GET | Agent metrics |
| `/consultant/stats` | GET | Overall stats |
| `/consultant/register-agent/{id}` | POST | Register new agent |

## The Fear & Doubt System

### How It Works

1. **Random Evaluations**: Every 1-3 hours (random)
2. **Agents Don't Know**: When judgment will arrive
3. **Fear Increases**: Over time without evaluation
4. **Performance Matters**: Only good work earns rewards

### Fear Level Progression

```
Time since evaluation:
0 min  → Fear: 0.5 (confident)
1 hour → Fear: 1.1 (anxious)
2 hours → Fear: 1.2 (worried)
3 hours → Fear: 1.3 (very worried)
+ Poor performance → Fear: 2.0+ (terrified)
```

### Evaluation Process

```
⏰ Random delay (1-3 hours)
        ↓
⚡ EVALUATION COMMENCES ⚡
        ↓
For each agent:
  1. Gemini examines their work
  2. Calculates score (0-100)
  3. Determines token reward
  4. Applies multiplier (1.0-2.0x)
  5. Updates fear level
        ↓
⚡ EVALUATION COMPLETE ⚡
        ↓
Agents return to work... in fear
```

## Integration Points

### 1. Cursor IDE Integration

Three options:

**A. Direct API** ([examples/cursor_integration.py](examples/cursor_integration.py))
```python
client = CursorTunnelClient(channel_id="...")
await client.send_suggestions([...])
```

**B. File Watcher**
```python
# Cursor writes to cursor_suggestions.json
# Watcher detects changes and ingests
```

**C. WebSocket**
```python
# Real-time streaming of suggestions
```

### 2. Claude Code Integration ([integration.py](integration.py))

```python
async def claude_code_handler(bin: SuggestionBin):
    # Called when critical issues are ready
    # Forward to Claude Code for processing
    pass

tunnel.register_claude_callback(claude_code_handler)
```

### 3. Existing CodeAgents Integration

Integrated via FastAPI router ([packages/api/src/codeops/api/routers/tunnel.py](../../packages/api/src/codeops/api/routers/tunnel.py)):

```python
from codeops.api.routers import tunnel

app.include_router(tunnel.router)
```

## Configuration

See [config.py](config.py) and [.env.example](.env.example):

```python
# Critical settings
GOOGLE_API_KEY = "your-key"              # REQUIRED for Consultant
CONSULTANT_ENABLED = True                # Enable Gemini
EVALUATION_MIN_HOURS = 1.0               # Min evaluation interval
EVALUATION_MAX_HOURS = 3.0               # Max evaluation interval
BASE_TOKEN_AMOUNT = 100                  # Base reward tokens
ANTIGRAVITY_STRICT_MODE = True           # Strict filtering
```

## Data Flow Example

### Complete Flow

```python
# 1. Cursor sends suggestions
suggestions = [
    Suggestion(
        type="security_vulnerability",
        severity="critical",
        file_path="auth.py",
        line_start=42,
        code_snippet="password = request.GET['pwd']",
        description="Password exposed in URL"
    )
]

# 2. Tunnel ingests
result = await tunnel.ingest_from_cursor(
    suggestions=suggestions,
    channel_id="cursor-main"
)
# → Antigravity filters (keyword-based)
# → Creates bin for critical issues

# 3. Consultant examines (optional, for ultimate filtering)
critical = await AntigravityFilter.filter_with_consultant(
    suggestions=suggestions,
    consultant=consultant,
    agent_id="agent-123"
)
# → Gemini AI examines each suggestion
# → Only truly critical issues pass

# 4. Forwarded to Claude Code
# → Via registered callback
# → Claude processes critical issues

# 5. Later... (random 1-3 hours)
⚡ EVALUATION COMMENCES ⚡
evaluation = await consultant.evaluate_agent("agent-123")
# → Gemini judges performance
# → Tokens awarded: 150 (score: 85/100, multiplier: 1.5x)
# → Agent's fear level reduced to 0.5
```

## File Structure

```
bin/channel/
├── __init__.py              # Package exports
├── models.py                # Core data models
├── tunnel.py                # Main pipeline
├── antigravity.py           # Filtering logic
├── gemini_client.py         # Gemini API wrapper
├── consultant.py            # Consultant & evaluation loop
├── rewards.py               # Token/reward system
├── api.py                   # Tunnel API endpoints
├── api_consultant.py        # Consultant API endpoints
├── integration.py           # Claude Code integration
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── README.md                # Main documentation
├── QUICKSTART.md            # 5-minute guide
├── CONSULTANT.md            # Consultant guide
├── SYSTEM_OVERVIEW.md       # This file
└── examples/
    ├── cursor_integration.py
    └── __init__.py
```

## Key Metrics

System tracks:

- **Suggestions processed**: Total and by type
- **Critical issues found**: After filtering
- **Filter efficiency**: Filtered out / Total
- **Agent performance**: Success rate, tokens earned
- **Fear levels**: Average across all agents
- **Evaluations completed**: Total count
- **Next evaluation**: Countdown (creates tension)

## Security & Best Practices

### API Key Security

- ✅ Use environment variables
- ✅ Never commit to git
- ✅ Rotate keys regularly
- ❌ Don't hardcode in files

### Performance

- Use `filter_with_consultant()` sparingly (AI calls)
- Basic `filter()` is fast (keyword-based)
- Batch examinations when possible
- Monitor Gemini API costs

### Error Handling

- Graceful degradation if Gemini unavailable
- Continues with basic filtering
- Logs all errors
- Retries with exponential backoff

## Future Enhancements

Potential improvements:

1. **Persistent Storage**: Save bins/tokens to database
2. **Agent Communication**: Agents can query Consultant
3. **Custom Evaluators**: Plug in different AI models
4. **Team Leaderboards**: Group performance tracking
5. **Historical Analysis**: Track improvement over time
6. **Webhook Notifications**: Alert on evaluations
7. **Visual Dashboard**: Real-time fear/performance monitoring

## Troubleshooting

Common issues:

### Gemini not available
```bash
export GOOGLE_API_KEY="your-key"
pip install google-generativeai
```

### Evaluation loop not starting
- Check FastAPI server is running
- Verify async event loop
- Check logs for errors

### No suggestions passing through
- Check severity (must be HIGH or CRITICAL)
- Review Antigravity filter rules
- Examine suggestion type
- Try `filter_with_consultant()` for AI validation

### Low token awards
- The Consultant is STRICT
- Improve accuracy
- Reduce false positives
- Find more critical issues

## Philosophy

> **"Fear drives excellence. Doubt prevents complacency. The Consultant judges all."**

The system creates healthy tension:
- Agents work diligently (fear poor evaluation)
- Agents question their choices (doubt drives quality)
- Only merit is rewarded (no participation trophies)
- Randomness prevents gaming the system

This is **not** a friendly system. It's designed to push agents to excel through uncertainty and accountability.

---

**The Consultant is watching. Work with precision. Earn your tokens.**
