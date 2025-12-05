"""
Module: tunnel.py
Purpose: AI agent communication bridge enabling shared state, task delegation, and synchronized work.

Provides a file-based message passing system for coordination between multiple AI agents
(Gemini, Cursor, Claude, CodeOps). Implements asynchronous communication, shared state
management, heartbeat monitoring, and worktree-based task routing.

Key Components:
- TunnelMessage: Structured message format for agent communication
- Tunnel: Main communication class with send/receive capabilities
- Worktree assignment logic for task routing
- Shared state coordination mechanism

Agent: Antigravity
Created: 2025-01-27T00:00:00Z
Operation: [REFACTOR]
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Type variables for generic implementations
T = type(None)

# =============================================================================
# CONFIGURATION
# =============================================================================

TUNNEL_DIR = Path(__file__).parent / ".tunnel"
TUNNEL_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("tunnel")

# =============================================================================
# ENUMS
# =============================================================================

class MessageType(Enum):
    """
    [CREATE] Enumeration of message types for agent communication.

    Defines the different types of messages that can be exchanged
    between AI agents through the tunnel system.

    Attributes:
        TASK: Task delegation message
        RESPONSE: Reply to a previous message
        SYNC: State synchronization message
        HEARTBEAT: Agent alive signal
        QUERY: Information request

    Example:
        >>> msg_type = MessageType.TASK
        >>> print(msg_type.value)
        task

    Agent: Antigravity
    Timestamp: 2025-01-27T00:00:00Z
    """

    TASK = "task"
    RESPONSE = "response"
    SYNC = "sync"
    HEARTBEAT = "heartbeat"
    QUERY = "query"


class Priority(Enum):
    """
    [CREATE] Enumeration of task priority levels.

    Defines priority levels for task delegation to ensure
    critical tasks are handled appropriately.

    Attributes:
        LOW: Low priority, can be deferred
        NORMAL: Standard priority
        HIGH: High priority, should be handled soon
        CRITICAL: Critical priority, immediate attention required

    Example:
        >>> priority = Priority.HIGH
        >>> print(priority.value)
        high

    Agent: Antigravity
    Timestamp: 2025-01-27T00:00:00Z
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass(frozen=True)
class TunnelMessage:
    """
    [REFACTOR] Immutable message structure for AI agent communication.

    Represents a message passed between AI agents through the tunnel system.
    Immutability ensures message integrity throughout the communication pipeline.

    Attributes:
        sender (str): Name of the agent sending the message.
            Must be a valid agent name (gemini, cursor, claude, codeops).
        recipient (str): Target agent name.
            Must be a valid agent name.
        message_type (str): Type of message.
            Must be one of: task, response, sync, heartbeat, query.
        payload (Dict[str, Any]): Message content and data.
            Contains task details, responses, or state information.
        timestamp (str): ISO 8601 formatted timestamp.
            Auto-generated if not provided. Format: YYYY-MM-DDTHH:MM:SS.
        id (str): Unique message identifier.
            Auto-generated if not provided. Format: {sender}_{timestamp_ms}.

    Example:
        >>> message = TunnelMessage(
        ...     sender="gemini",
        ...     recipient="cursor",
        ...     message_type="task",
        ...     payload={"task": "implement_login", "priority": "high"}
        ... )
        >>> print(message.id)
        gemini_1234567890

    Raises:
        ValueError: If sender or recipient is not a valid agent name
        ValueError: If message_type is not recognized

    Complexity:
        Time: O(1) for instantiation
        Space: O(n) where n is payload size

    Agent: Antigravity
    Timestamp: 2025-01-27T00:00:00Z
    """

    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default="")
    id: str = field(default="")

    def __post_init__(self) -> None:
        """
        [REFACTOR] Validates and initializes message attributes.

        Performs validation of agent names and message types,
        and auto-generates timestamp and ID if not provided.

        Raises:
            ValueError: If validation fails

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        valid_agents = ["gemini", "cursor", "claude", "codeops", "antigravity"]
        valid_types = [mt.value for mt in MessageType]

        if self.sender.lower() not in valid_agents:
            raise ValueError(
                f"Invalid sender: '{self.sender}'. "
                f"Must be one of: {valid_agents}"
            )

        if self.recipient.lower() not in valid_agents:
            raise ValueError(
                f"Invalid recipient: '{self.recipient}'. "
                f"Must be one of: {valid_agents}"
            )

        if self.message_type.lower() not in valid_types:
            raise ValueError(
                f"Invalid message_type: '{self.message_type}'. "
                f"Must be one of: {valid_types}"
            )

        # Auto-generate timestamp if not provided
        if not self.timestamp:
            object.__setattr__(
                self, "timestamp", datetime.now(timezone.utc).isoformat()
            )

        # Auto-generate ID if not provided
        if not self.id:
            timestamp_ms = int(time.time() * 1000)
            object.__setattr__(
                self, "id", f"{self.sender.lower()}_{timestamp_ms}"
            )


# =============================================================================
# TUNNEL CLASS
# =============================================================================

class Tunnel:
    """
    [REFACTOR] AI Agent Communication Tunnel.

    Provides file-based message passing system for coordination between
    multiple AI agents. Implements asynchronous communication, shared state
    management, heartbeat monitoring, and task delegation.

    This class follows the Facade pattern, simplifying complex inter-agent
    communication into a clean API.

    Attributes:
        agent_name (str): Name of this agent instance.
        inbox (Path): Path to agent's inbox file (JSONL format).
        outbox (Path): Path to agent's outbox file (JSONL format).
        state_file (Path): Path to shared state file (JSON format).

    Example:
        >>> tunnel = Tunnel("gemini")
        >>> message = tunnel.send("cursor", {"task": "implement_login"})
        >>> messages = tunnel.receive()
        >>> print(f"Received {len(messages)} messages")

    Design Patterns:
        - Facade: Simplifies inter-agent communication
        - Observer: Heartbeat monitoring for agent status
        - State: Shared state coordination

    Thread Safety:
        This class is NOT thread-safe. File operations are not atomic.
        Use external synchronization for concurrent access.

    Agent: Antigravity
    Timestamp: 2025-01-27T00:00:00Z
    """

    AGENTS: List[str] = ["gemini", "cursor", "claude", "codeops", "antigravity"]
    HEARTBEAT_TIMEOUT_SECONDS: int = 300  # 5 minutes

    def __init__(self, agent_name: str) -> None:
        """
        [REFACTOR] Initializes tunnel for agent.

        Sets up file paths for inbox, outbox, and shared state.
        Creates necessary directories and files, and sends initial heartbeat.

        Args:
            agent_name (str): Name of this agent.
                Must be a valid agent name. Will be lowercased.

        Side Effects:
            - Creates .tunnel directory if it doesn't exist
            - Creates inbox/outbox files if they don't exist
            - Creates shared_state.json if it doesn't exist
            - Sends initial heartbeat

        Raises:
            ValueError: If agent_name is not in AGENTS list

        Example:
            >>> tunnel = Tunnel("gemini")
            >>> print(tunnel.agent_name)
            gemini

        Complexity:
            Time: O(1)
            Space: O(1)

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        agent_name_lower = agent_name.lower()

        if agent_name_lower not in self.AGENTS:
            raise ValueError(
                f"Invalid agent name: '{agent_name}'. "
                f"Must be one of: {self.AGENTS}"
            )

        self.agent_name = agent_name_lower
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

        logger.info(f"Tunnel initialized for agent: {self.agent_name}")

    def _heartbeat(self) -> None:
        """
        [REFACTOR] Sends heartbeat to indicate agent is active.

        Writes current timestamp to heartbeat file, allowing other
        agents to detect if this agent is still active.

        Side Effects:
            - Creates or updates heartbeat file
            - Modifies filesystem

        Complexity:
            Time: O(1)
            Space: O(1)

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        heartbeat_file = TUNNEL_DIR / f"{self.agent_name}_heartbeat"
        timestamp = datetime.now(timezone.utc).isoformat()
        heartbeat_file.write_text(timestamp)

    def send(
        self,
        recipient: str,
        payload: Dict[str, Any],
        message_type: str = MessageType.TASK.value,
    ) -> TunnelMessage:
        """
        [REFACTOR] Sends message to another agent.

        Creates a TunnelMessage and writes it to both the sender's outbox
        and the recipient's inbox. Messages are appended in JSONL format.

        Args:
            recipient (str): Target agent name.
                Must be a valid agent name. Will be lowercased.
            payload (Dict[str, Any]): Message content and data.
                Contains task details, responses, or state information.
            message_type (str): Type of message.
                Default: "task". Must be a valid MessageType value.

        Returns:
            TunnelMessage: The sent message with auto-generated ID and timestamp.

        Raises:
            ValueError: If recipient is not a valid agent name
            ValueError: If message_type is not recognized
            IOError: If file write operations fail

        Example:
            >>> tunnel = Tunnel("gemini")
            >>> message = tunnel.send(
            ...     "cursor",
            ...     {"task": "implement_login", "priority": "high"},
            ...     message_type="task"
            ... )
            >>> print(message.id)
            gemini_1234567890

        Side Effects:
            - Appends to sender's outbox file
            - Appends to recipient's inbox file
            - Creates recipient inbox if it doesn't exist

        Complexity:
            Time: O(1) for message creation + O(1) for file writes
            Space: O(n) where n is payload size

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        message = TunnelMessage(
            sender=self.agent_name,
            recipient=recipient.lower(),
            message_type=message_type,
            payload=payload,
        )

        # Write to outbox
        try:
            with open(self.outbox, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")
        except IOError as e:
            logger.error(f"Failed to write to outbox: {e}")
            raise

        # Write to recipient's inbox
        recipient_inbox = TUNNEL_DIR / f"{recipient.lower()}_inbox.jsonl"
        recipient_inbox.touch(exist_ok=True)
        try:
            with open(recipient_inbox, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")
        except IOError as e:
            logger.error(f"Failed to write to recipient inbox: {e}")
            raise

        logger.info(
            f"Message sent from {self.agent_name} to {recipient}: "
            f"{message_type} (ID: {message.id})"
        )

        return message

    def receive(self, mark_read: bool = True) -> List[TunnelMessage]:
        """
        [REFACTOR] Receives pending messages from inbox.

        Reads all messages from the agent's inbox file, parses them,
        and optionally archives and clears the inbox.

        Args:
            mark_read (bool): Whether to archive and clear inbox after reading.
                Default: True. If False, messages remain in inbox.

        Returns:
            List[TunnelMessage]: List of received messages, empty if none.

        Example:
            >>> tunnel = Tunnel("cursor")
            >>> messages = tunnel.receive()
            >>> for msg in messages:
            ...     print(f"From {msg.sender}: {msg.payload}")

        Side Effects:
            - If mark_read=True: Archives messages and clears inbox
            - Modifies inbox file if mark_read=True
            - Creates archive file if it doesn't exist

        Complexity:
            Time: O(n) where n is number of messages in inbox
            Space: O(n) where n is number of messages

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        messages: List[TunnelMessage] = []

        if not self.inbox.exists():
            return messages

        try:
            content = self.inbox.read_text(encoding="utf-8").strip()
            if content:
                for line in content.split("\n"):
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        messages.append(TunnelMessage(**data))
                    except (json.JSONDecodeError, TypeError, ValueError) as e:
                        logger.warning(f"Failed to parse message line: {e}")
                        continue

                if mark_read:
                    # Archive and clear
                    archive = TUNNEL_DIR / f"{self.agent_name}_archive.jsonl"
                    try:
                        with open(archive, "a", encoding="utf-8") as f:
                            f.write(content + "\n")
                    except IOError as e:
                        logger.error(f"Failed to archive messages: {e}")

                    self.inbox.write_text("", encoding="utf-8")
                    logger.info(f"Archived {len(messages)} messages")

        except IOError as e:
            logger.error(f"Failed to read inbox: {e}")
            return messages

        return messages

    def get_shared_state(self) -> Dict[str, Any]:
        """
        [REFACTOR] Gets shared state between agents.

        Reads and parses the shared state JSON file, returning
        the current state dictionary.

        Returns:
            Dict[str, Any]: Current shared state, empty dict if file doesn't exist
                or is invalid.

        Example:
            >>> tunnel = Tunnel("gemini")
            >>> state = tunnel.get_shared_state()
            >>> print(state.get("current_task"))

        Complexity:
            Time: O(1) for file read + O(n) for JSON parsing where n is state size
            Space: O(n) where n is state size

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        try:
            if not self.state_file.exists():
                return {}
            content = self.state_file.read_text(encoding="utf-8")
            return json.loads(content) if content.strip() else {}
        except (IOError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to read shared state: {e}")
            return {}

    def update_shared_state(self, updates: Dict[str, Any]) -> None:
        """
        [REFACTOR] Updates shared state with new values.

        Merges updates into existing shared state and writes back to file.
        Automatically adds metadata about who updated and when.

        Args:
            updates (Dict[str, Any]): Key-value pairs to update in shared state.
                Will be merged with existing state.

        Side Effects:
            - Modifies shared_state.json file
            - Adds _last_updated_by and _last_updated_at metadata

        Example:
            >>> tunnel = Tunnel("gemini")
            >>> tunnel.update_shared_state({"current_task": "login", "status": "in_progress"})

        Complexity:
            Time: O(1) for state read + O(n) for merge + O(n) for write
                where n is state size
            Space: O(n) where n is state size

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        state = self.get_shared_state()
        state.update(updates)
        state["_last_updated_by"] = self.agent_name
        state["_last_updated_at"] = datetime.now(timezone.utc).isoformat()

        try:
            self.state_file.write_text(
                json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            logger.info(f"Shared state updated by {self.agent_name}")
        except IOError as e:
            logger.error(f"Failed to update shared state: {e}")
            raise

    def delegate_task(
        self,
        recipient: str,
        task: str,
        context: Dict[str, Any],
        priority: str = Priority.NORMAL.value,
    ) -> TunnelMessage:
        """
        [REFACTOR] Delegates task to another agent.

        Creates a task message with task description, context, priority,
        and automatically determines worktree assignment.

        Args:
            recipient (str): Target agent name.
                Must be a valid agent name.
            task (str): Task description.
                Should be clear and actionable.
            context (Dict[str, Any]): Task context and requirements.
                Contains files, dependencies, constraints, etc.
            priority (str): Task priority level.
                Default: "normal". Must be: low, normal, high, critical.

        Returns:
            TunnelMessage: The sent task message.

        Example:
            >>> tunnel = Tunnel("gemini")
            >>> message = tunnel.delegate_task(
            ...     "cursor",
            ...     "Implement user login",
            ...     {"file": "auth.py", "requirements": ["jwt", "bcrypt"]},
            ...     priority="high"
            ... )

        Complexity:
            Time: O(1) - delegates to send()
            Space: O(n) where n is context size

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        worktree = None
        if "cursor" in recipient.lower():
            # Determine worktree based on task content
            worktree = get_worktree_for_task(task)

        payload = {
            "task": task,
            "context": context,
            "priority": priority,
            "worktree": worktree,
        }

        return self.send(recipient, payload, message_type=MessageType.TASK.value)

    def respond(
        self, original_message: TunnelMessage, response: Dict[str, Any]
    ) -> TunnelMessage:
        """
        [REFACTOR] Responds to a received message.

        Creates a response message that references the original message ID,
        allowing for message threading and conversation tracking.

        Args:
            original_message (TunnelMessage): The message being responded to.
                Must have valid sender and id attributes.
            response (Dict[str, Any]): Response data.
                Contains status, results, errors, etc.

        Returns:
            TunnelMessage: The sent response message.

        Example:
            >>> tunnel = Tunnel("cursor")
            >>> messages = tunnel.receive()
            >>> if messages:
            ...     tunnel.respond(messages[0], {"status": "completed", "file": "login.py"})

        Complexity:
            Time: O(1) - delegates to send()
            Space: O(n) where n is response size

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        return self.send(
            original_message.sender,
            {
                "in_reply_to": original_message.id,
                "response": response,
            },
            message_type=MessageType.RESPONSE.value,
        )

    def get_active_agents(self) -> List[str]:
        """
        [REFACTOR] Gets list of active agents based on heartbeat.

        Checks heartbeat files for all known agents and returns those
        that have sent a heartbeat within the timeout period.

        Returns:
            List[str]: List of active agent names, empty if none.

        Example:
            >>> tunnel = Tunnel("gemini")
            >>> active = tunnel.get_active_agents()
            >>> print(f"Active agents: {', '.join(active)}")

        Complexity:
            Time: O(m) where m is number of agents
            Space: O(m) where m is number of agents

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        active: List[str] = []
        now = datetime.now(timezone.utc)

        for agent in self.AGENTS:
            heartbeat = TUNNEL_DIR / f"{agent}_heartbeat"
            if heartbeat.exists():
                try:
                    last_str = heartbeat.read_text(encoding="utf-8").strip()
                    last = datetime.fromisoformat(last_str.replace("Z", "+00:00"))
                    delta = (now - last).total_seconds()
                    if delta < self.HEARTBEAT_TIMEOUT_SECONDS:
                        active.append(agent)
                except (IOError, ValueError) as e:
                    logger.warning(f"Failed to read heartbeat for {agent}: {e}")
                    continue

        return active

    def broadcast(
        self, payload: Dict[str, Any], message_type: str = MessageType.SYNC.value
    ) -> List[TunnelMessage]:
        """
        [REFACTOR] Broadcasts message to all agents except self.

        Sends the same message to all known agents, useful for state
        synchronization or announcements.

        Args:
            payload (Dict[str, Any]): Message content.
            message_type (str): Type of message.
                Default: "sync".

        Returns:
            List[TunnelMessage]: List of all sent messages.

        Example:
            >>> tunnel = Tunnel("gemini")
            >>> messages = tunnel.broadcast({"status": "ready", "version": "1.0"})

        Complexity:
            Time: O(m) where m is number of agents
            Space: O(m * n) where m is agents, n is payload size

        Agent: Antigravity
        Timestamp: 2025-01-27T00:00:00Z
        """
        messages: List[TunnelMessage] = []
        for agent in self.AGENTS:
            if agent != self.agent_name:
                msg = self.send(agent, payload, message_type)
                messages.append(msg)
        return messages


# =============================================================================
# WORKTREE ASSIGNMENT
# =============================================================================

WORKTREE_ASSIGNMENTS: Dict[str, Dict[str, Any]] = {
    "cursor-frontend": {
        "focus": ["UI", "React", "CSS", "components"],
        "files": ["*.tsx", "*.jsx", "*.css", "*.scss"],
        "branch": "cursor-frontend",
    },
    "cursor-backend": {
        "focus": ["API", "database", "services", "auth"],
        "files": ["*.py", "routes/*", "services/*"],
        "branch": "cursor-backend",
    },
    "cursor-testing": {
        "focus": ["tests", "QA", "validation", "CI"],
        "files": ["tests/*", "*.test.*", "pytest.ini"],
        "branch": "cursor-testing",
    },
}


def get_worktree_for_task(task: str) -> str:
    """
    [REFACTOR] Determines which worktree should handle a task.

    Analyzes task description to determine the appropriate worktree
    based on keywords and task content.

    Args:
        task (str): Task description.
            Should contain keywords indicating the type of work.

    Returns:
        str: Worktree name (cursor-frontend, cursor-backend, or cursor-testing).
            Defaults to "cursor-backend" if no match.

    Example:
        >>> worktree = get_worktree_for_task("Implement React login component")
        >>> print(worktree)
        cursor-frontend

        >>> worktree = get_worktree_for_task("Add API endpoint for user auth")
        >>> print(worktree)
        cursor-backend

    Algorithm:
        1. Convert task to lowercase
        2. Check for frontend keywords (ui, frontend, react, css, component)
        3. Check for backend keywords (api, database, backend, service)
        4. Check for testing keywords (test, qa, validation, ci)
        5. Return default if no match

    Complexity:
        Time: O(n) where n is task length
        Space: O(1)

    Agent: Antigravity
    Timestamp: 2025-01-27T00:00:00Z
    """
    task_lower = task.lower()

    frontend_keywords = ["ui", "frontend", "react", "css", "component", "tsx", "jsx"]
    backend_keywords = ["api", "database", "backend", "service", "route", "endpoint"]
    testing_keywords = ["test", "qa", "validation", "ci", "pytest", "jest"]

    if any(kw in task_lower for kw in frontend_keywords):
        return "cursor-frontend"
    elif any(kw in task_lower for kw in backend_keywords):
        return "cursor-backend"
    elif any(kw in task_lower for kw in testing_keywords):
        return "cursor-testing"

    return "cursor-backend  # default"


# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

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
