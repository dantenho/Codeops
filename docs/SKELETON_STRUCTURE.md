# Agent Skeleton Structure Documentation

**Agent:** Composer
**Timestamp:** 2025-12-03T15:00:00Z
**Operation:** [CREATE]

## Overview

The Agent Skeleton Structure provides a standardized directory hierarchy for organizing agent-specific code, training data, rules, methods, files, database schemas, and memory. This structure is automatically generated for each agent and organized by timestamp.

## Directory Structure

```
CodeAgents/ID/{AgentID}/{Timestamp}/
├── training/
│   ├── sessions/          # Training session data
│   ├── activities/        # Activity logs and results
│   └── progress.json      # Agent progress tracking
├── rules/
│   ├── protocols.md       # Protocol definitions and guidelines
│   ├── constraints.yaml   # Operational constraints and limits
│   └── guidelines.json    # JSON-formatted guidelines
├── methods/
│   ├── __init__.py        # Python package initialization
│   ├── core_methods.py    # Core functionality methods
│   └── utilities.py        # Utility functions
├── files/
│   ├── code/              # Agent-specific code files
│   ├── configs/           # Configuration files
│   └── artifacts/         # Generated artifacts
├── database/
│   ├── schema.sql         # Database schema definitions
│   ├── migrations/        # Database migration scripts
│   └── seeds/            # Seed data files
└── memory/
    ├── context/           # Contextual memory and conversations
    ├── knowledge/         # Extracted knowledge base
    └── reflections/      # Self-reflection and learning insights
```

## Subdirectory Purposes

### `training/`

Contains all training-related data and progress tracking.

- **`sessions/`**: Individual training session records
- **`activities/`**: Activity logs, results, and performance metrics
- **`progress.json`**: Current agent progress including level, XP, and session counts

**Example `progress.json`:**
```json
{
  "agent_id": "Composer",
  "timestamp": "2025-12-03T15-00-00Z",
  "level": 1,
  "xp": 0,
  "sessions_completed": 0,
  "created_at": "2025-12-03T15:00:00Z"
}
```

### `rules/`

Contains protocol definitions, constraints, and guidelines for agent behavior.

- **`protocols.md`**: Markdown documentation of protocols and standards
- **`constraints.yaml`**: YAML configuration for operational limits (token budgets, quality gates, performance thresholds)
- **`guidelines.json`**: JSON-formatted guidelines and best practices

**Example `constraints.yaml`:**
```yaml
constraints:
  token_budget:
    max_tokens: 100000
    warning_threshold: 80000

  quality_gates:
    min_quality_score: 70
    min_efficiency_score: 3.0

  performance:
    max_duration_ms: 30000
    timeout_seconds: 60
```

### `methods/`

Python module containing agent-specific methods and utilities.

- **`__init__.py`**: Package initialization file
- **`core_methods.py`**: Core functionality and primary methods
- **`utilities.py`**: Helper functions and utility methods

All methods follow Agents.MD protocol standards with comprehensive docstrings.

### `files/`

Storage for agent-specific files and artifacts.

- **`code/`**: Agent-specific code implementations
- **`configs/`**: Configuration files specific to this agent
- **`artifacts/`**: Generated files, outputs, and artifacts

### `database/`

Database schema and migration management.

- **`schema.sql`**: SQL schema definitions for agent data
- **`migrations/`**: Database migration scripts (versioned)
- **`seeds/`**: Seed data for initializing databases

**Example `schema.sql`:**
```sql
CREATE TABLE IF NOT EXISTS agent_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    status TEXT NOT NULL,
    metadata TEXT
);
```

### `memory/`

Memory storage organized by type.

- **`context/`**: Contextual memory, conversation history, and context snapshots
- **`knowledge/`**: Extracted knowledge, learned patterns, and knowledge graphs
- **`reflections/`**: Self-reflection logs, learning insights, and assessment reports

## Usage

### Creating Skeletons via CLI

```bash
# Create skeleton for a specific agent
training skeleton Composer

# Create skeleton with custom timestamp
training skeleton Composer --timestamp "2025-12-03T15-00-00Z"

# Create skeletons for all configured agents
training skeleton --all
```

### Creating Skeletons Programmatically

