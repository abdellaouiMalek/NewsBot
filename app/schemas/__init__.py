# Import all schemas for easy access
from app.schemas.article import ArticleCreate, ArticleResponse, ArticleUpdate
from app.schemas.message import MessageCreate, MessageResponse

__all__ = [
    "ArticleCreate",
    "ArticleUpdate",
    "ArticleResponse",
    "MessageCreate",
    "MessageResponse",
]
