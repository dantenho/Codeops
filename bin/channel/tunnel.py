"""
Suggestion Tunnel - Main pipeline connecting Cursor IDE → Antigravity → Claude Code.
"""
import asyncio
from typing import List, Optional, Callable, Dict, Any
from datetime import datetime
import logging

from .models import Suggestion, SuggestionBin, Channel, SeverityLevel
from .antigravity import AntigravityFilter

logger = logging.getLogger(__name__)


class SuggestionTunnel:
    """
    The main pipeline for routing critical code suggestions.

    Flow:
    1. Cursor IDE sends suggestions to the tunnel
    2. Antigravity filter removes non-critical suggestions
    3. Critical suggestions are organized into bins
    4. Bins are forwarded to Claude Code for processing
    """

    def __init__(self):
        self.channels: Dict[str, Channel] = {}
        self.bins: Dict[str, SuggestionBin] = {}
        self.antigravity = AntigravityFilter()
        self.claude_callback: Optional[Callable] = None
        self._active = True

    def create_channel(
        self,
        name: str,
        description: str,
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> Channel:
        """Create a new communication channel."""
        channel = Channel(
            name=name,
            description=description,
            filter_criteria=filter_criteria or {}
        )
        self.channels[channel.id] = channel
        logger.info(f"Created channel: {name} ({channel.id})")
        return channel

    def create_bin(self, name: str, channel_id: str) -> SuggestionBin:
        """Create a new suggestion bin."""
        if channel_id not in self.channels:
            raise ValueError(f"Channel {channel_id} does not exist")

        bin = SuggestionBin(name=name, channel_id=channel_id)
        self.bins[bin.id] = bin
        logger.info(f"Created bin: {name} ({bin.id}) in channel {channel_id}")
        return bin

    def register_claude_callback(self, callback: Callable) -> None:
        """
        Register a callback function to send suggestions to Claude Code.
        Callback should accept: (bin: SuggestionBin) -> None
        """
        self.claude_callback = callback
        logger.info("Registered Claude Code callback")

    async def ingest_from_cursor(
        self,
        suggestions: List[Suggestion],
        channel_id: str,
        bin_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest suggestions from Cursor IDE and process through the tunnel.

        Args:
            suggestions: List of suggestions from Cursor IDE
            channel_id: Target channel ID
            bin_name: Optional bin name (auto-generated if not provided)

        Returns:
            Processing results with statistics
        """
        if channel_id not in self.channels:
            raise ValueError(f"Channel {channel_id} does not exist")

        logger.info(f"Ingesting {len(suggestions)} suggestions from Cursor IDE")

        # Step 1: Filter through Antigravity (critical only)
        critical_suggestions = self.antigravity.filter(suggestions)
        filtered_count = len(suggestions) - len(critical_suggestions)

        logger.info(
            f"Antigravity filtered out {filtered_count} non-critical suggestions. "
            f"{len(critical_suggestions)} critical issues remain."
        )

        if not critical_suggestions:
            return {
                "status": "no_critical_issues",
                "total_received": len(suggestions),
                "filtered_out": filtered_count,
                "critical_count": 0,
                "bin_id": None,
                "message": "No critical issues detected. All suggestions filtered by Antigravity."
            }

        # Step 2: Create or find bin
        if bin_name is None:
            bin_name = f"cursor_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        bin = self.create_bin(bin_name, channel_id)

        # Step 3: Add critical suggestions to bin
        for suggestion in critical_suggestions:
            bin.add_suggestion(suggestion)

        # Step 4: Send to Claude Code if callback registered
        if self.claude_callback:
            try:
                await self.claude_callback(bin)
                logger.info(f"Sent bin {bin.id} to Claude Code")
                for suggestion in bin.suggestions:
                    suggestion.sent_to_claude = True
            except Exception as e:
                logger.error(f"Error sending to Claude Code: {e}")
                bin.status = "error"
                raise

        bin.status = "processing"

        return {
            "status": "success",
            "total_received": len(suggestions),
            "filtered_out": filtered_count,
            "critical_count": len(critical_suggestions),
            "bin_id": bin.id,
            "bin_name": bin.name,
            "critical_breakdown": {
                "critical": sum(1 for s in critical_suggestions if s.severity == SeverityLevel.CRITICAL),
                "high": sum(1 for s in critical_suggestions if s.severity == SeverityLevel.HIGH),
            },
            "message": f"Processed {len(critical_suggestions)} critical issues through tunnel"
        }

    def get_bin(self, bin_id: str) -> Optional[SuggestionBin]:
        """Retrieve a bin by ID."""
        return self.bins.get(bin_id)

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Retrieve a channel by ID."""
        return self.channels.get(channel_id)

    def list_active_bins(self, channel_id: Optional[str] = None) -> List[SuggestionBin]:
        """List all active bins, optionally filtered by channel."""
        bins = [b for b in self.bins.values() if b.status != "closed"]
        if channel_id:
            bins = [b for b in bins if b.channel_id == channel_id]
        return sorted(bins, key=lambda b: b.priority, reverse=True)

    def close_bin(self, bin_id: str) -> None:
        """Mark a bin as closed."""
        if bin_id in self.bins:
            self.bins[bin_id].status = "closed"
            self.bins[bin_id].updated_at = datetime.utcnow()
            logger.info(f"Closed bin {bin_id}")

    async def process_suggestion_sync(
        self,
        suggestion: Suggestion,
        channel_id: str
    ) -> Dict[str, Any]:
        """
        Process a single suggestion synchronously.
        Useful for real-time Cursor IDE integration.
        """
        return await self.ingest_from_cursor(
            [suggestion],
            channel_id,
            bin_name=f"single_{suggestion.id[:8]}"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get tunnel statistics."""
        total_suggestions = sum(len(b.suggestions) for b in self.bins.values())
        critical_count = sum(b.get_critical_count() for b in self.bins.values())

        return {
            "channels": len(self.channels),
            "bins": len(self.bins),
            "active_bins": len([b for b in self.bins.values() if b.status != "closed"]),
            "total_suggestions": total_suggestions,
            "critical_suggestions": critical_count,
            "is_active": self._active
        }
