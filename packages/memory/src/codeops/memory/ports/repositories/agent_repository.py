"""
Port: Agent Repository Interface

Defines the contract for agent persistence operations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from codeops.memory.domain.entities import Agent


class AgentRepository(ABC):
    """
    Repository interface for Agent entities.

    This port defines the contract that must be implemented by
    any concrete adapter (SQLModel, MongoDB, etc.).
    """

    @abstractmethod
    async def create(self, agent: Agent) -> Agent:
        """
        Create a new agent.

        Args:
            agent: Agent entity to create

        Returns:
            Created agent entity

        Raises:
            EntityAlreadyExistsError: If agent with same ID already exists
        """
        pass

    @abstractmethod
    async def get_by_id(self, agent_id: UUID) -> Optional[Agent]:
        """
        Get agent by ID.

        Args:
            agent_id: Agent UUID

        Returns:
            Agent entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Agent]:
        """
        Get agent by name.

        Args:
            name: Agent name

        Returns:
            Agent entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """
        Get all agents with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of agent entities
        """
        pass

    @abstractmethod
    async def update(self, agent: Agent) -> Agent:
        """
        Update an existing agent.

        Args:
            agent: Agent entity with updated data

        Returns:
            Updated agent entity

        Raises:
            EntityNotFoundError: If agent doesn't exist
        """
        pass

    @abstractmethod
    async def delete(self, agent_id: UUID) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent UUID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, agent_id: UUID) -> bool:
        """
        Check if agent exists.

        Args:
            agent_id: Agent UUID

        Returns:
            True if exists, False otherwise
        """
        pass
