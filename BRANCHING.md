# Branch Structure

## Overview

```
                    ┌─────────┐
                    │  main   │
                    │(Production)
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐     ┌─────────┐     ┌──────────┐
   │ agents  │     │ backend │     │ frontend │
   │workspace│     │workspace│     │workspace │
   └─────────┘     └─────────┘     └──────────┘
        │                │                │
        │                │                │
        └────────┬───────┴────────┬───────┘
                 │                │
            ┌────▼────┐      ┌────▼────┐
            │ database │      │ api-calls
            │ (shared) │      │ (shared)
            └──────────┘      └──────────┘
```

## Branch Details

### Workspace Branches

#### workspace/agents
- **Purpose**: Agent development and orchestration
- **Dependencies**: shared/database, shared/api-calls
- **Sync From**: shared/database, shared/api-calls
- **Directories**: agents/, nodes/
- **Functions**:
  - Agent orchestration
  - Memory integration
  - Vector store management

#### workspace/backend
- **Purpose**: Backend API and services
- **Dependencies**: shared/database, shared/api-calls
- **Sync From**: shared/database, shared/api-calls
- **Directories**: backend/, packages/
- **Functions**:
  - API endpoints
  - Data processing
  - Service integration

#### workspace/frontend
- **Purpose**: Frontend UI and components
- **Dependencies**: shared/api-calls
- **Sync From**: shared/api-calls
- **Directories**: frontend/, frontend_prototype/
- **Functions**:
  - UI components
  - State management
  - API integration

### Shared Branches

#### shared/database
- **Purpose**: Database schema, migrations, models
- **Syncs To**: workspace/agents, workspace/backend
- **Directories**: database/
- **Functions**:
  - Schema management
  - Migrations
  - Data models

#### shared/api-calls
- **Purpose**: API contracts, endpoints, middleware
- **Syncs To**: workspace/agents, workspace/backend, workspace/frontend
- **Directories**: hub/
- **Functions**:
  - Endpoint definitions
  - Authentication
  - Request validation

### Main Branch

#### main
- **Purpose**: Production-ready code
- **Merges From**: All workspace branches
- **Protection**: Requires reviews, fast-forward preferred
- **Versioning**: Follow semver tags (v1.0.0)

## Sync Rules

### When Database Changes
```
shared/database 
    ↓
workspace/agents (git merge shared/database)
    ↓
workspace/backend (git merge shared/database)
```

### When API Changes
```
shared/api-calls
    ↓
workspace/agents (git merge shared/api-calls)
    ↓
workspace/backend (git merge shared/api-calls)
    ↓
workspace/frontend (git merge shared/api-calls)
```

### When Releasing
```
workspace/agents ─┐
workspace/backend┼─→ main
workspace/frontend┘
```

## Commit Flow

1. **Feature Branch** → Feature work
   ```
   feature/add-vector-store
   ```

2. **Workspace Branch** → Feature merged, tested
   ```
   workspace/agents ← merge feature/add-vector-store
   ```

3. **Shared Branch** (if needed) → Shared resources
   ```
   shared/database ← merge feature/update-schema
   ```

4. **Main Branch** → Production release
   ```
   main ← merge workspace/agents
   ```

## Branch Naming Convention

```
<type>/<description>

Types:
- feature/   Add new functionality
- fix/       Bug fixes
- refactor/  Code restructuring
- docs/      Documentation
- test/      Test additions

Examples:
feature/add-vector-store-integration
fix/resolve-memory-leak
refactor/optimize-db-queries
docs/update-api-specification
test/add-agent-unit-tests
```

## Merge Strategy

| From | To | Strategy | Note |
|------|----|-----------|----|
| feature/* | workspace/* | Squash | Clean history |
| shared/* | workspace/* | Merge commit | Track sync point |
| workspace/* | main | Merge commit | Preserve branch history |

## Timeline Example

```
Day 1: Feature development
├─ git checkout workspace/agents
├─ git checkout -b feature/add-memory
└─ Work and commit

Day 2: Code review & merge
├─ git checkout workspace/agents
├─ git merge feature/add-memory
└─ Shared database updates sync automatically

Day 3: Testing
├─ All workspaces pulled shared changes
└─ Integration tests pass

Day 4: Release
├─ git checkout main
├─ git merge workspace/agents
├─ git merge workspace/backend
├─ git merge workspace/frontend
└─ git tag v1.2.0 && git push --tags
```

## Emergency Hotfixes

```bash
# For critical production bugs
git checkout main
git checkout -b hotfix/critical-bug-name
# Fix and test
git checkout main
git merge hotfix/critical-bug-name
git tag v1.2.1 (patch version)

# Then backport to workspaces
git checkout workspace/agents
git merge main
```
