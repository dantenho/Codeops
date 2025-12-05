"""
Adapter: SentenceTransformer Embedding Service Implementation

Concrete implementation of EmbeddingServicePort using SentenceTransformers.
"""
from typing import List

from codeops.memory.domain.value_objects.embedding import Embedding
from codeops.memory.ports.services import EmbeddingServicePort

try:
    from sentence_transformers import SentenceTransformer
    import torch
except ImportError:
    SentenceTransformer = None
    torch = None


class SentenceTransformerEmbeddingService(EmbeddingServicePort):
    """SentenceTransformer implementation of EmbeddingServicePort."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "auto"):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the SentenceTransformer model
            device: Device to use ('cuda', 'cpu', or 'auto')
        """
        if not SentenceTransformer:
            raise ImportError("sentence-transformers is required for this service")

        # Auto-detect device
        if device == "auto":
            device = "cuda" if torch and torch.cuda.is_available() else "cpu"

        self._model_name = model_name
        self._device = device
        self._model = SentenceTransformer(model_name, device=device)
        self._dimension = self._model.get_sentence_embedding_dimension()

    async def generate_embedding(self, text: str) -> Embedding:
        """Generate embedding for a single text."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        embedding_vector = self._model.encode(text, convert_to_numpy=True)
        return Embedding.from_list(
            vector=embedding_vector.tolist(),
            model=self._model_name
        )

    async def generate_embeddings(self, texts: List[str]) -> List[Embedding]:
        """Generate embeddings for multiple texts."""
        if not texts:
            raise ValueError("Texts list cannot be empty")

        if any(not text or not text.strip() for text in texts):
            raise ValueError("All texts must be non-empty")

        embedding_vectors = self._model.encode(texts, convert_to_numpy=True)
        return [
            Embedding.from_list(vector=vec.tolist(), model=self._model_name)
            for vec in embedding_vectors
        ]

    def get_model_name(self) -> str:
        """Get the name of the embedding model being used."""
        return self._model_name

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self._dimension
