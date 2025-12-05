import os
import sys
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

# Ensure nodes are importable
# Assuming 'nodes' is at the root of the workspace
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
if workspace_root not in sys.path:
    sys.path.append(workspace_root)

try:
    from nodes.comfyui.node import ComfyUIInput, ComfyUINode
    from nodes.gas_tracker.node import GasTrackerInput, GasTrackerNode
    from nodes.gradio_eval.node import GradioEvalInput, GradioEvalNode
    from nodes.nft_mint.node import NFTMintInput, NFTMintNode
    from nodes.nft_trend.node import NFTTrendInput, NFTTrendNode
    from nodes.sales_strategy.node import SalesStrategyInput, SalesStrategyNode
except ImportError as e:
    print(f"Warning: Could not import nodes: {e}")
    # Dummy classes to prevent import errors during static analysis
    class NFTTrendNode: execute = lambda self, x: x
    class SalesStrategyNode: execute = lambda self, x: x
    class ComfyUINode: execute = lambda self, x: x
    class GradioEvalNode: execute = lambda self, x: x
    class GasTrackerNode: execute = lambda self, x: x
    class NFTMintNode: execute = lambda self, x: x

class AgentState(TypedDict):
    trend_chain: str
    trends: List[Dict[str, Any]]
    art_description: str
    sales_strategy: Dict[str, Any]
    workflow_json: Dict[str, Any]
    generated_images: List[str]
    approved: bool
    feedback: str
    gas_price: float
    mint_tx: str
    ipfs_url: str
    status: str

# Node Functions for the Graph
def research_node(state: AgentState):
    print("--- Researching Trends ---")
    node = NFTTrendNode(name="nft_trend")
    output = node.execute(NFTTrendInput(chain=state.get("trend_chain", "ethereum")))
    return {"trends": output.trends}

def gas_check_node(state: AgentState):
    print("--- Checking Gas ---")
    node = GasTrackerNode(name="gas_tracker")
    # We just want to get the price here for strategy/dashboard, not necessarily block flow yet
    output = node.execute(GasTrackerInput(threshold_gwei=9999.0))
    return {"gas_price": output.gas_price_gwei}

def strategy_node(state: AgentState):
    print("--- Formulating Strategy ---")
    node = SalesStrategyNode(name="sales_strategy")
    output = node.execute(SalesStrategyInput(
        trends=state.get("trends", []),
        gas_price=state.get("gas_price", 50.0),
        art_description=state.get("art_description", "Abstract Digital Art based on trends")
    ))
    return {"sales_strategy": {
        "price": output.listing_price_eth,
        "duration": output.listing_duration_days,
        "rationale": output.rationale
    }}

def generation_node(state: AgentState):
    print("--- Generating Content ---")
    node = ComfyUINode(name="comfyui")

    # Load template
    import json
    template_path = os.path.join(workspace_root, "nodes/comfyui/workflow_template.json")
    try:
        with open(template_path, "r") as f:
            wf = json.load(f)
    except FileNotFoundError:
        print("Workflow template not found, using empty.")
        wf = {}

    # Inject Prompt (Simple replacement for now)
    # In a real system, we'd find the CLIPTextEncode node ID dynamically
    # Here we assume node "6" is positive prompt based on our template
    prompt_text = state.get("art_description", "A beautiful landscape")
    if "6" in wf and "inputs" in wf["6"]:
        wf["6"]["inputs"]["text"] = prompt_text

    output = node.execute(ComfyUIInput(workflow_json=wf))
    return {"generated_images": output.images}

def review_node(state: AgentState):
    print("--- Human Review ---")
    node = GradioEvalNode(name="gradio_eval")
    img = state["generated_images"][0] if state.get("generated_images") else "placeholder.png"
    output = node.execute(GradioEvalInput(
        image_path=img,
        strategy=state.get("sales_strategy", {}),
        trends=state.get("trends", []),
        gas_price=state.get("gas_price", 0.0)
    ))
    return {"approved": output.approved, "feedback": output.feedback}

def mint_node(state: AgentState):
    print("--- Minting NFT ---")
    node = NFTMintNode(name="nft_mint")
    img = state["generated_images"][0]
    strategy = state["sales_strategy"]
    output = node.execute(NFTMintInput(
        image_path=img,
        name="Generated Art",
        description=strategy.get("rationale", "AI Art"),
        price_eth=strategy.get("price", 0.01)
    ))
    return {"mint_tx": output.tx_hash, "ipfs_url": output.ipfs_url, "status": output.status}

# Define Graph
workflow = StateGraph(AgentState)

workflow.add_node("research", research_node)
workflow.add_node("gas_check", gas_check_node)
workflow.add_node("strategy", strategy_node)
workflow.add_node("generation", generation_node)
workflow.add_node("review", review_node)
workflow.add_node("mint", mint_node)

workflow.set_entry_point("research")

workflow.add_edge("research", "gas_check")
workflow.add_edge("gas_check", "strategy")
workflow.add_edge("strategy", "generation")
workflow.add_edge("generation", "review")

def check_approval(state: AgentState):
    if state.get("approved"):
        return "mint"
    return END

workflow.add_conditional_edges("review", check_approval)
workflow.add_edge("mint", END)

app = workflow.compile()
