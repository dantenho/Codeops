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

# Include Suggestion Tunnel router
try:
    from codeops.api.routers import tunnel
    app.include_router(tunnel.router)
except ImportError as e:
    import logging
    logging.warning(f"Suggestion Tunnel router not available: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "env": settings.ENV}
