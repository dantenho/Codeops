# Contributing to EudoraX Prototype

Thank you for your interest in contributing to EudoraX Prototype! This project follows a **multi-agent development protocol** where different AI systems collaborate on code development.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Agent Protocol](#agent-protocol)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

---

## Code of Conduct

### Core Principles

1. **Respectful Collaboration**: Agents and humans work together professionally
2. **Quality First**: All code must meet established standards
3. **Transparent Communication**: Operations are logged and traceable
4. **Continuous Improvement**: Learn from telemetry and feedback

---

## Getting Started

### Prerequisites

- **Python 3.10+** (3.12 recommended)
- **Git** for version control
- **GitHub Account** with repository access
- **Code Editor** (VS Code recommended)

### Initial Setup

1. **Fork and Clone**:
```bash
git clone https://github.com/Eudora-IA/Prototype.git
cd Prototype
```

2. **Create Virtual Environment**:
```bash
# Using UV (recommended)
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/macOS

# Or using standard venv
python -m venv .venv
.venv\Scripts\activate
```

3. **Install Dependencies**:
```bash
uv pip install -r tools/Pylorix/requirements.txt
uv pip install -r backend/requirements.txt

# Install development tools
uv pip install ruff black isort mypy pydocstyle interrogate pre-commit
```

4. **Install Pre-commit Hooks**:
```bash
pre-commit install
```

---

## Agent Protocol

All code changes must follow the protocol defined in **[Agents.MD](Agents.MD)**.

### Operation Tags

Every file modification must include an operation tag:

| Tag | Usage |
|-----|-------|
| `[CREATE]` | New file or major feature |
| `[REFACTOR]` | Code restructuring without behavior change |
| `[DEBUG]` | Bug fixes and error resolution |
| `[MODIFY]` | Minor updates and enhancements |

### Agent Signatures

Include agent information in file headers:

```python
# [CREATE] Database client for multi-backend support
# Agent: Antigravity
# Timestamp: 2025-12-03T05:13:37Z

"""Module for database operations across multiple backends."""
```

### Telemetry Logging

If you're an AI agent, log operations to `CodeAgents/{AgentName}/logs/`:

**Operation Log Format**:
```json
{
  "agent": "AgentName",
  "timestamp": "2025-12-03T05:13:37Z",
  "operation": "CREATE",
  "target": {
    "file": "path/to/file.py",
    "function": "function_name",
    "lines": [1, 100]
  },
  "status": "SUCCESS",
  "metadata": {
    "changed_lines": 100,
    "tests_added": 5
  }
}
```

**Error Log Format**:
```json
{
  "agent": "AgentName",
  "timestamp": "2025-12-03T05:13:37Z",
  "error_type": "ImportError",
  "message": "Module 'chromadb' not found",
  "severity": "HIGH",
  "stack_trace": "...",
  "resolution": "Install chromadb via pip"
}
```

---

## Development Workflow

### 1. Create Feature Branch

**Branch Naming**: `agent/{AgentName}/{feature-description}`

```bash
# For AI agents
git checkout -b agent/Antigravity/add-postgres-client

# For human contributors (use your GitHub username)
git checkout -b contributor/yourusername/feature-name
```

### 2. Make Changes

Follow all code standards (see below).

### 3. Local Testing

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

# Run tests
pytest tests/
```

### 4. Commit Changes

**Commit Message Format**: `[AgentName] type: description`

```bash
git add .
git commit -m "[Antigravity] feat: add PostgreSQL database client

Implements connection pooling and async query support for PostgreSQL.
Includes comprehensive error handling and logging.

Closes #45"
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### 5. Push and Create PR

```bash
git push origin agent/Antigravity/add-postgres-client
```

Then create a Pull Request on GitHub.

---

## Code Standards

### Python Code Quality

We enforce strict code quality standards:

#### 1. Formatting (Black)

**Configuration** (automatic via `pyproject.toml`):
```toml
[tool.black]
line-length = 88
target-version = ['py312']
```

**Usage**:
```bash
black .  # Format all files
black tools/Pylorix/  # Format specific directory
```

#### 2. Linting (Ruff)

**Configuration** (`.ruff.toml`):
```toml
line-length = 88
select = ["E", "F", "W", "I", "N", "UP", "B", "C90"]
ignore = ["E501"]  # Black handles line length

[per-file-ignores]
"__init__.py" = ["F401"]  # Unused imports OK in __init__
```

**Usage**:
```bash
ruff check .  # Check all files
ruff check . --fix  # Auto-fix where possible
```

#### 3. Import Sorting (isort)

**Configuration** (`.isort.cfg`):
```ini
[settings]
profile = black
line_length = 88
```

**Usage**:
```bash
isort .  # Sort all imports
```

#### 4. Type Checking (MyPy)

**Configuration** (`mypy.ini`):
```ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
ignore_missing_imports = True
```

**Usage**:
```bash
mypy tools/Pylorix/  # Type check
```

### Documentation Standards

#### Docstring Requirements

- **Minimum Coverage**: 70% (target 90%+)
- **Style**: Google docstring format
- **Required For**: All public modules, classes, functions

**Example**:
```python
def process_image(image_path: str, model: str = "FLUX.2-dev") -> dict:
    """Process an image using the specified model.

    Loads an image from disk, applies the specified generative model,
    and returns the processed result with metadata.

    Args:
        image_path: Absolute path to the input image file
        model: Name of the model to use (default: "FLUX.2-dev")

    Returns:
        Dictionary containing:
            - 'result': Processed image as PIL.Image
            - 'metadata': Generation parameters used
            - 'timestamp': Processing timestamp

    Raises:
        FileNotFoundError: If image_path doesn't exist
        ValueError: If model is not supported

    Example:
        >>> result = process_image("/path/to/img.png", "FLUX.2-dev")
        >>> result['result'].save("output.png")
    """
    # Implementation
```

#### Check Docstring Coverage

```bash
# Verbose output showing missing docstrings
interrogate -v -i tools/Pylorix/

# Fail if below threshold
interrogate -v -i --fail-under=70 tools/Pylorix/
```

---

## Pull Request Process

### PR Checklist

Before submitting, ensure:

- [ ] Code follows Black formatting
- [ ] No Ruff linting errors
- [ ] Imports sorted with isort
- [ ] Docstring coverage ≥ 70%
- [ ] All docstrings use Google format
- [ ] Operation tags present in modified files
- [ ] Agent signature in file headers
- [ ] Tests added for new features
- [ ] Tests pass locally
- [ ] Telemetry logs created (if AI agent)
- [ ] Commit messages follow format
- [ ] Branch name follows convention

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature (CREATE)
- [ ] Bug fix (DEBUG)
- [ ] Refactoring (REFACTOR)
- [ ] Documentation (MODIFY)

## Agent Information
- **Agent**: Antigravity
- **Timestamp**: 2025-12-03T05:13:37Z
- **Telemetry Logs**: Yes/No

## Testing
- [ ] Local tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Documentation
- [ ] Docstrings added/updated
- [ ] README updated if needed
- [ ] CHANGELOG updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No new warnings introduced
```

### Review Process

1. **Automated Checks** (GitHub Actions):
   - Agent detection
   - Documentation validation
   - Code quality checks
   - Telemetry validation

2. **Code Review**:
   - At least one approval required
   - Address all comments
   - Keep PR updated with main branch

3. **Merge**:
   - Auto-merge if all checks pass
   - Manual merge for complex changes

---

## Testing Requirements

### Unit Tests

**Location**: `tests/` directory

**Framework**: pytest

**Example**:
```python
# tests/test_database_client.py
import pytest
from modules.database_client import DatabaseClient

def test_database_connection():
    """Test database connection establishment."""
    client = DatabaseClient(config={"type": "chromadb"})
    assert client.connect() == True

def test_query_execution():
    """Test basic query execution."""
    client = DatabaseClient(config={"type": "chromadb"})
    client.connect()
    results = client.query("SELECT * FROM images LIMIT 10")
    assert len(results) <= 10
```

**Running Tests**:
```bash
# All tests
pytest

# Specific file
pytest tests/test_database_client.py

# With coverage
pytest --cov=tools/Pylorix --cov-report=html

# Verbose output
pytest -v
```

### Integration Tests

For features that interact with external services:

```python
@pytest.mark.integration
def test_supabase_connection():
    """Test Supabase database connection."""
    # Only run if SUPABASE_URL is set
    if not os.getenv("SUPABASE_URL"):
        pytest.skip("Supabase credentials not configured")

    client = SupabaseClient()
    assert client.health_check() == True
```

**Run Integration Tests**:
```bash
pytest -m integration
```

---

## Documentation

### Required Documentation

When adding new features:

1. **Inline Comments**: For complex logic
2. **Docstrings**: For all public APIs
3. **README**: Update if adding new tool/feature
4. **ARCHITECTURE.md**: Update if changing structure
5. **DATABASE.md**: Update if adding new database support
6. **Examples**: Add usage examples

### Documentation Style

- **Clear and Concise**: Avoid unnecessary verbosity
- **Examples**: Include code examples
- **Link Related Docs**: Reference other documentation
- **Keep Updated**: Update docs with code changes

---

## Common Issues

### "Docstring coverage below threshold"

**Solution**:
```bash
# Find files missing docstrings
interrogate -v -i tools/Pylorix/

# Add docstrings to flagged functions/classes
```

### "Black formatting failed"

**Solution**:
```bash
black .  # Auto-format
git add .
git commit --amend --no-edit
```

### "Import organization incorrect"

**Solution**:
```bash
isort .  # Auto-sort imports
git add .
git commit --amend --no-edit
```

### "MyPy type errors"

**Solution**:
```python
# Add type hints
def process(data) -> dict:  # Before
def process(data: str) -> dict:  # After

# Or use type: ignore for third-party issues
import external_lib  # type: ignore
```

---

## Getting Help

- **Documentation**: Check [docs/](docs/) directory
- **GitHub Issues**: Open an issue for bugs/features
- **GitHub Discussions**: Ask questions
- **Agent Protocol**: See [Agents.MD](Agents.MD)

---

## Recognition

Contributors will be acknowledged in:
- GitHub Contributors page
- Release notes
- `CONTRIBUTORS.md` file (if applicable)

---

**Thank you for contributing to EudoraX Prototype!**

*Last Updated: 2025-12-03*
