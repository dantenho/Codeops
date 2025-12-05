"""
Domain Entity: Agent

This module defines the core Agent entity in the domain layer.
Pure business logic with no infrastructure dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4


@dataclass
class Agent:
    """
    Agent domain entity.

    Represents a conversational agent with specific role and capabilities.
    This is a pure domain entity with no database dependencies.
    """
    name: str
    role: str
    goal: str
    backstory: str
    verbose: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    task_ids: List[UUID] = field(default_factory=list)

    def __post_init__(self):
        """Validate agent data on initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Agent name cannot be empty")
        if not self.role or not self.role.strip():
            raise ValueError("Agent role cannot be empty")
        if not self.goal or not self.goal.strip():
            raise ValueError("Agent goal cannot be empty")

    def update_info(self, name: Optional[str] = None, role: Optional[str] = None,
                    goal: Optional[str] = None, backstory: Optional[str] = None) -> None:
        """Update agent information."""
        if name is not None:
            if not name.strip():
                raise ValueError("Agent name cannot be empty")
            self.name = name
        if role is not None:
            if not role.strip():
                raise ValueError("Agent role cannot be empty")
            self.role = role
        if goal is not None:
            if not goal.strip():
                raise ValueError("Agent goal cannot be empty")
            self.goal = goal
        if backstory is not None:
            self.backstory = backstory

        self.updated_at = datetime.utcnow()

    def assign_task(self, task_id: UUID) -> None:
        """Assign a task to this agent."""
        if task_id not in self.task_ids:
            self.task_ids.append(task_id)
            self.updated_at = datetime.utcnow()

    def remove_task(self, task_id: UUID) -> None:
        """Remove a task from this agent."""
        if task_id in self.task_ids:
            self.task_ids.remove(task_id)
            self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert agent to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "verbose": self.verbose,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "task_ids": [str(tid) for tid in self.task_ids]
        }
