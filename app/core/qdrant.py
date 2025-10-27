import logging

from qdrant_client import QdrantClient

from app.core.config import settings

logger = logging.getLogger(__name__)

client: QdrantClient = None


def connect_to_qdrant():
    global client
    if client is None:
        client = QdrantClient(url=settings.qdrant_api_url)
        logger.info(f"Connected to Qdrant at {settings.qdrant_api_url}")
    return client


def get_qdrant_client() -> QdrantClient:
    if client is None:
        raise RuntimeError(
            "Qdrant client not initialized. Call connect_to_qdrant() first."
        )
    return client
