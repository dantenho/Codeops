"""
AI Agent Tunneling System.

@module: tunnel
@description: Communication bridge between AI agents (Gemini, Cursor, Claude).
              Enables shared state, task delegation, and synchronized work.

## Usage:
```python
from tunnel import Tunnel

# Initialize tunnel
tunnel = Tunnel(agent_name="gemini")

# Send message to Cursor
tunnel.send("cursor", {"task": "implement_login", "priority": "high"})

# Receive messages
messages = tunnel.receive()
```

@suggestion: Run `python tunnel.py --serve` for persistent tunnel server
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# =============================================================================
# CONFIGURATION
# =============================================================================

TUNNEL_DIR = Path(__file__).parent / ".tunnel"
TUNNEL_DIR.mkdir(exist_ok=True)


# =============================================================================
# MESSAGE DATACLASS
# =============================================================================

@dataclass
class TunnelMessage:
    """
    Message passed between AI agents.

    @dataclass: TunnelMessage
    @param sender: Agent sending the message
    @param recipient: Target agent
    @param message_type: Type of message (task, response, sync, heartbeat)
    @param payload: Message content
    @param timestamp: ISO timestamp
    @param id: Unique message ID
    """
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: str = ""
    id: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.id:
            self.id = f"{self.sender}_{int(time.time()*1000)}"


# =============================================================================
# TUNNEL CLASS
# =============================================================================

class Tunnel:
    """
    AI Agent Communication Tunnel.

    @class: Tunnel
    @description: File-based message passing system for AI cooperation.

    @features:
    - Async message passing
    - Task delegation
    - State synchronization
    - Heartbeat monitoring

    @usage:
    ```python
    tunnel = Tunnel("gemini")
    tunnel.send("cursor", {"action": "implement", "file": "login.py"})
    ```
    """

    AGENTS = ["gemini", "cursor", "claude", "codeops"]

    def __init__(self, agent_name: str):
        """
        Initialize tunnel for agent.

        @param agent_name: Name of this agent
        """
        self.agent_name = agent_name.lower()
        self.inbox = TUNNEL_DIR / f"{self.agent_name}_inbox.jsonl"
        self.outbox = TUNNEL_DIR / f"{self.agent_name}_outbox.jsonl"
        self.state_file = TUNNEL_DIR / "shared_state.json"

        # Create files
        self.inbox.touch(exist_ok=True)
        self.outbox.touch(exist_ok=True)
        if not self.state_file.exists():
            self.state_file.write_text("{}")

        # Send heartbeat
        self._heartbeat()

    def _heartbeat(self):
        """Send heartbeat to indicate agent is active."""
        heartbeat_file = TUNNEL_DIR / f"{self.agent_name}_heartbeat"
        heartbeat_file.write_text(datetime.now().isoformat())

    def send(
        self,
        recipient: str,
        payload: Dict[str, Any],
        message_type: str = "task"
    ) -> TunnelMessage:
        """
        Send message to another agent.

        @param recipient: Target agent name
        @param payload: Message content
        @param message_type: Type (task, response, sync, query)
        @returns: The sent message
        """
        message = TunnelMessage(
            sender=self.agent_name,
            recipient=recipient.lower(),
            message_type=message_type,
            payload=payload
        )

        # Write to outbox
        with open(self.outbox, "a") as f:
            f.write(json.dumps(asdict(message)) + "\n")

        # Write to recipient's inbox
        recipient_inbox = TUNNEL_DIR / f"{recipient.lower()}_inbox.jsonl"
        recipient_inbox.touch(exist_ok=True)
        with open(recipient_inbox, "a") as f:
            f.write(json.dumps(asdict(message)) + "\n")

        return message

    def receive(self, mark_read: bool = True) -> List[TunnelMessage]:
        """
        Receive pending messages.

        @param mark_read: Clear inbox after reading
        @returns: List of messages
        """
        messages = []

        if self.inbox.exists():
            content = self.inbox.read_text().strip()
            if content:
                for line in content.split("\n"):
                    try:
                        data = json.loads(line)
                        messages.append(TunnelMessage(**data))
                    except:
                        pass

                if mark_read:
                    # Archive and clear
                    archive = TUNNEL_DIR / f"{self.agent_name}_archive.jsonl"
                    with open(archive, "a") as f:
                        f.write(content + "\n")
                    self.inbox.write_text("")

        return messages

    def get_shared_state(self) -> Dict[str, Any]:
        """Get shared state between agents."""
        try:
            return json.loads(self.state_file.read_text())
        except:
            return {}

    def update_shared_state(self, updates: Dict[str, Any]):
        """Update shared state."""
        state = self.get_shared_state()
        state.update(updates)
        state["_last_updated_by"] = self.agent_name
        state["_last_updated_at"] = datetime.now().isoformat()
        self.state_file.write_text(json.dumps(state, indent=2))

    def delegate_task(
        self,
        recipient: str,
        task: str,
        context: Dict[str, Any],
        priority: str = "normal"
    ) -> TunnelMessage:
        """
        Delegate task to another agent.

        @param recipient: Target agent
        @param task: Task description
        @param context: Task context
        @param priority: low, normal, high, critical
        """
        return self.send(recipient, {
            "task": task,
            "context": context,
            "priority": priority,
            "worktree": f"cursor-{recipient.split('-')[-1]}" if "cursor" in recipient else None
        }, message_type="task")

    def respond(self, original_message: TunnelMessage, response: Dict[str, Any]):
        """Respond to a received message."""
        return self.send(
            original_message.sender,
            {
                "in_reply_to": original_message.id,
                "response": response
            },
            message_type="response"
        )

    def get_active_agents(self) -> List[str]:
        """Get list of active agents (heartbeat within 5 min)."""
        active = []
        now = datetime.now()

        for agent in self.AGENTS:
            heartbeat = TUNNEL_DIR / f"{agent}_heartbeat"
            if heartbeat.exists():
                try:
                    last = datetime.fromisoformat(heartbeat.read_text())
                    if (now - last).seconds < 300:  # 5 minutes
                        active.append(agent)
                except:
                    pass

        return active

    def broadcast(self, payload: Dict[str, Any], message_type: str = "sync"):
        """Broadcast message to all agents."""
        for agent in self.AGENTS:
            if agent != self.agent_name:
                self.send(agent, payload, message_type)


# =============================================================================
# WORKTREE ASSIGNMENT
# =============================================================================

WORKTREE_ASSIGNMENTS = {
    "cursor-frontend": {
        "focus": ["UI", "React", "CSS", "components"],
        "files": ["*.tsx", "*.jsx", "*.css", "*.scss"],
        "branch": "cursor-frontend"
    },
    "cursor-backend": {
        "focus": ["API", "database", "services", "auth"],
        "files": ["*.py", "routes/*", "services/*"],
        "branch": "cursor-backend"
    },
    "cursor-testing": {
        "focus": ["tests", "QA", "validation", "CI"],
        "files": ["tests/*", "*.test.*", "pytest.ini"],
        "branch": "cursor-testing"
    }
}


def get_worktree_for_task(task: str) -> str:
    """Determine which worktree should handle a task."""
    task_lower = task.lower()

    if any(kw in task_lower for kw in ["ui", "frontend", "react", "css", "component"]):
        return "cursor-frontend"
    elif any(kw in task_lower for kw in ["api", "database", "backend", "service"]):
        return "cursor-backend"
    elif any(kw in task_lower for kw in ["test", "qa", "validation", "ci"]):
        return "cursor-testing"

    return "cursor-backend"  # default


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print(" AI Agent Tunnel System")
    print("=" * 60)

    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        print("\n🚀 Starting tunnel server...")
        tunnel = Tunnel("codeops")

        while True:
            messages = tunnel.receive(mark_read=False)
            if messages:
                print(f"\n📬 {len(messages)} pending messages")

            active = tunnel.get_active_agents()
            print(f"✅ Active agents: {', '.join(active) or 'none'}")

            time.sleep(5)
    else:
        # Status check
        tunnel = Tunnel("gemini")

        print("\n📍 Agent: gemini")
        print(f"📂 Tunnel dir: {TUNNEL_DIR}")
        print(f"✉️  Inbox: {tunnel.inbox}")

        print("\n🌳 Worktree Assignments:")
        for wt, config in WORKTREE_ASSIGNMENTS.items():
            print(f"   {wt}: {', '.join(config['focus'])}")

        active = tunnel.get_active_agents()
        print(f"\n🔗 Active agents: {', '.join(active) or 'none'}")

        messages = tunnel.receive(mark_read=False)
        print(f"📬 Pending messages: {len(messages)}")
