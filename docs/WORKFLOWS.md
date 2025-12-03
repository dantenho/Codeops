# GitHub Workflows Documentation

## Overview

EudoraX Prototype uses **GitHub Actions** to automate multi-agent compliance validation, ensuring consistent code quality and adherence to the agent protocol defined in `Agents.MD`.

## Workflow Architecture

### Automated CI/CD Pipeline

```
Pull Request / Push
        │
        ├──▶ Agent Detection
        │     └─ Identify which agent made changes
        │
        ├──▶ Documentation Validation
        │     ├─ Docstring coverage check (70%+ required)
        │     ├─ Docstring format validation (Google style)
        │     ├─ Operation tag verification
        │     └─ Agent signature check
        │
        ├──▶ Code Quality Checks
        │     ├─ Ruff (linting)
        │     ├─ Black (formatting)
        │     ├─ isort (import sorting)
        │     └─ MyPy (type checking)
        │
        ├──▶ Telemetry Validation
        │     └─ JSON schema verification
        │
        └──▶ Compliance Report
              └─ Summary with pass/fail status
```

---

## Workflows

### 1. Agent Validation Workflow

**File**: `.github/workflows/agent-validation.yml`

**Purpose**: Validates that all code changes comply with the multi-agent protocol.

**Triggers**:
- Pull requests to `main`, `develop`, or `staging` branches
- Pushes to `main` or `develop` branches
- Only for code files: `*.py`, `*.js`, `*.ts`, `*.go`, `*.rs`

**Jobs**:

#### Job 1: Detect Agent
Identifies which agent made the changes based on:
- Branch name pattern: `agent/{AgentName}/{feature}`
- Commit message pattern: `[AgentName]`

**Output**: Agent name and telemetry file existence

#### Job 2: Documentation Validation
Ensures comprehensive documentation:

**Checks**:
- **Docstring Coverage**: Minimum 90% using `interrogate`
- **Docstring Format**: Google/NumPy conventions using `pydocstyle`
- **Operation Tags**: Files must have `[CREATE]`, `[REFACTOR]`, `[DEBUG]`, or `[MODIFY]`
- **Agent Signatures**: Files must include `Agent:` comment

**Example of Compliant Code**:
```python
# [CREATE] New database client implementation
# Agent: Antigravity
# Timestamp: 2025-12-03T05:13:37Z

class DatabaseClient:
    """Client for database operations.

    This client provides a unified interface for interacting with
    multiple database backends including ChromaDB and PostgreSQL.

    Attributes:
        connection: Active database connection
        config: Configuration dictionary

    Example:
        >>> client = DatabaseClient(config)
        >>> client.connect()
        >>> results = client.query("SELECT * FROM images")
    """

    def __init__(self, config: dict):
        """Initialize database client.

        Args:
            config: Configuration dictionary with connection parameters
        """
        self.config = config
```

#### Job 3: Code Quality
Runs automated linting and formatting checks:

**Tools**:
- **Ruff** (0.1.9+): Fast Python linter
- **Black** (23.12.0+): Code formatter
- **isort** (5.13.0+): Import sorter
- **MyPy** (1.7.0+): Static type checker (warning only)

**Example** `.ruff.toml`:
```toml
[lint]
select = ["E", "F", "W", "I", "N"]
ignore = ["E501"]  # Line too long (Black handles this)

[format]
quote-style = "double"
indent-style = "space"
```

#### Job 4: Telemetry Validation
Validates agent telemetry logs against JSON schemas:

**Operation Schema**:
```json
{
  "type": "object",
  "required": ["agent", "timestamp", "operation", "target", "status"],
  "properties": {
    "agent": {"type": "string"},
    "timestamp": {"type": "string", "format": "date-time"},
    "operation": {"type": "string"},
    "target": {
      "type": "object",
      "properties": {
        "file": {"type": "string"},
        "function": {"type": "string"},
        "lines": {"type": "array"}
      }
    },
    "status": {"type": "string", "enum": ["SUCCESS", "FAILURE", "PENDING"]}
  }
}
```

