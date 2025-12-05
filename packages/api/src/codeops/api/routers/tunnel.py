"""
FastAPI router integration for Suggestion Tunnel.
Import the tunnel API and set up integration with Consultant.
"""
import sys
from pathlib import Path

# Add bin/channel to Python path
project_root = Path(__file__).parents[6]  # Navigate up to project root
channel_path = project_root / "bin" / "channel"
sys.path.insert(0, str(channel_path))

from api import router as tunnel_router, get_tunnel
from api_consultant import router as consultant_router, get_consultant
from integration import setup_tunnel_with_claude, create_default_channels, create_consultant

# Initialize tunnel with Claude Code integration
tunnel = get_tunnel()

# Create Consultant if configured
consultant = create_consultant()

# Setup integration
setup_tunnel_with_claude(tunnel, consultant)

# Create default channels
default_channels = create_default_channels(tunnel)

# Combine routers
from fastapi import APIRouter
router = APIRouter()
router.include_router(tunnel_router)
router.include_router(consultant_router)

# Export
__all__ = ["router", "default_channels", "consultant"]
