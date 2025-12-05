# Octagonal Architecture Documentation

## Overview

This memory package has been restructured using an **Octagonal Skeleton Architecture**, which is an evolution of the hexagonal (ports and adapters) architecture with additional organizational layers.

## Architecture Layers

### 1. Domain Layer (`domain/`)
**Pure business logic with zero external dependencies**

- **Entities** (`domain/entities/`):
  - `Agent` - Conversational agent entity
  - `Task` - Task entity with status management
  - `Document` - Document entity for RAG operations

- **Value Objects** (`domain/value_objects/`):
  - `Embedding` - Immutable embedding vector representation

- **Exceptions** (`domain/exceptions.py`):
  - Custom domain exceptions for business rule violations

**Key Principles:**
- No database dependencies
- No framework dependencies
- Pure Python business logic
- Domain entities contain business rules

### 2. Application Layer (`application/`)
**Orchestrates business operations using domain entities**

- **Use Cases** (`application/use_cases/`):
  - `agent_use_cases.py` - Create, Read, Update, Delete operations for agents
  - `rag_use_cases.py` - Document ingestion and search operations

**Key Principles:**
- Coordinates between domain and ports
- Implements application-specific workflows
- No knowledge of specific adapters

### 3. Ports Layer (`ports/`)
**Interfaces defining contracts**

- **Repository Ports** (`ports/repositories/`):
  - `AgentRepository` - Agent persistence interface
  - `TaskRepository` - Task persistence interface
  - `VectorRepository` - Vector database interface

- **Service Ports** (`ports/services/`):
  - `EmbeddingServicePort` - Embedding generation interface

**Key Principles:**
- Abstract interfaces only
- Define what operations are needed, not how they're implemented
- Enable dependency inversion

### 4. Adapters Layer (`adapters/`)
**Concrete implementations of ports**

- **Repository Adapters** (`adapters/repositories/`):
  - `SQLModelAgentRepository` - SQLModel implementation for agents
  - `SQLModelTaskRepository` - SQLModel implementation for tasks
  - `ChromaVectorRepository` - ChromaDB implementation for vectors

- **Service Adapters** (`adapters/services/`):
  - `SentenceTransformerEmbeddingService` - SentenceTransformers implementation

**Key Principles:**
- Implement port interfaces
- Handle external system integration
- Can be swapped without affecting core business logic

### 5. Infrastructure Layer (`infrastructure/`)
**External system connections and technical concerns**

- **Database** (`infrastructure/database/`):
  - `connection.py` - Database engine management
  - `session.py` - Session lifecycle management

- **Vector Database** (`infrastructure/vector_db/`):
  - (Future) Specific vector database clients

**Key Principles:**
- Manages connections to external systems
- Handles technical infrastructure concerns
- Configuration of external dependencies

### 6. Configuration Layer (`configuration/`)
**Dependency injection and application setup**

- `dependency_injection.py` - DI container managing all dependencies
- `settings.py` - Application settings from environment

**Key Principles:**
- Central configuration point
- Wires together all dependencies
- Environment-based configuration

### 7-8. Shared Layer (`shared/`)
**Cross-cutting concerns and utilities**

- `types.py` - Common type definitions
- `utils.py` - Utility functions

**Key Principles:**
- Reusable across all layers
- No business logic
- Helper functions and types

## Dependency Flow

```
┌─────────────────────────────────────────────────┐
│         Configuration / DI Container             │
│  (Wires everything together)                    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Application (Use Cases)                 │
│  Orchestrates business operations               │
└────────────┬────────────────────┬────────────────┘
             │                    │
             ▼                    ▼
┌─────────────────────┐  ┌──────────────────────┐
│   Domain Entities    │  │   Ports (Interfaces) │
│  (Business Logic)    │  │   Repository & Services│
└─────────────────────┘  └──────────┬────────────┘
                                     │
                                     ▼
                         ┌──────────────────────┐
                         │   Adapters            │
                         │  (Implementations)    │
                         └──────────┬────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Infrastructure      │
                         │  (External Systems)   │
                         └──────────────────────┘
```

## Benefits

1. **Separation of Concerns**: Each layer has a single, well-defined responsibility
2. **Testability**: Easy to test each layer in isolation with mocks
3. **Flexibility**: Can swap implementations without changing business logic
4. **Maintainability**: Clear structure makes code easier to understand and modify
5. **Scalability**: Easy to add new features or change technologies
6. **Technology Independence**: Core business logic doesn't depend on frameworks

## Usage Example

```python
from codeops.memory import DependencyContainer

# Initialize the container
container = DependencyContainer(
    database_url="sqlite:///./memory.db",
    chroma_path="./chroma_db",
    embedding_model="all-MiniLM-L6-v2"
)

# Initialize database tables
container.initialize_database()

# Agent Operations
with container.get_session_manager().get_session() as session:
    # Create an agent
    create_agent_uc = container.get_create_agent_use_case(session)
    agent = await create_agent_uc.execute(
        name="CodeAgent",
        role="Software Developer",
        goal="Write clean, maintainable code",
        backstory="Expert in software architecture"
    )

    # List agents
    list_agents_uc = container.get_list_agents_use_case(session)
    agents = await list_agents_uc.execute(skip=0, limit=10)

# RAG Operations (no session needed for vector operations)
# Ingest documents
ingest_uc = container.get_ingest_documents_use_case()
docs = await ingest_uc.execute(
    contents=["First document", "Second document"],
    metadatas=[{"source": "file1.txt"}, {"source": "file2.txt"}]
)

# Search documents
search_uc = container.get_search_documents_use_case()
results = await search_uc.execute("query text", n_results=5)
```

## Migration from Old Architecture

The old architecture mixed concerns:
- Database models contained business logic
- Direct database dependencies throughout
- No clear separation between layers
- Hard to test and modify

The new octagonal architecture provides:
- Clear separation of domain logic
- Abstracted persistence through ports
- Easy to swap implementations
- Highly testable
- Framework-independent core

## Testing Strategy

1. **Domain Layer**: Pure unit tests, no mocks needed
2. **Application Layer**: Test use cases with mock repositories
3. **Ports Layer**: Interface contracts (no implementation to test)
4. **Adapters Layer**: Integration tests with real or test databases
5. **Infrastructure Layer**: Integration tests
6. **Configuration Layer**: Configuration tests

## Future Enhancements

- Add event sourcing in domain layer
- Implement CQRS pattern
- Add domain events for cross-cutting concerns
- Support multiple vector databases (FAISS, Pinecone, etc.)
- Add caching layer
- Implement audit logging

## References

- Hexagonal Architecture (Ports and Adapters) - Alistair Cockburn
- Clean Architecture - Robert C. Martin
- Domain-Driven Design - Eric Evans
