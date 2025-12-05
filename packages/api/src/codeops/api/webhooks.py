import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

# Import orchestrator
# Assuming packages are installed or in path
try:
    from codeops.orchestrator.graph import app as graph_app
except ImportError:
    graph_app = None

router = APIRouter()

class TriggerRequest(BaseModel):
    trend_chain: str = "ethereum"
    art_description: str = "Abstract Digital Art"
    callback_url: Optional[str] = None

@router.post("/trigger/content-farm")
async def trigger_content_farm(request: TriggerRequest, background_tasks: BackgroundTasks):
    """Trigger the Digital Content Farm workflow."""
    if not graph_app:
        raise HTTPException(status_code=500, detail="Orchestrator not available")

    run_id = "run_" + os.urandom(4).hex()

    initial_state = {
        "trend_chain": request.trend_chain,
        "art_description": request.art_description,
        "trends": [],
        "sales_strategy": {},
        "workflow_json": {}, # Should load a default workflow
        "generated_images": [],
        "approved": False,
        "feedback": "",
        "gas_price": 0.0,
        "mint_tx": "",
        "ipfs_url": "",
        "status": "Started"
    }

    background_tasks.add_task(run_workflow, initial_state, run_id, request.callback_url)

    return {"status": "accepted", "run_id": run_id}

async def run_workflow(state: Dict[str, Any], run_id: str, callback_url: Optional[str]):
    print(f"Starting workflow run {run_id}")
    try:
        result = await graph_app.ainvoke(state)
        print(f"Workflow {run_id} completed: {result.get('status')}")

        if callback_url:
            # Notify callback
            import requests
            requests.post(callback_url, json={"run_id": run_id, "result": result})

    except Exception as e:
        print(f"Workflow {run_id} failed: {e}")
