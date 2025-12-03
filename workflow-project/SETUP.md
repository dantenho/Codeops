# Workflow Project Setup Guide

Quick start guide for setting up the EudoraX Workflow Rules Skeletal Project.

## Prerequisites

- Python 3.11+
- Node.js 18+ (for NVM)
- Git

## Installation Steps

### 1. Environment Setup

```bash
# Clone or navigate to the project
cd workflow-project

# Create Python virtual environment using UV
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
uv pip install black isort ruff mypy interrogate pydocstyle pytest

# Install Node.js dependencies if needed
nvm use 18
npm install  # if package.json exists
```

### 2. Code Quality Tools Setup

```bash
# Make scripts executable
chmod +x automation/code_quality.sh

# Run initial quality check
./automation/code_quality.sh
```

### 3. Telemetry System Setup

```bash
# Create CodeAgents directory structure
mkdir -p CodeAgents/{GrokIA,GeminiFlash25,GeminiPro25,GeminiPro30,ClaudeCode}/{{logs,errors,analysis}}

# Test telemetry logging
python scripts/telemetry_logger.py \
  --agent GrokIA \
  --operation CREATE \
  --file workflow-project/test.py \
  --status SUCCESS \
  --duration 1500 \
  --lines 1,50
```

### 4. Pre-commit Hooks (Optional)

```bash
# Install pre-commit hooks
uv pip install pre-commit
pre-commit install

# Test pre-commit on all files
pre-commit run --all-files
```

## Usage Examples

### Running Code Quality Checks

```bash
# Run all quality checks
./automation/code_quality.sh

# Run individual tools
black .                    # Format code
isort .                    # Sort imports
ruff check . --fix        # Lint and auto-fix
mypy .                    # Type checking
interrogate -v -i .       # Documentation coverage
```

### Using Templates

```bash
# Copy Python module template
cp templates/python_module.py my_new_module.py

# Edit the placeholders:
# - {module_name} -> my_new_module
# - {AgentName} -> GrokIA
# - {ISO_TIMESTAMP} -> 2025-12-03T10:29:00Z
```

### Logging Operations

```bash
# Log a successful operation
python scripts/telemetry_logger.py \
  --agent GrokIA \
  --operation REFACTOR \
  --file workflow-project/config/new_config.toml \
  --status SUCCESS \
  --duration 2000 \
  --lines 1,100

# Log an error
# Use the Python API directly for complex scenarios
```

## Project Structure

```
workflow-project/
├── README.md                    # Main project documentation
├── SETUP.md                     # This setup guide
├── config/                      # Configuration files
│   ├── ruff.toml               # Ruff linter configuration
│   └── mypy.ini               # MyPy type checker configuration
├── scripts/                     # Automation scripts
│   └── telemetry_logger.py     # Telemetry logging system
├── templates/                   # File templates
│   ├── python_module.py        # Python module template
│   └── telemetry_schema.json   # Telemetry data schema
├── automation/                  # CI/CD automation
│   └── code_quality.sh        # Code quality automation
├── docs/                       # Documentation (to be created)
└── monitoring/                 # Monitoring tools (to be created)
```

## Configuration Customization

### Modify Quality Thresholds

Edit `config/mypy.ini`:
```ini
[mypy]
disallow_untyped_defs = true  # Enable strict typing
```

Edit `automation/code_quality.sh`:
```bash
interrogate -v -i --fail-under=90  # Increase documentation coverage to 90%
```

### Add New Agents

1. Create agent directory in `CodeAgents/`
2. Update `templates/telemetry_schema.json` if needed
3. Add agent to `scripts/telemetry_logger.py` if required

## Troubleshooting

### Common Issues

**Virtual environment not activating:**
```bash
# Check Python version
python --version  # Should be 3.11+

# Recreate virtual environment
rm -rf .venv
uv venv
source .venv/bin/activate
```

**Missing tools:**
```bash
# Install all required tools
uv pip install black isort ruff mypy interrogate pydocstyle pytest
```

**Telemetry directory issues:**
```bash
# Ensure proper permissions
chmod -R 755 CodeAgents/
```

### Getting Help

1. Check the main README.md for project overview
2. Review CONTRIBUTION.md from the main project
3. Examine existing configuration files
4. Check GitHub Actions logs for CI issues

## Next Steps

1. Customize configurations for your specific needs
2. Integrate with your existing codebase
3. Set up GitHub Actions workflows
4. Train team members on the workflow protocols

---
Generated: 2025-12-03T10:29:00Z
Project: EudoraX Prototype
Agent: GrokIA
