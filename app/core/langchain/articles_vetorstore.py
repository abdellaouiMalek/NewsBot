from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient

from app.core.config import settings

qdrant = QdrantClient(url=settings.qdrant_api_url)

vector_store = Qdrant(
    client=qdrant,
    collection_name="articles_embeddings",
    embedding_function=None,
)
