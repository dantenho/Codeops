import uuid
from typing import Any, Dict, List, Optional

from codeops.memory.vector_store import VectorStoreBase, get_vector_store


class RAGEngine:
    """
    Retrieval-Augmented Generation (RAG) Engine.
    Orchestrates retrieval from VectorStore and (future) generation.
    """

    def __init__(self, vector_store_type: str = "chroma"):
        """
        Initialize the RAG Engine.

        Args:
            vector_store_type: Type of vector store to use ("chroma" or "faiss")
        """
        self.vector_store: VectorStoreBase = get_vector_store(vector_store_type)

    def ingest(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None) -> None:
        """
        Ingest documents into the vector store.

        Args:
            documents: List of text documents
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs (auto-generated if None)
        """
        if not documents:
            return

        if metadatas is None:
            metadatas = [{} for _ in documents]

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        self.vector_store.add_documents(documents, metadatas, ids)

    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Search for relevant documents.

        Args:
            query_text: The query string
            n_results: Number of results to return

        Returns:
            Dict containing search results (ids, documents, metadatas, distances)
        """
        return self.vector_store.search(query_text, n_results)
