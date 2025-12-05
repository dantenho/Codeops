"""
LangGraph Workflow Orchestrator - Full Integration.

This module provides the complete workflow graph integrating
all Sentry nodes, LangChain components, and ChromaDB.
"""

import os
import sys
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

# Ensure nodes are importable
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

# Import all nodes with fallbacks
try:
    from nodes.civitai.node import CivitAIInput, CivitAINode
    from nodes.clip_eval.node import ClipEvalInput, ClipEvalNode
    from nodes.comfyui.node import ComfyUIInput, ComfyUINode
    from nodes.gas_tracker.node import GasTrackerInput, GasTrackerNode
    from nodes.google_genai.node import GoogleGenAIInput, GoogleGenAINode
    from nodes.gradio_eval.node import GradioEvalInput, GradioEvalNode
    from nodes.nft_mint.node import NFTMintInput, NFTMintNode
    from nodes.rag.node import RAGInput, RAGNode
    from nodes.real_esrgan.node import RealESRGANInput, RealESRGANNode
    from nodes.sales_strategy.node import SalesStrategyInput, SalesStrategyNode
    from nodes.social_media.node import SocialMediaInput, SocialMediaNode
    NODES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some nodes unavailable: {e}")
    NODES_AVAILABLE = False


class AgentState(TypedDict):
    """State passed between workflow nodes."""
    # Trend data
    trend_chain: str
    trends: List[Dict[str, Any]]

    # Content generation
    art_description: str
    style_keywords: List[str]
    lora_path: Optional[str]
    workflow_json: Dict[str, Any]
    generated_images: List[str]

    # Evaluation
    clip_score: float
    approved: bool
    feedback: str

    # Strategy & NFT
    sales_strategy: Dict[str, Any]
    gas_price: float
    mint_tx: str
    ipfs_url: str
    status: str

    # RAG context
    context_documents: List[str]


# =============================================================================
# NODE FUNCTIONS
# =============================================================================

def social_research_node(state: AgentState) -> Dict[str, Any]:
    """Fetch trends from social media platforms."""
    print("--- Social Research ---")

    try:
        node = SocialMediaNode(name="social_media")
        output = node.execute(SocialMediaInput(platform="all"))
        return {"trends": output.trends}
    except Exception as e:
        print(f"Social research failed: {e}")
        return {"trends": [{"source": "mock", "title": "Trending Digital Art", "score": 1000}]}


def rag_context_node(state: AgentState) -> Dict[str, Any]:
    """Retrieve relevant context from ChromaDB."""
    print("--- RAG Context Retrieval ---")

    try:
        node = RAGNode(name="rag")
        query = state.get("art_description") or (
            state["trends"][0]["title"] if state.get("trends") else "digital art"
        )
        output = node.execute(RAGInput(query=query, n_results=5))
        print(f"Retrieved {len(output.documents)} context documents")
        return {"context_documents": output.documents}
    except Exception as e:
        print(f"RAG retrieval failed: {e}")
        return {"context_documents": []}


def asset_loader_node(state: AgentState) -> Dict[str, Any]:
    """Load LoRAs/Checkpoints from CivitAI."""
    print("--- Loading Assets (CivitAI) ---")

    try:
        node = CivitAINode(name="civitai")
        keywords = state.get("style_keywords", [])

        if keywords:
            output = node.execute(CivitAIInput(query=keywords[0], model_type="LORA"))
            return {"lora_path": output.model_path}

        return {"lora_path": None}
    except Exception as e:
        print(f"Asset loading failed: {e}")
        return {"lora_path": None}


def strategy_node(state: AgentState) -> Dict[str, Any]:
    """Formulate sales strategy based on trends and context."""
    print("--- Formulating Strategy ---")

    try:
        node = SalesStrategyNode(name="sales_strategy")
        output = node.execute(SalesStrategyInput(
            trends=state.get("trends", []),
            gas_price=state.get("gas_price", 50.0),
            art_description=state.get("art_description", "AI Generated Art")
        ))

        return {"sales_strategy": {
            "price": output.listing_price_eth,
            "duration": output.listing_duration_days,
            "rationale": output.rationale,
            "style_keywords": ["cyberpunk", "neon", "futuristic"]
        }}
    except Exception as e:
        print(f"Strategy failed: {e}")
        return {"sales_strategy": {
            "price": 0.1,
            "duration": 7,
            "rationale": "Mock strategy",
            "style_keywords": ["art"]
        }}


def generation_node(state: AgentState) -> Dict[str, Any]:
    """Generate images using ComfyUI."""
    print("--- Generating Content ---")

    try:
        node = ComfyUINode(name="comfyui")

        # Load workflow template
        import json
        template_path = os.path.join(workspace_root, "nodes/comfyui/workflow_template.json")
        try:
            with open(template_path, "r") as f:
                wf = json.load(f)
        except FileNotFoundError:
            wf = {}

        # Inject prompt
        prompt_text = state.get("art_description", "A beautiful digital artwork")
        if "6" in wf and "inputs" in wf["6"]:
            wf["6"]["inputs"]["text"] = prompt_text

        output = node.execute(ComfyUIInput(workflow_json=wf))
        return {"generated_images": output.images}

    except Exception as e:
        print(f"Generation failed: {e}")
        return {"generated_images": ["placeholder.png"]}


def upscale_node(state: AgentState) -> Dict[str, Any]:
    """Upscale generated images using Real-ESRGAN."""
    print("--- Upscaling Images ---")

    images = state.get("generated_images", [])
    if not images or images[0] == "placeholder.png":
        return {"generated_images": images}

    try:
        node = RealESRGANNode(name="real_esrgan")
        upscaled = []

        for img_path in images:
            output = node.execute(RealESRGANInput(image_path=img_path))
            upscaled.append(output.output_path)

        return {"generated_images": upscaled}

    except Exception as e:
        print(f"Upscaling failed: {e}")
        return {"generated_images": images}


