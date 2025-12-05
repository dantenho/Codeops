import time
from typing import Any, Dict, List

import gradio as gr
from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field

# Global state to share between Node and Gradio
# In a production system, use a database or Redis
shared_state = {
    "image_path": None,
    "strategy": None,
    "trends": [],
    "gas_price": 0.0,
    "feedback": None,
    "approved": False,
    "done": False
}

def create_demo():
    with gr.Blocks(title="Digital Content Farm Dashboard") as demo:
        gr.Markdown("# Digital Content Farm Dashboard")

        with gr.Tabs():
            with gr.TabItem("Review & Approve"):
                with gr.Row():
                    with gr.Column():
                        img = gr.Image(label="Generated Image", type="filepath")
                    with gr.Column():
                        strategy_text = gr.JSON(label="Sales Strategy")
                        gas_display = gr.Number(label="Current Gas (Gwei)")

                feedback = gr.Textbox(label="Feedback / Modification Request")
                status = gr.Textbox(label="Status", interactive=False)

                with gr.Row():
                    approve_btn = gr.Button("Approve & Mint", variant="primary")
                    reject_btn = gr.Button("Reject", variant="stop")

            with gr.TabItem("Market Intelligence"):
                gr.Markdown("## Current Trends")
                trends_display = gr.JSON(label="NFT Trends")

        # Refresh logic
        refresh_btn = gr.Button("Refresh Data")

        def on_refresh():
            return (
                shared_state["image_path"],
                shared_state["strategy"],
                shared_state["gas_price"],
                shared_state["trends"]
            )

        refresh_btn.click(on_refresh, outputs=[img, strategy_text, gas_display, trends_display])

        def on_approve(f):
            shared_state["feedback"] = f
            shared_state["approved"] = True
            shared_state["done"] = True
            return "Approved! Proceeding to Mint."

        def on_reject(f):
            shared_state["feedback"] = f
            shared_state["approved"] = False
            shared_state["done"] = True
            return "Rejected! Workflow will stop."

        approve_btn.click(on_approve, inputs=[feedback], outputs=[status])
        reject_btn.click(on_reject, inputs=[feedback], outputs=[status])

    return demo

# Singleton for the app
app_instance = None

class GradioEvalInput(NodeInput):
    image_path: str = Field(..., description="Path to image")
    strategy: Dict[str, Any] = Field(..., description="Sales strategy")
    trends: List[Dict[str, Any]] = Field(default=[], description="Market trends")
    gas_price: float = Field(default=0.0, description="Current gas price")

class GradioEvalOutput(NodeOutput):
    approved: bool = Field(..., description="Is approved?")
    feedback: str = Field(..., description="User feedback")

class GradioEvalNode(NodeBase):
    """Node for human evaluation via Gradio."""

    def execute(self, input_data: GradioEvalInput) -> GradioEvalOutput:
        global app_instance

        # Update state
        shared_state["image_path"] = input_data.image_path
        shared_state["strategy"] = input_data.strategy
        shared_state["trends"] = input_data.trends
        shared_state["gas_price"] = input_data.gas_price
        shared_state["done"] = False
        shared_state["approved"] = False

        print("Launching Gradio for evaluation...")

        if app_instance is None:
            demo = create_demo()
            # prevent_thread_lock=True allows the script to continue, but we want to block manually
            _, _, _ = demo.launch(server_name="0.0.0.0", server_port=7860, prevent_thread_lock=True)
            app_instance = demo

        print("Waiting for user input on http://localhost:7860 ...")
        print(f"Please review: {input_data.image_path}")

        # Block until done
        while not shared_state["done"]:
            time.sleep(1)

        return GradioEvalOutput(approved=shared_state["approved"], feedback=shared_state["feedback"] or "")
