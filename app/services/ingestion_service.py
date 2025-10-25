import pandas as pd

from app.services.article.article_service import ArticleService
from app.services.fetchers.api_fetchers import (
    fetch_articles_from_newsapi,
    get_api_sources,
)
from app.services.fetchers.rss_fetcher import fetch_feed, get_rss_sources
from app.utils.article_utils import deduplicate


async def fetch_and_store_rss_articles(db) -> int:
    """Fetch all RSS articles, deduplicate, and insert new ones."""
    article_service = ArticleService(db)
    feeds = get_rss_sources()

    all_articles = []
    for feed in feeds:
        articles = fetch_feed(feed)
        all_articles.extend(articles)

    if not all_articles:
        print("ℹ️ No RSS articles fetched.")
        return 0

    # Convert to DataFrame for deduplication
    new_articles_df = pd.DataFrame([a.dict() for a in all_articles])

    # Build optimized query for existing RSS articles
    query = {"fetch_method": "rss"}

    if not new_articles_df.empty:
        # Add date filter if published_at exists
        if "published_at" in new_articles_df.columns:
            new_articles_df["published_at"] = pd.to_datetime(
                new_articles_df["published_at"]
            )
            min_published_at = new_articles_df["published_at"].min()
            query["published_at"] = {"$gte": min_published_at}

    # Fetch only relevant existing RSS articles
    existing_articles = await article_service.collection.find(
        query, {"article_id": 1, "published_at": 1, "source_name": 1, "_id": 0}
    ).to_list(None)

    existing_df = pd.DataFrame(existing_articles)

    # Deduplicate
    deduplicated_df = deduplicate(new_articles_df.to_dict("records"), existing_df)

    if deduplicated_df.empty:
        print("ℹ️ No new RSS articles to insert after deduplication")
        return 0

    # Insert new articles
    records = deduplicated_df.to_dict("records")
    result = await article_service.collection.insert_many(records, ordered=False)
    print(f"💾 {len(result.inserted_ids)} new RSS articles inserted successfully")
    return len(result.inserted_ids)


async def fetch_and_store_api_articles(db) -> int:
    """Fetch all API articles, deduplicate, and insert new ones."""
    article_service = ArticleService(db)
    api_sources = get_api_sources()

    all_articles = []
    for source in api_sources:
        for key, value in source.items():
            if key == "newsapi":
                articles = fetch_articles_from_newsapi(source)
                all_articles.extend(articles)

    if not all_articles:
        print("ℹ️ No API articles fetched.")
        return 0

    # Convert to DataFrame for deduplication
    new_articles_df = pd.DataFrame([a.dict() for a in all_articles])

    # Find the earliest published_at in new articles for efficient querying
    if not new_articles_df.empty and "published_at" in new_articles_df.columns:
        # Convert to datetime if needed and find minimum
        new_articles_df["published_at"] = pd.to_datetime(
            new_articles_df["published_at"]
        )
        min_published_at = new_articles_df["published_at"].min()

        # Fetch only relevant existing articles (same method and after min date)
        existing_articles = await article_service.collection.find(
            {"fetch_method": "api", "published_at": {"$gte": min_published_at}},
            {"article_id": 1, "published_at": 1, "_id": 0},
        ).to_list(None)
    else:
        # Fallback: if no published_at, fetch all API articles (less efficient)
        existing_articles = await article_service.collection.find(
            {"fetch_method": "api"}, {"article_id": 1, "_id": 0}
        ).to_list(None)

    existing_df = pd.DataFrame(existing_articles)

    # Deduplicate
    deduplicated_df = deduplicate(new_articles_df.to_dict("records"), existing_df)

    if deduplicated_df.empty:
        print("ℹ️ No new API articles to insert after deduplication")
        return 0

    # Insert new articles
    records = deduplicated_df.to_dict("records")
    result = await article_service.collection.insert_many(records, ordered=False)
    print(f"💾 {len(result.inserted_ids)} new API articles inserted successfully")
    return len(result.inserted_ids)
