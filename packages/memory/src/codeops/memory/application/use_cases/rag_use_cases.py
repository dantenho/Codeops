"""
Application Layer: RAG Use Cases

Business logic for RAG (Retrieval-Augmented Generation) operations.
"""
from typing import Any, Dict, List
from uuid import UUID

from codeops.memory.domain.entities import Document
from codeops.memory.ports.repositories import VectorRepository
from codeops.memory.ports.services import EmbeddingServicePort


class IngestDocumentsUseCase:
    """Use case for ingesting documents into the vector store."""

    def __init__(self, vector_repository: VectorRepository,
                 embedding_service: EmbeddingServicePort):
        self.vector_repository = vector_repository
        self.embedding_service = embedding_service

    async def execute(self, contents: List[str],
                      metadatas: List[Dict[str, Any]] = None) -> List[Document]:
        """
        Ingest multiple documents into the vector store.

        Args:
            contents: List of document contents
            metadatas: Optional list of metadata dicts

        Returns:
            List of created document entities

        Raises:
            ValueError: If validation fails
        """
        if not contents:
            raise ValueError("Contents list cannot be empty")

        if metadatas is None:
            metadatas = [{} for _ in contents]

        if len(metadatas) != len(contents):
            raise ValueError("Metadatas and contents must have the same length")

        # Create document entities
        documents = [
            Document(content=content, metadata=metadata)
            for content, metadata in zip(contents, metadatas)
        ]

        # Generate embeddings for all documents
        embeddings = await self.embedding_service.generate_embeddings(
            [doc.content for doc in documents]
        )

        # Set embeddings on documents
        for doc, embedding in zip(documents, embeddings):
            doc.set_embedding(embedding.to_list())

        # Add documents to vector store
        await self.vector_repository.add_documents(documents)

        return documents


class SearchDocumentsUseCase:
    """Use case for searching similar documents."""

    def __init__(self, vector_repository: VectorRepository):
        self.vector_repository = vector_repository

    async def execute(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using text query.

        Args:
            query_text: Query text
            n_results: Number of results to return

        Returns:
            List of search results with documents, metadata, and distances

        Raises:
            ValueError: If validation fails
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")

        if n_results <= 0:
            raise ValueError("n_results must be positive")

        return await self.vector_repository.search_by_text(query_text, n_results)


class GetDocumentUseCase:
    """Use case for retrieving a document by ID."""

    def __init__(self, vector_repository: VectorRepository):
        self.vector_repository = vector_repository

    async def execute(self, document_id: UUID) -> Document:
        """
        Get document by ID.

        Args:
            document_id: Document UUID

        Returns:
            Document entity

        Raises:
            EntityNotFoundError: If document not found
        """
        from codeops.memory.domain.exceptions import EntityNotFoundError

        document = await self.vector_repository.get_by_id(document_id)
        if not document:
            raise EntityNotFoundError(f"Document with ID {document_id} not found")
        return document


class DeleteDocumentsUseCase:
    """Use case for deleting documents."""

    def __init__(self, vector_repository: VectorRepository):
        self.vector_repository = vector_repository

    async def execute(self, document_ids: List[UUID]) -> int:
        """
        Delete multiple documents.

        Args:
            document_ids: List of document UUIDs

        Returns:
            Number of documents deleted
        """
        if not document_ids:
            raise ValueError("Document IDs list cannot be empty")

        return await self.vector_repository.delete_many(document_ids)


class ClearVectorStoreUseCase:
    """Use case for clearing the entire vector store."""

    def __init__(self, vector_repository: VectorRepository):
        self.vector_repository = vector_repository

    async def execute(self) -> None:
        """
        Clear all documents from the vector store.

        Warning: This operation cannot be undone.
        """
        await self.vector_repository.clear()
