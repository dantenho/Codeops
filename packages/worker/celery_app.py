"""
Celery Worker for Parallel Image Generation.

This module provides distributed task processing for
generating images across multiple ComfyUI instances.
"""

import os
from typing import Any, Dict, List

from celery import Celery

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "content_farm",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["packages.worker.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)


@celery_app.task(bind=True, name="generate_image")
def generate_image_task(self, workflow_json: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """
    Celery task for image generation.

    Args:
        workflow_json: ComfyUI workflow configuration.
        prompt: Text prompt for generation.

    Returns:
        Dict with generated image paths and metadata.
    """
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

    from nodes.comfyui.node import ComfyUIInput, ComfyUINode

    # Update task state
    self.update_state(state="PROCESSING", meta={"prompt": prompt})

    try:
        node = ComfyUINode(name="comfyui_worker")

        # Inject prompt into workflow
        if "6" in workflow_json and "inputs" in workflow_json["6"]:
            workflow_json["6"]["inputs"]["text"] = prompt

        output = node.execute(ComfyUIInput(workflow_json=workflow_json))

        return {
            "status": "success",
            "images": output.images,
            "prompt": prompt
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "prompt": prompt
        }


@celery_app.task(bind=True, name="batch_generate")
def batch_generate_task(self, prompts: List[str]) -> List[Dict[str, Any]]:
    """
    Generate images for multiple prompts in parallel.

    Args:
        prompts: List of text prompts.

    Returns:
        List of generation results.
    """
    from celery import group

    # Load default workflow
    workflow_path = os.path.join(
        os.path.dirname(__file__),
        "../../nodes/comfyui/workflow_template.json"
    )

    try:
        import json
        with open(workflow_path, "r") as f:
            workflow = json.load(f)
    except FileNotFoundError:
        workflow = {}

    # Create group of tasks
    job = group(
        generate_image_task.s(workflow, prompt)
        for prompt in prompts
    )

    # Execute and wait for results
    result = job.apply_async()
    return result.get()
