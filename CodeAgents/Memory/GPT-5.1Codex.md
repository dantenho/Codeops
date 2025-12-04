# GPT-5.1 Codex Memory

## 🧠 Active Context

- **Current Project Phase:** Development
- **Active Branch:** HEAD (detached)
- **Last Task ID:** training-bootstrap-2025-12-04
- **Current Focus:** Fixing ATS CLI dependencies and running initial training session.

## 📚 Learned Protocols
>
> "Read Once, Remember Forever"

- [x] **NVM/UV Usage:** I understand I must use `nvm` and `uv` (not pip/npm directly).
- [x] **Commit Messages:** I know the format `feat(scope): description`.
- [x] **Telemetry:** I know to log operations to `CodeAgents/Telemetry`.
- [x] **Testing:** I know to run tests before requesting review.

## 🔑 Key Decisions & Architecture Log

| Date | Decision | Rationale | Context |
|------|----------|-----------|---------|
| 2025-12-04 | Switch chromadb Collection import source | `chromadb.api.types` no longer exposes `Collection`, so importing from `chromadb.api.models` restores CLI execution. | `CodeAgents/Training/src/training/data/client.py`, `.../repositories.py` |

## 🧩 Recurring Patterns & Snippets

*Store frequently used code snippets or patterns here to avoid reinventing the wheel.*

```python
# Example: Standard Error Handler
def handle_error(e):
    logger.error(f"Error: {e}")
    raise
```

## ⚠️ Known Issues & Watchlist

- [ ] Issue #123: Flaky test in module X
- [ ] Watch out for circular imports in `models.py`
