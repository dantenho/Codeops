# Quick Start Guide - Agent Training System

Get started with the Agent Training System in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- UV package manager ([installation guide](https://github.com/astral-sh/uv))
- Git (for version control)

## Installation

### Step 1: Navigate to Training Directory

```bash
cd CodeAgents/Training
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment with UV
uv venv

# Activate the environment
# On Windows:
.venv\Scripts\activate

# On Unix/Mac:
source .venv/bin/activate
```

### Step 3: Install Package

```bash
# Install in development mode with all dependencies
uv pip install -e ".[dev]"
```

## Quick Start

### Initialize Your Agent Profile

```bash
training init ClaudeCode
```

Expected output:
```
Initializing agent: ClaudeCode
Display Name: Claude Code
Specializations: precise_coding, documentation
Primary Languages: python, typescript, go
Learning Style: structured

Agent ClaudeCode initialized successfully!
```

### View Configuration

```bash
training config --show
```

### Check Progress

```bash
training progress ClaudeCode
```

### Get Training Recommendation

```bash
training recommend ClaudeCode
```

## Your First Training Session

### Option 1: Daily Training (30 minutes)

```bash
training start ClaudeCode --type daily
```

This will launch a 30-minute training session with:
- 5 minutes warmup (flashcard review)
- 20 minutes main practice (exercises + code review)
- 5 minutes cooldown (reflection)

### Option 2: Focused Practice

```bash
training start ClaudeCode --focus python,error_handling
```

This creates a custom session focused on specific skills.

### Option 3: Flashcard Review Only

```bash
training flashcards ClaudeCode --limit 20
```

Review up to 20 flashcards using spaced repetition.

## Working with Skeletal Exercises

Skeletal exercises are partially completed code files with TODOs for you to fill in.

### Find an Exercise

```bash
ls SkeletalStructure/Level_01_Foundations/
```

### Complete an Exercise

1. Open the exercise file:
   ```bash
   # Example: Python variables exercise
   code SkeletalStructure/Level_01_Foundations/01_syntax/variables.py
   ```

2. Fill in the TODOs

3. Run the tests:
   ```bash
   python SkeletalStructure/Level_01_Foundations/01_syntax/variables.py
   ```

## Understanding the System

### XP and Levels

- **Level 1 (Foundations)**: 0 XP
- **Level 2 (Intermediate)**: 500 XP
- **Level 3 (Advanced)**: 1,500 XP
- **Level 4 (Expert)**: 4,000 XP
- **Level 5 (Master)**: 10,000 XP

### Earning XP

- Complete exercise: 50 XP (×difficulty)
- Perfect score bonus: +25 XP
- First attempt bonus: +15 XP
- Review flashcard: 5 XP
- Daily streak: 10 XP per day

### Training Schedule

| Type | Duration | Frequency |
|------|----------|-----------|
| Daily | 30 min | Every day |
| Weekly | 3 hours | Every Saturday |
| Monthly | 6 hours | Last Saturday of month |
| Quarterly | 8 hours | Every 3 months |

## Spaced Repetition

The system uses the SM-2 algorithm for flashcard scheduling:

- **New cards**: Start with 1-minute intervals
- **Learning cards**: Graduate to daily reviews
- **Mature cards**: Intervals grow exponentially (1d → 4d → 10d → 25d...)

### Flashcard Ratings

When reviewing flashcards, rate your recall:

- **Again (0)**: Complete failure - resets the card
- **Hard (1)**: Correct but difficult - smaller interval increase
- **Good (2)**: Correct with effort - normal interval increase
- **Easy (3)**: Effortless recall - larger interval increase

## Progress Tracking

### View Detailed Progress

```bash
training progress ClaudeCode --detailed
```

### Generate Report

```bash
# Weekly report
training report ClaudeCode --period week

# Monthly report
training report ClaudeCode --period month

# Save to file
training report ClaudeCode --output my_report.txt
```

### View Leaderboard

```bash
training leaderboard --top 10
```

## Development Workflow

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_models.py
```

### Code Quality

```bash
# Format code
black src/training

# Lint code
ruff check src/training

# Type check
mypy src/training
```

## Integration with AMES

All training sessions are automatically logged to the Agent Metrics & Evaluation System (AMES):

- **Logs**: `CodeAgents/ClaudeCode/logs/`
- **Analysis**: `CodeAgents/ClaudeCode/analysis/`

View AMES metrics:

```python
from training.utils import AMESIntegration

ames = AMESIntegration(agent_id="ClaudeCode")
metrics = ames.get_performance_metrics()
print(metrics)
```

## Customization

### Modify Training Schedule

Edit `config/training_schedule.yaml`:

```yaml
schedule:
  daily:
    duration_minutes: 45  # Change from 30 to 45
```

### Adjust Difficulty

Edit `config/difficulty_curves.yaml`:

```yaml
xp_rewards:
  exercise_completion:
    base: 75  # Increase from 50 to 75
```

### Configure Spaced Repetition

Edit `config/spaced_repetition.yaml`:

```yaml
daily_limits:
  new_cards: 30  # Increase from 20 to 30
```

## Troubleshooting

### Command Not Found

If `training` command is not found after installation:

```bash
# Reinstall in editable mode
uv pip install -e .

# Or use python module syntax
python -m training.cli init ClaudeCode
```

### Import Errors

Make sure you've activated the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# Unix/Mac
source .venv/bin/activate
```

### Configuration Errors

Validate configuration:

```bash
training config --show
```

If errors appear, check YAML syntax in `config/*.yaml` files.

## Next Steps

1. **Complete Daily Training**: Build a streak!
2. **Explore Skeletal Exercises**: Work through Level 1
3. **Review Flashcards**: Build long-term retention
4. **Track Progress**: Monitor your improvement
5. **Level Up**: Reach Level 2 (500 XP)

## Resources

- **Full Documentation**: See `AGENT_TRAINING_SYSTEM.md`
- **Implementation Guide**: See `CLAUDE_CODE_TODO_TRAINING_SYSTEM.md`
- **AMES Integration**: See `AGENT_METRICS_EVALUATION.md`
- **Protocol**: See `Agents.MD`

## Support

For issues or questions:

1. Check this quickstart guide
2. Review the main documentation
3. Examine the example code in `tests/`
4. Inspect configuration files in `config/`

---

**Happy Training! 🚀**

*Remember: Consistency beats intensity. Daily practice is the key to mastery.*
