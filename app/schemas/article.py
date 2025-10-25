from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.enums import FetchMethod


class ArticleCreate(BaseModel):
    """Schema for creating an article from feed extraction."""

    article_id: str = Field(..., description="Unique identifier for the article")
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
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
    media_thumbnail: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = Field(None, max_length=220)
    entities: Optional[List[str]] = None
    raw_data: Optional[dict] = None
    embedding: Optional[List[float]] = None


class ArticleUpdate(BaseModel):
    """Schema for updating an article."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=10000)
    author: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    media_thumbnail: Optional[str] = None
    tags: Optional[List[str]] = None
    sentiment: Optional[str] = Field(None, max_length=220)
    entities: Optional[List[str]] = None
    embedding: Optional[List[float]] = None
    raw_data: Optional[dict] = None


class ArticleResponse(BaseModel):
    """Schema for article response."""

    id: str
    article_id: str
    title: str
    content: Optional[str]
    summary: Optional[str]
    author: Optional[str]
    published_at: datetime
    fetched_at: datetime
    source_name: str
    source_url: str
    article_url: str
    category: Optional[str]
    language: Optional[str]
    country: Optional[str]
    fetch_method: FetchMethod
    media_thumbnail: Optional[str]
    tags: List[str]
    sentiment: Optional[str]
    entities: Optional[List[str]]
    raw_data: Optional[dict]
    embedding: Optional[List[float]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
