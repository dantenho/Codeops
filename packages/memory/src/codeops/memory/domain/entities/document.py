"""
Domain Entity: Document

This module defines the core Document entity for RAG operations.
Pure business logic with no infrastructure dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


@dataclass
class Document:
    """
    Document domain entity.

    Represents a document stored in the vector database for RAG operations.
    This is a pure domain entity with no database dependencies.
    """
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    embedding: Optional[list] = None

    def __post_init__(self):
        """Validate document data on initialization."""
        if not self.content or not self.content.strip():
            raise ValueError("Document content cannot be empty")

    def update_content(self, content: str) -> None:
        """Update document content."""
        if not content or not content.strip():
            raise ValueError("Document content cannot be empty")
        self.content = content
        self.embedding = None  # Clear embedding when content changes
        self.updated_at = datetime.utcnow()

    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update document metadata."""
        self.metadata.update(metadata)
        self.updated_at = datetime.utcnow()

    def set_embedding(self, embedding: list) -> None:
        """Set document embedding vector."""
        if not embedding:
            raise ValueError("Embedding cannot be empty")
        self.embedding = embedding
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert document to dictionary representation."""
        return {
            "id": str(self.id),
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "has_embedding": self.embedding is not None
        }
