import os
import subprocess
import sys

from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class RealESRGANInput(NodeInput):
    image_path: str = Field(..., description="Path to image to upscale")
    scale: int = Field(default=4, description="Upscaling factor (2 or 4)")
    face_enhance: bool = Field(default=True, description="Use GFPGAN for face enhancement")

class RealESRGANOutput(NodeOutput):
    output_path: str = Field(..., description="Path to upscaled image")

class RealESRGANNode(NodeBase):
    """Node for Real-ESRGAN image restoration."""

    def execute(self, input_data: RealESRGANInput) -> RealESRGANOutput:
        print(f"Upscaling image: {input_data.image_path}")

        # Path to inference script
        tools_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../tools/Real-ESRGAN"))
        inference_script = os.path.join(tools_dir, "inference_realesrgan.py")

        if not os.path.exists(inference_script):
            print(f"Error: Real-ESRGAN script not found at {inference_script}")
            return RealESRGANOutput(output_path=input_data.image_path)

        output_dir = os.path.join(os.path.dirname(input_data.image_path), "upscaled")
        os.makedirs(output_dir, exist_ok=True)

        # Construct command
        # python inference_realesrgan.py -n RealESRGAN_x4plus -i input.jpg -o output_dir --face_enhance
        cmd = [
            sys.executable,
            inference_script,
            "-n", "RealESRGAN_x4plus",
            "-i", input_data.image_path,
            "-o", output_dir,
            "-s", str(input_data.scale)
        ]

        if input_data.face_enhance:
            cmd.append("--face_enhance")

        try:
            # We need to run this in the tools directory context or ensure dependencies are met
            # For now, let's try running it directly. It might fail if dependencies aren't installed in the main env.
            subprocess.run(cmd, check=True, cwd=tools_dir)

            # Determine output filename
            base_name = os.path.basename(input_data.image_path)
            name, ext = os.path.splitext(base_name)
            out_name = f"{name}_out{ext}"
            out_path = os.path.join(output_dir, out_name)

            if os.path.exists(out_path):
                return RealESRGANOutput(output_path=out_path)
            else:
                print("Warning: Output file not found, returning input.")
                return RealESRGANOutput(output_path=input_data.image_path)

        except Exception as e:
            print(f"Real-ESRGAN failed: {e}")
            return RealESRGANOutput(output_path=input_data.image_path)
