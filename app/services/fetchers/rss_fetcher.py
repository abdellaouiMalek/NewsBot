from datetime import datetime
from typing import Dict, List

import feedparser
import yaml
from dateutil import parser as date_parser
from pydantic import ValidationError

from app.models.enums import FetchMethod
from app.schemas.article import ArticleCreate
from app.utils.article_utils import clean_rss_text, enhance_metadata


def get_rss_sources() -> List[Dict]:
    """Load RSS feed sources from YAML configuration and return a list of feeds."""
    with open("./app/config/sources/rss-sources.yml", "r") as f:
        rss_sources = yaml.safe_load(f).get("rss", {})

    feeds: List[Dict] = []
    for category, feed_list in rss_sources.items():
        for feed in feed_list:
            feed["category"] = category
            feeds.append(feed)
    return feeds


def fetch_feed(feed: Dict) -> List[ArticleCreate]:
    """Fetch RSS feed and return a list of ArticleCreate objects."""
    try:
        parsed_feed = feedparser.parse(feed["url"])
    except Exception as e:
        print(f"⚠️ Error fetching {feed['name']}: {e}")
        return []

    if not parsed_feed.entries:
        return []

    articles = []
    for i, entry in enumerate(parsed_feed.entries, 1):
        try:
            published = entry.get(
                "published", entry.get("updated", datetime.now().isoformat())
            )
            try:
                published_dt = date_parser.parse(published)
                published_dt = published_dt.replace(tzinfo=None)
            except Exception:
                published_dt = datetime.utcnow()

            content = entry.get("summary", "")
            if "content" in entry and entry.content:
                content = entry.content[0].value

            content = clean_rss_text(content)

            summary = entry.get("summary", "")

            summary = clean_rss_text(summary)

            article = ArticleCreate(
                article_id=entry.get("link"),
                title=entry.get("title", f"No Title {i}"),
                content=content,
                summary=summary,
                author=entry.get("author"),
                published_at=published_dt,
                fetched_at=datetime.utcnow(),
                source_name=feed["source"],
                source_url=feed["url"],
                article_url=entry.get("link", ""),
                category=feed.get("category"),
                language=feed.get("language"),
                country=feed.get("country"),
                fetch_method=FetchMethod.RSS,
                media_thumbnail=(
                    entry.get("media_thumbnail", [{}])[0].get("url")
                    if isinstance(entry.get("media_thumbnail"), list)
                    else entry.get("media_thumbnail")
                ),
                tags=[t.term for t in entry.tags] if "tags" in entry else [],
                sentiment=None,  # optional
                entities=None,  # optional
                raw_data=dict(entry),
                embedding_primary_text=None,
                embedding_secondary_text=None,
                embedding_primary=None,
                embedding_secondary=None,
            )

            article = enhance_metadata(article)

            articles.append(article)
        except ValidationError as ve:
            print(f"⚠️ {feed['name']} Entry {i}: Validation error: {ve}")
    return articles
