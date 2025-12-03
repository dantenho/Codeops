# Training System Analysis & Hierarchical Plan

## 1. Methodology Review

- **Execution Flow**: `training orchestrate` now serves as the canonical runner for simultaneous agent sessions, capturing per-token throughput and GPU telemetry per run. Solo sessions still live under `training start` for ad-hoc drills.
- **Deduplication Policy**: The new `training dedupe` command scans physical assets (default: `SkeletalStructure/`) and optionally dedupes stored materials in ChromaDB, preventing agent-generated clutter from earlier training passes.
- **Diagnostics Pipeline**: `training diagnostics` enumerates collection sizes, summarizes average scores/tokens/GPU utilization for each agent, and prints the latest error log entries so deviations are caught before merges.

## 2. Database Hierarchy

- `src/training/data/client.py` wraps `chromadb.PersistentClient` and exposes a `CollectionSet` for training, score, error, and log data.
- `src/training/data/repositories.py` implements repositories per collection, handling metadata enrichment (file hashes, timestamps) and duplicate removal.
- `MemoryService` now consumes the repository registry, keeping business logic decoupled from the storage mechanism and enabling per-agent analytics through typed helpers.

## 3. Metrics, Logs & Errors

- **Metrics Stored per Score**:
  - `tokens_processed`
  - `tokens_per_second`
  - `score_per_token`
  - `gpu_utilization_avg`
  - `gpu_memory_used_mb`
- **Diagnostics Command Output**:
  - Collection document counts
  - Per-agent average score, score/min, tokens, GPU utilization
  - Consolidated error table (agent, timestamp, severity, context, message)
- **Structure Report**: `training structure-report --output structure_report.json` exports every YAML config (with metadata headers) plus recent performance summaries. These reports can be diffed pre-merge for compliance with Agents.MD.

## 4. Agent Memory Alignment

- Added `CodeAgents/Memory/Composer.md` so Composer's actions, learned protocols, and architectural decisions persist across tasks.
- Telemetry log recorded in `CodeAgents/Composer/logs` for this restructuring effort to satisfy Agents.MD reporting rules.
