"""
Application Layer: Agent Use Cases

Business logic for agent management operations.
"""
from typing import List, Optional
from uuid import UUID

from codeops.memory.domain.entities import Agent
from codeops.memory.domain.exceptions import EntityNotFoundError
from codeops.memory.ports.repositories import AgentRepository


class CreateAgentUseCase:
    """Use case for creating a new agent."""

    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository

    async def execute(self, name: str, role: str, goal: str,
                      backstory: str, verbose: bool = True) -> Agent:
        """
        Create a new agent.

        Args:
            name: Agent name
            role: Agent role
            goal: Agent goal
            backstory: Agent backstory
            verbose: Whether agent is verbose

        Returns:
            Created agent entity

        Raises:
            EntityAlreadyExistsError: If agent with same ID already exists
            ValidationError: If validation fails
        """
        agent = Agent(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=verbose
        )
        return await self.agent_repository.create(agent)


class GetAgentUseCase:
    """Use case for retrieving an agent."""

    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository

    async def execute(self, agent_id: UUID) -> Agent:
        """
        Get agent by ID.

        Args:
            agent_id: Agent UUID

        Returns:
            Agent entity

        Raises:
            EntityNotFoundError: If agent not found
        """
        agent = await self.agent_repository.get_by_id(agent_id)
        if not agent:
            raise EntityNotFoundError(f"Agent with ID {agent_id} not found")
        return agent


class ListAgentsUseCase:
    """Use case for listing agents."""

    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """
        List all agents with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of agent entities
        """
        return await self.agent_repository.get_all(skip=skip, limit=limit)


class UpdateAgentUseCase:
    """Use case for updating an agent."""

    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository

    async def execute(self, agent_id: UUID, name: Optional[str] = None,
                      role: Optional[str] = None, goal: Optional[str] = None,
                      backstory: Optional[str] = None) -> Agent:
        """
        Update an agent.

        Args:
            agent_id: Agent UUID
            name: New name (optional)
            role: New role (optional)
            goal: New goal (optional)
            backstory: New backstory (optional)

        Returns:
            Updated agent entity

        Raises:
            EntityNotFoundError: If agent not found
            ValidationError: If validation fails
        """
        agent = await self.agent_repository.get_by_id(agent_id)
        if not agent:
            raise EntityNotFoundError(f"Agent with ID {agent_id} not found")

        agent.update_info(name=name, role=role, goal=goal, backstory=backstory)
        return await self.agent_repository.update(agent)


class DeleteAgentUseCase:
    """Use case for deleting an agent."""

    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository

    async def execute(self, agent_id: UUID) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent UUID

        Returns:
            True if deleted, False if not found
        """
        return await self.agent_repository.delete(agent_id)


class AssignTaskToAgentUseCase:
    """Use case for assigning a task to an agent."""

    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository

    async def execute(self, agent_id: UUID, task_id: UUID) -> Agent:
        """
        Assign a task to an agent.

        Args:
            agent_id: Agent UUID
            task_id: Task UUID

        Returns:
            Updated agent entity

        Raises:
            EntityNotFoundError: If agent not found
        """
        agent = await self.agent_repository.get_by_id(agent_id)
        if not agent:
            raise EntityNotFoundError(f"Agent with ID {agent_id} not found")

        agent.assign_task(task_id)
        return await self.agent_repository.update(agent)
