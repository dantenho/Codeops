"""
FastAPI Dashboard with WebSocket Real-time Monitoring.

This module provides a web dashboard for monitoring
the Digital Content Farm in real-time.
"""

from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(
    title="Digital Content Farm Dashboard",
    description="Real-time monitoring for AI content generation",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        import json
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass


manager = ConnectionManager()


# Data models
class WorkflowStatus(BaseModel):
    id: str
    status: str
    node: str
    progress: float
    created_at: datetime

class GenerationRequest(BaseModel):
    prompt: str
    batch_size: int = 1


# In-memory state (replace with Redis in production)
workflow_states: Dict[str, WorkflowStatus] = {}
metrics: Dict[str, Any] = {
    "total_generations": 0,
    "successful": 0,
    "failed": 0,
    "avg_time_seconds": 0.0,
    "gpu_utilization": 0.0
}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Content Farm Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: #fff; margin: 0; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #00ff88; }
            .card { background: #1a1a2e; border-radius: 12px; padding: 20px; margin: 10px 0; }
            .metric { display: inline-block; margin: 10px 20px; text-align: center; }
            .metric-value { font-size: 2em; color: #00ff88; }
            .metric-label { color: #888; }
            .status-running { color: #ffd700; }
            .status-completed { color: #00ff88; }
            .status-failed { color: #ff4444; }
            #log { background: #0a0a0a; padding: 10px; border-radius: 8px; max-height: 300px; overflow-y: auto; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Digital Content Farm</h1>

            <div class="card">
                <h2>Metrics</h2>
                <div class="metric">
                    <div class="metric-value" id="total">0</div>
                    <div class="metric-label">Total Generations</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="success">0</div>
                    <div class="metric-label">Successful</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="gpu">0%</div>
                    <div class="metric-label">GPU Usage</div>
                </div>
            </div>

            <div class="card">
                <h2>Live Log</h2>
                <div id="log"></div>
            </div>
        </div>

        <script>
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'metrics') {
                    document.getElementById('total').textContent = data.total_generations;
                    document.getElementById('success').textContent = data.successful;
                    document.getElementById('gpu').textContent = data.gpu_utilization.toFixed(1) + '%';
                } else if (data.type === 'log') {
                    const log = document.getElementById('log');
                    log.innerHTML += `<div>[${new Date().toLocaleTimeString()}] ${data.message}</div>`;
                    log.scrollTop = log.scrollHeight;
                }
            };
        </script>
    </body>
    </html>
    """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_json({"type": "metrics", **metrics})

        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/metrics")
async def get_metrics():
    """Get current metrics."""
    return metrics


@app.get("/api/workflows")
async def get_workflows():
    """Get active workflow states."""
    return list(workflow_states.values())


@app.post("/api/generate")
async def trigger_generation(request: GenerationRequest):
    """Trigger a new image generation."""
    import uuid

    workflow_id = str(uuid.uuid4())[:8]

    # Broadcast to connected clients
    await manager.broadcast({
        "type": "log",
        "message": f"Starting generation: {request.prompt[:50]}..."
    })

    metrics["total_generations"] += 1

    await manager.broadcast({"type": "metrics", **metrics})

    return {"workflow_id": workflow_id, "status": "queued"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
