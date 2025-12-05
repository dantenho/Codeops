import asyncio
import os
import sys

# Ensure packages are in path
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
if workspace_root not in sys.path:
    sys.path.append(workspace_root)
    sys.path.append(os.path.join(workspace_root, "packages/core/src"))
    sys.path.append(os.path.join(workspace_root, "packages/orchestrator/src"))

# Mock ComfyUI server for testing
# In reality, you'd need a running ComfyUI instance.
# This test will likely fail on the connection step unless we mock the node execution.

async def test_image_generation():
    print("Testing Image Generation Flow...")

    try:
        from codeops.orchestrator.graph import app

        initial_state = {
            "trend_chain": "ethereum",
            "art_description": "A futuristic cyberpunk city with neon lights, high quality, 8k",
            "trends": [],
            "sales_strategy": {},
            "workflow_json": {}, # Will be loaded by the node
            "generated_images": [],
            "approved": True, # Auto-approve for test
            "feedback": "Looks good",
            "gas_price": 20.0, # Low gas to pass check
            "mint_tx": "",
            "ipfs_url": "",
            "status": "Started"
        }

        # We need to mock the ComfyUINode.execute method if no server is running
        # But let's try to run it and see if it handles the connection error gracefully (we added try/except)

        result = await app.ainvoke(initial_state)

        print("Workflow finished.")
        print(f"Generated Images: {result.get('generated_images')}")
        print(f"Status: {result.get('status')}")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_generation())
