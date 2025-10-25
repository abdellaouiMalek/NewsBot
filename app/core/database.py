import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager."""

    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


db = Database()


async def connect_to_mongo():
    """Create database connection."""
    try:
        db.client = AsyncIOMotorClient(settings.mongo_uri)
        db.database = db.client[settings.mongo_db]

        # Test the connection
        await db.client.admin.command("ping")
        logger.info(f"Successfully connected to MongoDB: {settings.mongo_db}")

        # Create indexes (production-ready, background)
        await create_article_indexes(db.database)

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if db.database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return db.database


async def create_article_indexes(db: AsyncIOMotorDatabase):
    """Create indexes for the articles collection."""
    try:
        # Unique index on article_id to prevent duplicates
        await db.articles.create_index("article_id", unique=True, background=True)

        # Index on published_at for fast recent-articles queries
        await db.articles.create_index([("published_at", -1)], background=True)

        # Optional: compound index for filtering by
        #   source_name + category + published_at
        await db.articles.create_index(
            [("source_name", 1), ("category", 1), ("published_at", -1)], background=True
        )

        logger.info("✅ Article indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Failed to create article indexes: {e}")
