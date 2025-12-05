from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class AgentBase(SQLModel):
    """Base model for Agent configuration."""
    name: str = Field(index=True)
    role: str
    goal: str
    backstory: str
    verbose: bool = True

class Agent(AgentBase, table=True):
    """Agent database model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: List["Task"] = Relationship(back_populates="agent")

class TaskBase(SQLModel):
    """Base model for Task configuration."""
    description: str
    expected_output: str
    status: str = Field(default="pending") # pending, running, completed, failed
    agent_id: Optional[UUID] = Field(default=None, foreign_key="agent.id")

class Task(TaskBase, table=True):
    """Task database model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[str] = None

    agent: Optional[Agent] = Relationship(back_populates="tasks")
