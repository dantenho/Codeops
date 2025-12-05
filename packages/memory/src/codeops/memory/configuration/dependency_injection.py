"""
Configuration Layer: Dependency Injection Container

Manages dependencies and provides instances of repositories, services, and use cases.
"""
from typing import Optional

from sqlmodel import Session

from codeops.memory.adapters.repositories import (
    ChromaVectorRepository,
    SQLModelAgentRepository,
    SQLModelTaskRepository,
)
from codeops.memory.adapters.services import SentenceTransformerEmbeddingService
from codeops.memory.application.use_cases.agent_use_cases import (
    AssignTaskToAgentUseCase,
    CreateAgentUseCase,
    DeleteAgentUseCase,
    GetAgentUseCase,
    ListAgentsUseCase,
    UpdateAgentUseCase,
)
from codeops.memory.application.use_cases.rag_use_cases import (
    ClearVectorStoreUseCase,
    DeleteDocumentsUseCase,
    GetDocumentUseCase,
    IngestDocumentsUseCase,
    SearchDocumentsUseCase,
)
from codeops.memory.infrastructure.database.connection import DatabaseConnection
from codeops.memory.infrastructure.database.session import SessionManager
from codeops.memory.ports.repositories import (
    AgentRepository,
    TaskRepository,
    VectorRepository,
)
from codeops.memory.ports.services import EmbeddingServicePort


class DependencyContainer:
    """
    Dependency injection container for the memory package.

    Provides centralized configuration and initialization of all dependencies.
    """

    def __init__(
        self,
        database_url: str = "sqlite:///./memory.db",
        chroma_path: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
        echo_sql: bool = False,
    ):
        """
        Initialize dependency container.

        Args:
            database_url: Database connection URL
            chroma_path: Path for ChromaDB persistence
            embedding_model: Name of the embedding model
            echo_sql: Whether to echo SQL statements
        """
        # Infrastructure
        self._db_connection = DatabaseConnection(database_url, echo=echo_sql)
        self._session_manager = SessionManager(self._db_connection)

        # Services
        self._embedding_service: Optional[EmbeddingServicePort] = None

        # Repositories
        self._agent_repository: Optional[AgentRepository] = None
        self._task_repository: Optional[TaskRepository] = None
        self._vector_repository: Optional[VectorRepository] = None

        # Configuration
        self._chroma_path = chroma_path
        self._embedding_model = embedding_model

    def initialize_database(self):
        """Initialize database tables."""
        self._db_connection.create_tables()

    def get_db_connection(self) -> DatabaseConnection:
        """Get database connection."""
        return self._db_connection

    def get_session_manager(self) -> SessionManager:
        """Get session manager."""
        return self._session_manager

    def get_session(self) -> Session:
        """Get a new database session."""
        return self._session_manager.create_session()

    def get_embedding_service(self) -> EmbeddingServicePort:
        """Get embedding service (singleton)."""
        if self._embedding_service is None:
            self._embedding_service = SentenceTransformerEmbeddingService(
                model_name=self._embedding_model
            )
        return self._embedding_service

    def get_agent_repository(self, session: Session) -> AgentRepository:
        """
        Get agent repository.

        Args:
            session: Database session

        Returns:
            Agent repository instance
        """
        return SQLModelAgentRepository(session)

    def get_task_repository(self, session: Session) -> TaskRepository:
        """
        Get task repository.

        Args:
            session: Database session

        Returns:
            Task repository instance
        """
        return SQLModelTaskRepository(session)

    def get_vector_repository(self) -> VectorRepository:
        """Get vector repository (singleton)."""
        if self._vector_repository is None:
            self._vector_repository = ChromaVectorRepository(
                embedding_service=self.get_embedding_service(),
                persist_path=self._chroma_path,
            )
        return self._vector_repository

    # Use case factories
    def get_create_agent_use_case(self, session: Session) -> CreateAgentUseCase:
        """Get create agent use case."""
        return CreateAgentUseCase(self.get_agent_repository(session))

    def get_get_agent_use_case(self, session: Session) -> GetAgentUseCase:
        """Get agent retrieval use case."""
        return GetAgentUseCase(self.get_agent_repository(session))

    def get_list_agents_use_case(self, session: Session) -> ListAgentsUseCase:
        """Get list agents use case."""
        return ListAgentsUseCase(self.get_agent_repository(session))

    def get_update_agent_use_case(self, session: Session) -> UpdateAgentUseCase:
        """Get update agent use case."""
        return UpdateAgentUseCase(self.get_agent_repository(session))

    def get_delete_agent_use_case(self, session: Session) -> DeleteAgentUseCase:
        """Get delete agent use case."""
        return DeleteAgentUseCase(self.get_agent_repository(session))

    def get_assign_task_use_case(self, session: Session) -> AssignTaskToAgentUseCase:
        """Get assign task to agent use case."""
        return AssignTaskToAgentUseCase(self.get_agent_repository(session))

    def get_ingest_documents_use_case(self) -> IngestDocumentsUseCase:
        """Get ingest documents use case."""
        return IngestDocumentsUseCase(
            self.get_vector_repository(), self.get_embedding_service()
        )

    def get_search_documents_use_case(self) -> SearchDocumentsUseCase:
        """Get search documents use case."""
        return SearchDocumentsUseCase(self.get_vector_repository())

    def get_get_document_use_case(self) -> GetDocumentUseCase:
        """Get document retrieval use case."""
        return GetDocumentUseCase(self.get_vector_repository())

    def get_delete_documents_use_case(self) -> DeleteDocumentsUseCase:
        """Get delete documents use case."""
        return DeleteDocumentsUseCase(self.get_vector_repository())

    def get_clear_vector_store_use_case(self) -> ClearVectorStoreUseCase:
        """Get clear vector store use case."""
        return ClearVectorStoreUseCase(self.get_vector_repository())
