
import os
from pathlib import Path

AGENTS = [
    "GrokIA",
    "GeminiFlash25",
    "GeminiPro25",
    "GeminiPro30",
    "Jules",
    "ClaudeCode",
    "Composer"
]

TEMPLATE = """# {agent_name} Memory

## 🧠 Active Context
- Current Project Phase: Phase 1: Foundation & Refactoring
- Active Branch: main
- Last Task: Memory Initialization

## 📚 Learned Protocols
- [x] NVM/UV Usage
- [x] Commit Message Format
- [x] Telemetry Logging

## 🔑 Key Decisions & Architecture
- [2025-12-04] Decision: Enforced strict JSON schema for telemetry logs.
"""

def init_memory():
    base_path = Path("CodeAgents/Memory")
    base_path.mkdir(parents=True, exist_ok=True)

    for agent in AGENTS:
        file_path = base_path / f"{agent}.md"
        if not file_path.exists():
            print(f"Creating memory for {agent}...")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(TEMPLATE.format(agent_name=agent))
        else:
            print(f"Memory for {agent} already exists.")

if __name__ == "__main__":
    init_memory()
