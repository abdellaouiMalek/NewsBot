import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.tasks.news_tasks import fetch_all_news_job

logger = logging.getLogger(__name__)

# Create a singleton scheduler instance
scheduler = AsyncIOScheduler()


def configure_jobs():
    """Add all jobs to the scheduler if not already added."""
    if not scheduler.get_job("fetch_news"):
        scheduler.add_job(
            fetch_all_news_job,
            trigger=IntervalTrigger(minutes=15),
            id="fetch_news",
            replace_existing=True,
            max_instances=1,
        )
        logger.info("✅ Scheduled job 'fetch_news' added")


def start_scheduler():
    """Start APScheduler if not running."""
    if not scheduler.running:
        scheduler.start()
        logger.info("✅ APScheduler started")
        logger.info(f"Current jobs: {[job.id for job in scheduler.get_jobs()]}")
