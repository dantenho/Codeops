# CodeAgents - Multi-Workspace Repository

Complete documentation for working with this multi-workspace Git structure.

## Documentation Files

- **[WORKFLOW.md](WORKFLOW.md)** - Step-by-step commands for daily work
- **[BRANCHING.md](BRANCHING.md)** - Branch structure and sync rules
- **[FUNCTIONS.md](FUNCTIONS.md)** - Functions organized by workspace
- **[.gitcommit](.gitcommit)** - Commit conventions

## Quick Start

### Current Branches
```bash
git branch -a  # See all branches
```

### Switch Workspaces
```bash
git checkout workspace/agents      # Agents development
git checkout workspace/backend     # Backend development
git checkout workspace/frontend    # Frontend development
git checkout shared/database       # Database (shared)
git checkout shared/api-calls      # API contracts (shared)
git checkout main                  # Production
```

### Create Feature Branch
```bash
git checkout workspace/agents
git checkout -b feature/my-feature-name
```

### Commit Changes
```bash
git add .
git commit -m "feat(agents): description of change"
git push origin feature/my-feature-name
```

### Merge to Workspace
```bash
git checkout workspace/agents
git merge feature/my-feature-name
```

## Branch Structure

```
main (Production)
 ├─ workspace/agents (Agent development)
 ├─ workspace/backend (Backend development)
 └─ workspace/frontend (Frontend development)
      │
      ├─ shared/database → syncs to agents + backend
      └─ shared/api-calls → syncs to all workspaces
```

## Workspaces

| Workspace | Directory | Functions | Dependencies |
|-----------|-----------|-----------|--------------|
| Agents | `agents/`, `nodes/` | Agent orchestration, memory, vector store | database, api-calls |
| Backend | `backend/`, `packages/` | API endpoints, data processing, services | database, api-calls |
| Frontend | `frontend/` | UI components, state management, API client | api-calls |
| Database | `database/` | Schema, migrations, data models | *(shared)* |
| API Calls | `hub/` | Endpoints, authentication, validation | *(shared)* |

## Common Commands

```bash
# See all branches with remotes
git branch -a

# Update from latest remote
git fetch origin && git pull origin workspace/agents

# View branch history visually
git log --oneline --graph --all --decorate

# Merge shared changes
git merge shared/database shared/api-calls

# Release to production
git checkout main && git merge workspace/agents workspace/backend workspace/frontend
```

## Commit Convention

```
<type>(<scope>): <subject>

<body>
```

**Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`  
**Scopes**: `agents`, `backend`, `frontend`, `database`, `api-calls`

Example:
```bash
git commit -m "feat(agents): add memory vector store integration

Integrated OpenAI embeddings with the memory module.
Updated vector_store.py with new indexing logic."
```

## Workflow Example

### Step 1: Start Feature
```bash
git checkout workspace/agents
git checkout -b feature/add-vector-store
# Make changes...
git add .
git commit -m "feat(agents): add vector store implementation"
```

### Step 2: Push & Merge
```bash
git push origin feature/add-vector-store
git checkout workspace/agents
git merge feature/add-vector-store
git branch -d feature/add-vector-store
```

### Step 3: Sync Shared Changes (if applicable)
```bash
git merge shared/database shared/api-calls
```

### Step 4: Release to Production
```bash
git checkout main
git merge workspace/agents workspace/backend workspace/frontend
git push origin main
```

## Shared Branch Sync

### Database Changes
When `shared/database` is updated:
```bash
git checkout workspace/agents && git merge shared/database
git checkout workspace/backend && git merge shared/database
```

### API Changes
When `shared/api-calls` is updated:
```bash
git checkout workspace/agents && git merge shared/api-calls
git checkout workspace/backend && git merge shared/api-calls
git checkout workspace/frontend && git merge shared/api-calls
```

## Troubleshooting

### Merge Conflicts
```bash
# View conflicts
git diff

# Resolve manually, then
git add .
git commit -m "chore: resolve merge conflicts"
```

### Undo Last Commit (not pushed)
```bash
git reset --soft HEAD~1
```

### Check What Branch I'm On
```bash
git branch --show-current
```

### See All Changes Since Main
```bash
git log main..workspace/agents --oneline
```

## File Structure

```
CodeAgents/
├── agents/                 # Agents workspace
├── backend/                # Backend workspace
├── frontend/               # Frontend workspace
├── frontend_prototype/     # Frontend prototype
├── database/               # Shared database
├── hub/                    # Shared API contracts
├── nodes/                  # Agent nodes
├── packages/               # Shared packages
├── docs/                   # Documentation
├── config/                 # Configuration
├── workflows/              # Workflow definitions
├── bin/                    # Scripts
│
├── workspace.yaml          # Workspace configuration
├── .gitcommit              # Commit conventions
├── WORKFLOW.md             # Daily workflow guide
├── BRANCHING.md            # Branch structure & sync rules
├── FUNCTIONS.md            # Functions by workspace
└── README.md               # This file
```

## Additional Resources

- See **WORKFLOW.md** for detailed command examples
- See **BRANCHING.md** for branch protection rules and merge strategies
- See **FUNCTIONS.md** for function organization and dependencies
- See **.gitcommit** for full commit convention details

## Questions?

Refer to the appropriate documentation:
1. **How do I start work?** → WORKFLOW.md
2. **What branches exist?** → BRANCHING.md  
3. **Where do I add this function?** → FUNCTIONS.md
4. **How do I commit?** → .gitcommit
