import logging

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.config import settings

logger = logging.getLogger(__name__)

client: QdrantClient = None
COLLECTION_NAME = "articles_embeddings"


def connect_to_qdrant():
    global client
    if client is None:
        client = QdrantClient(url=settings.qdrant_api_url)
        logger.info(f"Connected to Qdrant at {settings.qdrant_api_url}")

        # Ensure collection exists with multi-vector configuration
        create_multi_vector_collection()

    return client


def get_qdrant_client() -> QdrantClient:
    if client is None:
        raise RuntimeError(
            "Qdrant client not initialized. Call connect_to_qdrant() first."
        )
    return client


def create_multi_vector_collection():
    """Create or update collection with multiple vector configurations"""
    global client
    if client is None:
        connect_to_qdrant()

    try:
        # Check if collection exists
        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        logger.info(f"✅ Collection '{COLLECTION_NAME}' already exists")

        # Verify it has the right vector configuration
        existing_vectors = collection_info.config.params.vectors
        required_vectors = {
            "title_embedding",
            "primary_embedding",
            "secondary_embedding",
        }

        if isinstance(existing_vectors, dict):
            existing_vector_names = set(existing_vectors.keys())
            if existing_vector_names == required_vectors:
                logger.info("✅ Collection has correct multi-vector configuration")
                return
            else:
                logger.warning(
                    "⚠️ Collection has different vector configuration. Recreating..."
                )
                # Collection exists but with wrong configuration, recreate it
                client.recreate_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=_get_vectors_config(),
                )
                logger.info(
                    f"✅ Recreated collection '{COLLECTION_NAME}' with multi-vector configuration"
                )
        else:
            # Single vector collection, recreate as multi-vector
            logger.warning(
                "⚠️ Single vector collection detected. Recreating as multi-vector..."
            )
            client.recreate_collection(
                collection_name=COLLECTION_NAME, vectors_config=_get_vectors_config()
            )
            logger.info(
                f"✅ Recreated collection '{COLLECTION_NAME}' with multi-vector configuration"
            )

    except Exception as e:
        logger.error("error: ", e)
        # Collection doesn't exist, create it
        logger.info(f"Creating new multi-vector collection '{COLLECTION_NAME}'...")
        client.recreate_collection(
            collection_name=COLLECTION_NAME, vectors_config=_get_vectors_config()
        )
        logger.info(f"✅ Created multi-vector collection '{COLLECTION_NAME}'")


def _get_vectors_config():
    """Get the vector configuration for multi-vector setup"""
    return {
        "title_embedding": VectorParams(size=768, distance=Distance.COSINE),
        "primary_embedding": VectorParams(size=768, distance=Distance.COSINE),
        "secondary_embedding": VectorParams(size=768, distance=Distance.COSINE),
    }


def get_collection_name() -> str:
    """Get the collection name for embeddings"""
    return COLLECTION_NAME
