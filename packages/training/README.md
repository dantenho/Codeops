# Agent Training System (ATS) - SkeletalMind

Periodic training, memorization, and skill reinforcement for AI coding agents.

## Overview

The Agent Training System implements a comprehensive training framework with:

- **Structured Learning**: 5-level skeletal structure from foundations to mastery
- **Spaced Repetition**: SM-2 algorithm for long-term retention
- **Gamification**: XP, levels, badges, and streaks
- **Multi-Agent Support**: Tracks progress for all agents (GrokIA, GeminiFlash25, GeminiPro25, GeminiPro30, Jules, ClaudeCode, Composer)
- **Scheduled Training**: Daily (30min), Weekly (3hr), Monthly (6hr), Quarterly (8hr)

## Installation

```bash
cd CodeAgents/Training

# Create virtual environment with UV
uv venv

# Activate environment
# On Windows:
.venv\Scripts\activate
# On Unix/Mac:
source .venv/bin/activate

# Install package
uv pip install -e ".[dev]"
```

## Quick Start

```bash
# Initialize agent profile
training init ClaudeCode

# Start daily training session
training start ClaudeCode --type daily

# Review flashcards
training flashcards ClaudeCode --limit 20

# Check progress
training progress ClaudeCode --detailed

# View leaderboard
training leaderboard --top 10

# Generate report
training report ClaudeCode --period week
```

## CLI Commands

The `training` Typer CLI now provides a complete workflow for managing agent drills:

| Command | Purpose |
| --- | --- |
| `training init <agent>` | Create or reset an agent profile. Add `--force` to overwrite existing progress. |
| `training start <agent> --type daily|weekly|market_analysis` | Launches a structured session, simulates activity results, records XP, and logs token metrics. |
| `training progress <agent> [--detailed]` | Displays current level, streaks, XP breakdown, and aggregated token stats. |
| `training recommend <agent>` | Suggests the next session type based on weaknesses and efficiency data. |
| `training flashcards [--deck python_syntax_level1] [--limit 5]` | Lists decks or previews the specified deck while logging daily activity. |
| `training leaderboard [--top 10]` | Ranks agents by total XP for quick comparisons. |
| `training report <agent> [--output reports/agent.json]` | Generates a JSON snapshot containing XP, streaks, token stats, and recommendations. |
| `training simulate <agent> [--iterations 10]` | Runs repeated solo sessions, publishes token usage totals, and surfaces optimization suggestions. |

All commands automatically feed `MemoryService`, `TokenTracker`, and telemetry logging so CI/CD workflows can audit training runs.

## Architecture

```
CodeAgents/Training/
├── src/training/          # Core package
│   ├── models/            # Pydantic data models
│   ├── services/          # Business logic
│   ├── utils/             # Helper functions
│   └── cli.py             # Command-line interface
├── config/                # YAML configurations
├── SkeletalStructure/     # 25 training modules (5 levels × 5 topics)
├── Flashcards/            # Spaced repetition decks
├── Progress/              # Agent progress tracking
└── Assessments/           # Checkpoints and certifications
```

## Training Levels

1. **Foundations**: Syntax, data types, control flow, functions, error handling
2. **Intermediate**: OOP basics, data structures, algorithms, file I/O, testing
3. **Advanced**: Design patterns, concurrency, networking, databases, security
4. **Expert**: Architecture, distributed systems, performance, compiler theory, ML integration
5. **Master**: System design, language internals, novel algorithms, research implementation, cross-domain

## Integration

- **Agents.MD Protocol**: Enforces code standards and telemetry
- **AMES Evaluation**: Provides performance metrics and feedback
- **Telemetry System**: Logs all training activities
- **Threndia Branch**: `https://github.com/Eudora-IA/Threndia` serves as the market-analysis & training extension of EudoraX. Scraped/API intel is normalized through the Threndia integration service, tagged as “mutual cooperation – Eudora-X Pylorix,” and logged under `CodeAgents/EudoraX-Pylorix/`.

## Development

```bash
# Run tests
pytest

# Type checking
mypy src/training

# Code formatting
black src/training
ruff check src/training
```

## Documentation

See the following documents for complete specifications:

- `AGENT_TRAINING_SYSTEM.md`: Full system specification
- `CLAUDE_CODE_TODO_TRAINING_SYSTEM.md`: Implementation roadmap
- `AGENT_METRICS_EVALUATION.md`: Evaluation integration

---

*Managed by Agents.MD Protocol v3.0*
