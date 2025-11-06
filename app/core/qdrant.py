import logging
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.config import settings

logger = logging.getLogger(__name__)

# single module-level client (sync)
_client: Optional[QdrantClient] = None
COLLECTION_NAME = "articles_embeddings"


def connect_to_qdrant() -> QdrantClient:
    """
    Initialize (or return) a sync QdrantClient and ensure the collection exists
    with the required multi-vector configuration.
    """
    global _client
    if _client is None:
        _client = QdrantClient(
            url=settings.qdrant_api_url,
            api_key=getattr(settings, "qdrant_api_key", None),
        )
        logger.info("Connected to Qdrant at %s", settings.qdrant_api_url)
        ensure_multi_vector_collection(_client)
    return _client


def get_qdrant_client() -> QdrantClient:
    if _client is None:
        raise RuntimeError(
            "Qdrant client not initialized. Call connect_to_qdrant() first."
        )
    return _client


def _vectors_config():
    # Make sizes configurable from settings if needed
    size = getattr(settings, "vector_size", 768)
    return {
        "title_embedding": VectorParams(size=size, distance=Distance.COSINE),
        "primary_embedding": VectorParams(size=size, distance=Distance.COSINE),
        "secondary_embedding": VectorParams(size=size, distance=Distance.COSINE),
    }


def ensure_multi_vector_collection(client: QdrantClient):
    """
    Ensure collection exists and has the named vector configuration.
    If the collection exists with a different vector config, we recreate it intentionally.
    """
    try:
        info = client.get_collection(collection_name=COLLECTION_NAME)
        logger.info("Qdrant collection '%s' exists", COLLECTION_NAME)

        # `info.config.params.vectors` may be a VectorParams or a dict - handle accordingly
        existing_vectors = getattr(info.config.params, "vectors", None)

        required_vector_names = set(_vectors_config().keys())
        if isinstance(existing_vectors, dict):
            existing_names = set(existing_vectors.keys())
            if existing_names == required_vector_names:
                logger.info("Collection already has required named vectors.")
                return
            else:
                logger.warning(
                    "Collection %s has different vector names (%s). Recreating...",
                    COLLECTION_NAME,
                    existing_names,
                )
                client.recreate_collection(
                    collection_name=COLLECTION_NAME, vectors_config=_vectors_config()
                )
                logger.info("Recreated collection with multi-vector config.")
                return
        else:
            # single vector or unexpected format — recreate with multi-vector config
            logger.warning(
                "Collection vectors format is not named vectors. Recreating as multi-vector collection."
            )
            client.recreate_collection(
                collection_name=COLLECTION_NAME, vectors_config=_vectors_config()
            )
            logger.info("Recreated collection as multi-vector.")
            return

    except Exception:
        # If get_collection fails (collection not found, etc.) create it
        logger.info("Creating new multi-vector collection '%s'...", COLLECTION_NAME)
        try:
            client.create_collection(
                collection_name=COLLECTION_NAME, vectors_config=_vectors_config()
            )
            logger.info("Created collection '%s'", COLLECTION_NAME)
        except Exception:
            # fall back to recreate_collection if create_collection isn't available in client version
            logger.exception(
                "create_collection failed; attempting recreate_collection..."
            )
            client.recreate_collection(
                collection_name=COLLECTION_NAME, vectors_config=_vectors_config()
            )
            logger.info("Recreated collection '%s' after fallback", COLLECTION_NAME)


def get_collection_name() -> str:
    return COLLECTION_NAME
