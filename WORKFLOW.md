# CodeAgents Workflow

## Quick Reference

### Switch to Workspace
```bash
git checkout workspace/agents      # Agents
git checkout workspace/backend     # Backend
git checkout workspace/frontend    # Frontend
```

### Create Feature Branch
```bash
git checkout workspace/agents
git checkout -b feature/my-feature-name
```

### Work on Shared Resources
```bash
git checkout shared/database       # Database changes
git checkout shared/api-calls      # API changes
```

## Complete Workflow

### 1. Start New Feature (Workspace)

```bash
# Switch to your workspace
git checkout workspace/agents

# Create feature branch
git checkout -b feature/add-memory-vector-store

# Make changes, commit
git add .
git commit -m "feat(agents): add memory vector store integration"

# Push
git push origin feature/add-memory-vector-store
```

### 2. Merge to Workspace

```bash
# Switch to workspace
git checkout workspace/agents

# Merge feature branch
git merge feature/add-memory-vector-store

# Delete feature branch (optional)
git branch -d feature/add-memory-vector-store
```

### 3. Shared Changes (Database/API)

#### Database Changes
```bash
git checkout shared/database
git checkout -b feature/add-users-table

# Make changes
git add .
git commit -m "feat(database): add users table schema"
git push origin feature/add-users-table

# Merge to shared/database
git checkout shared/database
git merge feature/add-users-table

# Sync to dependent workspaces
git checkout workspace/agents
git merge shared/database

git checkout workspace/backend
git merge shared/database
```

#### API Changes
```bash
git checkout shared/api-calls
git checkout -b feature/add-auth-endpoint

# Make changes
git add .
git commit -m "feat(api-calls): add auth endpoint contract"
git push origin feature/add-auth-endpoint

# Merge to shared/api-calls
git checkout shared/api-calls
git merge feature/add-auth-endpoint

# Sync to all workspaces
git checkout workspace/agents && git merge shared/api-calls
git checkout workspace/backend && git merge shared/api-calls
git checkout workspace/frontend && git merge shared/api-calls
```

### 4. Release to Production

```bash
# Ensure all workspaces are up-to-date with shared branches
git checkout workspace/agents && git merge shared/database shared/api-calls
git checkout workspace/backend && git merge shared/database shared/api-calls
git checkout workspace/frontend && git merge shared/api-calls

# Merge all to main
git checkout main
git merge workspace/agents
git merge workspace/backend
git merge workspace/frontend

# Push to production
git push origin main
```

## Commit Convention

Format:
```
<type>(<scope>): <subject>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

Scopes: `agents`, `backend`, `frontend`, `database`, `api-calls`

Examples:
```bash
git commit -m "feat(agents): add memory vector store"
git commit -m "fix(backend): resolve api timeout issue"
git commit -m "refactor(database): optimize schema queries"
git commit -m "docs(api-calls): update endpoint documentation"
```

## Branch Protection Rules

| Branch | Who Can Push | Requires Review |
|--------|-------------|-----------------|
| main | Admin only | Yes (2 approvals) |
| workspace/* | Team | No |
| shared/* | Team | No |
| feature/* | Author | No |

## Common Commands

```bash
# See all branches and remotes
git branch -a

# Check current branch
git branch --show-current

# Update from remote
git fetch origin
git pull origin workspace/agents

# View branch relationships
git log --oneline --graph --all --decorate

# Stash work temporarily
git stash
git stash pop

# Discard changes
git restore .
```

## Troubleshooting

### Merge Conflicts
```bash
# View conflicts
git diff

# Resolve conflicts manually, then
git add .
git commit -m "chore: resolve merge conflicts"
git push origin branch-name
```

### Sync Out of Date Branch
```bash
# Pull latest from shared branch
git checkout workspace/agents
git pull origin shared/database
```

### Undo Last Commit (Not Pushed)
```bash
git reset --soft HEAD~1
```

### Undo Pushed Commit (Careful!)
```bash
git revert HEAD
git push origin branch-name
```
