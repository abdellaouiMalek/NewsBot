import hashlib
import logging
from typing import Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import FieldCondition, Filter, MatchValue, PointStruct

from app.core.qdrant import get_collection_name, get_qdrant_client
from app.schemas.article_embedding import (
    ArticleEmbeddingCreate,
    ArticleEmbeddingResponse,
)

logger = logging.getLogger(__name__)

COLLECTION_NAME = get_collection_name()


class EmbeddingService:
    """Service for managing article embeddings in Qdrant using Pydantic schemas."""

    def __init__(self):
        self.client: QdrantClient = get_qdrant_client()

    def _url_to_point_id(self, url: str) -> int:
        """Convert URL (article_id) to deterministic integer point ID using MD5."""
        hash_object = hashlib.md5(url.encode("utf-8"))
        hash_hex = hash_object.hexdigest()
        # keep first 16 hex chars -> fits in 64-bit
        point_id = int(hash_hex[:16], 16)
        return point_id

    def upsert_embedding(
        self, embedding: ArticleEmbeddingCreate
    ) -> ArticleEmbeddingResponse:
        """Insert or update a single embedding with multiple named vectors."""
        if not embedding.vectors:
            logger.warning("No vectors provided for %s", embedding.article_id)
            raise ValueError("No vectors provided")

        point_id = self._url_to_point_id(embedding.article_id)

        # Qdrant supports PointStruct.vector as either a list (single vector) or a dict (named vectors)
        point = PointStruct(
            id=point_id,
            vector=embedding.vectors,  # named-vectors dict expected
            payload={
                "article_id": embedding.article_id,
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
        logger.info("Upserted embedding for article %s", embedding.article_id)

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
        points: List[PointStruct] = []
        responses: List[ArticleEmbeddingResponse] = []

        required_vectors = [
            "title_embedding",
            "primary_embedding",
            "secondary_embedding",
        ]

        for emb in embeddings:
            if not emb.vectors:
                logger.warning("Skipping %s - no vectors", emb.article_id)
                continue
            missing = [v for v in required_vectors if v not in emb.vectors]
            if missing:
                logger.warning(
                    "Skipping %s - missing vectors %s", emb.article_id, missing
                )
                continue

            pid = self._url_to_point_id(emb.article_id)
            points.append(
                PointStruct(
                    id=pid,
                    vector=emb.vectors,
                    payload={
                        "article_id": emb.article_id,
                        "category": emb.category,
                        "source_name": emb.source_name,
                        "published_at": (
                            emb.published_at.isoformat() if emb.published_at else None
                        ),
                    },
                )
            )
            responses.append(
                ArticleEmbeddingResponse(
                    id=emb.article_id,
                    article_id=emb.article_id,
                    vectors=emb.vectors,
                    category=emb.category,
                    source_name=emb.source_name,
                    published_at=emb.published_at,
                )
            )

        if points:
            self.client.upsert(collection_name=COLLECTION_NAME, points=points)
            logger.info("Batch upserted %d embeddings", len(points))
        else:
            logger.warning("No valid embeddings to upsert")

        return responses

    def _build_filter(
        self, category: Optional[str], source_name: Optional[str]
    ) -> Optional[Filter]:
        conditions = []
        if category:
            conditions.append(
                FieldCondition(key="category", match=MatchValue(value=category))
            )
        if source_name:
            conditions.append(
                FieldCondition(key="source_name", match=MatchValue(value=source_name))
            )
        return Filter(must=conditions) if conditions else None

    def search_similar(
        self,
        query_vector: List[float],
        vector_name: str = "primary_embedding",
        limit: int = 10,
        category: Optional[str] = None,
        source_name: Optional[str] = None,
    ) -> List[str]:
        """
        Search similar articles using the named vector.
        IMPORTANT: for named vectors we pass query_vector as a mapping: {vector_name: vector}
        """
        q_filter = self._build_filter(category, source_name)

        # For named vectors we pass a dict: { "primary_embedding": [..] }
        named_query_vector = {vector_name: query_vector}

        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=named_query_vector,
            query_filter=q_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        article_ids = []
        for res in results:
            aid = res.payload.get("article_id")
            if aid:
                article_ids.append(aid)
            else:
                logger.warning(
                    "Search hit missing article_id for point %s",
                    getattr(res, "id", "<unknown>"),
                )

        return article_ids

    def search_similar_multi(
        self,
        query_vectors: Dict[str, List[float]],
        limit: int = 10,
        category: Optional[str] = None,
        source_name: Optional[str] = None,
    ) -> Dict[str, List[str]]:
        """
        Search using multiple named vectors. We call Qdrant per named vector.
        """
        q_filter = self._build_filter(category, source_name)
        results = {}
        for name, vec in query_vectors.items():
            named_query_vector = {name: vec}
            hits = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=named_query_vector,
                query_filter=q_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            article_ids = [
                h.payload.get("article_id") for h in hits if h.payload.get("article_id")
            ]
            results[name] = article_ids
        return results

    def get_embedding_by_article_id(
        self, article_id: str
    ) -> Optional[ArticleEmbeddingResponse]:
        pid = self._url_to_point_id(article_id)
        points = self.client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[pid],
            with_vectors=True,
            with_payload=True,
        )
        if not points:
            return None
        p = points[0]
        return ArticleEmbeddingResponse(
            id=p.payload.get("article_id", article_id),
            article_id=p.payload.get("article_id", article_id),
            vectors=p.vector,
            category=p.payload.get("category"),
            source_name=p.payload.get("source_name"),
            published_at=p.payload.get("published_at"),
        )

    def delete_embedding(self, article_id: str):
        pid = self._url_to_point_id(article_id)
        self.client.delete(
            collection_name=COLLECTION_NAME, points_selector={"ids": [pid]}
        )
        logger.info("Deleted embedding for %s", article_id)

    def batch_get_embeddings(
        self, article_ids: List[str]
    ) -> List[ArticleEmbeddingResponse]:
        pids = [self._url_to_point_id(aid) for aid in article_ids]
        points = self.client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=pids,
            with_vectors=True,
            with_payload=True,
        )
        out = []
        for p in points:
            original_id = p.payload.get("article_id")
            if original_id:
                out.append(
                    ArticleEmbeddingResponse(
                        id=original_id,
                        article_id=original_id,
                        vectors=p.vector,
                        category=p.payload.get("category"),
                        source_name=p.payload.get("source_name"),
                        published_at=p.payload.get("published_at"),
                    )
                )
            else:
                logger.warning(
                    "Point %s missing article_id", getattr(p, "id", "<unknown>")
                )
        return out

    def get_all_embeddings(
        self, batch_size: int = 100
    ) -> List[ArticleEmbeddingResponse]:
        # use scroll to iterate through collection
        all_points = []
        offset = 0
        while True:
            records, next_offset = self.client.scroll(
                collection_name=COLLECTION_NAME,
                limit=batch_size,
                offset=offset,
                with_vectors=True,
                with_payload=True,
            )
            if not records:
                break
            all_points.extend(records)
            if next_offset is None:
                break
            offset = next_offset

        responses = []
        for p in all_points:
            original_id = p.payload.get("article_id")
            if original_id:
                responses.append(
                    ArticleEmbeddingResponse(
                        id=original_id,
                        article_id=original_id,
                        vectors=p.vector,
                        category=p.payload.get("category"),
                        source_name=p.payload.get("source_name"),
                        published_at=p.payload.get("published_at"),
                    )
                )
            else:
                logger.warning(
                    "Point %s missing article_id", getattr(p, "id", "<unknown>")
                )
        return responses
