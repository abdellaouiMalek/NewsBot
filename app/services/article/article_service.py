from datetime import datetime, timedelta
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


class ArticleService:
    """Service for managing articles from feed extraction."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.articles

    async def create_article(self, article_data: ArticleCreate) -> Article:
        """Create a new article from feed extraction."""
        article_dict = article_data.dict()
        article_dict["fetched_at"] = datetime.utcnow()
        article_dict["created_at"] = datetime.utcnow()
        article_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(article_dict)
        article_dict["_id"] = result.inserted_id

        return Article(**article_dict)

    async def get_article_by_id(self, article_id: str) -> Optional[Article]:
        """Get an article by MongoDB ObjectId."""
        if not ObjectId.is_valid(article_id):
            return None

        article_data = await self.collection.find_one({"_id": ObjectId(article_id)})
        if article_data:
            return Article(**article_data)
        return None

    async def get_article_by_article_id(self, article_id: str) -> Optional[Article]:
        """Get an article by its custom article_id field."""
        article_data = await self.collection.find_one({"article_id": article_id})
        if article_data:
            return Article(**article_data)
        return None

    async def get_articles(
        self,
        skip: int = 0,
        limit: int = 10,
        category: Optional[str] = None,
        source_name: Optional[str] = None,
        fetch_method: Optional[str] = None,
        language: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[Article]:
        """Get articles with optional filtering."""
        query = {}

        if category:
            query["category"] = category
        if source_name:
            query["source_name"] = source_name
        if fetch_method:
            query["fetch_method"] = fetch_method
        if language:
            query["language"] = language
        if country:
            query["country"] = country

        cursor = (
            self.collection.find(query).skip(skip).limit(limit).sort("published_at", -1)
        )
        articles = []
        async for article_data in cursor:
            articles.append(Article(**article_data))
        return articles

    async def update_article(
        self, article_id: str, article_update: ArticleUpdate
    ) -> Optional[Article]:
        """Update an article."""
        if not ObjectId.is_valid(article_id):
            return None

        update_data = article_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()

            await self.collection.update_one(
                {"_id": ObjectId(article_id)}, {"$set": update_data}
            )

        return await self.get_article_by_id(article_id)

    async def delete_article(self, article_id: str) -> bool:
        """Delete an article."""
        if not ObjectId.is_valid(article_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(article_id)})
        return result.deleted_count > 0

    async def article_exists(self, article_id: str) -> bool:
        """Check if an article with the given article_id already exists."""
        count = await self.collection.count_documents({"article_id": article_id})
        return count > 0

    async def get_articles_by_source(
        self, source_name: str, limit: int = 100
    ) -> List[Article]:
        """Get articles from a specific source."""
        cursor = (
            self.collection.find({"source_name": source_name})
            .limit(limit)
            .sort("published_at", -1)
        )
        articles = []
        async for article_data in cursor:
            articles.append(Article(**article_data))
        return articles

    async def get_recent_articles(
        self, hours: int = 24, limit: int = 100
    ) -> List[Article]:
        """Get articles published within the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        cursor = (
            self.collection.find({"published_at": {"$gte": cutoff_time}})
            .limit(limit)
            .sort("published_at", -1)
        )
        articles = []
        async for article_data in cursor:
            articles.append(Article(**article_data))
        return articles

    async def search_articles(self, query: str, limit: int = 50) -> List[Article]:
        """Search articles by title and content."""
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}},
                {"summary": {"$regex": query, "$options": "i"}},
            ]
        }

        cursor = (
            self.collection.find(search_query).limit(limit).sort("published_at", -1)
        )
        articles = []
        async for article_data in cursor:
            articles.append(Article(**article_data))
        return articles

    async def bulk_insert_articles(self, articles: list[dict]) -> List[Article]:
        """Insert multiple articles and return Article instances
        of inserted/updated docs."""
        if not articles:
            return []

        operations = [
            UpdateOne(
                {"article_id": a["article_id"]},
                {
                    "$setOnInsert": {
                        **a,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "fetched_at": datetime.utcnow(),
                    }
                },
                upsert=True,
            )
            for a in articles
        ]

        await self.collection.bulk_write(operations, ordered=False)

        # Fetch inserted/updated articles without the _id field
        article_ids = [a["article_id"] for a in articles]
        inserted_docs = await self.collection.find(
            {"article_id": {"$in": article_ids}}, {"_id": 0}
        ).to_list(None)

        return [Article(**doc) for doc in inserted_docs]

    async def update_entities_bulk(self, articles: list[dict]) -> int:
        """
        Update the 'entities' field for multiple articles in bulk.
        Each article dict must have 'article_id' and 'entities'.
        Returns the number of articles updated.
        """
        if not articles:
            return 0

        operations = []
        for article in articles:
            if "article_id" not in article or "entities" not in article:
                continue  # skip invalid entries

            operations.append(
                UpdateOne(
                    {"article_id": article["article_id"]},
                    {
                        "$set": {
                            "entities": article["entities"],
                            "updated_at": datetime.utcnow(),
                        }
                    },
                )
            )

        if not operations:
            return 0

        result = await self.collection.bulk_write(operations, ordered=False)
        return result.modified_count

    async def update_embeddings_bulk(self, articles: list[dict]) -> int:
        """
        Bulk update embedding fields for multiple articles.
        Each article dict must have 'article_id' and embedding fields.
        Returns the number of articles updated.
        """
        if not articles:
            return 0

        operations = []
        for article in articles:
            article_id = article.get("article_id")
            if not article_id:
                continue

            update_fields = {}
            for key in [
                "embedding_primary_text",
                "embedding_secondary_text",
                "embedding_primary",
                "embedding_secondary",
            ]:
                if key in article:
                    update_fields[key] = article[key]

            if not update_fields:
                continue

            update_fields["updated_at"] = datetime.utcnow()

            operations.append(
                UpdateOne(
                    {"article_id": article_id},
                    {"$set": update_fields},
                )
            )

        if not operations:
            return 0

        result = await self.collection.bulk_write(operations, ordered=False)
        return result.modified_count
