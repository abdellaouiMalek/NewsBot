# app/services/embedding_service.py
import logging
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import FieldCondition, Filter, MatchValue, PointStruct

from app.db.qdrant import get_qdrant_client
from app.schemas.article_embedding import (
    ArticleEmbeddingCreate,
    ArticleEmbeddingResponse,
)

logger = logging.getLogger(__name__)

COLLECTION_NAME = "articles_embeddings"


class EmbeddingService:
    """Service for managing article embeddings in Qdrant using Pydantic schemas."""

    def __init__(self):
        self.client: QdrantClient = get_qdrant_client()

    def upsert_embedding(
        self, embedding: ArticleEmbeddingCreate
    ) -> ArticleEmbeddingResponse:
        """Insert or update a single embedding."""
        point = PointStruct(
            id=embedding.article_id,
            vectors=embedding.vectors,
            payload={
                "category": embedding.category,
                "source_name": embedding.source_name,
                "published_at": (
                    embedding.published_at.isoformat()
                    if embedding.published_at
                    else None
                ),
            },
        )

        self.client.upsert(collection_name=COLLECTION_NAME, points=[point])
        logger.info(f"✅ Upserted embedding for article {embedding.article_id}")

        return ArticleEmbeddingResponse(
            id=embedding.article_id,
            article_id=embedding.article_id,
            vectors=embedding.vectors,
            category=embedding.category,
            source_name=embedding.source_name,
            published_at=embedding.published_at,
        )

    def batch_upsert(
        self, embeddings: List[ArticleEmbeddingCreate]
    ) -> List[ArticleEmbeddingResponse]:
        """Upsert multiple embeddings at once."""
        points: List[PointStruct] = []
        responses: List[ArticleEmbeddingResponse] = []

        for embedding in embeddings:
            if not embedding.vectors:
                continue
            points.append(
                PointStruct(
                    id=embedding.article_id,
                    vectors=embedding.vectors,
                    payload={
                        "category": embedding.category,
                        "source_name": embedding.source_name,
                        "published_at": (
                            embedding.published_at.isoformat()
                            if embedding.published_at
                            else None
                        ),
                    },
                )
            )
            responses.append(
                ArticleEmbeddingResponse(
                    id=embedding.article_id,
                    article_id=embedding.article_id,
                    vectors=embedding.vectors,
                    category=embedding.category,
                    source_name=embedding.source_name,
                    published_at=embedding.published_at,
                )
            )

        if points:
            self.client.upsert(collection_name=COLLECTION_NAME, points=points)
            logger.info(f"✅ Batch upserted {len(points)} embeddings into Qdrant")
        else:
            logger.warning("No embeddings to upsert in batch")

        return responses

    def search_similar(
        self,
        query_vector: List[float],
        vector_name: str = "primary_embedding",
        limit: int = 10,
        category: Optional[str] = None,
        source_name: Optional[str] = None,
    ) -> List[str]:
        """Search for similar embeddings and return list of article_ids."""
        filter_conditions = []
        if category:
            filter_conditions.append(
                FieldCondition(key="category", match=MatchValue(value=category))
            )
        if source_name:
            filter_conditions.append(
                FieldCondition(key="source_name", match=MatchValue(value=source_name))
            )

        q_filter = Filter(must=filter_conditions) if filter_conditions else None

        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            vector_name=vector_name,
            filter=q_filter,
            limit=limit,
        )

        return [res.id for res in results]

    def get_embedding_point(
        self, article_id: str
    ) -> Optional[ArticleEmbeddingResponse]:
        """Retrieve an embedding by article_id."""
        points = self.client.retrieve(collection_name=COLLECTION_NAME, ids=[article_id])
        if not points:
            return None

        point = points[0]
        return ArticleEmbeddingResponse(
            id=point.id,
            article_id=point.id,
            vectors=point.vectors,
            category=point.payload.get("category"),
            source_name=point.payload.get("source_name"),
            published_at=point.payload.get("published_at"),
        )

    def delete_embedding(self, article_id: str):
        """Delete an embedding by article_id."""
        self.client.delete(
            collection_name=COLLECTION_NAME, points_selector={"ids": [article_id]}
        )
        logger.info(f"🗑️ Deleted embedding for article {article_id}")
