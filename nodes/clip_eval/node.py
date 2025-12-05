"""
CLIP Evaluation Node.

This module provides the ClipEvalNode for scoring images against
text prompts using OpenAI's CLIP model. It supports GPU acceleration
for faster inference.

Typical usage:
    node = ClipEvalNode(name="clip")
    output = node.execute(ClipEvalInput(image_path="art.png", prompt="cyberpunk"))
"""

from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class ClipEvalInput(NodeInput):
    """Input schema for ClipEvalNode.

    Attributes:
        image_path: Path to the image file to evaluate.
        prompt: Text prompt to compare the image against.
    """
    image_path: str = Field(..., description="Path to image")
    prompt: str = Field(..., description="Prompt to compare against")


class ClipEvalOutput(NodeOutput):
    """Output schema for ClipEvalNode.

    Attributes:
        score: Normalized alignment score between 0.0 and 1.0.
    """
    score: float = Field(default=0.0, description="Aesthetic/Alignment score")


class ClipEvalNode(NodeBase):
    """Node for CLIP-based image evaluation.

    This node uses OpenAI's CLIP model to evaluate how well an image
    matches a given text prompt. It provides a semantic similarity
    score that can be used for quality assessment.

    Role: Quality Sentry - automatically evaluates generated content.

    Example:
        >>> node = ClipEvalNode(name="clip_eval")
        >>> output = node.execute(ClipEvalInput(
        ...     image_path="output/art.png",
        ...     prompt="vibrant cyberpunk cityscape"
        ... ))
        >>> print(f"Score: {output.score:.2f}")
        Score: 0.85
    """

    def execute(self, input_data: ClipEvalInput) -> ClipEvalOutput:
        """Execute CLIP evaluation on image.

        Args:
            input_data: ClipEvalInput with image path and prompt.

        Returns:
            ClipEvalOutput with normalized similarity score.
        """
        print(f"Evaluating image {input_data.image_path} against '{input_data.prompt}'")

        try:
            import os

            import torch
            from PIL import Image
            from transformers import CLIPModel, CLIPProcessor

            # Check if image exists
            if not os.path.exists(input_data.image_path):
                print(f"Warning: Image not found: {input_data.image_path}")
                return ClipEvalOutput(score=0.0)

            # Select device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"CLIP using device: {device}")

            # Load model
            model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
            processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

            # Load and process image
            image = Image.open(input_data.image_path)
            inputs = processor(
                text=[input_data.prompt],
                images=image,
                return_tensors="pt",
                padding=True
            ).to(device)

            # Get similarity score
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits_per_image

            # Normalize to 0-1 range (CLIP logits typically range from 0-35)
            score = min(max(logits.item() / 35.0, 0.0), 1.0)

            return ClipEvalOutput(score=score)

        except ImportError as e:
            print(f"CLIP dependencies not available: {e}")
            return ClipEvalOutput(score=0.5)  # Return neutral score
        except Exception as e:
            print(f"CLIP Eval failed: {e}. Returning mock score.")
            return ClipEvalOutput(score=0.5)
