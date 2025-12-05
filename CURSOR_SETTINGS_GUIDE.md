# Cursor IDE Configuration Guide

[CREATE] Comprehensive configuration reference for Cursor IDE with autonomous agent workflows, GitHub integration, and project scaffolding.

**Agent:** Composer
**Timestamp:** 2025-12-05T01:50:00Z

---

## Table of Contents

- [Settings Locations](#settings-locations)
- [Core Configuration](#core-configuration)
- [Agent Rules](#agent-rules)
- [GitHub Integration](#github-integration)
- [Project Templates](#project-templates)
- [JSON Schemas](#json-schemas)
- [Task Automation](#task-automation)
- [Snippets Reference](#snippets-reference)
- [Troubleshooting](#troubleshooting)

---

## Settings Locations

| Scope | Location | Priority |
|-------|----------|----------|
| Workspace | `.vscode/settings.json` | Highest |
| User (Windows) | `%APPDATA%\Cursor\User\settings.json` | Medium |
| User (macOS) | `~/Library/Application Support/Cursor/User/settings.json` | Medium |
| User (Linux) | `~/.config/Cursor/User/settings.json` | Medium |
| Default | Built-in | Lowest |

### Rules Files

| File | Purpose |
|------|---------|
| `.cursorrules` | Project-level agent instructions |
| `.cursor/rules/*.mdc` | Modular rule definitions |
| `~/.cursor/rules/` | Global user rules |

---

## Core Configuration

### settings.json

```json
{
  "editor.formatOnSave": true,
  "editor.tabSize": 4,
  "editor.rulers": [100],
  "editor.wordWrap": "off",
  "editor.bracketPairColorization.enabled": true,
  "editor.guides.bracketPairs": true,
  "editor.inlineSuggest.enabled": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit",
    "source.fixAll": "explicit"
  },

  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.associations": {
    "*.mdc": "markdown",
    ".cursorrules": "markdown",
    "Agents.MD": "markdown"
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/*.egg-info": true,
    "**/.ruff_cache": true
  },

  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.docstringFormat": "google",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  "python.analysis.inlayHints.functionReturnTypes": true,
  "python.analysis.inlayHints.variableTypes": false,

  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },

  "[json][jsonc]": {
    "editor.defaultFormatter": "vscode.json-language-features",
    "editor.tabSize": 2
  },

  "[yaml]": {
    "editor.tabSize": 2,
    "editor.autoIndent": "advanced"
  },

  "[markdown]": {
    "editor.wordWrap": "on",
    "editor.quickSuggestions": {
      "other": true,
      "comments": true,
      "strings": true
    }
  },

  "git.autofetch": false,
  "git.confirmSync": true,
  "git.enableSmartCommit": false,
  "git.postCommitCommand": "none",
  "git.branchProtection": ["main", "master"],
  "git.pruneOnFetch": false,
  "git.fetchOnPull": false,

  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "terminal.integrated.defaultProfile.linux": "bash",
  "terminal.integrated.scrollback": 10000,

  "json.schemas": [
    {
      "fileMatch": ["agents.schema.json"],
      "url": "./schemas/agents.schema.json"
    },
    {
      "fileMatch": ["tasks/*.json"],
      "url": "./schemas/task.schema.json"
    }
  ],

  "cursor.ai.enableCodeActions": true,
  "cursor.ai.enableInlineCompletion": true
}
```

---

## Agent Rules

### .cursorrules File

Create a `.cursorrules` file in your project root:

```markdown
# Agent Rules for This Project

## Code Style
- Follow Agents.MD protocol
- Use Google-style docstrings
- All branches are local-only by default
- Include operation tags: [CREATE], [REFACTOR], [DEBUG], etc.

## Python Standards
- Use type hints
- Maximum line length: 100 characters
- Use Ruff for linting and formatting
- Follow PEP 8 with project-specific overrides

## Git Workflow
- All branches are local-only
- Use `agent/{AgentName}/{feature-description}` naming
- Never use `git push -u` (no upstream tracking)
```

### Modular Rules (.cursor/rules/)

Create rule modules in `.cursor/rules/`:

```
.cursor/
└── rules/
    ├── python.mdc
    ├── git.mdc
    └── telemetry.mdc
```

Example `python.mdc`:
```markdown
# Python Coding Standards

- Always include type hints
- Use dataclasses for data structures
- Follow Agents.MD docstring template
- Include complexity analysis for algorithms
```

---

## GitHub Integration

### ⚠️ CRITICAL: All Branches Are Local

**All branches MUST be local-only by default** (per Agents.MD Protocol).

- ❌ **FORBIDDEN:** Automatic upstream tracking (`git push -u origin branch`)
- ✅ **REQUIRED:** Create branches locally without remote tracking
- ✅ **ALLOWED:** Push branches only when explicitly needed for PRs
- ✅ **REQUIRED:** Unset upstream tracking if accidentally set: `git branch --unset-upstream`

### Branch Naming Convention

```
agent/{AgentName}/{feature-description}
```

### Git Configuration

Apply global Git settings:

```bash
git config --global push.default simple
git config --global push.autoSetupRemote false
git config --global branch.autoSetupMerge false
```

Or use the provided `.gitconfig.local` template.

### Workflow

1. **Create Local Branch:**
   ```bash
   git checkout -b agent/Composer/new-feature
   ```

2. **Work Locally:**
   ```bash
   git add .
   git commit -m "[Composer] feat: add new feature"
   ```

3. **Push When Ready for PR:**
   ```bash
   git push origin agent/Composer/new-feature
   ```

4. **Fix Accidental Tracking:**
   ```bash
   git branch --unset-upstream
   ```

---

## Project Templates

### Python Module Template

Use the `docstring-module` snippet to create new modules:

```python
"""
Module: {module_name}.py
Purpose: {one_line_description}

{extended_description}

Agent: {AgentName}
Created: {ISO_TIMESTAMP}
Operation: [CREATE]
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional, TypeVar

# Type variables for generic implementations
T = TypeVar("T")
```

### Function Template

Use the `docstring-func` snippet for full function documentation.

---

## JSON Schemas

### Schema Registration

Schemas are registered in `settings.json`:

```json
{
  "json.schemas": [
    {
      "fileMatch": ["agents.schema.json"],
      "url": "./schemas/agents.schema.json"
    },
    {
      "fileMatch": ["tasks/*.json"],
      "url": "./schemas/task.schema.json"
    }
  ]
}
```

### Available Schemas

- `agents.schema.json` - Agent configuration schema
- `task.schema.json` - Task definition schema
- Telemetry schemas in `CodeAgents/schemas/`

---

## Task Automation

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pre-commit install
```

### Automated Formatting

Formatting runs automatically on save:
- Ruff formatting for Python
- Import organization
- Trailing whitespace removal

### Telemetry Collection

Telemetry logs are automatically created in:
- `CodeAgents/{AgentName}/logs/`
- `CodeAgents/{AgentName}/errors/`
- `CodeAgents/{AgentName}/analysis/`

---

## Snippets Reference

### Available Snippets

| Prefix | Description |
|--------|-------------|
| `docstring-func` | Full function docstring template |
| `docstring-simple` | Simple function docstring |
| `docstring-class` | Class docstring template |
| `docstring-module` | Module header template |
| `dataclass-template` | Dataclass with docstring |
| `abc-template` | Abstract base class template |
| `telemetry-log` | Telemetry log entry template |

### Using Snippets

1. Type the snippet prefix (e.g., `docstring-func`)
2. Press `Tab` or `Enter`
3. Fill in placeholders:
   - `${1|...|}` - Select from dropdown
   - `${2:...}` - Type your value
   - `CURRENT_TIMESTAMP` - Auto-filled

### Example

```python
def process_data(input_path: Path) -> dict[str, Any]:
    # Type: docstring-func
    # Press Tab
    """
    [CREATE] Process data from file.

    Extended description...

    Args:
        input_path (Path): Path to input file.

    Returns:
        dict[str, Any]: Processed data.

    Agent: Composer
    Timestamp: 2025-12-05T01:50:00Z
    """
    pass
```

---

## Troubleshooting

### Snippets Not Working

1. Check if snippets file exists: `.vscode/python.code-snippets`
2. Reload Cursor: `Ctrl+Shift+P` → `Developer: Reload Window`
3. Verify Python extension is installed

### Formatting Not Working

1. Check Python extension is installed
2. Verify Ruff extension is installed: `charliermarsh.ruff`
3. Check `[python].editor.defaultFormatter` in settings
4. Verify Ruff is in PATH or configured

### Git Branch Tracking Issues

**Error:** "couldn't find remote ref"

**Fix:**
```bash
git branch --unset-upstream
```

**Error:** "fatal: The current branch has no upstream branch"

**Fix:** This is expected! Push explicitly:
```bash
git push origin branch-name
```

### Docstring Format Issues

1. Verify `python.docstringFormat` is set to `"google"`
2. Check Pylance extension is enabled
3. Restart Cursor IDE

### Type Checking Not Working

1. Verify `python.analysis.typeCheckingMode` is set
2. Check Pylance extension is installed
3. Ensure Python interpreter is selected

### JSON Schema Validation

1. Verify schema files exist in `schemas/` directory
2. Check `json.schemas` configuration in settings
3. Reload window after schema changes

---

## Quick Reference

### Essential Extensions

| Extension | ID | Purpose |
|-----------|----|---------|
| Python | `ms-python.python` | Python language support |
| Pylance | `ms-python.vscode-pylance` | Type checking |
| Ruff | `charliermarsh.ruff` | Linting & formatting |
| GitLens | `eamodio.gitlens` | Git visualization |

### Key Commands

| Command | Shortcut | Purpose |
|---------|----------|---------|
| Open Settings (JSON) | `Ctrl+Shift+P` → `Preferences: Open User Settings (JSON)` | Edit settings |
| Reload Window | `Ctrl+Shift+P` → `Developer: Reload Window` | Apply changes |
| Format Document | `Shift+Alt+F` | Format current file |
| Organize Imports | `Ctrl+Shift+P` → `Organize Imports` | Sort imports |

### File Locations

- **Workspace Settings:** `.vscode/settings.json`
- **Python Snippets:** `.vscode/python.code-snippets`
- **Agent Rules:** `.cursorrules`
- **Git Config Template:** `.gitconfig.local`
- **Git Local Branches Guide:** `GIT_LOCAL_BRANCHES.md`

---

## Related Documentation

- **Agents.MD Protocol:** See `Agents.MD` in project root
- **Git Local Branches:** See `GIT_LOCAL_BRANCHES.md`
- **Installation Script:** See `install-cursor-settings.ps1`
- **Git Config Template:** See `.gitconfig.local`

---

**Agent:** Composer
**Last Updated:** 2025-12-05T01:50:00Z
