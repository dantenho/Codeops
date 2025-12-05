from typing import Any, Dict, List

from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class RAGInput(NodeInput):
    query: str = Field(..., description="Query to search in memory")
    n_results: int = Field(default=5, description="Number of results to return")

class RAGOutput(NodeOutput):
    documents: List[str] = Field(..., description="Retrieved documents")
    metadatas: List[Dict[str, Any]] = Field(..., description="Metadata for documents")

class RAGNode(NodeBase):
    """Node for Retrieval Augmented Generation (RAG)."""

    def execute(self, input_data: RAGInput) -> RAGOutput:
        from codeops.memory.vector_store import get_vector_store

        # Initialize store (will use GPU if configured in vector_store.py)
        store = get_vector_store("chroma")

        print(f"RAG Searching for: {input_data.query}")
        results = store.search(input_data.query, n_results=input_data.n_results)

        # Chroma returns list of lists
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        return RAGOutput(documents=docs, metadatas=metas)
