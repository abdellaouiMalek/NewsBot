import logging
import os
from typing import Dict, List, Optional

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient

from app.core.config import settings

logger = logging.getLogger(__name__)

# Respect environment override for embedding device, default to CPU to avoid OOM
# during import. For GPU usage, set EMBEDDING_DEVICE=cuda in your env.
DEVICE = os.environ.get("EMBEDDING_DEVICE", "cpu")


class LangchainQdrantConnector:
    """
    High-level connector between LangChain and Qdrant.
    Handles text → embeddings → vector search seamlessly.
    """

    def __init__(
        self,
        vector_name: str = "primary_embedding",
        embedding_model: Optional[str] = None,
    ):
        self.vector_name = vector_name
        # Default to all-mpnet-base-v2 (768 dims) to match Qdrant collection
        # Override via env var EMBEDDING_MODEL_NAME or parameter
        self.embedding_model_name = embedding_model or os.environ.get(
            "EMBEDDING_MODEL_NAME", "sentence-transformers/all-mpnet-base-v2"
        )

        # Qdrant connection
        self.client = QdrantClient(
            url=settings.qdrant_api_url,
            api_key=getattr(settings, "QDRANT_API_KEY", None),
        )

        # LangChain embeddings - use CPU by default to avoid OOM during import
        # Set EMBEDDING_DEVICE=cuda in environment to use GPU
        logger.info(f"🔧 Loading HuggingFace embeddings on device={DEVICE}")
        self.embedding_fn = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": DEVICE},
        )

        # Vector store (reuse existing client to avoid extra client kwargs)
        self.vector_store = Qdrant(
            client=self.client,
            embeddings=self.embedding_fn,
            collection_name=settings.qdrant_collection,
            vector_name=self.vector_name,
        )

        logger.info(
            f"✅ LangchainQdrantConnector initialized using '{self.embedding_model_name}'"
        )

    def _build_filter(self, filters: Optional[Dict]) -> Optional[Dict]:
        """Convert a dict into Qdrant-compatible filter structure."""
        if not filters:
            return None
        return {"must": [{"key": k, "match": {"value": v}} for k, v in filters.items()]}

    def search(
        self,
        query: Optional[str] = None,
        *,
        query_text: Optional[str] = None,
        k: int = 10,
        filters: Optional[Dict] = None,
    ) -> List[Document]:
        """
        Perform semantic similarity search for a text query.

        Args:
            query: plain text to search semantically (preferred positional argument)
            query_text: backwards-compatible alias for `query`
            k: number of neighbors to return
            filters: optional metadata filters (e.g., {"category": "Science"})

        Returns:
            List[Document]: LangChain Documents with metadata and scores
        """
        if query is None and query_text is None:
            raise ValueError("A query string is required")

        if query is None:
            query = query_text

        # 1️⃣ Compute embedding
        logger.debug(f"Generating embedding for query: {query[:50]}...")
        query_vector = self.embedding_fn.embed_query(query)

        # 2️⃣ Perform vector search in Qdrant
        logger.debug(
            f"Searching in collection '{settings.qdrant_collection}' with vector '{self.vector_name}'"
        )
        results = self.client.search(
            collection_name=settings.qdrant_collection,
            query_vector=(self.vector_name, query_vector),
            query_filter=self._build_filter(filters),
            limit=k,
            with_payload=True,
        )

        # 3️⃣ Convert to LangChain Documents
        documents = [
            Document(
                page_content=point.payload.get("content", ""),
                metadata={
                    "article_id": point.payload.get("article_id"),
                    "category": point.payload.get("category"),
                    "source_name": point.payload.get("source_name"),
                    "published_at": point.payload.get("published_at"),
                    "score": point.score,
                },
            )
            for point in results
        ]

        logger.info(
            f"🔍 Found {len(documents)} similar documents for query '{query[:30]}...'"
        )
        return documents
