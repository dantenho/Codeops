"""
Module: main.py
Purpose: FastAPI backend for EudoraX Prototype.

Provides REST API endpoints for agent telemetry, metrics, and coordination.

Agent: ClaudeCode
Created: 2025-12-04T12:00:00Z
Operation: [MODIFY]
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from core.telemetry import (
    get_telemetry_service,
    TelemetryEvent,
    OperationMetric,
    OperationType,
    OperationStatus
)

app = FastAPI(
    title="EudoraX Prototype API",
    description="Multi-Agent AI Development Workspace Backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================
# Request/Response Models
# ========================

class EventRequest(BaseModel):
    """Request model for recording events."""
    event_type: str
    agent_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetricRequest(BaseModel):
    """Request model for recording metrics."""
    operation_id: str
    agent_id: str
    operation_type: str
    duration_ms: int
    status: str
    file_path: Optional[str] = None
    lines_changed: int = 0
    complexity_score: float = 0.0


class AgentSummaryResponse(BaseModel):
    """Response model for agent summaries."""
    agent_id: str
    total_operations: int
    success_rate: Optional[float] = None
    average_duration_ms: Optional[float] = None
    operations_by_type: Dict[str, int] = Field(default_factory=dict)
    recent_operations: List[Dict[str, Any]] = Field(default_factory=list)
    message: Optional[str] = None


# ========================
# Health Endpoints
# ========================

@app.get("/")
def read_root():
    """Root endpoint with API info."""
    return {
        "name": "EudoraX Prototype API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    telemetry = get_telemetry_service()
    health = telemetry.get_system_health()
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "telemetry": health
    }


# ========================
# Telemetry Endpoints
# ========================

@app.post("/telemetry/events")
def record_event(request: EventRequest):
    """
    Record a telemetry event.
    
    Args:
        request: Event data including type, agent_id, and payload
        
    Returns:
        Event ID and confirmation
    """
    telemetry = get_telemetry_service()
    
    event = TelemetryEvent(
        event_type=request.event_type,
        agent_id=request.agent_id,
        data=request.data,
        metadata=request.metadata
    )
    
    event_id = telemetry.record_event(event)
    
    return {
        "status": "recorded",
        "event_id": event_id,
        "timestamp": event.timestamp
    }


@app.post("/telemetry/metrics")
def record_metric(request: MetricRequest):
    """
    Record an operation metric.
    
    Args:
        request: Metric data including operation details and performance
        
    Returns:
        Metric ID and confirmation
    """
    telemetry = get_telemetry_service()
    
    try:
        operation_type = OperationType(request.operation_type.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid operation_type: {request.operation_type}. "
                   f"Must be one of: {[e.value for e in OperationType]}"
        )
    
    try:
        status = OperationStatus(request.status.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {request.status}. "
                   f"Must be one of: {[e.value for e in OperationStatus]}"
        )
    
    metric = OperationMetric(
        operation_id=request.operation_id,
        agent_id=request.agent_id,
        operation_type=operation_type,
        duration_ms=request.duration_ms,
        status=status,
        file_path=request.file_path,
        lines_changed=request.lines_changed,
        complexity_score=request.complexity_score
    )
    
    metric_id = telemetry.record_metric(metric)
    
    return {
        "status": "recorded",
        "metric_id": metric_id,
        "timestamp": metric.timestamp
    }


@app.get("/telemetry/agents/{agent_id}/summary", response_model=AgentSummaryResponse)
def get_agent_summary(agent_id: str, limit: int = 100):
    """
    Get performance summary for an agent.
    
    Args:
        agent_id: The agent to summarize
        limit: Maximum number of records to analyze
        
    Returns:
        Summary statistics for the agent
    """
    telemetry = get_telemetry_service()
    summary = telemetry.get_agent_summary(agent_id, limit)
    return AgentSummaryResponse(**summary)


@app.get("/telemetry/system/health")
def get_system_health():
    """Get overall system health metrics."""
    telemetry = get_telemetry_service()
    return telemetry.get_system_health()


# ========================
# Agent Management Endpoints
# ========================

VALID_AGENTS = [
    "GrokIA", "Cline", "Antigravity", "Cursor",
    "GeminiFlash25", "GeminiPro25", "GeminiPro30",
    "Jules", "ClaudeCode", "Composer"
]


@app.get("/agents")
def list_agents():
    """List all registered agents."""
    return {
        "agents": VALID_AGENTS,
        "count": len(VALID_AGENTS)
    }


@app.get("/agents/{agent_id}")
def get_agent_info(agent_id: str):
    """Get information about a specific agent."""
    if agent_id not in VALID_AGENTS:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' not found. Valid agents: {VALID_AGENTS}"
        )
    
    telemetry = get_telemetry_service()
    summary = telemetry.get_agent_summary(agent_id, limit=50)
    
    return {
        "agent_id": agent_id,
        "status": "active",
        "summary": summary
    }


# ========================
# Startup Event
# ========================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Pre-initialize the telemetry service
    get_telemetry_service()
    print("✅ EudoraX Prototype API started successfully")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
