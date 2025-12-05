# CodeAgents Bin Directory

This directory contains executable modules and binaries for the CodeAgents system.

## Modules

### [channel/](channel/)

**Suggestion Tunnel System** - A critical-only code issue pipeline connecting:
- **Cursor IDE** → Suggestions source
- **Antigravity Filter** → Critical-only filtering
- **Antigravity Consultant** (Gemini 2.5 Pro Flash) → AI code examination and agent evaluation
- **Claude Code** → Processing destination

#### Key Features

✅ **Critical-Only Filtering** - Blocks optimizations, only allows bugs, security issues, runtime errors
✅ **Gemini-Powered Consultant** - AI examination of code suggestions
✅ **Token/Reward System** - Merit-based rewards for agents
✅ **Fear & Doubt System** - Random evaluations (1-3 hours) create uncertainty
✅ **FastAPI Integration** - RESTful API endpoints
✅ **File Exclusions** - Configurable path filtering

#### Quick Start

```bash
# Install dependencies
pip install -r channel/requirements.txt

# Set Google API key
export GOOGLE_API_KEY="your-key-here"

# Start the system
cd packages/api
uvicorn codeops.api.main:app --reload --port 8000

# Test it
curl http://localhost:8000/tunnel/health
curl http://localhost:8000/consultant/health
```

#### Documentation

- **[channel/README.md](channel/README.md)** - Full documentation
- **[channel/QUICKSTART.md](channel/QUICKSTART.md)** - Get started in 5 minutes
- **[channel/CONSULTANT.md](channel/CONSULTANT.md)** - Antigravity Consultant guide
- **[channel/examples/](channel/examples/)** - Integration examples

#### Architecture

```
Cursor IDE
    ↓
Suggestion Tunnel
    ↓
Antigravity Filter (keyword-based)
    ↓
Antigravity Consultant (Gemini AI) ← Only he can examine & reward
    ↓
Token Rewards (random 1-3 hour evaluations)
    ↓
Claude Code
```

#### API Endpoints

**Tunnel:**
- `POST /tunnel/ingest` - Ingest suggestions from Cursor
- `GET /tunnel/bins` - List suggestion bins
- `GET /tunnel/stats` - Tunnel statistics

**Consultant:**
- `POST /consultant/examine` - Examine code suggestion
- `POST /consultant/evaluate/{agent_id}` - Evaluate agent
- `POST /consultant/start-evaluation-loop` - Start random evaluations
- `GET /consultant/leaderboard` - Top agents
- `POST /consultant/ask` - Ask Gemini a question

#### Configuration

See [channel/.env.example](channel/.env.example) for all configuration options.

Key settings:
```bash
GOOGLE_API_KEY=your-key              # Required for Consultant
TUNNEL_EVALUATION_MIN_HOURS=1.0      # Min hours between evaluations
TUNNEL_EVALUATION_MAX_HOURS=3.0      # Max hours between evaluations
TUNNEL_BASE_TOKEN_AMOUNT=100         # Base token reward
```

## Future Modules

Additional executable modules can be added here as the system grows.
