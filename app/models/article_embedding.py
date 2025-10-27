from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ArticleEmbedding(BaseModel):
    article_id: str
    vectors: dict
    category: Optional[str] = None
    source_name: Optional[str] = None
    published_at: Optional[datetime] = None
