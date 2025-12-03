# Create Agent Skeleton - Quick Instructions

## CLI Method (Easiest)

```bash
# Create skeleton for an agent
training skeleton Composer

# Create with custom timestamp
training skeleton Composer --timestamp "2025-12-03T15-00-00Z"

# Create for all agents
training skeleton --all
```

## Python Method

```python
from CodeAgents.core.skeleton_generator import create_skeleton_generator

generator = create_skeleton_generator()
path = generator.create_agent_skeleton("Composer")
print(f"Created at: {path}")
```

## What Gets Created

```
CodeAgents/ID/{AgentID}/{Timestamp}/
├── training/     # Progress and sessions
├── rules/        # Protocols and constraints
├── methods/      # Python code
├── files/        # Code, configs, artifacts
├── database/     # Schema and migrations
└── memory/       # Context, knowledge, reflections
```

## Notes

- Timestamp auto-generated if not provided (format: `YYYY-MM-DDTHH-MM-SSZ`)
- All placeholder files created automatically
- Follows Agents.MD protocol standards

