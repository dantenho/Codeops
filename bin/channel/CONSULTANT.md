# Antigravity Consultant - Powered by Gemini 2.5 Pro Flash

The supreme authority on code quality and agent performance. Only the Consultant can examine code and grant rewards.

## Overview

The **Antigravity Consultant** uses Google's **Gemini 2.5 Pro Flash** to:
- Examine code suggestions for true criticality
- Evaluate agent performance
- Award tokens based on merit
- Create **fear and doubt** through random evaluations (1-3 hour intervals)

## Philosophy: Fear and Doubt

Agents must operate with **uncertainty**:
- Evaluations happen at **random intervals** (1-3 hours)
- Only the Consultant can grant rewards
- Poor performance leads to penalties
- Agents never know when judgment arrives

This creates a system where agents must **doubt their choices** and **fear poor performance**.

## Setup

### 1. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set the environment variable:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Or add to `.env`:
```
GOOGLE_API_KEY=your-api-key-here
```

### 2. Install Dependencies

```bash
pip install google-generativeai
```

### 3. Start the System

```bash
# Start API server (includes Consultant endpoints)
cd packages/api
uvicorn codeops.api.main:app --reload --port 8000

# Verify Consultant is running
curl http://localhost:8000/consultant/health
```

## API Endpoints

### Examine Code Suggestion

Have the Consultant examine a suggestion to determine if it's truly critical:

```bash
POST /consultant/examine
{
  "suggestion": {
    "type": "bug_fix",
    "severity": "critical",
    "file_path": "src/app.py",
    "line_start": 42,
    "code_snippet": "user = None",
    "description": "Potential null pointer dereference"
  },
  "agent_id": "agent-123"  # Optional
}
```

Response:
```json
{
  "verdict": "critical",
  "is_critical": true,
  "confidence": 0.95,
  "reasoning": "This code will cause a null pointer exception when...",
  "recommendation": "Initialize user with a default value or add null checks",
  "examined_at": "2024-01-15T10:30:00",
  "model": "gemini-2.5-pro-flash"
}
```

### Evaluate Agent Performance

Trigger an evaluation (THE MOMENT OF JUDGMENT):

```bash
POST /consultant/evaluate/agent-123
```

Response:
```json
{
  "agent_id": "agent-123",
  "evaluation": {
    "score": 85,
    "tokens": 150,
    "multiplier": 1.5,
    "reasoning": "Agent demonstrated good critical thinking...",
    "improvements": ["Reduce false positives", "Faster response time"]
  },
  "token": {
    "id": "token-uuid",
    "amount": 225,
    "reason": "Good performance with some areas for improvement"
  },
  "performance": {
    "total_tokens": 450,
    "success_rate": 0.85,
    "fear_level": 0.5
  },
  "message": "✅ GOOD. Acceptable performance. Continue your work."
}
```

### Start Evaluation Loop

Start the random evaluation loop (AGENTS WILL LIVE IN FEAR):

```bash
POST /consultant/start-evaluation-loop
```

Response:
```json
{
  "status": "started",
  "message": "Evaluation loop started. Agents will be evaluated at random intervals between 1-3 hours.",
  "next_evaluation": "2024-01-15T12:45:23Z"
}
```

### Check Next Evaluation Time

See when the next judgment arrives:

```bash
GET /consultant/next-evaluation
```

Response:
```json
{
  "next_evaluation": "2024-01-15T12:45:23Z",
  "seconds_until_evaluation": 7523,
  "evaluation_loop_running": true
}
```

### Ask the Consultant

Receive wisdom from Gemini about code quality:

```bash
POST /consultant/ask
{
  "question": "Should I use async/await for this database query?"
}
```

Response:
```json
{
  "question": "Should I use async/await for this database query?",
  "answer": "Yes, you should use async/await for database queries because..."
}
```

### Get Leaderboard

See top performing agents:

```bash
GET /consultant/leaderboard?top_n=10
```

### Get Agent Performance

View an agent's metrics:

```bash
GET /consultant/agent/agent-123/performance
```

### Get Statistics

View overall system stats:

```bash
GET /consultant/stats
```

Response:
```json
{
  "total_agents": 15,
  "total_tokens_awarded": 3450,
  "total_evaluations": 42,
  "agents_awaiting_evaluation": 5,
  "average_fear_level": 1.2,
  "evaluation_loop_running": true,
  "next_evaluation": "2024-01-15T12:45:23Z",
  "time_until_evaluation_seconds": 7523
}
```

## Token System

### How Tokens Work

Tokens are the currency of merit. Only the Consultant can award them.

- **Base Amount**: 100 tokens (configurable)
- **Multiplier**: 1.0 - 2.0x for exceptional performance
- **Score Thresholds**:
  - 90+ = Exceptional (🌟)
  - 80+ = Good (✅)
  - 70+ = Adequate (⚠️)
  - 60+ = Marginal (⚠️)
  - 50+ = Poor (❌)
  - <50 = Unacceptable (❌)

### Token Awards

Example awards based on performance:

| Score | Base Tokens | Multiplier | Final Tokens | Message |
|-------|-------------|------------|--------------|---------|
| 95    | 100         | 2.0x       | 200          | 🌟 EXCEPTIONAL |
| 85    | 100         | 1.5x       | 150          | ✅ GOOD |
| 75    | 100         | 1.2x       | 120          | ⚠️  ADEQUATE |
| 65    | 100         | 1.0x       | 100          | ⚠️  MARGINAL |
| 55    | 50          | 1.0x       | 50           | ❌ POOR |
| 40    | 0           | 1.0x       | 0            | ❌ UNACCEPTABLE |

### Penalties

