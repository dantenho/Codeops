"""
Port: Vector Repository Interface

Defines the contract for vector database operations (RAG).
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from codeops.memory.domain.entities import Document


class VectorRepository(ABC):
    """
    Repository interface for vector database operations.

    This port defines the contract for RAG operations that must be implemented
    by concrete adapters (Chroma, FAISS, Pinecone, etc.).
    """

    @abstractmethod
    async def add_document(self, document: Document) -> None:
        """
        Add a single document to the vector store.

        Args:
            document: Document entity to add

        Raises:
            ValueError: If document has no embedding
        """
        pass

    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> None:
        """
        Add multiple documents to the vector store.

        Args:
            documents: List of document entities to add

        Raises:
            ValueError: If any document has no embedding
        """
        pass

    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """
        Get document by ID.

        Args:
            document_id: Document UUID

        Returns:
            Document entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using embedding.

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return

        Returns:
            List of search results with documents, metadata, and distances
        """
        pass

    @abstractmethod
    async def search_by_text(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using text query.

        The implementation should handle embedding generation.

        Args:
            query_text: Query text
            n_results: Number of results to return

        Returns:
            List of search results with documents, metadata, and distances
        """
        pass

    @abstractmethod
    async def delete(self, document_id: UUID) -> bool:
        """
        Delete a document.

        Args:
            document_id: Document UUID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def delete_many(self, document_ids: List[UUID]) -> int:
        """
        Delete multiple documents.

        Args:
            document_ids: List of document UUIDs

        Returns:
            Number of documents deleted
        """
        pass

    @abstractmethod
    async def clear(self) -> None:
        """
        Clear all documents from the vector store.

        Warning: This operation cannot be undone.
        """
        pass

    @abstractmethod
    async def count(self) -> int:
        """
        Get total count of documents in the vector store.

        Returns:
            Number of documents
        """
        pass
