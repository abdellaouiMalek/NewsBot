import logging
import os
from typing import Dict, List, Optional

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient

from app.core.config import settings
from app.core.database import get_database
from app.services.article.article_service import ArticleService

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

    async def search(
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

        # 3️⃣ Fetch full articles from MongoDB using article_ids
        article_ids = [
            point.payload.get("article_id")
            for point in results
            if point.payload.get("article_id")
        ]

        if article_ids:
            database = get_database()
            article_service = ArticleService(database)

            # Fetch full articles using ArticleService
            articles = []
            for article_id in article_ids:
                article = await article_service.get_article_by_article_id(article_id)
                if article:
                    articles.append(article)

            # Create a lookup dict for quick access
            articles_by_id = {article.article_id: article for article in articles}
        else:
            articles_by_id = {}

        # 4️⃣ Convert to LangChain Documents with full content
        documents = []
        for point in results:
            article_id = point.payload.get("article_id")
            full_article = articles_by_id.get(article_id) if article_id else None

            # Use embedding_primary_text as page_content if available, otherwise fallback to Qdrant payload
            page_content = ""
            if full_article and full_article.embedding_primary_text:
                page_content = full_article.embedding_primary_text
            else:
                page_content = point.payload.get("content", "")

            # Build comprehensive metadata
            metadata = {
                "article_id": article_id,
                "score": point.score,
            }

            # Add metadata from Qdrant payload
            for key in ["category", "source_name", "published_at"]:
                value = point.payload.get(key)
                if value is not None:
                    metadata[key] = value

            # Add additional metadata from full MongoDB article if available
            if full_article:
                for key in [
                    "title",
                    "summary",
                    "author",
                    "article_url",
                    "language",
                    "country",
                    "tags",
                    "sentiment",
                    "entities",
                ]:
                    value = getattr(full_article, key, None)
                    if value is not None:
                        metadata[key] = value

            documents.append(
                Document(
                    page_content=page_content,
                    metadata=metadata,
                )
            )

        logger.info(
            f"🔍 Found {len(documents)} similar documents for query '{query[:30]}...' (with full content from MongoDB)"
        )
        return documents
