# app/schemas/article_embedding.py
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# -------------------------------------------------------
# Create/Upsert Schema
# -------------------------------------------------------
class ArticleEmbeddingCreate(BaseModel):
    """Schema for creating/upserting article embeddings in Qdrant."""

    article_id: str = Field(..., description="Unique identifier for the article")
    vectors: Dict[str, List[float]] = Field(
        ...,
        description="Named embeddings for the article (e.g., title, primary, secondary)",
    )
    category: Optional[str] = Field(None, max_length=500)
    source_name: Optional[str] = Field(None, max_length=500)
    published_at: Optional[datetime] = Field(
        None, description="Original article publish datetime"
    )


# -------------------------------------------------------
# Update Schema
# -------------------------------------------------------
class ArticleEmbeddingUpdate(BaseModel):
    """Schema for updating embeddings or metadata in Qdrant."""

    vectors: Optional[Dict[str, List[float]]] = Field(
        None, description="Named embeddings to update"
    )
    category: Optional[str] = Field(None, max_length=500)
    source_name: Optional[str] = Field(None, max_length=500)
    published_at: Optional[datetime] = Field(None)
    language: Optional[str] = Field(None, max_length=100)


# -------------------------------------------------------
# Response Schema
# -------------------------------------------------------
class ArticleEmbeddingResponse(BaseModel):
    """Schema for returning embeddings and metadata from Qdrant."""

    id: str = Field(..., description="Original article URL")
    article_id: str = Field(..., description="Original article URL (same as id)")
    vectors: Dict[str, List[float]] = Field(..., description="Stored embeddings")
    category: Optional[str] = None
    source_name: Optional[str] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True
