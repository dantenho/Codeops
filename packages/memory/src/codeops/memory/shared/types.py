"""
Shared: Common Types

Common type definitions used across the memory package.
"""
from typing import Any, Dict, List
from uuid import UUID

# Type aliases for clarity
DocumentID = UUID
AgentID = UUID
TaskID = UUID
Metadata = Dict[str, Any]
EmbeddingVector = List[float]
SearchResult = Dict[str, Any]
