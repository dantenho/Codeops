"""
Integration module for connecting Suggestion Tunnel with Claude Code.
Includes Antigravity Consultant integration with Gemini 2.5 Pro Flash.
"""
import logging
import os
from typing import Any, Dict, Optional
from .models import SuggestionBin
from .tunnel import SuggestionTunnel
from .consultant import AntigravityConsultant
from .config import settings

logger = logging.getLogger(__name__)


async def claude_code_handler(bin: SuggestionBin) -> None:
    """
    Handler function that sends critical suggestions to Claude Code.
    This is registered as a callback in the SuggestionTunnel.

    Args:
        bin: A SuggestionBin containing critical code issues
    """
    logger.info(f"Sending bin {bin.id} to Claude Code")
    logger.info(f"Bin contains {len(bin.suggestions)} critical suggestions")

    # Format suggestions for Claude Code
    for suggestion in bin.suggestions:
        logger.info(
            f"Critical Issue: {suggestion.type.value} "
            f"[{suggestion.severity.value}] in {suggestion.file_path}:{suggestion.line_start}"
        )
        logger.info(f"Description: {suggestion.description}")

    # Here you would integrate with actual Claude Code API/interface
    # For now, we log the critical issues
    # TODO: Implement actual Claude Code integration based on your setup

    return None


def setup_tunnel_with_claude(
    tunnel: SuggestionTunnel,
    consultant: Optional[AntigravityConsultant] = None
) -> None:
    """
    Setup the tunnel with Claude Code integration and Consultant.
    Call this during application startup.

    Args:
        tunnel: The SuggestionTunnel instance
        consultant: Optional AntigravityConsultant instance
    """
    tunnel.register_claude_callback(claude_code_handler)
    logger.info("Suggestion Tunnel connected to Claude Code")

    # Setup Consultant if available
    if consultant:
        logger.info("Antigravity Consultant integrated with tunnel")

        # Auto-start evaluation loop if configured
        if settings.CONSULTANT_AUTO_START_LOOP:
            import asyncio
            try:
                asyncio.create_task(consultant.start_evaluation_loop())
                logger.info("Auto-started Consultant evaluation loop")
            except RuntimeError:
                logger.warning("Could not auto-start evaluation loop - no running event loop")


def create_consultant() -> Optional[AntigravityConsultant]:
    """
    Create an Antigravity Consultant instance if configured.

    Returns:
        AntigravityConsultant instance or None if not configured
    """
    if not settings.CONSULTANT_ENABLED:
        logger.info("Consultant disabled in settings")
        return None

    # Check for API key
    api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.warning(
            "GOOGLE_API_KEY not set. Consultant will not be available. "
            "Set GOOGLE_API_KEY environment variable to enable."
        )
        return None

    try:
        consultant = AntigravityConsultant(gemini_api_key=api_key)
        logger.info("✨ Antigravity Consultant initialized with Gemini 2.5 Pro Flash")
        return consultant
    except Exception as e:
        logger.error(f"Failed to initialize Consultant: {e}")
        return None


def create_default_channels(tunnel: SuggestionTunnel) -> Dict[str, str]:
    """
    Create default channels for common use cases.
    Returns a dict mapping channel names to channel IDs.
    """
    channels = {}

    # Main channel for Cursor IDE suggestions
    cursor_channel = tunnel.create_channel(
        name="cursor-ide-main",
        description="Main channel for critical code suggestions from Cursor IDE",
        filter_criteria={"source": "cursor_ide"}
    )
    channels["cursor-main"] = cursor_channel.id

    # Security-specific channel
    security_channel = tunnel.create_channel(
        name="security-alerts",
        description="Channel for security vulnerabilities only",
        filter_criteria={"type": "security_vulnerability"}
    )
    channels["security"] = security_channel.id

    # Runtime errors channel
    runtime_channel = tunnel.create_channel(
        name="runtime-errors",
        description="Channel for runtime and breaking change errors",
        filter_criteria={"types": ["runtime_error", "breaking_change"]}
    )
    channels["runtime"] = runtime_channel.id

    logger.info(f"Created {len(channels)} default channels")
    return channels
