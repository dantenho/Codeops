"""
Module: vector_store.py
Purpose: Manages interactions with ChromaDB for vector storage and retrieval.

This module handles the initialization of the ChromaDB client, collection management,
and document embedding/retrieval operations.

Agent: Antigravity
Created: 2025-12-04
Operation: [CREATE]
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, List, Optional

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class VectorStoreConfig:
    """Configuration for the VectorStore."""
    path: str = "./CodeAgents/Training/chroma_db"
    collection_name: str = "agent_knowledge"
    embedding_model: str = "all-MiniLM-L6-v2"

class VectorStore:
    """
    Manages the Vector Database (ChromaDB).

    Attributes:
        client (chromadb.Client): The ChromaDB client instance.
        collection (chromadb.Collection): The active collection.
    """

    def __init__(self, config: VectorStoreConfig = VectorStoreConfig()) -> None:
        """
        Initializes the VectorStore.

        Args:
            config (VectorStoreConfig): Configuration options.
        """
        self.config = config
        self._initialize_client()
        self._initialize_collection()

    def _initialize_client(self) -> None:
        """Sets up the ChromaDB client."""
        try:
            os.makedirs(self.config.path, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.config.path)
            logger.info(f"ChromaDB client initialized at {self.config.path}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise

    def _initialize_collection(self) -> None:
        """Gets or creates the collection."""
        try:
            # Use default embedding function (Sentence Transformers)
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.config.embedding_model
            )

            self.collection = self.client.get_or_create_collection(
                name=self.config.collection_name,
                embedding_function=ef
            )
            logger.info(f"Collection '{self.config.collection_name}' ready.")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Adds documents to the vector store.

        Args:
            documents (List[str]): List of text documents.
            metadatas (Optional[List[dict]]): Metadata for each document.
            ids (Optional[List[str]]): Unique IDs. Generated if not provided.
        """
        if not documents:
            return

        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]

        if metadatas is None:
            metadatas = [{} for _ in documents]

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to store.")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[dict] = None
    ) -> dict:
        """
        Queries the vector store for similar documents.

        Args:
            query_text (str): The query string.
            n_results (int): Number of results to return.
            where (Optional[dict]): Metadata filter.

        Returns:
            dict: Query results (ids, distances, metadatas, documents).
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            return results
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
