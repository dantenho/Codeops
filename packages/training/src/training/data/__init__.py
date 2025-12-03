"""
Data access layer for the Agent Training System.

Provides structured helpers for interacting with the persistent ChromaDB
back-end so higher-level services can remain storage agnostic.
"""

from .client import ChromaDatabase, CollectionSet
from .repositories import RepositoryRegistry

__all__ = ["ChromaDatabase", "CollectionSet", "RepositoryRegistry"]
