import os
import sys

# Add the package root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/core/src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from nodes.anime4k.node import Anime4kInput, Anime4kNode
from nodes.civitai.node import CivitAIInput, CivitAINode
from nodes.comfyui.node import ComfyUIInput, ComfyUINode
from nodes.denoiser.node import DenoiserInput, DenoiserNode
from nodes.firecrawl.node import FirecrawlInput, FirecrawlNode
from nodes.flux.node import FluxInput, FluxNode
from nodes.playwright.node import PlaywrightInput, PlaywrightNode
from nodes.realesrgan.node import RealESRGANInput, RealESRGANNode
from nodes.threadreader.node import ThreadReaderInput, ThreadReaderNode


def test_nodes():
    print("Testing FirecrawlNode...")
    node = FirecrawlNode(name="firecrawl")
    output = node.execute(FirecrawlInput(url="http://example.com"))
    print(output)

    print("\nTesting ComfyUINode...")
    node = ComfyUINode(name="comfyui")
    output = node.execute(ComfyUIInput(workflow_json={"node": "test"}))
    print(output)

    print("\nTesting Anime4kNode...")
    node = Anime4kNode(name="anime4k")
    output = node.execute(Anime4kInput(input_video_path="in.mp4", output_video_path="out.mp4"))
    print(output)

    print("\nTesting PlaywrightNode...")
    node = PlaywrightNode(name="playwright")
    output = node.execute(PlaywrightInput(url="http://example.com"))
    print(output)

    print("\nTesting ThreadReaderNode...")
    node = ThreadReaderNode(name="threadreader")
    output = node.execute(ThreadReaderInput(thread_url="http://twitter.com/thread"))
    print(output)

    print("\nTesting RealESRGANNode...")
    node = RealESRGANNode(name="realesrgan")
    output = node.execute(RealESRGANInput(image_path="in.png"))
    print(output)

    print("\nTesting DenoiserNode...")
    node = DenoiserNode(name="denoiser")
    output = node.execute(DenoiserInput(image_path="in.png"))
    print(output)

    print("\nTesting FluxNode...")
    node = FluxNode(name="flux")
    output = node.execute(FluxInput(prompt="a cat"))
    print(output)

    print("\nTesting CivitAINode...")
    node = CivitAINode(name="civitai")
    output = node.execute(CivitAIInput(model_id="12345"))
    print(output)

if __name__ == "__main__":
    test_nodes()
