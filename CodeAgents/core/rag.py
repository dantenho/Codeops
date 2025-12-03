"""
Module: rag.py
Purpose: RAG system using ChromaDB and FAISS with GPU support.

Provides a vector store interface for storing and retrieving code embeddings,
utilizing GPU acceleration where available.

Agent: Antigravity
Created: 2025-12-03T05:12:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import logging
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Import torch to check for GPU
try:
    import torch
    GPU_AVAILABLE = torch.cuda.is_available()
except ImportError:
    GPU_AVAILABLE = False

logger = logging.getLogger("core.rag")

@dataclass
class SearchResult:
    """
    [CREATE] Structure for RAG search results.
    """
    id: str
    document: str
    metadata: Dict[str, Any]
    distance: float

class RAGEngine:
    """
    [CREATE] Manages the Vector Database and Retrieval operations.

    Uses ChromaDB as the primary interface. If configured, it can leverage
    GPU-accelerated embedding generation and potentially underlying FAISS indices
    (though Chroma manages the index implementation details, we configure it for speed).
    """

    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "codebase"):
        """
        Initialize the RAG Engine.

        Args:
            persist_directory: Where to store the database.
            collection_name: Name of the collection to use.
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Configure ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Use a high-performance embedding function
        # We default to 'all-MiniLM-L6-v2' which is fast and effective for code/text
        # If GPU is available, we want to ensure the embedding model runs on it.
        device = "cuda" if GPU_AVAILABLE else "cpu"
        logger.info(f"Initializing RAG Engine. Device: {device}")

        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2",
            device=device
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        [CREATE] Add documents to the vector store.

        Args:
            documents: List of text content (code snippets).
            metadatas: List of metadata dicts (filepath, function name, etc).
            ids: List of unique IDs.
        """
        logger.info(f"Adding {len(documents)} documents to RAG store.")
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, n_results: int = 5) -> List[SearchResult]:
        """
        [CREATE] Semantic search for code.

        Args:
            query: The natural language query or code snippet.
            n_results: Number of results to return.

        Returns:
            List[SearchResult]: Ranked results.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        search_results = []
        if results["ids"]:
            # Chroma returns lists of lists (one per query)
            for i in range(len(results["ids"][0])):
                search_results.append(SearchResult(
                    id=results["ids"][0][i],
                    document=results["documents"][0][i] if results["documents"] else "",
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                    distance=results["distances"][0][i] if results["distances"] else 0.0
                ))

        return search_results

    def count(self) -> int:
        """Return total number of documents."""
        return self.collection.count()

# Singleton for easy access
rag_engine = RAGEngine()
