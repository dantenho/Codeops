"""
Value Object: Embedding

Represents an immutable embedding vector for documents.
"""
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Embedding:
    """
    Embedding value object.

    Represents an immutable embedding vector.
    """
    vector: tuple
    model: str
    dimension: int

    def __post_init__(self):
        """Validate embedding data."""
        if not self.vector:
            raise ValueError("Embedding vector cannot be empty")
        if len(self.vector) != self.dimension:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {len(self.vector)}")
        if not self.model or not self.model.strip():
            raise ValueError("Embedding model cannot be empty")

    @classmethod
    def from_list(cls, vector: List[float], model: str) -> "Embedding":
        """Create embedding from list."""
        return cls(
            vector=tuple(vector),
            model=model,
            dimension=len(vector)
        )

    def to_list(self) -> List[float]:
        """Convert embedding to list."""
        return list(self.vector)

    def cosine_similarity(self, other: "Embedding") -> float:
        """Calculate cosine similarity with another embedding."""
        if self.dimension != other.dimension:
            raise ValueError("Cannot compare embeddings of different dimensions")

        import math
        dot_product = sum(a * b for a, b in zip(self.vector, other.vector))
        magnitude_a = math.sqrt(sum(a * a for a in self.vector))
        magnitude_b = math.sqrt(sum(b * b for b in other.vector))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)
