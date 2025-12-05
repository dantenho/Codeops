from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class DenoiserInput(NodeInput):
    image_path: str = Field(..., description="Path to input image")
    strength: float = Field(default=0.5, description="Denoising strength")

class DenoiserOutput(NodeOutput):
    output_path: str = Field(..., description="Path to denoised image")

class DenoiserNode(NodeBase):
    """Node for image denoising."""

    def execute(self, input_data: DenoiserInput) -> DenoiserOutput:
        # Placeholder for Denoiser execution
        print(f"Denoising image {input_data.image_path} with strength {input_data.strength}")
        return DenoiserOutput(output_path="denoised_image.png")
