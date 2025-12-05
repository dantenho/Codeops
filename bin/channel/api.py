"""
FastAPI endpoints for the Suggestion Tunnel system.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from .models import Suggestion, SuggestionBin, Channel, SuggestionType, SeverityLevel
from .tunnel import SuggestionTunnel

# Initialize the tunnel
tunnel = SuggestionTunnel()

# Create API router
router = APIRouter(prefix="/tunnel", tags=["suggestion-tunnel"])


# Request/Response Models
class CreateChannelRequest(BaseModel):
    name: str
    description: str
    filter_criteria: Optional[Dict[str, Any]] = None


class IngestSuggestionsRequest(BaseModel):
    suggestions: List[Suggestion]
    channel_id: str
    bin_name: Optional[str] = None


class ProcessSuggestionRequest(BaseModel):
    suggestion: Suggestion
    channel_id: str


# Endpoints
@router.post("/channels", status_code=status.HTTP_201_CREATED)
async def create_channel(request: CreateChannelRequest) -> Channel:
    """Create a new communication channel."""
    try:
        channel = tunnel.create_channel(
            name=request.name,
            description=request.description,
            filter_criteria=request.filter_criteria
        )
        return channel
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create channel: {str(e)}"
        )


@router.get("/channels")
async def list_channels() -> List[Channel]:
    """List all channels."""
    return list(tunnel.channels.values())


@router.get("/channels/{channel_id}")
async def get_channel(channel_id: str) -> Channel:
    """Get a specific channel."""
    channel = tunnel.get_channel(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel {channel_id} not found"
        )
    return channel


@router.post("/ingest", status_code=status.HTTP_200_OK)
async def ingest_suggestions(request: IngestSuggestionsRequest) -> Dict[str, Any]:
    """
    Main endpoint: Ingest suggestions from Cursor IDE.
    Processes through Antigravity filter and routes to Claude Code.
    """
    try:
        result = await tunnel.ingest_from_cursor(
            suggestions=request.suggestions,
            channel_id=request.channel_id,
            bin_name=request.bin_name
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest suggestions: {str(e)}"
        )


@router.post("/process-single", status_code=status.HTTP_200_OK)
async def process_single_suggestion(request: ProcessSuggestionRequest) -> Dict[str, Any]:
    """Process a single suggestion in real-time."""
    try:
        result = await tunnel.process_suggestion_sync(
            suggestion=request.suggestion,
            channel_id=request.channel_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process suggestion: {str(e)}"
        )


@router.get("/bins")
async def list_bins(channel_id: Optional[str] = None) -> List[SuggestionBin]:
    """List all active bins, optionally filtered by channel."""
    return tunnel.list_active_bins(channel_id)


@router.get("/bins/{bin_id}")
async def get_bin(bin_id: str) -> SuggestionBin:
    """Get a specific bin."""
    bin = tunnel.get_bin(bin_id)
    if not bin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bin {bin_id} not found"
        )
    return bin


@router.post("/bins/{bin_id}/close")
async def close_bin(bin_id: str) -> Dict[str, str]:
    """Close a bin."""
    bin = tunnel.get_bin(bin_id)
    if not bin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bin {bin_id} not found"
        )
    tunnel.close_bin(bin_id)
    return {"status": "closed", "bin_id": bin_id}


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get tunnel statistics."""
    return tunnel.get_stats()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "suggestion-tunnel"}


# Helper function to get the tunnel instance (for external integration)
def get_tunnel() -> SuggestionTunnel:
    """Get the global tunnel instance."""
    return tunnel
