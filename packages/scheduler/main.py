"""
Scheduler for Autonomous Runs.

This module provides cron-based scheduling for
autonomous workflow execution.
"""

import asyncio
import os
from datetime import datetime
from typing import Any, Callable, Dict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


class ContentFarmScheduler:
    """Scheduler for autonomous content generation runs."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[str, Any] = {}

    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        print("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        print("Scheduler stopped")

    def add_cron_job(
        self,
        job_id: str,
        func: Callable,
        cron_expression: str,
        **kwargs
    ) -> str:
        """
        Add a cron-based job.

        Args:
            job_id: Unique identifier for the job.
            func: Function to execute.
            cron_expression: Cron expression (e.g., "0 */4 * * *" for every 4 hours).
            **kwargs: Additional arguments passed to the function.

        Returns:
            Job ID.
        """
        # Parse cron expression
        parts = cron_expression.split()

        trigger = CronTrigger(
            minute=parts[0] if len(parts) > 0 else "*",
            hour=parts[1] if len(parts) > 1 else "*",
            day=parts[2] if len(parts) > 2 else "*",
            month=parts[3] if len(parts) > 3 else "*",
            day_of_week=parts[4] if len(parts) > 4 else "*"
        )

        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            kwargs=kwargs,
            replace_existing=True
        )

        self.jobs[job_id] = job
        print(f"Added cron job: {job_id} with schedule: {cron_expression}")

        return job_id

    def add_interval_job(
        self,
        job_id: str,
        func: Callable,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        **kwargs
    ) -> str:
        """
        Add an interval-based job.

        Args:
            job_id: Unique identifier.
            func: Function to execute.
            hours/minutes/seconds: Interval timing.

        Returns:
            Job ID.
        """
        trigger = IntervalTrigger(
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )

        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            kwargs=kwargs,
            replace_existing=True
        )

        self.jobs[job_id] = job
        print(f"Added interval job: {job_id} running every {hours}h {minutes}m {seconds}s")

        return job_id

    def remove_job(self, job_id: str):
        """Remove a scheduled job."""
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            print(f"Removed job: {job_id}")

    def list_jobs(self) -> Dict[str, Dict[str, Any]]:
        """List all scheduled jobs."""
        return {
            job_id: {
                "next_run": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job_id, job in self.jobs.items()
        }


# Predefined workflows
async def run_content_generation():
    """Run the full content generation workflow."""
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

    print(f"[{datetime.now()}] Running scheduled content generation...")

    try:
        from packages.orchestrator.src.codeops.orchestrator.graph import app

        result = app.invoke({
            "trend_chain": "ethereum",
            "art_description": "Automated: Trending Digital Art"
        })

        print(f"[{datetime.now()}] Generation complete: {result.get('status', 'unknown')}")

    except Exception as e:
        print(f"[{datetime.now()}] Generation failed: {e}")


async def run_trend_analysis():
    """Run trend analysis and store in ChromaDB."""
    print(f"[{datetime.now()}] Running scheduled trend analysis...")

    try:
        from nodes.social_media.node import SocialMediaInput, SocialMediaNode

        node = SocialMediaNode(name="scheduled_trends")
        output = node.execute(SocialMediaInput(platform="all"))

        print(f"[{datetime.now()}] Found {len(output.trends)} trends")

    except Exception as e:
        print(f"[{datetime.now()}] Trend analysis failed: {e}")


async def check_gas_prices():
    """Check gas prices and alert if favorable."""
    print(f"[{datetime.now()}] Checking gas prices...")

    try:
        from nodes.gas_tracker.node import GasTrackerInput, GasTrackerNode

        node = GasTrackerNode(name="scheduled_gas")
        output = node.execute(GasTrackerInput(threshold_gwei=30.0))

        if output.proceed:
            print(f"[{datetime.now()}] Gas favorable: {output.gas_price_gwei} gwei - PROCEED")
        else:
            print(f"[{datetime.now()}] Gas too high: {output.gas_price_gwei} gwei - WAIT")

    except Exception as e:
        print(f"[{datetime.now()}] Gas check failed: {e}")


# Create global scheduler instance
scheduler = ContentFarmScheduler()


def setup_default_schedule():
    """Set up default scheduled jobs."""
    # Run content generation every 4 hours
    scheduler.add_cron_job(
        "content_generation",
        run_content_generation,
        "0 */4 * * *"
    )

    # Run trend analysis every hour
    scheduler.add_cron_job(
        "trend_analysis",
        run_trend_analysis,
        "0 * * * *"
    )

    # Check gas every 15 minutes
    scheduler.add_interval_job(
        "gas_check",
        check_gas_prices,
        minutes=15
    )


if __name__ == "__main__":
    setup_default_schedule()
    scheduler.start()

    # Keep running
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        scheduler.stop()
