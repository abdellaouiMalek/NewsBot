import logging

from fastapi import BackgroundTasks

from app.core.database import get_database
from app.services.ingestion_service import (
    fetch_and_store_api_articles,
    fetch_and_store_rss_articles,
)

logger = logging.getLogger(__name__)


async def fetch_all_news(db):
    background_tasks = BackgroundTasks()
    rss_count = await fetch_and_store_rss_articles(db, background_tasks)
    api_count = await fetch_and_store_api_articles(db, background_tasks)
    logger.info(f"📰 Fetched {rss_count} RSS and {api_count} API articles")


async def fetch_all_news_job():
    """Async job for AsyncIOScheduler."""
    try:
        db = get_database()
        await fetch_all_news(db)
        logger.info("✅ fetch_all_news_job executed successfully")
    except Exception as e:
        logger.error(f"❌ Error running fetch_all_news_job: {e}")
