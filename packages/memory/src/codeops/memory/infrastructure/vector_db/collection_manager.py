"""
ChromaDB Collection Manager - Multi-Collection Vectorial Dataset Architecture.

Manages multiple specialized ChromaDB collections with different embedding functions
for various data types (documents, code, images, workflows, etc.).
"""

from typing import Dict, Any, List, Optional
import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection


# Collection Definitions
COLLECTIONS = {
    "documents": {
        "description": "General text documents for RAG",
        "embedding_function": "sentence-transformers/all-MiniLM-L6-v2",
        "metadata_schema": {
            "source": "str",  # File path or URL
            "type": "str",  # "code", "documentation", "article"
            "language": "str",  # "python", "javascript", "english"
            "created_at": "str",  # ISO timestamp
            "tags": "List[str]"
        }
    },

    "code_snippets": {
        "description": "Code snippets with semantic search",
        "embedding_function": "microsoft/codebert-base",
        "metadata_schema": {
            "language": "str",  # Programming language
            "repo": "str",  # Repository name
            "file_path": "str",  # File path in repo
            "function_name": "str",  # Function/class name
            "docstring": "str",  # Function documentation
            "complexity": "int",  # Cyclomatic complexity
            "lines": "int"  # Number of lines
        }
    },

    "workflow_templates": {
        "description": "LangGraph workflow templates",
        "embedding_function": "sentence-transformers/all-MiniLM-L6-v2",
        "metadata_schema": {
            "workflow_name": "str",
            "node_count": "int",
            "complexity": "str",  # "simple", "medium", "complex"
            "use_case": "str",  # "image_generation", "data_processing"
            "tags": "List[str]",
            "success_rate": "float",
            "average_duration": "float"  # Average execution time in seconds
        }
    },

    "artifacts": {
        "description": "Generated artifacts (CLIP embeddings for images)",
        "embedding_function": "openai/clip-vit-base-patch32",
        "metadata_schema": {
            "artifact_type": "str",  # "image", "video", "3d_model", "audio"
            "execution_id": "str",  # UUID of execution that created it
            "workflow_id": "str",  # UUID of workflow
            "prompt": "str",  # Generation prompt
            "model_used": "str",  # Model name
            "resolution": "str",  # "1024x1024", etc.
            "file_size": "int",  # Size in bytes
            "storage_path": "str",  # Path to actual file
            "created_at": "str"  # ISO timestamp
        }
    },

    "agent_memories": {
        "description": "Agent conversation history and learnings",
        "embedding_function": "sentence-transformers/all-MiniLM-L6-v2",
        "metadata_schema": {
            "agent_id": "str",  # UUID of agent
            "conversation_id": "str",  # Conversation UUID
            "timestamp": "str",  # ISO timestamp
            "role": "str",  # "user", "assistant", "system"
            "sentiment": "str",  # "positive", "neutral", "negative"
            "topics": "List[str]",  # Extracted topics
            "followup_needed": "bool",  # Whether followup is needed
            "importance": "int"  # 1-5 importance score
        }
    },

    "tool_documentation": {
        "description": "Documentation for integrated tools",
        "embedding_function": "sentence-transformers/all-MiniLM-L6-v2",
        "metadata_schema": {
            "tool_name": "str",  # Tool name
            "integration_type": "str",  # Type of integration
            "doc_type": "str",  # "api_reference", "tutorial", "example"
            "version": "str",  # Tool version
            "url": "str",  # Documentation URL
            "last_updated": "str"  # ISO timestamp
        }
    },

    "error_patterns": {
        "description": "Historical error patterns for debugging and self-healing",
        "embedding_function": "sentence-transformers/all-MiniLM-L6-v2",
        "metadata_schema": {
            "error_type": "str",  # Error class/category
            "package": "str",  # Package where error occurred
            "resolution": "str",  # How it was resolved
            "frequency": "int",  # How many times seen
            "last_seen": "str",  # ISO timestamp
            "severity": "str",  # "low", "medium", "high", "critical"
            "auto_resolved": "bool"  # Whether it was auto-resolved
        }
    },

    "agent_instructions": {
        "description": "State-of-the-art code agent conversation instructions and prompt templates",
        "embedding_function": "sentence-transformers/all-MiniLM-L6-v2",
        "metadata_schema": {
            "instruction_id": "str",  # Unique identifier
            "agent_type": "str",  # Type of agent (e.g., "spec-requirements", "spec-design")
            "instruction_category": "str",  # "system_prompt", "conversation_pattern", "error_handling", "tool_usage", "response_formatting"
            "version": "str",  # Version of the instruction template
            "author": "str",  # Author or source
            "tags": "List[str]",  # Tags for categorization
            "usage_examples": "str",  # Usage examples or notes
            "created_at": "str"  # ISO timestamp
        }
    },

    "agent_documents": {
        "description": "Agent specification files and documentation with hierarchical metadata",
        "embedding_function": "sentence-transformers/all-MiniLM-L6-v2",
        "metadata_schema": {
            "agent_name": "str",  # Agent name (e.g., "kfc")
            "file_type": "str",  # File type (e.g., "requirements", "design", "impl")
            "spec_type": "str",  # Spec type from .claude path (e.g., "spec-requirements")
            "hierarchy_path": "str",  # Full file path (e.g., "agents/kfc/requirements.md")
            "category": "str",  # Category (e.g., "agent_instruction")
            "version": "str",  # Version
            "tags": "List[str]",  # Tags for search
            "chunk_index": "int",  # Chunk index for large files
            "total_chunks": "int",  # Total chunks for the file
            "created_at": "str"  # ISO timestamp
        }
    }
}


