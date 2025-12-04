# Composer Memory

## 🧠 Active Context

- **Current Project Phase:** Training & Development
- **Active Branch:** main
- **Last Task ID:** training-session-init
- **Current Focus:** Completed initial training session, analyzing codebase structure, reinforcing Agents.MD protocols.

## 📚 Learned Protocols
>
> "Read Once, Remember Forever"

- [x] **NVM/UV Usage:** Environment bootstrapped with `uv venv` + `uv pip install`.
- [x] **Commit Messages:** Follow `[AgentName] description` per Agents.MD.
- [x] **Telemetry:** Log JSON entries under `CodeAgents/Composer/logs`.
- [x] **Testing:** Run targeted commands (`training gpu`, `training orchestrate`, `training structure-report`) before handoff.

## 🔑 Key Decisions & Architecture Log

| Date       | Decision                                     | Rationale                                                                 | Context                  |
|------------|----------------------------------------------|---------------------------------------------------------------------------|--------------------------|
| 2025-12-03 | Introduced `data/` layer around ChromaDB     | Remove global state, enable hierarchical repositories, simplify dedupe    | `src/training/data/*`    |
| 2025-12-03 | Added GPU + per-token metrics to score docs  | Provide comparable telemetry across agents before merge reviews           | `cli._run_training_session` |
| 2025-12-03 | Created `training diagnostics` + report cmds | Needed structured analysis of metrics/logs/errors per Agents.MD checklist | `cli.diagnostics`, `structure-report` |
| 2025-12-03 | Implemented file + memory dedupe command     | Clear duplicate training artifacts produced by previous agents            | `cli.dedupe`, `utils/dedupe.py` |
| 2025-12-04 | Completed initial training session           | Reinforce Agents.MD protocols, understand training system architecture    | `train_session.py`, telemetry logging |
| 2025-12-04 | Used UV for environment setup                | Follow Agents.MD protocol - UV is mandatory, faster than pip             | `.venv` setup, dependency installation |

## 🧩 Recurring Patterns & Snippets

```python
from training.data.repositories import RepositoryRegistry

registry = RepositoryRegistry()
scores = registry.scores.fetch_scores(agent_id="Composer", topic=None, limit=10)
```

## ⚠️ Known Issues & Watchlist

- [ ] Pytest suite still fails due to legacy model expectations (`ActivityType.EXERCISE`, flashcard schemas). Needs follow-up refactor.
- [ ] ChromaDB delete operations are best-effort; consider migrating to Postgres-backed vector store for stronger guarantees.
