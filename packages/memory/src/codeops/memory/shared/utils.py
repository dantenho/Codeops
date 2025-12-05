"""
Shared: Utility Functions

Common utility functions used across the memory package.
"""
from datetime import datetime
from typing import Any, Dict
from uuid import UUID


def uuid_to_str(uuid_obj: UUID) -> str:
    """Convert UUID to string."""
    return str(uuid_obj)


def str_to_uuid(uuid_str: str) -> UUID:
    """Convert string to UUID."""
    return UUID(uuid_str)


def serialize_datetime(dt: datetime) -> str:
    """Serialize datetime to ISO format string."""
    return dt.isoformat()


def deserialize_datetime(dt_str: str) -> datetime:
    """Deserialize ISO format string to datetime."""
    return datetime.fromisoformat(dt_str)


def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validate metadata dictionary.

    Args:
        metadata: Metadata dictionary

    Returns:
        True if valid

    Raises:
        ValueError: If metadata is invalid
    """
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary")

    # Check for None values in metadata (ChromaDB doesn't support None)
    for key, value in metadata.items():
        if value is None:
            raise ValueError(f"Metadata value for key '{key}' cannot be None")

    return True
