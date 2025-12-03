# ClaudeCode Memory

## 🧠 Active Context
- **Current Project Phase:** Initialization
- **Active Branch:** main
- **Last Task ID:** N/A
- **Current Focus:** Setting up Agent Training System (ATS) and Memory Protocols.

## 📚 Learned Protocols
> "Read Once, Remember Forever"

- [x] **NVM/UV Usage:** I understand I must use `nvm` and `uv` (not pip/npm directly).
- [x] **Commit Messages:** I know the format `feat(scope): description`.
- [x] **Telemetry:** I know to log operations to `CodeAgents/Telemetry`.
- [x] **Testing:** I know to run tests before requesting review.

## 🔑 Key Decisions & Architecture Log
| Date | Decision | Rationale | Context |
|------|----------|-----------|---------|
| 2025-12-03 | **Agent Training System Architecture** | Selected a modular design with Pydantic models for strict validation and YAML for configuration. | ATS Implementation |
| 2025-12-03 | **Memory Protocol** | Implemented a "Memory First" approach to reduce redundant context reading and improve agent efficiency. | Agents.MD Refactor |

## 🧩 Recurring Patterns & Snippets
*Store frequently used code snippets or patterns here to avoid reinventing the wheel.*

```python
# Standard Pydantic Model with Timestamp
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

## ⚠️ Known Issues & Watchlist
- [ ] Monitor Pylint false positives with Pydantic v2 `Field` definitions.
