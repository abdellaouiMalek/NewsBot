from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.enums import FetchMethod


# -------------------------------------------------------
# Create Schema
# -------------------------------------------------------
class ArticleCreate(BaseModel):
    """Schema for creating an article from feed or API extraction."""

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

    # Entities stored as formatted string (e.g., "persons: John Doe | orgs: BBC")
    entities: Optional[str] = Field(
        None, description="Formatted named entities extracted from the article text."
    )

    raw_data: Optional[dict] = None

    # --- Embedding-related fields ---
    embedding_primary_text: Optional[str] = Field(
        None, description="Text used for the primary embedding (semantic core)."
    )
    embedding_secondary_text: Optional[str] = Field(
        None, description="Text used for the secondary embedding (context/metadata)."
    )
    embedding_primary: Optional[List[float]] = Field(
        None, description="Numerical vector from primary embedding model."
    )
    embedding_secondary: Optional[List[float]] = Field(
        None, description="Numerical vector from secondary embedding model."
    )


# -------------------------------------------------------
# Update Schema
# -------------------------------------------------------
class ArticleUpdate(BaseModel):
    """Schema for updating an existing article."""

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

    # Formatted entities string
    entities: Optional[str] = Field(
        None, description="Formatted named entities extracted from the article text."
    )

    raw_data: Optional[dict] = None

    # --- Embedding-related fields (for re-embedding or updates) ---
    embedding_primary_text: Optional[str] = None
    embedding_secondary_text: Optional[str] = None
    embedding_primary: Optional[List[float]] = None
    embedding_secondary: Optional[List[float]] = None


# -------------------------------------------------------
# Response Schema
# -------------------------------------------------------
class ArticleResponse(BaseModel):
    """Schema for returning articles in API responses."""

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

    # Entities as formatted string (human-readable)
    entities: Optional[str]

    raw_data: Optional[dict]

    # --- Embedding-related fields ---
    embedding_primary_text: Optional[str]
    embedding_secondary_text: Optional[str]
    embedding_primary: Optional[List[float]]
    embedding_secondary: Optional[List[float]]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Paginated list response for articles."""

    articles: List[ArticleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True