class CollectionManager:
    """
    Manages multiple ChromaDB collections with different embedding functions.

    This class provides a centralized way to manage multiple specialized collections
    in ChromaDB, each with its own embedding function optimized for its data type.
    """

    def __init__(
        self,
        persist_path: str = "./chroma_db",
        allow_reset: bool = False
    ):
        """
        Initialize collection manager.

        Args:
            persist_path: Path for ChromaDB persistence
            allow_reset: Whether to allow resetting collections
        """
        self.persist_path = persist_path
        self.client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(
                allow_reset=allow_reset,
                anonymized_telemetry=False
            )
        )
        self._collections: Dict[str, Collection] = {}

    def initialize_collections(self):
        """Create all collections with proper embedding functions."""
        for name, config in COLLECTIONS.items():
            try:
                embedding_fn = self._get_embedding_function(
                    config["embedding_function"]
                )

                collection = self.client.get_or_create_collection(
                    name=name,
                    embedding_function=embedding_fn,
                    metadata={
                        "description": config["description"],
                        "embedding_model": config["embedding_function"]
                    }
                )

                self._collections[name] = collection
                print(f"✓ Initialized collection: {name}")

            except Exception as e:
                print(f"✗ Failed to initialize collection {name}: {e}")

    def get_collection(self, name: str) -> Collection:
        """
        Get a specific collection.

        Args:
            name: Collection name

        Returns:
            ChromaDB Collection instance

        Raises:
            ValueError: If collection not initialized
        """
        if name not in self._collections:
            # Try to load it if not in cache
            if name in COLLECTIONS:
                config = COLLECTIONS[name]
                embedding_fn = self._get_embedding_function(
                    config["embedding_function"]
                )
                self._collections[name] = self.client.get_or_create_collection(
                    name=name,
                    embedding_function=embedding_fn
                )
            else:
                raise ValueError(
                    f"Collection '{name}' not initialized. "
                    f"Available: {list(COLLECTIONS.keys())}"
                )

        return self._collections[name]

    def list_collections(self) -> List[str]:
        """List all available collections."""
        return list(COLLECTIONS.keys())

    def get_collection_info(self, name: str) -> Dict[str, Any]:
        """
        Get information about a collection.

        Args:
            name: Collection name

        Returns:
            Dict with collection metadata
        """
        if name not in COLLECTIONS:
            raise ValueError(f"Unknown collection: {name}")

        config = COLLECTIONS[name]
        collection = self.get_collection(name)

        return {
            "name": name,
            "description": config["description"],
            "embedding_model": config["embedding_function"],
            "metadata_schema": config["metadata_schema"],
            "count": collection.count()
        }

    def get_all_collection_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get stats for all collections."""
        stats = {}
        for name in COLLECTIONS.keys():
            try:
                collection = self.get_collection(name)
                stats[name] = {
                    "count": collection.count(),
                    "description": COLLECTIONS[name]["description"],
                    "embedding_model": COLLECTIONS[name]["embedding_function"]
                }
            except Exception as e:
                stats[name] = {"error": str(e)}

        return stats

    def clear_collection(self, name: str):
        """
        Clear all data from a collection.

        Args:
            name: Collection name
        """
        collection = self.get_collection(name)
        # Get all IDs and delete them
        results = collection.get()
        if results and results['ids']:
            collection.delete(ids=results['ids'])
            print(f"Cleared {len(results['ids'])} items from {name}")

    def delete_collection(self, name: str):
        """
        Delete a collection entirely.

        Args:
            name: Collection name
        """
        self.client.delete_collection(name)
        if name in self._collections:
            del self._collections[name]
        print(f"Deleted collection: {name}")

    def reset_all_collections(self):
        """Reset all collections (delete and recreate)."""
        for name in list(self._collections.keys()):
            try:
                self.delete_collection(name)
            except Exception as e:
                print(f"Error deleting {name}: {e}")

        self._collections = {}
        self.initialize_collections()

    def _get_embedding_function(self, model_name: str):
        """
        Get embedding function for model.

        Args:
            model_name: Model identifier

        Returns:
            ChromaDB embedding function
        """
        # For CLIP models (image embeddings)
        if "clip" in model_name.lower():
            try:
                from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
                return OpenCLIPEmbeddingFunction()
            except ImportError:
                print(f"Warning: CLIP model not available, using default")
                return None

        # For CodeBERT (code embeddings)
        elif "codebert" in model_name.lower():
            try:
                from chromadb.utils import embedding_functions
                return embedding_functions.HuggingFaceEmbeddingFunction(
                    api_key=None,
                    model_name=model_name
                )
            except Exception as e:
                print(f"Warning: CodeBERT model not available ({e}), using default")
                return None

        # For sentence transformers (default for most text)
        else:
            try:
                from chromadb.utils import embedding_functions
                # Extract model name after slash
                model_id = model_name.split("/")[-1] if "/" in model_name else model_name
                return embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=model_id
                )
            except Exception as e:
                print(f"Warning: Model {model_name} not available ({e}), using default")
                return None

    def add_to_collection(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to a collection.

        Args:
            collection_name: Name of collection
            documents: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs
        """
        collection = self.get_collection(collection_name)

        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query_collection(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query a collection.

        Args:
            collection_name: Name of collection
            query_texts: List of query texts
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            Query results
        """
        collection = self.get_collection(collection_name)

        return collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where
        )


# Convenience function
def create_collection_manager(
    persist_path: str = "./chroma_db",
    initialize: bool = True
) -> CollectionManager:
    """
    Create and optionally initialize a collection manager.

    Args:
        persist_path: Path for ChromaDB persistence
        initialize: Whether to initialize all collections immediately

    Returns:
        Initialized CollectionManager
    """
    manager = CollectionManager(persist_path=persist_path)

    if initialize:
        manager.initialize_collections()

    return manager
