"""
Domain Entity: Task

This module defines the core Task entity in the domain layer.
Pure business logic with no infrastructure dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """
    Task domain entity.

    Represents a task assigned to an agent.
    This is a pure domain entity with no database dependencies.
    """
    description: str
    expected_output: str
    agent_id: Optional[UUID] = None
    status: TaskStatus = TaskStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    result: Optional[str] = None

    def __post_init__(self):
        """Validate task data on initialization."""
        if not self.description or not self.description.strip():
            raise ValueError("Task description cannot be empty")
        if not self.expected_output or not self.expected_output.strip():
            raise ValueError("Task expected output cannot be empty")

        # Convert string status to enum if needed
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)

    def start(self) -> None:
        """Mark task as running."""
        if self.status != TaskStatus.PENDING:
            raise ValueError(f"Cannot start task in {self.status} status")
        self.status = TaskStatus.RUNNING
        self.updated_at = datetime.utcnow()

    def complete(self, result: str) -> None:
        """Mark task as completed with result."""
        if self.status != TaskStatus.RUNNING:
            raise ValueError(f"Cannot complete task in {self.status} status")
        if not result or not result.strip():
            raise ValueError("Task result cannot be empty")
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.updated_at = datetime.utcnow()

    def fail(self, error: str) -> None:
        """Mark task as failed."""
        if self.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            raise ValueError(f"Cannot fail task in {self.status} status")
        self.status = TaskStatus.FAILED
        self.result = f"Error: {error}"
        self.updated_at = datetime.utcnow()

    def assign_to_agent(self, agent_id: UUID) -> None:
        """Assign task to an agent."""
        self.agent_id = agent_id
        self.updated_at = datetime.utcnow()

    def unassign(self) -> None:
        """Remove agent assignment."""
        if self.status == TaskStatus.RUNNING:
            raise ValueError("Cannot unassign a running task")
        self.agent_id = None
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert task to dictionary representation."""
        return {
            "id": str(self.id),
            "description": self.description,
            "expected_output": self.expected_output,
            "status": self.status.value,
            "agent_id": str(self.agent_id) if self.agent_id else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "result": self.result
        }