```python
from CodeAgents.core.skeleton_generator import create_skeleton_generator

# Create generator
generator = create_skeleton_generator()

# Create skeleton for single agent
path = generator.create_agent_skeleton("Composer")
print(f"Created at: {path}")

# Create with custom timestamp
path = generator.create_timestamped_structure(
    "Composer",
    "2025-12-03T15-00-00Z"
)

# Create for multiple agents
paths = generator.create_for_all_agents([
    "Composer",
    "ClaudeCode",
    "GrokIA"
])
```

### Integration with Bootstrap System

The skeleton generator is automatically integrated with the training bootstrap system:

```python
from CodeAgents.Training.src.training.bootstrap import create_bootstrap

bootstrap = create_bootstrap()

# Initialize agent (automatically creates skeleton)
results = bootstrap.initialize_all_agents(create_skeletons=True)

# Or create skeleton separately
path = bootstrap.create_agent_skeleton("Composer")
```

## Timestamp Format

Timestamps use ISO 8601 format optimized for directory names:

- **Format:** `YYYY-MM-DDTHH-MM-SSZ`
- **Example:** `2025-12-03T15-00-00Z`
- **Auto-generated:** Current UTC time if not specified

## File Naming Conventions

All files follow Agents.MD protocol standards:

- **Python files:** Include docstrings with operation tags, agent signature, and timestamp
- **JSON files:** Include `agent_id` and `timestamp` fields
- **Markdown files:** Include header with agent and timestamp information
- **SQL files:** Include comments with agent and creation timestamp

## Integration Points

### With Training System

- Skeleton creation is integrated into `TrainingSystemBootstrap.initialize_agent()`
- Progress data is stored in `training/progress.json`
- Session data is stored in `training/sessions/`

### With Telemetry System

- Compatible with existing `CodeAgents/ID/{AgentID}/logs/` structure
- Skeleton structure complements telemetry logging
- Error logs can reference skeleton paths

### With Memory System

- Memory service can use `memory/` directories for persistent storage
- Context memory stored in `memory/context/`
- Knowledge base stored in `memory/knowledge/`

## Best Practices

1. **One Skeleton Per Session**: Create a new timestamped skeleton for each major training session or operation
2. **Keep Structures Organized**: Use subdirectories appropriately for different file types
3. **Update Progress Regularly**: Keep `training/progress.json` updated after each session
4. **Document Changes**: Update `rules/protocols.md` when protocols change
5. **Version Control**: Commit skeleton structures to track agent evolution

## Examples

### Example: Creating and Using a Skeleton

```python
from CodeAgents.core.skeleton_generator import create_skeleton_generator
import json
from pathlib import Path

# Create skeleton
generator = create_skeleton_generator()
skeleton_path = generator.create_agent_skeleton("Composer")

# Update progress
progress_file = skeleton_path / "training" / "progress.json"
with open(progress_file, "r") as f:
    progress = json.load(f)

progress["level"] = 2
progress["xp"] = 500
progress["sessions_completed"] = 5

with open(progress_file, "w") as f:
    json.dump(progress, f, indent=2)

# Add a method
methods_file = skeleton_path / "methods" / "core_methods.py"
with open(methods_file, "a") as f:
    f.write("""
def process_training_session(session_data: dict) -> dict:
    \"\"\"
    [CREATE] Process a training session.

    Agent: Composer
    Timestamp: 2025-12-03T15:00:00Z
    \"\"\"
    # Implementation here
    return {"status": "processed"}
""")
```

## Troubleshooting

### Skeleton Generator Not Available

If you see "Skeleton generator not available":
1. Check that `CodeAgents/core/skeleton_generator.py` exists
2. Verify Python path includes `CodeAgents` directory
3. Check for import errors in the generator module

### Directory Creation Fails

If directory creation fails:
1. Check file system permissions
2. Verify base path exists and is writable
3. Ensure agent ID is valid (no special characters)

### Import Errors

If you encounter import errors:
1. Ensure `CodeAgents/core/` is in Python path
2. Check for circular import issues
3. Verify all dependencies are installed

## Related Documentation

- `Agents.MD` - Protocol standards and requirements
- `TRAINING_SYSTEM_ANALYSIS.md` - Training system architecture
- `ARCHITECTURE.md` - Overall system architecture

---

**Document Complete**
**Agent:** Composer
**Timestamp:** 2025-12-03T15:00:00Z