**Error Schema**:
```json
{
  "type": "object",
  "required": ["agent", "timestamp", "error_type", "message", "severity"],
  "properties": {
    "agent": {"type": "string"},
    "timestamp": {"type": "string"},
    "error_type": {"type": "string"},
    "message": {"type": "string"},
    "severity": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]}
  }
}
```

#### Job 5: Compliance Report
Generates summary report visible in GitHub Actions:

**Example Output**:
```markdown
## 🤖 Agent Compliance Report

| Check | Status |
|-------|--------|
| Agent Detected | `Antigravity` |
| Documentation | ✅ Pass |
| Code Quality | ✅ Pass |
| Telemetry | ✅ Pass (15 files validated) |

---
*Validated against Agents.MD protocol v3.0*
```

---

### 2. Branch Sync Workflow

**File**: `.github/workflows/branch-sync.yml`

**Purpose**: Automatically synchronize changes between branches

**Triggers**:
- Push to `develop` branch
- Manual workflow dispatch

**Actions**:
1. Checkout all branches
2. Identify changes in `develop`
3. Create PRs to merge into feature branches
4. Auto-merge if tests pass

---

### 3. Merge Orchestrator

**File**: `.github/workflows/merge-orchestrator.yml`

**Purpose**: Coordinate complex multi-branch merges

**Triggers**:
- PR labeled with `auto-merge`
- Scheduled (daily at midnight UTC)

**Actions**:
1. Validate all checks passed
2. Check for merge conflicts
3. Auto-merge if clean
4. Notify on failures

---

### 4. Telemetry Collector

**File**: `.github/workflows/telemetry-collector.yml`

**Purpose**: Aggregate agent telemetry data

**Triggers**:
- Daily schedule
- Manual workflow dispatch

**Actions**:
1. Collect all agent logs
2. Generate statistics:
   - Operations per agent
   - Success/failure rates
   - Most modified files
   - Average response time
3. Create summary report
4. Upload to artifact storage

**Example Report**:
```markdown
# Agent Activity Report - 2025-12-03

## Summary
- **Total Operations**: 127
- **Success Rate**: 94.5%
- **Active Agents**: 5

## Per-Agent Statistics

| Agent | Operations | Success | Failure | Avg Time |
|-------|-----------|---------|---------|----------|
| Antigravity | 45 | 43 | 2 | 2.3s |
| ClaudeCode | 38 | 37 | 1 | 3.1s |
| GeminiFlash25 | 25 | 24 | 1 | 1.8s |
| GeminiPro25 | 15 | 15 | 0 | 4.2s |
| GrokIA | 4 | 4 | 0 | 2.9s |

## Most Modified Files
1. `tools/Pylorix/modules/database_tester.py` (12 edits)
2. `CodeAgents/Training/chroma_db/schema.py` (8 edits)
3. `backend/main.py` (6 edits)
```

---

## Development Workflow

### Creating Compliant Pull Requests

#### 1. Branch Naming Convention

**Pattern**: `agent/{AgentName}/{feature-description}`

**Examples**:
```bash
git checkout -b agent/Antigravity/add-postgres-support
git checkout -b agent/ClaudeCode/refactor-database-client
git checkout -b agent/GeminiFlash25/fix-image-upscaling
```

#### 2. Commit Message Format

**Pattern**: `[AgentName] {type}: {description}`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Examples**:
```bash
git commit -m "[Antigravity] feat: add PostgreSQL database client"
git commit -m "[ClaudeCode] docs: update database migration guide"
git commit -m "[GeminiFlash25] fix: resolve CLIP embedding dimension mismatch"
```

#### 3. Code Requirements Checklist

Before pushing:
- [ ] All new code has docstrings (Google style)
- [ ] Docstring coverage ≥ 70%
- [ ] Operation tags present: `[CREATE]`, `[REFACTOR]`, etc.
- [ ] Agent signature in file comments
- [ ] Code formatted with Black
- [ ] Imports sorted with isort
- [ ] No Ruff linting errors
- [ ] Telemetry log created (if applicable)

#### 4. Local Pre-Commit Checks

**Install pre-commit hooks**:
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

**`.pre-commit-config.yaml`** (create in project root):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pycqa/pydocstyle
    rev: 6.3.0
    hooks:
      - id: pydocstyle
        args: [--convention=google]
```

**Run manually**:
```bash
# Format code
black .
isort .

