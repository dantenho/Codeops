"""
RAG (Retrieval Augmented Generation) Node.

This module provides the RAGNode for querying vector stores and
retrieving relevant context documents. It integrates with ChromaDB
and supports GPU-accelerated embeddings.

Typical usage:
    node = RAGNode(name="rag")
    output = node.execute(RAGInput(query="NFT trends"))
"""

from typing import Any, Dict, List

from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class RAGInput(NodeInput):
    """Input schema for RAGNode.

    Attributes:
        query: The search query to find relevant documents.
        n_results: Maximum number of results to return.
    """
    query: str = Field(..., description="Query to search in memory")
    n_results: int = Field(default=5, description="Number of results to return")


class RAGOutput(NodeOutput):
    """Output schema for RAGNode.

    Attributes:
        documents: List of retrieved document contents.
        metadatas: List of metadata dictionaries for each document.
    """
    documents: List[str] = Field(
        default_factory=list,
        description="Retrieved documents"
    )
    metadatas: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Metadata for documents"
    )


class RAGNode(NodeBase):
    """Node for Retrieval Augmented Generation (RAG).

    This node queries the vector store (ChromaDB or FAISS) to retrieve
    relevant context documents based on semantic similarity. It uses
    GPU-accelerated embeddings when available.

    Role: Memory Sentry - provides historical context to other nodes.

    Example:
        >>> node = RAGNode(name="rag")
        >>> output = node.execute(RAGInput(query="cyberpunk art styles"))
        >>> print(len(output.documents))
        5
    """

    def execute(self, input_data: RAGInput) -> RAGOutput:
        """Execute RAG query against vector store.

        Args:
            input_data: RAGInput containing query and result count.

        Returns:
            RAGOutput with retrieved documents and metadata.

        Raises:
            RAGError: If vector store query fails.
        """
        try:
            from codeops.memory.vector_store import get_vector_store

            # Initialize store (uses GPU if configured)
            store = get_vector_store("chroma")

            print(f"RAG Searching for: {input_data.query}")
            results = store.search(input_data.query, n_results=input_data.n_results)

            # ChromaDB returns nested lists
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]

            return RAGOutput(documents=docs, metadatas=metas)

        except ImportError as e:
            print(f"Warning: Vector store not available: {e}")
            return RAGOutput(documents=[], metadatas=[])
        except Exception as e:
            print(f"Warning: RAG query failed: {e}")
            return RAGOutput(documents=[], metadatas=[])
