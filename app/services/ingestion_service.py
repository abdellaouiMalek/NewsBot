from typing import List

import pandas as pd
from fastapi import BackgroundTasks

from app.services.article.article_service import ArticleService
from app.services.fetchers.api_fetchers import (
    fetch_articles_from_newsapi,
    get_api_sources,
)
from app.services.fetchers.rss_fetcher import fetch_feed, get_rss_sources
from app.utils.article_utils import (
    deduplicate,
    extract_embeddings,
    extract_embeddings_qdrant,
    extract_entities,
)


async def fetch_and_store_rss_articles(db, background_tasks: BackgroundTasks) -> List:
    """Fetch all RSS articles, deduplicate, insert new ones,
    and return Article instances."""
    article_service = ArticleService(db)
    feeds = get_rss_sources()

    all_articles = []
    for feed in feeds:
        articles = fetch_feed(feed)
        all_articles.extend(articles)

    if not all_articles:
        print("ℹ️ No RSS articles fetched.")
        return []

    new_articles_df = pd.DataFrame([a.dict() for a in all_articles])

    query = {"fetch_method": "rss"}
    if "published_at" in new_articles_df.columns:
        new_articles_df["published_at"] = pd.to_datetime(
            new_articles_df["published_at"]
        )
        min_published_at = new_articles_df["published_at"].min()
        query["published_at"] = {"$gte": min_published_at}

    existing_articles = await article_service.collection.find(
        query, {"article_id": 1, "published_at": 1, "source_name": 1, "_id": 0}
    ).to_list(None)

    existing_df = pd.DataFrame(existing_articles)
    deduplicated_df = deduplicate(new_articles_df.to_dict("records"), existing_df)

    if deduplicated_df.empty:
        print("ℹ️ No new RSS articles to insert after deduplication")
        return []

    records = deduplicated_df.to_dict("records")
    inserted_articles = await article_service.bulk_insert_articles(records)

    # Schedule background processing (safe)
    try:
        background_tasks.add_task(
            entities_and_embeddings_process, inserted_articles, db
        )
    except Exception as e:
        print(f"⚠️ Failed to schedule background tasks: {e}")

    print(f"💾 {len(inserted_articles)} new RSS articles inserted successfully")
    return inserted_articles


async def fetch_and_store_api_articles(db, background_tasks: BackgroundTasks) -> List:
    """Fetch all API articles, deduplicate, insert new ones,
    and return Article instances."""
    article_service = ArticleService(db)
    api_sources = get_api_sources()

    all_articles = []
    for source in api_sources:
        if "newsapi" in source:
            articles = fetch_articles_from_newsapi(source)
            all_articles.extend(articles)

    if not all_articles:
        print("ℹ️ No API articles fetched.")
        return []

    new_articles_df = pd.DataFrame([a.dict() for a in all_articles])

    if "published_at" in new_articles_df.columns:
        new_articles_df["published_at"] = pd.to_datetime(
            new_articles_df["published_at"]
        )
        min_published_at = new_articles_df["published_at"].min()
        existing_articles = await article_service.collection.find(
            {"fetch_method": "api", "published_at": {"$gte": min_published_at}},
            {"article_id": 1, "published_at": 1, "_id": 0},
        ).to_list(None)
    else:
        existing_articles = await article_service.collection.find(
            {"fetch_method": "api"}, {"article_id": 1, "_id": 0}
        ).to_list(None)

    existing_df = pd.DataFrame(existing_articles)
    deduplicated_df = deduplicate(new_articles_df.to_dict("records"), existing_df)

    if deduplicated_df.empty:
        print("ℹ️ No new API articles to insert after deduplication")
        return []

    records = deduplicated_df.to_dict("records")
    inserted_articles = await article_service.bulk_insert_articles(records)

    # Schedule background processing (safe)
    try:
        background_tasks.add_task(
            entities_and_embeddings_process, inserted_articles, db
        )
    except Exception as e:
        print(f"⚠️ Failed to schedule background tasks: {e}")

    print(f"💾 {len(inserted_articles)} new API articles inserted successfully")
    return inserted_articles


async def entities_and_embeddings_process(articles, db):
    """
    Extract entities first, then compute embeddings.
    """
    await extract_entities(articles, db)
    await extract_embeddings(articles, db)
    await extract_embeddings_qdrant(articles, db)
