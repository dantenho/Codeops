"""
Alert System for Discord and Email Notifications.

This module provides alerting capabilities for
critical events in the content generation pipeline.
"""

import asyncio
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertSystem:
    """Multi-channel alert system for notifications."""

    def __init__(self):
        # Discord configuration
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

        # Email configuration
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.alert_emails = os.getenv("ALERT_EMAILS", "").split(",")

    async def send_discord_alert(
        self,
        title: str,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        fields: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send alert to Discord webhook.

        Args:
            title: Alert title.
            message: Alert message.
            level: Severity level.
            fields: Additional embed fields.

        Returns:
            True if sent successfully.
        """
        if not self.discord_webhook_url:
            print("Discord webhook not configured")
            return False

        # Color based on level
        colors = {
            AlertLevel.INFO: 0x00ff88,      # Green
            AlertLevel.WARNING: 0xffd700,   # Gold
            AlertLevel.ERROR: 0xff4444,     # Red
            AlertLevel.CRITICAL: 0xff0000   # Bright red
        }

        # Build embed
        embed = {
            "title": f"🚨 {title}",
            "description": message,
            "color": colors.get(level, 0x00ff88),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Content Farm Alert System"}
        }

        if fields:
            embed["fields"] = [
                {"name": f["name"], "value": str(f["value"]), "inline": f.get("inline", True)}
                for f in fields
            ]

        payload = {"embeds": [embed]}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.discord_webhook_url,
                    json=payload
                ) as response:
                    return response.status == 204

        except Exception as e:
            print(f"Discord alert failed: {e}")
            return False

    def send_email_alert(
        self,
        subject: str,
        body: str,
        level: AlertLevel = AlertLevel.INFO
    ) -> bool:
        """
        Send email alert.

        Args:
            subject: Email subject.
            body: Email body (HTML supported).
            level: Severity level.

        Returns:
            True if sent successfully.
        """
        if not self.smtp_user or not self.smtp_password:
            print("Email not configured")
            return False

        if not self.alert_emails or not self.alert_emails[0]:
            print("No alert recipients configured")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{level.value.upper()}] {subject}"
            msg["From"] = self.smtp_user
            msg["To"] = ", ".join(self.alert_emails)

            # HTML body
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; padding: 20px;">
                <h2 style="color: #00ff88;">Content Farm Alert</h2>
                <div style="background: #0f0f0f; padding: 15px; border-radius: 8px;">
                    <strong>Level:</strong> {level.value.upper()}<br>
                    <strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br><br>
                    {body}
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Email alert failed: {e}")
            return False

    async def alert(
        self,
        title: str,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        channels: List[str] = None
    ):
        """
        Send alert to multiple channels.

        Args:
            title: Alert title.
            message: Alert message.
            level: Severity level.
            channels: List of channels ("discord", "email"). Default: all.
        """
        if channels is None:
            channels = ["discord", "email"]

        results = {}

        if "discord" in channels:
            results["discord"] = await self.send_discord_alert(title, message, level)

        if "email" in channels:
            results["email"] = self.send_email_alert(title, message, level)

        print(f"Alert sent: {title} | Results: {results}")
        return results


# Predefined alert functions
alert_system = AlertSystem()


async def alert_generation_complete(
    prompt: str,
    images: List[str],
    time_seconds: float
):
    """Alert when generation completes."""
    await alert_system.alert(
        "Generation Complete",
        f"Successfully generated {len(images)} images in {time_seconds:.1f}s",
        AlertLevel.INFO
    )


async def alert_generation_failed(
    prompt: str,
    error: str
):
    """Alert when generation fails."""
    await alert_system.alert(
        "Generation Failed",
        f"Prompt: {prompt[:50]}...\nError: {error}",
        AlertLevel.ERROR
    )


async def alert_low_gas(gas_price: float):
    """Alert when gas price is favorable."""
    await alert_system.alert(
        "Low Gas Alert",
        f"Current gas price: {gas_price:.1f} gwei - Good time to mint!",
        AlertLevel.INFO
    )


async def alert_mint_success(tx_hash: str, ipfs_url: str):
    """Alert on successful NFT mint."""
    await alert_system.alert(
        "NFT Minted Successfully",
        f"TX: {tx_hash}\nIPFS: {ipfs_url}",
        AlertLevel.INFO
    )


if __name__ == "__main__":
    # Test alerts
    async def test():
        await alert_system.alert(
            "Test Alert",
            "This is a test message from the Content Farm alert system.",
            AlertLevel.INFO
        )

    asyncio.run(test())