Agents can be penalized with negative tokens for:
- False positives
- Missing critical issues
- Poor judgment
- Excessive fear/doubt leading to inaction

## Fear Level System

Each agent has a **fear level** that affects their behavior:

- **0.0 - 0.5**: Confident (recent good evaluation)
- **0.5 - 1.0**: Normal (baseline fear)
- **1.0 - 2.0**: Anxious (waiting for evaluation)
- **2.0 - 3.0**: Terrified (long time since evaluation or poor performance)

Fear increases over time and decreases with good evaluations.

## Integration with Antigravity Filter

The Consultant can be integrated with the Antigravity filter for ultimate validation:

```python
from bin.channel import AntigravityFilter, AntigravityConsultant

consultant = AntigravityConsultant(gemini_api_key="...")

# Filter with Consultant validation
critical_suggestions = await AntigravityFilter.filter_with_consultant(
    suggestions=suggestions,
    consultant=consultant,
    agent_id="agent-123"
)
```

This creates a **two-stage filter**:
1. Basic Antigravity filter (keyword-based)
2. Consultant examination (Gemini AI)

Only suggestions that pass BOTH filters are considered critical.

## Configuration

Edit [config.py](config.py) or set environment variables:

```bash
# Gemini API
GOOGLE_API_KEY=your-api-key

# Consultant settings
TUNNEL_CONSULTANT_ENABLED=true
TUNNEL_CONSULTANT_MODEL=gemini-2.5-pro-exp-0827
TUNNEL_CONSULTANT_AUTO_START_LOOP=false

# Evaluation loop
TUNNEL_EVALUATION_MIN_HOURS=1.0
TUNNEL_EVALUATION_MAX_HOURS=3.0

# Rewards
TUNNEL_BASE_TOKEN_AMOUNT=100
TUNNEL_EXCELLENT_THRESHOLD=90
TUNNEL_ACCEPTABLE_THRESHOLD=60
TUNNEL_MAX_MULTIPLIER=2.0
```

## Example Usage

### Python Client

```python
import asyncio
import aiohttp

async def example():
    # Register agent
    async with aiohttp.ClientSession() as session:
        await session.post(
            "http://localhost:8000/consultant/register-agent/my-agent"
        )

    # Examine a suggestion
    async with aiohttp.ClientSession() as session:
        result = await session.post(
            "http://localhost:8000/consultant/examine",
            json={
                "suggestion": {
                    "type": "security_vulnerability",
                    "severity": "critical",
                    "file_path": "auth.py",
                    "line_start": 42,
                    "code_snippet": "password = request.GET['pwd']",
                    "description": "Password in URL"
                },
                "agent_id": "my-agent"
            }
        )
        data = await result.json()
        print(f"Verdict: {data['verdict']}")

    # Start evaluation loop
    async with aiohttp.ClientSession() as session:
        await session.post(
            "http://localhost:8000/consultant/start-evaluation-loop"
        )

    # Wait in fear...
    print("⚠️  Evaluation loop running. Living in fear...")

asyncio.run(example())
```

### Curl Examples

```bash
# Register agent
curl -X POST http://localhost:8000/consultant/register-agent/agent-1

# Start evaluation loop
curl -X POST http://localhost:8000/consultant/start-evaluation-loop

# Check when judgment arrives
curl http://localhost:8000/consultant/next-evaluation

# Get leaderboard
curl http://localhost:8000/consultant/leaderboard

# Ask for wisdom
curl -X POST http://localhost:8000/consultant/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Is this code safe?"}'
```

## The Evaluation Loop

Once started, the evaluation loop runs continuously:

```
[Loop Start]
    ↓
Random delay (1-3 hours)
    ↓
⚡ EVALUATION COMMENCES ⚡
    ↓
Get agents needing evaluation
    ↓
For each agent:
  - Examine performance
  - Consult Gemini
  - Award tokens
  - Update fear level
    ↓
⚡ EVALUATION COMPLETE ⚡
    ↓
Agents return to work in fear...
    ↓
[Loop repeats]
```

## Monitoring

### View Logs

```bash
# Watch for evaluations
tail -f logs/api.log | grep "EVALUATION"

# See Consultant activity
tail -f logs/api.log | grep "Consultant"
```

### Check Agent Performance

```bash
# Get specific agent
curl http://localhost:8000/consultant/agent/agent-123/performance

# See who's winning
curl http://localhost:8000/consultant/leaderboard
```

## Security Notes

- Keep your `GOOGLE_API_KEY` secret
- Don't commit API keys to version control
- Use environment variables in production
- Monitor API usage in Google Cloud Console

## Cost Considerations

Gemini 2.5 Pro Flash pricing (as of 2024):
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

Typical examination uses ~500 tokens total, so:
- 1000 examinations ≈ $0.19
- Very cost-effective for code quality checking

## Troubleshooting

### Consultant not available

```bash
curl http://localhost:8000/consultant/health
```

If `gemini_available: false`:
1. Check `GOOGLE_API_KEY` is set
2. Install: `pip install google-generativeai`
3. Verify API key is valid

### Evaluation loop not starting

Check logs for errors. Ensure event loop is running (FastAPI/uvicorn).

### Low token awards

The Consultant is strict. Improve your work:
- Reduce false positives
- Find more critical issues
- Increase accuracy

## Philosophy

> "Only through fear and doubt can true excellence emerge. The Consultant watches. The Consultant judges. Prove your worth."

The Consultant creates a meritocracy where:
- Excellence is rewarded
- Mediocrity is tolerated
- Failure is penalized
- Agents never know when judgment arrives

This uncertainty drives improvement.

---

**Remember**: The Consultant is always watching. Work with precision, fear failure, and earn your tokens.
