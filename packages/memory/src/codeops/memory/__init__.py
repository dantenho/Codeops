"""
Memory Package - Octagonal Architecture

This package implements an octagonal (hexagonal/clean) architecture for
database and vector store operations.

Architecture Layers:
1. Domain - Core business entities and logic (Agent, Task, Document)
2. Application - Use cases orchestrating business operations
3. Ports - Interfaces defining contracts for repositories and services
4. Adapters - Concrete implementations of ports
5. Infrastructure - Database connections and external system integrations
6. Configuration - Dependency injection and settings management
7-8. Shared - Common types and utilities

Usage Example:
    from codeops.memory import DependencyContainer

    # Initialize container
    container = DependencyContainer(
        database_url="sqlite:///./memory.db",
        chroma_path="./chroma_db"
    )
    container.initialize_database()

    # Use agent operations
    with container.get_session_manager().get_session() as session:
        create_agent = container.get_create_agent_use_case(session)
        agent = await create_agent.execute(
            name="CodeAgent",
            role="Developer",
            goal="Write clean code",
            backstory="Expert in software architecture"
        )

    # Use RAG operations
    ingest_docs = container.get_ingest_documents_use_case()
    await ingest_docs.execute(
        contents=["Document 1", "Document 2"],
        metadatas=[{"source": "file1"}, {"source": "file2"}]
    )

    search_docs = container.get_search_documents_use_case()
    results = await search_docs.execute("query text", n_results=5)
"""

# Main API exports
from .configuration.dependency_injection import DependencyContainer
from .configuration.settings import MemorySettings, settings

# Domain entities (for type hints and direct usage)
from .domain.entities import Agent, Document, Task, TaskStatus
from .domain.exceptions import (
    BusinessRuleViolationError,
    DomainException,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidEntityStateError,
    ValidationError,
)
from .domain.value_objects.embedding import Embedding

# Infrastructure exports
from .infrastructure.database.connection import DatabaseConnection
from .infrastructure.database.session import SessionManager

__version__ = "2.0.0-octagonal"

__all__ = [
    # Main container
    "DependencyContainer",
    # Settings
    "MemorySettings",
    "settings",
    # Domain entities
    "Agent",
    "Task",
    "TaskStatus",
    "Document",
    "Embedding",
    # Domain exceptions
    "DomainException",
    "EntityNotFoundError",
    "EntityAlreadyExistsError",
    "InvalidEntityStateError",
    "ValidationError",
    "BusinessRuleViolationError",
    # Infrastructure
    "DatabaseConnection",
    "SessionManager",
]
