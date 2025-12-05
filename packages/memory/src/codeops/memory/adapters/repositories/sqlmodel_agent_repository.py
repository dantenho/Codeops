"""
Adapter: SQLModel Agent Repository Implementation

Concrete implementation of AgentRepository using SQLModel.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Session, SQLModel, select

from codeops.memory.domain.entities import Agent as DomainAgent
from codeops.memory.domain.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from codeops.memory.ports.repositories import AgentRepository


# SQLModel table model (infrastructure concern)
class AgentTable(SQLModel, table=True):
    """SQLModel table for Agent persistence."""
    __tablename__ = "agents"

    id: UUID = Field(primary_key=True)
    name: str = Field(index=True)
    role: str
    goal: str
    backstory: str
    verbose: bool = True
    created_at: datetime
    updated_at: datetime
    task_ids: str = Field(default="")  # Stored as comma-separated UUIDs


class SQLModelAgentRepository(AgentRepository):
    """SQLModel implementation of AgentRepository."""

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def _domain_to_table(self, agent: DomainAgent) -> AgentTable:
        """Convert domain entity to table model."""
        return AgentTable(
            id=agent.id,
            name=agent.name,
            role=agent.role,
            goal=agent.goal,
            backstory=agent.backstory,
            verbose=agent.verbose,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            task_ids=",".join(str(tid) for tid in agent.task_ids) if agent.task_ids else ""
        )

    def _table_to_domain(self, table: AgentTable) -> DomainAgent:
        """Convert table model to domain entity."""
        task_ids = [UUID(tid) for tid in table.task_ids.split(",") if tid] if table.task_ids else []
        return DomainAgent(
            id=table.id,
            name=table.name,
            role=table.role,
            goal=table.goal,
            backstory=table.backstory,
            verbose=table.verbose,
            created_at=table.created_at,
            updated_at=table.updated_at,
            task_ids=task_ids
        )

    async def create(self, agent: DomainAgent) -> DomainAgent:
        """Create a new agent."""
        # Check if agent already exists
        existing = self.session.get(AgentTable, agent.id)
        if existing:
            raise EntityAlreadyExistsError(f"Agent with ID {agent.id} already exists")

        table_agent = self._domain_to_table(agent)
        self.session.add(table_agent)
        self.session.commit()
        self.session.refresh(table_agent)

        return self._table_to_domain(table_agent)

    async def get_by_id(self, agent_id: UUID) -> Optional[DomainAgent]:
        """Get agent by ID."""
        table_agent = self.session.get(AgentTable, agent_id)
        return self._table_to_domain(table_agent) if table_agent else None

    async def get_by_name(self, name: str) -> Optional[DomainAgent]:
        """Get agent by name."""
        statement = select(AgentTable).where(AgentTable.name == name)
        result = self.session.exec(statement).first()
        return self._table_to_domain(result) if result else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[DomainAgent]:
        """Get all agents with pagination."""
        statement = select(AgentTable).offset(skip).limit(limit)
        results = self.session.exec(statement).all()
        return [self._table_to_domain(agent) for agent in results]

    async def update(self, agent: DomainAgent) -> DomainAgent:
        """Update an existing agent."""
        existing = self.session.get(AgentTable, agent.id)
        if not existing:
            raise EntityNotFoundError(f"Agent with ID {agent.id} not found")

        # Update fields
        existing.name = agent.name
        existing.role = agent.role
        existing.goal = agent.goal
        existing.backstory = agent.backstory
        existing.verbose = agent.verbose
        existing.updated_at = datetime.utcnow()
        existing.task_ids = ",".join(str(tid) for tid in agent.task_ids) if agent.task_ids else ""

        self.session.add(existing)
        self.session.commit()
        self.session.refresh(existing)

        return self._table_to_domain(existing)

    async def delete(self, agent_id: UUID) -> bool:
        """Delete an agent."""
        agent = self.session.get(AgentTable, agent_id)
        if not agent:
            return False

        self.session.delete(agent)
        self.session.commit()
        return True

    async def exists(self, agent_id: UUID) -> bool:
        """Check if agent exists."""
        return self.session.get(AgentTable, agent_id) is not None
