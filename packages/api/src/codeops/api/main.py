from codeops.core.config import settings
from codeops.core.logging import configure_logging
from fastapi import FastAPI

configure_logging()

app = FastAPI(
    title="CodeOps API",
    version="0.1.0",
    debug=settings.DEBUG
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "env": settings.ENV}
