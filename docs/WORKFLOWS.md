<!-- [REFACTOR] Workflow doc vibe refresh
Agent: GPT-5.1 Codex
Timestamp: 2025-12-03T10:25:00Z -->

# GitHub Workflows -- Compliance Vibe Guide

This document explains how the automation stack keeps every branch aligned with the vibe described in [`CONTRIBUTING.md`](../CONTRIBUTING.md) and `Agents.MD`. Think of it as the operations map: what runs, when it runs, and how to keep the CI signal clean.

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [Workflow Reference](#workflow-reference)
   - [Agent Validation](#agent-validation)
   - [Branch Sync](#branch-sync)
   - [Merge Orchestrator](#merge-orchestrator)
   - [Telemetry Collector](#telemetry-collector)
3. [Optimization Patterns](#optimization-patterns)
4. [Failure Recovery Patterns](#failure-recovery-patterns)
5. [Manual Triggers & Monitoring](#manual-triggers--monitoring)
6. [Reference Links](#reference-links)

---

## Pipeline Overview

| Stage | What Happens | Why it Matters |
| --- | --- | --- |
| Agent Detection | Branch name + commit metadata identifies the agent. | Enables telemetry lookups and enforces protocol tags. |
| Documentation Validation | Docstring coverage, operation tags, and signatures validated via `interrogate` and `pydocstyle`. | Prevents low-signal docs from reaching reviewers. |
| Code Quality | `ruff`, `black`, `isort`, `mypy` keep style and types aligned. | Mirrors the local stack documented in `CONTRIBUTING.md`. |
| Telemetry Validation | JSON audits against schemas in `CodeAgents/schemas`. | Guarantees every automated change leaves an auditable trail. |
| Compliance Report | Summarizes pass/fail for each block with actionable messages. | Gives reviewers a single glance status page. |

---

## Workflow Reference

### Agent Validation

**File**: `.github/workflows/agent-validation.yml`

| Trigger | Details |
| --- | --- |
| Pull Requests | Targets `main`, `develop`, `staging` when code files (`*.py`, `*.js`, `*.ts`, `*.go`, `*.rs`) change. |
| Push | Runs on direct pushes to `main` and `develop`. |

**Job Flow**
1. **Detect Agent** -- Parses branch name (`agent/<name>/...`) and commit subjects (`[AgentName] ...`). Emits `agent_id` and `has_telemetry` outputs.
2. **Documentation Validation** -- Runs `interrogate`, `pydocstyle`, and an operation-tag scanner. Coverage target defaults to 90%; configure via repo vars if needed.
3. **Code Quality** -- Executes `ruff`, `black`, `isort`, and `mypy`. `mypy` currently warns only; promote to required once types stabilize.
4. **Unit Tests** -- Sets `PYTHONPATH=$GITHUB_WORKSPACE:$GITHUB_WORKSPACE/CodeAgents/Training/src` so `training.*` modules resolve, then runs `python -m pytest CodeAgents/GitHub/tests -v` and `python -m pytest CodeAgents/Training/tests -v`.
5. **Telemetry Validation** -- Conditional on `has_telemetry`. Uses the JSON schemas in `CodeAgents/schemas/` to check structure and severity enums.
6. **Compliance Report** -- Creates a Markdown summary with ✅/❌ entries and posts it to the PR via `checks: write` permissions.

**Acceleration Tips**
- Cache `~/.cache/pip` and `.venv` between jobs where possible.
- Scope workflow run paths to `backend/**`, `tools/**`, etc. to skip doc-only edits when safe.
- Use matrix builds sparingly; default to `ubuntu-latest` unless platform coverage is required.

### Branch Sync

**File**: `.github/workflows/branch-sync.yml`

Purpose: keep long-lived branches current with `develop`.

Flow:
1. Checkout repo and fetch all remotes.
2. Detect delta between `develop` and each `agent/*` branch.
3. Open PRs (or update existing ones) that merge the latest `develop` changes.
4. Auto-merge if CI passes; otherwise leave actionable comments.

Use cases:
- Automatically remind agents when they fall behind.
- Reduce manual `git fetch && rebase` loops.

### Merge Orchestrator

**File**: `.github/workflows/merge-orchestrator.yml`

Trigger: PR labeled `auto-merge` or scheduled nightly runs.

Responsibilities:
- Confirm `agent-validation` succeeded.
- Re-run smoke tests if the PR is over a configurable age.
- Perform a merge using the GitHub API and surface conflicts early.
- Notify in case of failure via PR comment + optional Slack/webhook integration.

### Telemetry Collector

**File**: `.github/workflows/telemetry-collector.yml`

Trigger: Daily schedule or manual dispatch.

Steps:
1. Crawl `CodeAgents/**/logs/*.json`.
2. Aggregate stats (operations per agent, pass/fail ratio, most touched files, average duration).
3. Write a Markdown summary.
4. Upload results as workflow artifacts for later analysis.

---

## Optimization Patterns

| Pattern | Implementation | Benefit |
| --- | --- | --- |
| Dependency Caching | Use `actions/cache` keyed by `hashFiles('**/requirements.txt')` and `.venv`. | Cuts setup time for Python tooling. |
| Targeted Paths | Add `paths`/`paths-ignore` filters to workflows. | Avoids running validation on unrelated markdown-only commits when permissible. |
| Conditional Jobs | `if: needs.detect-agent.outputs.has_telemetry == 'true'`. | Skips telemetry validation when no logs exist. |
| Matrix Trim | Restrict OS/python versions to the combos we actually ship. | Keeps queue times short. |
| Reusable Commands | Wrap repeated command bundles in composite actions or scripts under `tools/ci/`. | Centralizes updates to lint/test invocations. |

---

## Failure Recovery Patterns

| Signal | Mitigation |
| --- | --- |
| **Docstring coverage < 90%** | Run `interrogate -v -i`, add docstrings, re-run locally before pushing. |
| **Operation tag missing** | Ensure file headers follow the `[TAG]/Agent/Timestamp` format described in `CONTRIBUTING.md`. |
| **Telemetry schema error** | Validate JSON with `python -m json.tool` and compare keys with `CodeAgents/schemas/operation_schema.json`. |
| **Black/isort drift** | Execute `black . && isort .`, recommit, and push. |
| **MyPy warnings promoted to errors** | Tighten signatures or isolate third-party typing gaps with `# type: ignore[rule]`. |
| **Cache miss delays** | Bump cache keys to the latest dependencies or prime caches with a manual workflow run. |

---

## Manual Triggers & Monitoring

| Action | Command |
| --- | --- |
| List recent agent-validation runs | `gh run list --workflow=agent-validation.yml` |
| Trigger agent validation | `gh workflow run agent-validation.yml --ref agent/Name/feature` |
| Trigger telemetry collector | `gh workflow run telemetry-collector.yml` |
| Inspect run logs | `gh run view <run_id> --log` |
| Download artifacts | `gh run download <run_id>` |

Keep the `checks` and `statuses` permissions in each workflow block so reports can be attached directly to PRs.

---

## Reference Links

- [`CONTRIBUTING.md`](../CONTRIBUTING.md) -- full contributor playbook.
- [`Agents.MD`](../Agents.MD) -- authoritative protocol definitions.
- `CodeAgents/schemas/operation_schema.json` and `error_schema.json` -- telemetry validation sources.
- `.github/workflows/*.yml` -- actual workflow implementations. Cross-reference comments there when editing.

Align these workflows with your branch habits and telemetry discipline to keep the automation green and the vibe consistent.
