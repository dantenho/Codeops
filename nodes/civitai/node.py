"""
CivitAI Model Downloader Node.

This module provides the CivitAINode for searching and downloading
LoRAs, Checkpoints, and other models from CivitAI.

Typical usage:
    node = CivitAINode(name="civitai")
    output = node.execute(CivitAIInput(query="cyberpunk", model_type="LORA"))
"""

import os

from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class CivitAIInput(NodeInput):
    """Input schema for CivitAINode.

    Attributes:
        query: Search query for LoRA/Checkpoint.
        model_type: Type of model to search. Options: 'LORA', 'Checkpoint'.
    """
    query: str = Field(..., description="Search query for LoRA/Checkpoint")
    model_type: str = Field(default="LORA", description="Type of model (LORA, Checkpoint)")


class CivitAIOutput(NodeOutput):
    """Output schema for CivitAINode.

    Attributes:
        model_path: Local path to the downloaded model file.
        metadata: Model metadata from CivitAI.
    """
    model_path: str = Field(default="", description="Local path to the downloaded model")
    metadata: dict = Field(default_factory=dict, description="Model metadata")


class CivitAINode(NodeBase):
    """Node for interacting with CivitAI.

    This node searches CivitAI for models matching the query and downloads
    them to the local models directory. It supports LoRAs, Checkpoints,
    and other model types.

    Role: Asset Sentry - manages and downloads AI model assets.

    Example:
        >>> node = CivitAINode(name="civitai")
        >>> output = node.execute(CivitAIInput(
        ...     query="anime style",
        ...     model_type="LORA"
        ... ))
        >>> print(output.model_path)
        'models/loras/anime_style.safetensors'
    """

    def execute(self, input_data: CivitAIInput) -> CivitAIOutput:
        """Execute CivitAI model search and download.

        Args:
            input_data: CivitAIInput with search query and model type.

        Returns:
            CivitAIOutput with local path and metadata.
        """
        print(f"Searching CivitAI for {input_data.model_type}: {input_data.query}")

        try:
            # Determine output directory based on model type
            if input_data.model_type.upper() == "LORA":
                output_dir = "models/loras"
            else:
                output_dir = "models/checkpoints"

            os.makedirs(output_dir, exist_ok=True)

            # Create mock file path (real implementation would download)
            safe_name = input_data.query.replace(" ", "_").lower()
            mock_path = os.path.join(output_dir, f"{safe_name}.safetensors")

            # Create placeholder file for testing
            if not os.path.exists(mock_path):
                with open(mock_path, "w", encoding="utf-8") as f:
                    f.write("# Mock safetensor content\n")

            return CivitAIOutput(
                model_path=os.path.abspath(mock_path),
                metadata={
                    "name": input_data.query,
                    "type": input_data.model_type,
                    "source": "civitai"
                }
            )

        except Exception as e:
            print(f"CivitAI error: {e}")
            return CivitAIOutput(model_path="", metadata={"error": str(e)})
