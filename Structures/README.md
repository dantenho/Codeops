# Structures Blueprint

This directory stores reusable filesystem skeletons for agent-specific workspaces.
Each agent captures its training inputs, rules, and memory artifacts inside a timestamped folder so future runs can reproduce the same context quickly.

## Naming Convention
- `Structures/<AGENTID>/<TIMESTAMP>/`
  - `AGENTID`: uppercase identifier that matches the value recorded in `CodeAgents/ID/`.
  - `TIMESTAMP`: ISO-8601 string without colons, e.g. `2025-12-03T000000Z`.

## Required Subdirectories
| Path | Purpose |
| --- | --- |
| `training/` | Lesson plans, exercises, spaced repetition assets. |
| `rules/` | Agent protocols (Agents.MD extracts, policy deltas). |
| `methods/` | Step-by-step strategies, playbooks, and workflows. |
| `files/` | Raw reference files, datasets, or prompts. |
| `database/` | Lightweight state (SQLite, JSON) used during training. |
| `memory/` | Summaries, reflections, and telemetry snapshots. |

Each folder should include a minimal `README.md` describing how to populate it.
See `AGENT_TEMPLATE/2025-12-03T000000Z/` for the canonical starter skeleton.
