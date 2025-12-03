# Agent Skeleton Usage Guide

This template shows how every agent should organize its training and memory artifacts.
Copy the entire folder, rename `AGENT_TEMPLATE` to your Agent ID, and update the timestamp to the current ISO-8601 string without colons.

## Populate the Skeleton
1. **training/** – Move lesson plans, spaced repetition decks, and evaluation notebooks here. Reference relevant modules from `CodeAgents/Training`.
2. **rules/** – Store extracted `Agents.MD` sections, policy overrides, and task-specific constraints.
3. **methods/** – Document repeatable procedures or debugging flows. Each method should cite the telemetry/task that proved it works.
4. **files/** – Keep raw reference documents and datasets. Derived artifacts should mention the source filename and checksum.
5. **database/** – Place lightweight stores (SQLite/JSON/embeddings) generated during the session. Include a manifest describing schema/version.
6. **memory/** – Capture reflections or long-term summaries that eventually sync with `CodeAgents/Memory/<Agent>.md`.

## Telemetry & Compliance Checklist
- Log operations using `CodeAgents/core/telemetry.py` whenever you create or modify training assets.
- Ensure every README update includes agent signature + timestamp if it records decisions.
- When archiving a session, zip the timestamped folder and attach it to the relevant issue or training report.

## Discovery
This template is referenced from `PROJECT_STATUS.md` so collaborators can locate the latest skeleton quickly.