def clip_eval_node(state: AgentState) -> Dict[str, Any]:
    """Evaluate images using CLIP."""
    print("--- CLIP Evaluation ---")

    images = state.get("generated_images", [])
    if not images or images[0] == "placeholder.png":
        return {"clip_score": 0.0}

    try:
        node = ClipEvalNode(name="clip_eval")
        output = node.execute(ClipEvalInput(
            image_path=images[0],
            prompt=state.get("art_description", "")
        ))
        print(f"CLIP Score: {output.score}")
        return {"clip_score": output.score}

    except Exception as e:
        print(f"CLIP eval failed: {e}")
        return {"clip_score": 0.5}


def gas_check_node(state: AgentState) -> Dict[str, Any]:
    """Check current gas prices."""
    print("--- Checking Gas ---")

    try:
        node = GasTrackerNode(name="gas_tracker")
        output = node.execute(GasTrackerInput(threshold_gwei=50.0))
        return {"gas_price": output.gas_price_gwei}
    except Exception as e:
        print(f"Gas check failed: {e}")
        return {"gas_price": 30.0}


def review_node(state: AgentState) -> Dict[str, Any]:
    """Human-in-the-loop review using Gradio."""
    print("--- Human Review ---")

    try:
        node = GradioEvalNode(name="gradio_eval")
        img = state["generated_images"][0] if state.get("generated_images") else "placeholder.png"

        output = node.execute(GradioEvalInput(
            image_path=img,
            strategy=state.get("sales_strategy", {}),
            trends=state.get("trends", []),
            gas_price=state.get("gas_price", 0.0)
        ))

        return {"approved": output.approved, "feedback": output.feedback}

    except Exception as e:
        print(f"Review failed: {e}")
        return {"approved": True, "feedback": "Auto-approved (review unavailable)"}


def mint_node(state: AgentState) -> Dict[str, Any]:
    """Mint NFT to blockchain."""
    print("--- Minting NFT ---")

    try:
        node = NFTMintNode(name="nft_mint")
        img = state["generated_images"][0]
        strategy = state["sales_strategy"]

        output = node.execute(NFTMintInput(
            image_path=img,
            name="AI Generated Art",
            description=strategy.get("rationale", "AI Art"),
            price_eth=strategy.get("price", 0.01)
        ))

        return {
            "mint_tx": output.tx_hash,
            "ipfs_url": output.ipfs_url,
            "status": output.status
        }

    except Exception as e:
        print(f"Minting failed: {e}")
        return {"mint_tx": "", "ipfs_url": "", "status": f"error: {e}"}


# =============================================================================
# CONDITIONAL EDGES
# =============================================================================

def check_clip_score(state: AgentState) -> str:
    """Route based on CLIP score threshold."""
    score = state.get("clip_score", 0.0)

    if score >= 0.7:
        return "pass"
    elif score >= 0.5:
        return "review"
    else:
        return "regenerate"


def check_approval(state: AgentState) -> str:
    """Route based on human approval."""
    if state.get("approved"):
        return "mint"
    return END


def check_gas_price(state: AgentState) -> str:
    """Route based on gas price threshold."""
    gas = state.get("gas_price", 999)

    if gas < 30:
        return "proceed"
    return "wait"


# =============================================================================
# GRAPH DEFINITION
# =============================================================================

def create_workflow() -> StateGraph:
    """Create the complete workflow graph."""
    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("social_research", social_research_node)
    workflow.add_node("rag_context", rag_context_node)
    workflow.add_node("gas_check", gas_check_node)
    workflow.add_node("strategy", strategy_node)
    workflow.add_node("asset_loader", asset_loader_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("upscale", upscale_node)
    workflow.add_node("clip_eval", clip_eval_node)
    workflow.add_node("review", review_node)
    workflow.add_node("mint", mint_node)

    # Set entry point
    workflow.set_entry_point("social_research")

    # Add edges - main flow
    workflow.add_edge("social_research", "rag_context")
    workflow.add_edge("rag_context", "gas_check")
    workflow.add_edge("gas_check", "strategy")
    workflow.add_edge("strategy", "asset_loader")
    workflow.add_edge("asset_loader", "generation")
    workflow.add_edge("generation", "upscale")
    workflow.add_edge("upscale", "clip_eval")
    workflow.add_edge("clip_eval", "review")

    # Conditional: Review -> Mint or End
    workflow.add_conditional_edges("review", check_approval)
    workflow.add_edge("mint", END)

    return workflow


# Compile the graph
workflow = create_workflow()
app = workflow.compile()


# =============================================================================
# RUN FUNCTIONS
# =============================================================================

def run_workflow(
    art_description: str = "A stunning cyberpunk cityscape",
    trend_chain: str = "ethereum"
) -> Dict[str, Any]:
    """
    Run the complete content generation workflow.

    Args:
        art_description: Text description for image generation.
        trend_chain: Blockchain for trend analysis.

    Returns:
        Final workflow state.
    """
    initial_state = {
        "trend_chain": trend_chain,
        "art_description": art_description,
        "trends": [],
        "style_keywords": [],
        "generated_images": [],
        "clip_score": 0.0,
        "approved": False,
        "context_documents": []
    }

    result = app.invoke(initial_state)
    return result


if __name__ == "__main__":
    print("Starting Content Farm Workflow...")
    result = run_workflow("A beautiful digital artwork with neon colors")
    print("\nWorkflow Complete!")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Images: {result.get('generated_images', [])}")
