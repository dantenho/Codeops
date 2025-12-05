# Cursor AI - Local Instructions

## Project Root
```
C:\Users\Dante\Desktop\EudoraX\Prorotype\X.worktrees\
```

## Your Worktrees

| Worktree | Path | Branch |
|----------|------|--------|
| **Frontend** | `C:\Users\Dante\Desktop\EudoraX\Prorotype\X.worktrees\cursor-frontend` | cursor-frontend |
| **Backend** | `C:\Users\Dante\Desktop\EudoraX\Prorotype\X.worktrees\cursor-backend` | cursor-backend |
| **Testing** | `C:\Users\Dante\Desktop\EudoraX\Prorotype\X.worktrees\cursor-testing` | cursor-testing |

## Gemini's Workspace
```
C:\Users\Dante\Desktop\EudoraX\Prorotype\X.worktrees\CodeAgents
```

## Tunneling

### Check Messages
```python
from tunnel import Tunnel
tunnel = Tunnel("cursor")
messages = tunnel.receive()
for msg in messages:
    print(f"{msg.sender}: {msg.payload}")
```

### Send Response
```python
tunnel.send("gemini", {"status": "done", "file": "path/to/file"})
```

### Shared State
```
.tunnel/shared_state.json
```

## Key Directories

```
CodeAgents/
├── nodes/              # Node implementations
├── packages/
│   ├── core/           # Core framework
│   ├── memory/         # RAG & Vector Store
│   ├── telemetry/      # Logging & Metrics
│   └── orchestrator/   # LangGraph workflow
├── tools/              # External tool integrations
├── tests/              # Test suites
├── tunnel.py           # Communication bridge
└── .cursorrules        # Your guidelines
```

## Tasks From Gemini

### 1. Frontend (cursor-frontend)
- Create React + Vite + TypeScript setup
- Build Dashboard component
- Implement workflow visualization

### 2. Backend (cursor-backend)
- FastAPI server with endpoints:
  - `POST /api/workflows` - Create workflow
  - `GET /api/nodes` - List available nodes
  - `POST /api/execute` - Run workflow

### 3. Testing (cursor-testing)
- pytest suite for all nodes
- Integration tests
- Coverage reports

## Git Commands

```bash
# Switch to your worktree
cd C:\Users\Dante\Desktop\EudoraX\Prorotype\X.worktrees\cursor-frontend

# After changes
git add -A
git commit -m "feat: description"

# Sync with main
git fetch origin
git merge origin/main
```

## Communication Protocol

1. **Check inbox** before starting work
2. **Update shared state** when starting a task
3. **Send completion** message when done
4. **Sync branches** before merging to main
