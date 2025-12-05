from abc import ABC, abstractmethod
from typing import Any, Dict, List

import chromadb
import numpy as np
from chromadb.config import Settings
from codeops.core.config import settings
from codeops.core.exceptions import RAGError

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    faiss = None
    SentenceTransformer = None


class VectorStoreBase(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search for similar documents."""
        pass


class ChromaVectorStore(VectorStoreBase):
    """ChromaDB implementation of VectorStore with GPU support."""

    def __init__(self, collection_name: str = "codebase", embedding_model: str = "all-MiniLM-L6-v2"):
        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=Settings(allow_reset=True)
            )

            # Initialize GPU-accelerated embedding function if available
            self.embedding_func = None
            try:
                import torch
                from chromadb.utils import embedding_functions

                device = "cuda" if torch.cuda.is_available() else "cpu"
                print(f"ChromaDB using device: {device}")

                # We use the default SentenceTransformer embedding function but ensure it runs on the right device
                # Note: Chroma's default wrapper might not expose device easily, so we might need a custom wrapper
                # For now, we rely on the default which is usually CPU-bound, or we can use a custom one.
                # Let's use a custom wrapper to ensure CUDA usage.

                class CudaEmbeddingFunction(embedding_functions.EmbeddingFunction):
                    def __init__(self, model_name):
                        from sentence_transformers import SentenceTransformer
                        self.model = SentenceTransformer(model_name, device=device)

                    def __call__(self, input: List[str]) -> List[List[float]]:
                        embeddings = self.model.encode(input, convert_to_numpy=True)
                        return embeddings.tolist()

                self.embedding_func = CudaEmbeddingFunction(embedding_model)

            except ImportError:
                print("Warning: Could not initialize CUDA embeddings. Using default.")
                self.embedding_func = None

            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_func
            )
        except Exception as e:
            raise RAGError(f"Failed to initialize ChromaDB: {str(e)}")

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            raise RAGError(f"Failed to add documents to ChromaDB: {str(e)}")

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        try:
            return self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
        except Exception as e:
            raise RAGError(f"Failed to search documents in ChromaDB: {str(e)}")


class FaissVectorStore(VectorStoreBase):
    """FAISS implementation of VectorStore (In-Memory)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not faiss or not SentenceTransformer:
            raise ImportError("faiss-cpu and sentence-transformers are required for FaissVectorStore")

        try:
            self.encoder = SentenceTransformer(model_name)
            self.dimension = self.encoder.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents: Dict[str, str] = {}
            self.metadatas: Dict[str, Dict[str, Any]] = {}
            self.id_map: Dict[int, str] = {}  # Maps FAISS index ID to document ID
        except Exception as e:
            raise RAGError(f"Failed to initialize FAISS: {str(e)}")

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        try:
            embeddings = self.encoder.encode(documents)
            self.index.add(np.array(embeddings).astype('float32'))

            start_idx = len(self.id_map)
            for i, doc_id in enumerate(ids):
                self.id_map[start_idx + i] = doc_id
                self.documents[doc_id] = documents[i]
                self.metadatas[doc_id] = metadatas[i]
        except Exception as e:
            raise RAGError(f"Failed to add documents to FAISS: {str(e)}")

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        try:
            query_vector = self.encoder.encode([query])
            distances, indices = self.index.search(np.array(query_vector).astype('float32'), n_results)

            results = {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

            for i, idx in enumerate(indices[0]):
                if idx != -1:  # -1 means not found
                    doc_id = self.id_map[idx]
                    results["ids"][0].append(doc_id)
                    results["documents"][0].append(self.documents[doc_id])
                    results["metadatas"][0].append(self.metadatas[doc_id])
                    results["distances"][0].append(float(distances[0][i]))

            return results
        except Exception as e:
            raise RAGError(f"Failed to search documents in FAISS: {str(e)}")


def get_vector_store(store_type: str = "chroma") -> VectorStoreBase:
    """Factory method to get vector store instance."""
    if store_type.lower() == "chroma":
        return ChromaVectorStore()
    elif store_type.lower() == "faiss":
        return FaissVectorStore()
    else:
        raise ValueError(f"Unknown vector store type: {store_type}")
