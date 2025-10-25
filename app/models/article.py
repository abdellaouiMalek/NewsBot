from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.models.base import BaseDocument
from app.models.enums import FetchMethod


class Article(BaseDocument):
    """Article model for feed extraction."""

    article_id: str = Field(..., description="Unique identifier for the article")
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = Field(None)
    summary: Optional[str] = Field(None, max_length=10000)
    author: Optional[str] = Field(None, max_length=1000)
    published_at: datetime = Field(...)
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    source_name: str = Field(..., max_length=500)
    source_url: str = Field(...)
    article_url: str = Field(...)
    category: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    fetch_method: FetchMethod = Field(...)
    media_thumbnail: Optional[str] = Field(None)
    tags: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = Field(None, max_length=220)
    entities: Optional[List[str]] = Field(None)
    raw_data: Optional[dict] = Field(None)
    embedding: Optional[List[float]] = Field(None)
