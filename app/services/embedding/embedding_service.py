import hashlib
import logging
from typing import Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import FieldCondition, Filter, MatchValue, PointStruct

from app.core.qdrant import get_qdrant_client
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

    def _url_to_point_id(self, url: str) -> int:
        """Convert URL to integer point ID using hash."""
        hash_object = hashlib.md5(url.encode())
        hash_hex = hash_object.hexdigest()
        point_id = int(hash_hex[:16], 16)
        return point_id

    def upsert_embedding(
        self, embedding: ArticleEmbeddingCreate
    ) -> ArticleEmbeddingResponse:
        """Insert or update a single embedding with multiple vectors."""
        point_id = self._url_to_point_id(embedding.article_id)

        point = PointStruct(
            id=point_id,  # Use integer hash internally
            vector=embedding.vectors,
            payload={
                "article_id": embedding.article_id,  # Store original URL
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

        # Return response with original article_id, not the point_id
        return ArticleEmbeddingResponse(
            id=embedding.article_id,  # Return original URL as ID
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
                logger.warning(f"Skipping article {embedding.article_id} - no vectors")
                continue

            # Validate that all required vectors are present
            required_vectors = [
                "title_embedding",
                "primary_embedding",
                "secondary_embedding",
            ]
            missing_vectors = [
                vec for vec in required_vectors if vec not in embedding.vectors
            ]

            if missing_vectors:
                logger.warning(
                    f"Article {embedding.article_id} missing vectors: {missing_vectors}"
                )
                continue

            point_id = self._url_to_point_id(embedding.article_id)

            points.append(
                PointStruct(
                    id=point_id,  # Use integer hash internally
                    vector=embedding.vectors,
                    payload={
                        "article_id": embedding.article_id,  # Store original URL
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
            # Return response with original article_id, not the point_id
            responses.append(
                ArticleEmbeddingResponse(
                    id=embedding.article_id,  # Return original URL as ID
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
        """Search for similar embeddings and return list of article URLs."""
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
            query_filter=q_filter,
            limit=limit,
            with_payload=True,  # We need payload to get the original article_id
            with_vectors=False,
        )

        # Return the original article URLs from payload
        article_ids = []
        for res in results:
            article_id = res.payload.get("article_id")
            if article_id:
                article_ids.append(article_id)
            else:
                logger.warning(f"Search result missing article_id in payload: {res.id}")

        return article_ids

    def search_similar_multi(
        self,
        query_vectors: Dict[str, List[float]],
        limit: int = 10,
        category: Optional[str] = None,
        source_name: Optional[str] = None,
    ) -> Dict[str, List[str]]:
        """Search using multiple vectors and return results for each."""
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

        results = {}
        for vector_name, query_vector in query_vectors.items():
            search_results = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                query_filter=q_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            article_ids = []
            for res in search_results:
                article_id = res.payload.get("article_id")
                if article_id:
                    article_ids.append(article_id)
                else:
                    logger.warning(
                        f"Search result missing article_id in payload: {res.id}"
                    )

            results[vector_name] = article_ids

        return results

    def get_embedding_by_article_id(
        self, article_id: str
    ) -> Optional[ArticleEmbeddingResponse]:
        """Retrieve an embedding by article URL - returns original URL in response."""
        point_id = self._url_to_point_id(article_id)
        points = self.client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[point_id],
            with_vectors=True,
            with_payload=True,
        )
        if not points:
            return None

        point = points[0]

        # Extract the original article_id from payload
        original_article_id = point.payload.get("article_id", article_id)

        return ArticleEmbeddingResponse(
            id=original_article_id,  # Return original URL
            article_id=original_article_id,
            vectors=point.vector,
            category=point.payload.get("category"),
            source_name=point.payload.get("source_name"),
            published_at=point.payload.get("published_at"),
        )

    def get_embedding_by_point_id(
        self, point_id: int
    ) -> Optional[ArticleEmbeddingResponse]:
        """Retrieve an embedding by point ID - returns original URL in response."""
        points = self.client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[point_id],
            with_vectors=True,
            with_payload=True,
        )
        if not points:
            return None

        point = points[0]
        original_article_id = point.payload.get("article_id")

        if not original_article_id:
            logger.warning(f"Point {point_id} missing article_id in payload")
            return None

        return ArticleEmbeddingResponse(
            id=original_article_id,  # Return original URL
            article_id=original_article_id,
            vectors=point.vector,
            category=point.payload.get("category"),
            source_name=point.payload.get("source_name"),
            published_at=point.payload.get("published_at"),
        )

    def delete_embedding(self, article_id: str):
        """Delete an embedding by article URL."""
        point_id = self._url_to_point_id(article_id)
        self.client.delete(
            collection_name=COLLECTION_NAME, points_selector={"ids": [point_id]}
        )
        logger.info(f"🗑️ Deleted embedding for article {article_id}")

    def batch_get_embeddings(
        self, article_ids: List[str]
    ) -> List[ArticleEmbeddingResponse]:
        """Get multiple embeddings by article URLs."""
        point_ids = [self._url_to_point_id(article_id) for article_id in article_ids]
        points = self.client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=point_ids,
            with_vectors=True,
            with_payload=True,
        )

        responses = []
        for point in points:
            original_article_id = point.payload.get("article_id")
            if original_article_id:
                responses.append(
                    ArticleEmbeddingResponse(
                        id=original_article_id,  # Return original URL
                        article_id=original_article_id,
                        vectors=point.vector,
                        category=point.payload.get("category"),
                        source_name=point.payload.get("source_name"),
                        published_at=point.payload.get("published_at"),
                    )
                )
            else:
                logger.warning(f"Point {point.id} missing article_id in payload")

        return responses

    def get_all_embeddings(self, limit: int = 1000) -> List[ArticleEmbeddingResponse]:
        """Get all embeddings with original URLs."""
        # Use scroll API to get all points
        all_points = []
        next_page_offset = None

        while True:
            records, next_page_offset = self.client.scroll(
                collection_name=COLLECTION_NAME,
                limit=min(limit, 100),  # Scroll in batches
                offset=next_page_offset,
                with_vectors=True,
                with_payload=True,
            )

            if not records:
                break

            all_points.extend(records)

            if next_page_offset is None:
                break

        responses = []
        for point in all_points:
            original_article_id = point.payload.get("article_id")
            if original_article_id:
                responses.append(
                    ArticleEmbeddingResponse(
                        id=original_article_id,  # Return original URL
                        article_id=original_article_id,
                        vectors=point.vector,
                        category=point.payload.get("category"),
                        source_name=point.payload.get("source_name"),
                        published_at=point.payload.get("published_at"),
                    )
                )
            else:
                logger.warning(f"Point {point.id} missing article_id in payload")

        return responses