# Check linting
ruff check . --fix

# Check docstrings
pydocstyle --convention=google tools/Pylorix/

# Check coverage
interrogate -v -i --fail-under=70 tools/Pylorix/
```

---

## Troubleshooting Workflow Failures

### "Docstring coverage below 90%"

**Solution**:
```bash
# Check which files need docstrings
interrogate -v -i tools/Pylorix/

# Add docstrings to flagged files
# Focus on public functions and classes
```

### "Missing operation tag"

**Solution**:
Add operation tag to file header:
```python
# [CREATE] New feature implementation
# Or: [REFACTOR], [DEBUG], [MODIFY]
```

### "Black formatting check failed"

**Solution**:
```bash
# Auto-format all files
black .

# Commit formatted files
git add .
git commit -m "chore: apply Black formatting"
```

### "Ruff linting errors"

**Solution**:
```bash
# Show errors
ruff check .

# Auto-fix where possible
ruff check . --fix

# Review remaining errors and fix manually
```

### "Telemetry schema validation failed"

**Solution**:
Ensure your telemetry JSON matches the required schema:
```json
{
  "agent": "Antigravity",
  "timestamp": "2025-12-03T05:13:37Z",
  "operation": "CREATE",
  "target": {
    "file": "tools/Pylorix/modules/new_module.py",
    "function": "new_function",
    "lines": [1, 50]
  },
  "status": "SUCCESS"
}
```

---

## Manual Workflow Triggers

### Trigger Agent Validation Manually

```bash
# Via GitHub CLI
gh workflow run agent-validation.yml

# Via GitHub UI
# Actions → Agent Compliance Validation → Run workflow
```

### Trigger Telemetry Collection

```bash
gh workflow run telemetry-collector.yml
```

---

## Workflow Permissions

GitHub Actions requires specific permissions:

**`.github/workflows/agent-validation.yml`**:
```yaml
permissions:
  contents: read       # Read repository
  pull-requests: write # Comment on PRs
  checks: write        # Create check runs
  statuses: write      # Update status checks
```

---

## Best Practices

### 1. Small, Focused PRs
- Each PR should address one feature or bug
- Easier to review and validate
- Faster CI/CD execution

### 2. Write Descriptive Commit Messages
```bash
# Good
git commit -m "[Antigravity] feat: add ChromaDB batch operations support

Implements batch insert and query operations for ChromaDB to improve
performance when handling multiple image embeddings.

Closes #123"

# Bad
git commit -m "fixed stuff"
```

### 3. Keep Branches Updated
```bash
# Regularly sync with main
git checkout agent/Antigravity/my-feature
git fetch origin
git rebase origin/main
```

### 4. Address CI Failures Promptly
- Don't ignore red checks
- Fix failures before requesting review
- Use draft PRs for work-in-progress

### 5. Use Meaningful Branch Names
```bash
# Good
agent/Antigravity/add-supabase-integration
agent/ClaudeCode/refactor-vector-db-client

# Bad
agent/Antigravity/fix
agent/ClaudeCode/temp
```

---

## Advanced Configuration

### Custom Workflow Variables

Add to repository secrets (Settings → Secrets):

```yaml
env:
  PYTHON_VERSION: ${{ vars.PYTHON_VERSION || '3.12' }}
  MIN_COVERAGE: ${{ vars.MIN_DOCSTRING_COVERAGE || '70' }}
```

### Conditional Job Execution

```yaml
jobs:
  validate-telemetry:
    if: needs.detect-agent.outputs.has_telemetry == 'true'
    # Only run if telemetry files exist
```

### Matrix Testing

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest, windows-latest, macos-latest]

steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
```

---

## Monitoring Workflow Health

### View Workflow Runs

```bash
# List recent runs
gh run list --workflow=agent-validation.yml

# View specific run
gh run view 12345678

# Download logs
gh run download 12345678
```

### Workflow Metrics

Check in GitHub:
- **Actions** tab → **Agent Compliance Validation**
- Success rate over time
- Average execution time
- Most common failures

---

**Last Updated**: 2025-12-03
**For Agent Protocol Details**: See [Agents.MD](../Agents.MD)
**For Contribution Guidelines**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
