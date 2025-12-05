"""
Adapter: ChromaDB Vector Repository Implementation

Concrete implementation of VectorRepository using ChromaDB.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

import chromadb
from chromadb.config import Settings

from codeops.memory.domain.entities import Document
from codeops.memory.domain.exceptions import EntityNotFoundError
from codeops.memory.ports.repositories import VectorRepository
from codeops.memory.ports.services import EmbeddingServicePort


class ChromaVectorRepository(VectorRepository):
    """ChromaDB implementation of VectorRepository."""

    def __init__(self, embedding_service: EmbeddingServicePort,
                 persist_path: str = "./chroma_db",
                 collection_name: str = "documents"):
        """
        Initialize ChromaDB repository.

        Args:
            embedding_service: Service for generating embeddings
            persist_path: Path to persist ChromaDB data
            collection_name: Name of the collection
        """
        self.embedding_service = embedding_service
        self.client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)

    async def add_document(self, document: Document) -> None:
        """Add a single document to the vector store."""
        if not document.embedding:
            raise ValueError("Document must have an embedding before adding to vector store")

        self.collection.add(
            ids=[str(document.id)],
            documents=[document.content],
            metadatas=[document.metadata],
            embeddings=[document.embedding]
        )

    async def add_documents(self, documents: List[Document]) -> None:
        """Add multiple documents to the vector store."""
        if not all(doc.embedding for doc in documents):
            raise ValueError("All documents must have embeddings before adding to vector store")

        self.collection.add(
            ids=[str(doc.id) for doc in documents],
            documents=[doc.content for doc in documents],
            metadatas=[doc.metadata for doc in documents],
            embeddings=[doc.embedding for doc in documents]
        )

    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        try:
            result = self.collection.get(ids=[str(document_id)])
            if not result["ids"]:
                return None

            # Reconstruct document from ChromaDB data
            doc = Document(
                id=UUID(result["ids"][0]),
                content=result["documents"][0],
                metadata=result["metadatas"][0] if result["metadatas"] else {}
            )
            if result.get("embeddings"):
                doc.embedding = result["embeddings"][0]

            return doc
        except Exception:
            return None

    async def search(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using embedding."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        # Transform results into list of dicts
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                search_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i] if results["documents"] else None,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results.get("distances") else None
                })

        return search_results

    async def search_by_text(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using text query."""
        # Generate embedding for query text
        embedding_obj = await self.embedding_service.generate_embedding(query_text)
        query_embedding = embedding_obj.to_list()

        return await self.search(query_embedding, n_results)

    async def delete(self, document_id: UUID) -> bool:
        """Delete a document."""
        try:
            self.collection.delete(ids=[str(document_id)])
            return True
        except Exception:
            return False

    async def delete_many(self, document_ids: List[UUID]) -> int:
        """Delete multiple documents."""
        try:
            ids_to_delete = [str(doc_id) for doc_id in document_ids]
            self.collection.delete(ids=ids_to_delete)
            return len(ids_to_delete)
        except Exception:
            return 0

    async def clear(self) -> None:
        """Clear all documents from the vector store."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(name=self.collection.name)

    async def count(self) -> int:
        """Get total count of documents in the vector store."""
        return self.collection.count()
