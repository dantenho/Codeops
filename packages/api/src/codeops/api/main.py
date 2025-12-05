from codeops.api.routers import agents
from codeops.core.config import settings
from codeops.core.logging import configure_logging
from fastapi import FastAPI

configure_logging()

app = FastAPI(
    title="CodeOps API",
    version="0.1.0",
    debug=settings.DEBUG
)

app.include_router(agents.router)

# Include Nodes router
try:
    from codeops.api.routers import nodes
    app.include_router(nodes.router)
except ImportError as e:
    import logging
    logging.warning(f"Nodes router not available: {e}")

# Include Workflows router
try:
    from codeops.api.routers import workflows
    app.include_router(workflows.router)
except ImportError as e:
    import logging
    logging.warning(f"Workflows router not available: {e}")

# Include Execute router
try:
    from codeops.api.routers import execute
    app.include_router(execute.router)
except ImportError as e:
    import logging
    logging.warning(f"Execute router not available: {e}")

# Include Suggestion Tunnel router
try:
    from codeops.api.routers import tunnel
    app.include_router(tunnel.router)
except ImportError as e:
    import logging
    logging.warning(f"Suggestion Tunnel router not available: {e}")

# Include Webhooks router
try:
    from codeops.api import webhooks
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
except ImportError as e:
    import logging
    logging.warning(f"Webhooks router not available: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "env": settings.ENV}
