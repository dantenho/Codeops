"""
Configuration Layer: Settings

Application settings and configuration management.
"""
import os
from typing import Optional


class MemorySettings:
    """Settings for the memory package."""

    def __init__(self):
        """Initialize settings from environment variables."""
        # Database settings
        self.DATABASE_URL: str = os.getenv(
            "MEMORY_DATABASE_URL", "sqlite:///./memory.db"
        )
        self.DATABASE_ECHO: bool = os.getenv("MEMORY_DATABASE_ECHO", "false").lower() == "true"

        # ChromaDB settings
        self.CHROMA_DB_PATH: str = os.getenv("MEMORY_CHROMA_PATH", "./chroma_db")
        self.CHROMA_COLLECTION_NAME: str = os.getenv(
            "MEMORY_CHROMA_COLLECTION", "documents"
        )

        # Embedding settings
        self.EMBEDDING_MODEL: str = os.getenv(
            "MEMORY_EMBEDDING_MODEL", "all-MiniLM-L6-v2"
        )
        self.EMBEDDING_DEVICE: str = os.getenv("MEMORY_EMBEDDING_DEVICE", "auto")

        # General settings
        self.DEBUG: bool = os.getenv("MEMORY_DEBUG", "false").lower() == "true"

    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            "DATABASE_URL": self.DATABASE_URL,
            "DATABASE_ECHO": self.DATABASE_ECHO,
            "CHROMA_DB_PATH": self.CHROMA_DB_PATH,
            "CHROMA_COLLECTION_NAME": self.CHROMA_COLLECTION_NAME,
            "EMBEDDING_MODEL": self.EMBEDDING_MODEL,
            "EMBEDDING_DEVICE": self.EMBEDDING_DEVICE,
            "DEBUG": self.DEBUG,
        }


# Global settings instance
settings = MemorySettings()
