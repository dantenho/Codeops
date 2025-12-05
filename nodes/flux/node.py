from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class FluxInput(NodeInput):
    prompt: str = Field(..., description="Text prompt for image generation")
    width: int = Field(default=1024, description="Image width")
    height: int = Field(default=1024, description="Image height")

class FluxOutput(NodeOutput):
    image_path: str = Field(..., description="Path to generated image")

class FluxNode(NodeBase):
    """Node for Flux2.Dev image generation."""

    def execute(self, input_data: FluxInput) -> FluxOutput:
        # Placeholder for Flux execution
        print(f"Generating image with Flux: {input_data.prompt}")
        return FluxOutput(image_path="flux_image.png")
