import json
import urllib.parse
import urllib.request
import uuid
from typing import Any, Dict, List

import websocket
from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class ComfyUIInput(NodeInput):
    workflow_json: Dict[str, Any] = Field(..., description="ComfyUI workflow JSON")
    server_address: str = Field(default="127.0.0.1:8188", description="ComfyUI server address")

class ComfyUIOutput(NodeOutput):
    images: List[str] = Field(..., description="List of generated image paths")
    history: Dict[str, Any] = Field(default={}, description="Execution history")

class ComfyUINode(NodeBase):
    """Node for ComfyUI integration."""

    def queue_prompt(self, prompt: Dict[str, Any], client_id: str, server_address: str):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(self, filename: str, subfolder: str, folder_type: str, server_address: str):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
            return response.read()

    def get_history(self, prompt_id: str, server_address: str):
        with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())

    def execute(self, input_data: ComfyUIInput) -> ComfyUIOutput:
        server_address = input_data.server_address
        client_id = str(uuid.uuid4())

        try:
            ws = websocket.WebSocket()
            ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
        except Exception as e:
            print(f"Failed to connect to ComfyUI at {server_address}: {e}")
            # Return empty/mock if connection fails, or raise
            # raise e
            return ComfyUIOutput(images=[], history={"error": str(e)})

        # Dynamic Prompt Replacement
        # We assume the input workflow_json might contain placeholders or we might want to inject values
        # For this implementation, we'll just use the workflow_json as is,
        # but in a real scenario, we'd traverse the dict and replace keys.

        prompt_id = self.queue_prompt(input_data.workflow_json, client_id, server_address)['prompt_id']

        output_images = []
        current_history = {}

        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break # Execution done
            else:
                continue

        history = self.get_history(prompt_id, server_address)[prompt_id]
        current_history = history

        # Download images
        import os
        os.makedirs("output/comfyui", exist_ok=True)

        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                for image in node_output['images']:
                    fname = image['filename']
                    subfolder = image['subfolder']
                    folder_type = image['type']

                    image_data = self.get_image(fname, subfolder, folder_type, server_address)

                    save_path = os.path.join("output/comfyui", fname)
                    with open(save_path, "wb") as f:
                        f.write(image_data)

                    output_images.append(os.path.abspath(save_path))

        ws.close()
        return ComfyUIOutput(images=output_images, history=current_history)
