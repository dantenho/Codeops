"""
Integrated Node Registry and Flow Configuration.

This module provides a unified registry for all nodes
and their integration with LangGraph workflows.
"""

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List

# Add paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


@dataclass
class NodeConfig:
    """Configuration for a node in the workflow."""
    name: str
    module_path: str
    input_class: str
    output_class: str
    node_class: str
    description: str = ""
    gpu_enabled: bool = False
    requires_api_key: bool = False
    dependencies: List[str] = field(default_factory=list)


# Node Registry
NODE_REGISTRY: Dict[str, NodeConfig] = {
    # Data Sentry Nodes
    "social_media": NodeConfig(
        name="social_media",
        module_path="nodes.social_media.node",
        input_class="SocialMediaInput",
        output_class="SocialMediaOutput",
        node_class="SocialMediaNode",
        description="Fetches trends from Reddit, YouTube, TikTok",
        dependencies=["praw", "google-api-python-client"]
    ),

    "firecrawl": NodeConfig(
        name="firecrawl",
        module_path="nodes.firecrawl.node",
        input_class="FirecrawlInput",
        output_class="FirecrawlOutput",
        node_class="FirecrawlNode",
        description="Web scraping and crawling",
        requires_api_key=True
    ),

    "rag": NodeConfig(
        name="rag",
        module_path="nodes.rag.node",
        input_class="RAGInput",
        output_class="RAGOutput",
        node_class="RAGNode",
        description="Retrieval Augmented Generation queries",
        gpu_enabled=True,
        dependencies=["chromadb", "sentence-transformers"]
    ),

    # Visual Sentry Nodes
    "comfyui": NodeConfig(
        name="comfyui",
        module_path="nodes.comfyui.node",
        input_class="ComfyUIInput",
        output_class="ComfyUIOutput",
        node_class="ComfyUINode",
        description="Image generation via ComfyUI",
        gpu_enabled=True
    ),

    "real_esrgan": NodeConfig(
        name="real_esrgan",
        module_path="nodes.real_esrgan.node",
        input_class="RealESRGANInput",
        output_class="RealESRGANOutput",
        node_class="RealESRGANNode",
        description="Image upscaling and restoration",
        gpu_enabled=True
    ),

    "anime4k": NodeConfig(
        name="anime4k",
        module_path="nodes.anime4k.node",
        input_class="Anime4kInput",
        output_class="Anime4kOutput",
        node_class="Anime4kNode",
        description="Anime-style upscaling",
        gpu_enabled=True
    ),

    "clip_eval": NodeConfig(
        name="clip_eval",
        module_path="nodes.clip_eval.node",
        input_class="ClipEvalInput",
        output_class="ClipEvalOutput",
        node_class="ClipEvalNode",
        description="CLIP-based image evaluation",
        gpu_enabled=True,
        dependencies=["transformers", "torch"]
    ),

    # Asset Sentry Nodes
    "civitai": NodeConfig(
        name="civitai",
        module_path="nodes.civitai.node",
        input_class="CivitAIInput",
        output_class="CivitAIOutput",
        node_class="CivitAINode",
        description="LoRA and Checkpoint downloads from CivitAI",
        requires_api_key=True
    ),

    # Code Sentry Nodes
    "google_genai": NodeConfig(
        name="google_genai",
        module_path="nodes.google_genai.node",
        input_class="GoogleGenAIInput",
        output_class="GoogleGenAIOutput",
        node_class="GoogleGenAINode",
        description="AI code generation via Gemini",
        requires_api_key=True
    ),

    # Blockchain Nodes
    "gas_tracker": NodeConfig(
        name="gas_tracker",
        module_path="nodes.gas_tracker.node",
        input_class="GasTrackerInput",
        output_class="GasTrackerOutput",
        node_class="GasTrackerNode",
        description="Ethereum gas price tracking",
        requires_api_key=True
    ),

    "asset_publisher": NodeConfig(
        name="asset_publisher",
        module_path="codeops.core.integrations.asset_publisher",
        input_class="AssetPublisher",
        output_class="PublishResult",
        node_class="LocalAssetPublisher",
        description="Generic asset publishing (local, IPFS, S3, Cloudinary)",
        requires_api_key=False
    ),

    # UI Nodes
    "gradio_eval": NodeConfig(
        name="gradio_eval",
        module_path="nodes.gradio_eval.node",
        input_class="GradioEvalInput",
        output_class="GradioEvalOutput",
        node_class="GradioEvalNode",
        description="Human-in-the-loop evaluation UI"
    ),
}


def get_node(name: str) -> Any:
    """
    Dynamically load and instantiate a node.

    Args:
        name: Node name from registry.

    Returns:
        Instantiated node.
    """
    if name not in NODE_REGISTRY:
        raise ValueError(f"Unknown node: {name}")

    config = NODE_REGISTRY[name]

    # Dynamic import
    import importlib
    module = importlib.import_module(config.module_path)

    node_class = getattr(module, config.node_class)
    return node_class(name=config.name)


def get_node_input(name: str, **kwargs) -> Any:
    """
    Create input instance for a node.

    Args:
        name: Node name.
        **kwargs: Input parameters.

    Returns:
        Input instance.
    """
    if name not in NODE_REGISTRY:
        raise ValueError(f"Unknown node: {name}")

    config = NODE_REGISTRY[name]

    import importlib
    module = importlib.import_module(config.module_path)

    input_class = getattr(module, config.input_class)
    return input_class(**kwargs)


def list_nodes(gpu_only: bool = False, with_api_key: bool = None) -> List[NodeConfig]:
    """
    List available nodes with optional filtering.

    Args:
        gpu_only: Only return GPU-enabled nodes.
        with_api_key: Filter by API key requirement.

    Returns:
        List of node configurations.
    """
    nodes = list(NODE_REGISTRY.values())

    if gpu_only:
        nodes = [n for n in nodes if n.gpu_enabled]

    if with_api_key is not None:
        nodes = [n for n in nodes if n.requires_api_key == with_api_key]

    return nodes


def check_dependencies() -> Dict[str, bool]:
    """Check if all node dependencies are available."""
    results = {}

    for name, config in NODE_REGISTRY.items():
        try:
            get_node(name)
            results[name] = True
        except Exception as e:
            results[name] = False
            print(f"Node {name} unavailable: {e}")

    return results


# Workflow Templates
WORKFLOW_TEMPLATES = {
    "content_generation": [
        "social_media",
        "rag",
        "civitai",
        "comfyui",
        "real_esrgan",
        "clip_eval",
        "gradio_eval"
    ],

    "trend_analysis": [
        "social_media",
        "rag",
        "google_genai"
    ],

    "content_publishing_pipeline": [
        "social_media",
        "comfyui",
        "clip_eval",
        "asset_publisher"
    ],

    "upscale_batch": [
        "real_esrgan",
        "anime4k"
    ]
}


def get_workflow_nodes(workflow_name: str) -> List[Any]:
    """Get instantiated nodes for a workflow template."""
    if workflow_name not in WORKFLOW_TEMPLATES:
        raise ValueError(f"Unknown workflow: {workflow_name}")

    return [get_node(name) for name in WORKFLOW_TEMPLATES[workflow_name]]


if __name__ == "__main__":
    # Test registry
    print("Available Nodes:")
    for name, config in NODE_REGISTRY.items():
        print(f"  - {name}: {config.description}")

    print("\nChecking dependencies...")
    results = check_dependencies()
    for name, available in results.items():
        status = "✅" if available else "❌"
        print(f"  {status} {name}")
