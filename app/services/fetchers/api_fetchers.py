from datetime import datetime
from typing import Dict, List

import requests
import yaml

from app.models.enums import FetchMethod
from app.schemas.article import ArticleCreate
from app.utils.article_utils import enhance_metadata


def get_api_sources() -> List[Dict]:
    """Load API sources from YAML configuration and return a list of feeds."""
    with open("./app/config/sources/api-sources.yml", "r") as f:
        api_sources = yaml.safe_load(f).get("api", {})

    sources: List[Dict] = []

    for category, api_resources in api_sources.items():
        for source in api_resources:
            source["category"] = category
            sources.append(source)
    return sources


def fetch_articles_from_newsapi(source: Dict) -> List[ArticleCreate]:
    newsapi_info = source.get("newsapi", {})
    url = newsapi_info.get("url")
    headers = newsapi_info.get("headers", {})
    params = newsapi_info.get("params", {})

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            print(f"⚠️ NewsAPI returned error: {data.get('message')}")
            return []

        articles_list = []
        for item in data.get("articles", []):
            article_id = item.get("url")
            published_at = item.get("publishedAt")
            if published_at:
                published_at = datetime.fromisoformat(
                    published_at.replace("Z", "+00:00")
                )

            article = ArticleCreate(
                article_id=article_id,
                title=item.get("title") or "No title",
                content=item.get("content", item.get("description")),
                summary=item.get("description"),
                author=item.get("author"),
                published_at=published_at or datetime.utcnow(),
                fetched_at=datetime.utcnow(),
                source_name=item.get("source", {}).get("name")
                or newsapi_info.get("name"),
                source_url=url,
                article_url=item.get("url"),
                category=source.get("category"),
                language=params.get("language"),
                country=params.get("country"),
                fetch_method=FetchMethod.API,
                media_thumbnail=item.get("urlToImage"),
                tags=[t.term for t in item.tags] if "tags" in item else [],
                sentiment=None,
                entities=None,
                raw_data=item,
            )

            article = enhance_metadata(article)

            articles_list.append(article)

        return articles_list

    except requests.RequestException as e:
        print(f"❌ Request error for source {newsapi_info.get('name')}: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error for source {newsapi_info.get('name')}: {e}")
        return []
