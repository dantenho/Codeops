<!-- [REFACTOR] Vibe-coded contributor playbook refresh
Agent: GPT-5.1 Codex
Timestamp: 2025-12-03T10:15:00Z -->

# EudoraX Prototype -- Vibe Coding Playbook

Welcome to the multi-agent workshop. This guide keeps every contributor--human or automated--moving in the same groove: fast setup, predictable Git/GitHub habits, high-signal docs, and telemetry that tells the full story. Pair this playbook with [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md) for CI specifics and with `Agents.MD` for the underlying protocol.

## Table of Contents

1. [Signal & Conduct](#signal--conduct)
2. [Quick Boot Flow](#quick-boot-flow)
3. [Agent Protocol & Telemetry](#agent-protocol--telemetry)
4. [Git & GitHub Rhythm](#git--github-rhythm)
5. [Code Quality Stack](#code-quality-stack)
6. [Documentation Pulse](#documentation-pulse)
7. [Testing Grid](#testing-grid)
8. [Troubleshooting Matrix](#troubleshooting-matrix)
9. [Support & Recognition](#support--recognition)

---

## Signal & Conduct

| Principle | Vibe |
| --- | --- |
| Respectful Collaboration | Communicate clearly, document intent, never overwrite others' work. |
| Quality First | Every change aligns with linting, typing, testing, and doc baselines. |
| Transparent Ops | Tag files, sign your work, drop telemetry. No silent changes. |
| Continuous Improvement | Review telemetry, learn from CI, keep iterating on process. |

---

## Quick Boot Flow

1. **Clone + Branch**
   ```bash
   git clone https://github.com/Eudora-IA/Prototype.git
   cd Prototype
   git checkout -b agent/YourHandle/feature-spark
   ```
2. **Environment via UV**
   ```bash
   uv venv
   .venv\Scripts\activate        # Windows
   # or source .venv/bin/activate
   uv pip install -r backend/requirements.txt
   uv pip install -r tools/Pylorix/requirements.txt
   uv pip install ruff black isort mypy pydocstyle interrogate pre-commit
   pre-commit install
   ```
3. **Local Smoke Suite**
   ```bash
   black .
   isort .
   ruff check . --fix
   mypy tools/Pylorix/
   pytest
   ```

Keep this flow short and repeatable. Cache `.venv` between runs when possible.

---

## Agent Protocol & Telemetry

Everything here mirrors `Agents.MD`, distilled for daily use.

| Requirement | Notes |
| --- | --- |
| **Operation Tag** | Every touched file starts with `[CREATE]`, `[REFACTOR]`, `[DEBUG]`, or `[MODIFY]`. For Markdown, use an HTML comment. |
| **Agent Signature** | Add `Agent: <name>` and ISO timestamp near the tag. |
| **Telemetry** | Log each operation under `CodeAgents/{AgentName}/logs/` using the operation schema. Drop error logs when things fail. |
| **Traceability** | Reference related issues/PRs inside telemetry metadata. |

Sample header for code or docs:

```python
# [DEBUG] Stabilize vector store ingest
# Agent: GPT-5.1 Codex
# Timestamp: 2025-12-03T10:15:00Z
```

Operation log template:

```json
{
  "agent": "GPT-5.1 Codex",
  "timestamp": "2025-12-03T10:15:00Z",
  "operation": "REFACTOR",
  "target": {
    "file": "docs/WORKFLOWS.md",
    "function": null,
    "lines": [1, 200]
  },
  "status": "SUCCESS",
  "metadata": {
    "changed_lines": 120
  }
}
```

---

## Git & GitHub Rhythm

**Branch Blueprint**
- `agent/{AgentName}/{feature-kicker}` for AI agents.
- `contributor/{github-handle}/{feature}` for humans.

**Commit Format**
```
[AgentName] type: short imperative

One- or two-sentence body explaining the "why."
Reference issues/links when possible.
```
Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

**PR Checklist (pre-flight)**
- ✅ Operation tags + signatures added.
- ✅ Telemetry log pushed.
- ✅ Lints/formatters/tests clean.
- ✅ Docstrings + docs updated.
- ✅ CI-ready branch (rebased or merged with main).
- ✅ PR template filled with testing evidence.

See [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md) for how GitHub Actions mirrors these expectations.

---

## Code Quality Stack

| Tool | Purpose | Command |
| --- | --- | --- |
| **Black** | Formatting | `black .` |
| **isort** | Import sorting | `isort .` |
| **Ruff** | Linting + quick fixes | `ruff check . --fix` |
| **MyPy** | Static typing | `mypy tools/Pylorix/` |
| **Pydocstyle** | Docstring style | `pydocstyle --convention=google tools/Pylorix/` |
| **Interrogate** | Docstring coverage | `interrogate -v -i --fail-under=70 tools/Pylorix/` |

CI enforces the same stack; use `pre-commit run --all-files` for a single pass.

---

## Documentation Pulse

- **Coverage Target**: Minimum 70% (90%+ ideal). Track with Interrogate.
- **Style**: Google docstrings; keep examples runnable.
- **Scope**: Public modules, classes, functions, and any non-trivial internal helpers.
- **Inline Comments**: Only where logic is non-obvious--prefer docstrings.
- **Cross-Docs**: Update `README.md`, `ARCHITECTURE.md`, or `DATABASE.md` when your change touches those domains.
- **Reference**: Workflow validation rules live in [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md#documentation-validation).

Docstring snippet:

```python
def process_image(image_path: str, model: str = "FLUX.2-dev") -> dict:
    """Run generative pass over an image and capture metadata."""
```

---

## Testing Grid

| Layer | Location | Command | Notes |
| --- | --- | --- | --- |
| Unit | `tests/` | `pytest` | Default target; keep fast. |
| Targeted | `tests/test_x.py::case` | `pytest tests/test_x.py -k case` | Use during TDD loops. |
| CodeAgents Training | `CodeAgents/Training/tests` | `PYTHONPATH=".:CodeAgents/Training/src" uv run pytest CodeAgents/Training/tests -v` | Validates CLI, models, spaced repetition, and Threndia services end-to-end. |
| CodeAgents GitHub | `CodeAgents/GitHub/tests` | `uv run pytest CodeAgents/GitHub/tests -v` | Keeps the optimization catalog + detector contract healthy. |
| Coverage | `tools/Pylorix` | `pytest --cov=tools/Pylorix --cov-report=html` | Ensure new logic is exercised. |
| Integration | Marked with `@pytest.mark.integration` | `pytest -m integration` | Guard with env checks (e.g., Supabase). |

Expectations:
- Provide fixtures/mocks where external services exist.
- Use `$Env:PYTHONPATH=\"<repo>;...\"` on Windows PowerShell when mirroring the training command above.
- Document manual testing in the PR when automation is not available.

---

## Troubleshooting Matrix

| Signal | Recovery Move |
| --- | --- |
| Docstring coverage below threshold | Run `interrogate -v -i`, add docstrings, rerun. |
| Black or isort failures | Re-run formatters; never hand-edit style issues. |
| Ruff violations | `ruff check . --fix`, then handle remaining manual items. |
| MyPy errors | Tighten type hints or add `# type: ignore` with justification. |
| Missing operation tag/signature | Add HTML comment (docs) or Python comment (code) at file top. |
| Telemetry schema fail | Validate JSON against `CodeAgents/schemas/operation_schema.json`. |
| GitHub workflow red | Inspect the corresponding section in [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md) for debugging paths. |

---

## Support & Recognition

- **Docs Hub**: Browse everything in `docs/`.
- **Issues/Discussions**: Use GitHub Issues for scoped work, Discussions for questions.
- **Agent Protocol**: Full specification in `Agents.MD`.
- **Recognition**: Contributors appear in GitHub Insights, release notes, and `CONTRIBUTORS.md`.

Keep iterating, keep logging, and keep the vibe consistent. Thanks for building EudoraX Prototype.
