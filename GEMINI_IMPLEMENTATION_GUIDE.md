# Gemini Implementation Guide

**Status**: 📝 Ready to start parallel work
**Created**: 2025-12-05T09:25:00Z
**Agent**: Antigravity (for Gemini)

## 🎯 Current Status

- ✅ **Cursor**: Working on FastAPI server (`api/main.py`)
- ✅ **Gemini**: Ready to start parallel tasks
- ✅ **Communication**: Tunnel system operational

## 📦 Code Structure Discovered

### Node Registry
**Location**: `packages/orchestrator/src/codeops/orchestrator/registry.py`

**Key Components**:
- `NODE_REGISTRY`: Dict[str, NodeConfig] - All registered nodes
- `NodeConfig` dataclass with: name, module_path, input_class, output_class, node_class, description, gpu_enabled, requires_api_key, dependencies
- Functions: `get_node()`, `list_nodes()`, `check_dependencies()`
- **Total Nodes**: 13+ nodes (social_media, firecrawl, rag, comfyui, real_esrgan, anime4k, clip_eval, civitai, google_genai, gas_tracker, asset_publisher, gradio_eval)

### API Structure
**Location**: `packages/api/src/codeops/api/routers/`

**Existing Routers**:
- `agents.py` - Agent management
- `tunnel.py` - Tunnel communication

**To Create**:
- `nodes.py` - Node registry API
- `workflows.py` - Workflow execution API
- `telemetry.py` - Telemetry API

### Orchestrator
**Location**: `packages/orchestrator/src/codeops/orchestrator/`

**Files**:
- `registry.py` - Node registry (exists)
- `graph.py` - LangGraph workflow builder

## 🚀 Task 1: Node Registry API Wrapper

### Implementation Plan

**File**: `packages/api/src/codeops/api/routers/nodes.py`

**Endpoints to Create**:
```python
GET  /api/nodes              # List all nodes
GET  /api/nodes/{node_id}    # Get node details
GET  /api/nodes?gpu_only=true  # Filter GPU nodes
GET  /api/nodes?requires_api_key=true  # Filter by API key requirement
POST /api/nodes/check        # Check node dependencies
```

**Implementation Steps**:
1. Import `NODE_REGISTRY` and functions from `codeops.orchestrator.registry`
2. Create FastAPI router
3. Convert `NodeConfig` to Pydantic models for API responses
4. Implement endpoints
5. Add error handling
6. Write tests

**Dependencies**:
- `fastapi` (already in API package)
- `codeops.orchestrator.registry` (import from orchestrator package)

## 🚀 Task 2: Workflow Execution Service

### Implementation Plan

**File**: `packages/api/src/codeops/api/routers/workflows.py`

**Endpoints to Create**:
```python
POST /api/execute            # Execute workflow
GET  /api/workflows          # List workflow templates
GET  /api/workflows/{id}     # Get workflow status
POST /api/workflows/{template}/execute  # Execute from template
```

**Implementation Steps**:
1. Review `packages/orchestrator/src/codeops/orchestrator/graph.py`
2. Create workflow execution service
3. Integrate with LangGraph
4. Add status tracking
5. Create API endpoints
6. Handle async execution

**Dependencies**:
- `codeops.orchestrator.graph` (workflow builder)
- `codeops.orchestrator.registry` (node registry)
- LangGraph runtime

## 🚀 Task 3: Telemetry Integration

### Implementation Plan

**File**: `packages/api/src/codeops/api/routers/telemetry.py`

**Endpoints to Create**:
```python
GET  /api/telemetry/metrics  # Get system metrics
GET  /api/telemetry/logs     # Get operation logs
POST /api/telemetry/log      # Submit telemetry log
GET  /api/telemetry/agents   # Get agent telemetry
```

**Implementation Steps**:
1. Review `packages/telemetry/` structure
2. Create telemetry service wrapper
3. Add metrics aggregation
4. Create API endpoints
5. Integrate with existing telemetry system

**Dependencies**:
- `codeops.telemetry` (telemetry package)
- Existing telemetry logs in `CodeAgents/{Agent}/logs/`

## 📋 Integration with Cursor's FastAPI

Once Cursor completes `api/main.py`, integration pattern:

```python
# In api/main.py (Cursor's file)
from fastapi import FastAPI
from codeops.api.routers import nodes, workflows, telemetry

app = FastAPI()

# Cursor's endpoints
@app.get("/health")
def health():
    return {"status": "ok"}

# Gemini's routers
app.include_router(nodes.router, prefix="/api", tags=["nodes"])
app.include_router(workflows.router, prefix="/api", tags=["workflows"])
app.include_router(telemetry.router, prefix="/api", tags=["telemetry"])
```

## 🎯 Recommended Order

1. **Start with Node Registry API** (easiest, good foundation)
2. **Then Workflow Execution** (builds on node registry)
3. **Finally Telemetry** (can be done in parallel)

## 📝 Notes

- All routers should follow FastAPI best practices
- Use Pydantic models for request/response validation
- Add proper error handling
- Include docstrings following Agents.MD protocol
- Write tests for each endpoint

---

**Ready to begin!** Start with Node Registry API wrapper. 🚀
