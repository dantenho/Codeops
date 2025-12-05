from uuid import uuid4

from codeops.api.celery_client import celery_client
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/agents", tags=["agents"])

class AgentRunRequest(BaseModel):
    inputs: dict

@router.post("/run")
async def run_agent(request: AgentRunRequest):
    """Trigger an agent run."""
    task_id = str(uuid4())
    celery_client.send_task(
        "codeops.worker.tasks.run_agent_task",
        kwargs={"task_id": task_id, "inputs": request.inputs}
    )
    return {"task_id": task_id, "status": "queued"}
