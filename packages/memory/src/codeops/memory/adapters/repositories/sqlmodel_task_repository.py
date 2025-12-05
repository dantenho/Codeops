"""
Adapter: SQLModel Task Repository Implementation

Concrete implementation of TaskRepository using SQLModel.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Session, SQLModel, select

from codeops.memory.domain.entities import Task as DomainTask, TaskStatus
from codeops.memory.domain.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from codeops.memory.ports.repositories import TaskRepository


# SQLModel table model (infrastructure concern)
class TaskTable(SQLModel, table=True):
    """SQLModel table for Task persistence."""
    __tablename__ = "tasks"

    id: UUID = Field(primary_key=True)
    description: str
    expected_output: str
    status: str = Field(default="pending")
    agent_id: Optional[UUID] = Field(default=None, foreign_key="agents.id")
    created_at: datetime
    updated_at: datetime
    result: Optional[str] = None


class SQLModelTaskRepository(TaskRepository):
    """SQLModel implementation of TaskRepository."""

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def _domain_to_table(self, task: DomainTask) -> TaskTable:
        """Convert domain entity to table model."""
        return TaskTable(
            id=task.id,
            description=task.description,
            expected_output=task.expected_output,
            status=task.status.value,
            agent_id=task.agent_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            result=task.result
        )

    def _table_to_domain(self, table: TaskTable) -> DomainTask:
        """Convert table model to domain entity."""
        return DomainTask(
            id=table.id,
            description=table.description,
            expected_output=table.expected_output,
            status=TaskStatus(table.status),
            agent_id=table.agent_id,
            created_at=table.created_at,
            updated_at=table.updated_at,
            result=table.result
        )

    async def create(self, task: DomainTask) -> DomainTask:
        """Create a new task."""
        # Check if task already exists
        existing = self.session.get(TaskTable, task.id)
        if existing:
            raise EntityAlreadyExistsError(f"Task with ID {task.id} already exists")

        table_task = self._domain_to_table(task)
        self.session.add(table_task)
        self.session.commit()
        self.session.refresh(table_task)

        return self._table_to_domain(table_task)

    async def get_by_id(self, task_id: UUID) -> Optional[DomainTask]:
        """Get task by ID."""
        table_task = self.session.get(TaskTable, task_id)
        return self._table_to_domain(table_task) if table_task else None

    async def get_by_agent_id(self, agent_id: UUID) -> List[DomainTask]:
        """Get all tasks for an agent."""
        statement = select(TaskTable).where(TaskTable.agent_id == agent_id)
        results = self.session.exec(statement).all()
        return [self._table_to_domain(task) for task in results]

    async def get_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[DomainTask]:
        """Get tasks by status with pagination."""
        statement = select(TaskTable).where(TaskTable.status == status.value).offset(skip).limit(limit)
        results = self.session.exec(statement).all()
        return [self._table_to_domain(task) for task in results]

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[DomainTask]:
        """Get all tasks with pagination."""
        statement = select(TaskTable).offset(skip).limit(limit)
        results = self.session.exec(statement).all()
        return [self._table_to_domain(task) for task in results]

    async def update(self, task: DomainTask) -> DomainTask:
        """Update an existing task."""
        existing = self.session.get(TaskTable, task.id)
        if not existing:
            raise EntityNotFoundError(f"Task with ID {task.id} not found")

        # Update fields
        existing.description = task.description
        existing.expected_output = task.expected_output
        existing.status = task.status.value
        existing.agent_id = task.agent_id
        existing.updated_at = datetime.utcnow()
        existing.result = task.result

        self.session.add(existing)
        self.session.commit()
        self.session.refresh(existing)

        return self._table_to_domain(existing)

    async def delete(self, task_id: UUID) -> bool:
        """Delete a task."""
        task = self.session.get(TaskTable, task_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True

    async def exists(self, task_id: UUID) -> bool:
        """Check if task exists."""
        return self.session.get(TaskTable, task_id) is not None
