from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel


class NodeInput(BaseModel):
    """Base class for node inputs."""
    pass

class NodeOutput(BaseModel):
    """Base class for node outputs."""
    pass

class NodeBase(ABC):
    """Abstract base class for all nodes."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def execute(self, input_data: NodeInput) -> NodeOutput:
        """
        Execute the node's logic.

        Args:
            input_data: The input data for the node.

        Returns:
            The output of the node execution.
        """
        pass
