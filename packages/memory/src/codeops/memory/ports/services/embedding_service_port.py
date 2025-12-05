"""
Port: Embedding Service Interface

Defines the contract for embedding generation services.
"""
from abc import ABC, abstractmethod
from typing import List

from codeops.memory.domain.value_objects.embedding import Embedding


class EmbeddingServicePort(ABC):
    """
    Service interface for generating embeddings.

    This port defines the contract that must be implemented by
    concrete adapters (SentenceTransformers, OpenAI, Cohere, etc.).
    """

    @abstractmethod
    async def generate_embedding(self, text: str) -> Embedding:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding value object
        """
        pass

    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[Embedding]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of embedding value objects
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the embedding model being used.

        Returns:
            Model name
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.

        Returns:
            Embedding dimension
        """
        pass
