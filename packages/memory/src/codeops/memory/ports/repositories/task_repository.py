"""
Port: Task Repository Interface

Defines the contract for task persistence operations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from codeops.memory.domain.entities import Task, TaskStatus


class TaskRepository(ABC):
    """
    Repository interface for Task entities.

    This port defines the contract that must be implemented by
    any concrete adapter (SQLModel, MongoDB, etc.).
    """

    @abstractmethod
    async def create(self, task: Task) -> Task:
        """
        Create a new task.

        Args:
            task: Task entity to create

        Returns:
            Created task entity

        Raises:
            EntityAlreadyExistsError: If task with same ID already exists
        """
        pass

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """
        Get task by ID.

        Args:
            task_id: Task UUID

        Returns:
            Task entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_agent_id(self, agent_id: UUID) -> List[Task]:
        """
        Get all tasks for an agent.

        Args:
            agent_id: Agent UUID

        Returns:
            List of task entities
        """
        pass

    @abstractmethod
    async def get_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Get tasks by status with pagination.

        Args:
            status: Task status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of task entities
        """
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Get all tasks with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of task entities
        """
        pass

    @abstractmethod
    async def update(self, task: Task) -> Task:
        """
        Update an existing task.

        Args:
            task: Task entity with updated data

        Returns:
            Updated task entity

        Raises:
            EntityNotFoundError: If task doesn't exist
        """
        pass

    @abstractmethod
    async def delete(self, task_id: UUID) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task UUID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, task_id: UUID) -> bool:
        """
        Check if task exists.

        Args:
            task_id: Task UUID

        Returns:
            True if exists, False otherwise
        """
        pass
