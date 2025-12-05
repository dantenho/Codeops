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
    """ChromaDB implementation of VectorStore."""

    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=Settings(allow_reset=True)
            )
            self.collection = self.client.get_or_create_collection("codebase")
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
