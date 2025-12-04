"""
Module: rag_engine.py
Purpose: Implements Retrieval-Augmented Generation (RAG) logic.

This module coordinates between the VectorStore and the LLM (via agent)
to provide context-aware responses.

Agent: Antigravity
Created: 2025-12-04
Operation: [CREATE]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from backend.core.vector_store import VectorStore

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class RAGConfig:
    """Configuration for the RAG Engine."""
    max_context_length: int = 2000
    n_retrieval_results: int = 3

class RAGEngine:
    """
    Retrieval-Augmented Generation Engine.

    Attributes:
        vector_store (VectorStore): The vector store instance.
        config (RAGConfig): Configuration options.
    """

    def __init__(self, vector_store: VectorStore, config: RAGConfig = RAGConfig()) -> None:
        """
        Initializes the RAG Engine.

        Args:
            vector_store (VectorStore): Initialized VectorStore.
            config (RAGConfig): Configuration.
        """
        self.vector_store = vector_store
        self.config = config

    def retrieve_context(self, query: str) -> str:
        """
        Retrieves relevant context for a query.

        Args:
            query (str): The user query.

        Returns:
            str: Formatted context string.
        """
        try:
            results = self.vector_store.query(
                query_text=query,
                n_results=self.config.n_retrieval_results
            )

            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]

            context_parts = []
            for doc, meta in zip(documents, metadatas):
                source = meta.get('source', 'Unknown')
                context_parts.append(f"Source: {source}\nContent: {doc}")

            full_context = "\n\n".join(context_parts)

            # Simple truncation if too long (can be improved with token counting)
            if len(full_context) > self.config.max_context_length:
                full_context = full_context[:self.config.max_context_length] + "...(truncated)"

            return full_context
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return ""

    def augment_prompt(self, query: str, base_prompt: str = "") -> str:
        """
        Augments the prompt with retrieved context.

        Args:
            query (str): The user query.
            base_prompt (str): The original system or user prompt.

        Returns:
            str: The augmented prompt.
        """
        context = self.retrieve_context(query)

        if not context:
            return f"{base_prompt}\n\nQuery: {query}"

        augmented_prompt = (
            f"{base_prompt}\n\n"
            f"Relevant Context:\n{context}\n\n"
            f"Based on the context above, please answer the following:\n"
            f"Query: {query}"
        )

        return augmented_prompt
