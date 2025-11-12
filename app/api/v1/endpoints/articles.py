import math
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_database
from app.schemas.article import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
)
from app.services.article.article_service import ArticleService

router = APIRouter()


@router.get("/categories", response_model=List[str])
async def get_categories(db=Depends(get_database)):
    """Return a list of all available article categories (sorted)."""
    article_service = ArticleService(db)
    categories = await article_service.get_categories()
    return categories


def _to_response(article) -> ArticleResponse:
    """Normalize Article (pydantic model or raw dict) into ArticleResponse.

    Ensures the MongoDB ObjectId is converted to a string `id` field so
    FastAPI response validation accepts the payload.
    """
    # If it's a pydantic model (Article), prefer model_dump()
    try:
        if hasattr(article, "model_dump"):
            data = article.model_dump()
        else:
            data = dict(article)
    except Exception:
        data = dict(article)

    # Normalize _id or id to string
    oid = data.get("id") or data.get("_id")
    data["id"] = str(oid) if oid is not None else None
    data.pop("_id", None)

    return ArticleResponse(**data)


@router.get("/", response_model=ArticleListResponse)
async def get_articles(
    page: int = 1,
    page_size: int = 10,
    category: Optional[str] = None,
    source_name: Optional[str] = None,
    fetch_method: Optional[str] = None,
    language: Optional[str] = None,
    country: Optional[str] = None,
    db=Depends(get_database),
):
    """Get paginated articles with optional filtering.

    Returns a paginated envelope matching ArticleListResponse.
    """
    # Normalize paging params
    page = max(1, page)
    page_size = max(1, min(100, page_size))

    skip = (page - 1) * page_size

    article_service = ArticleService(db)
    total = await article_service.count_articles(
        category=category,
        source_name=source_name,
        fetch_method=fetch_method,
        language=language,
        country=country,
    )

    articles = await article_service.get_articles(
        skip=skip,
        limit=page_size,
        category=category,
        source_name=source_name,
        fetch_method=fetch_method,
        language=language,
        country=country,
    )

    total_pages = math.ceil(total / page_size) if page_size else 0

    return ArticleListResponse(
        articles=[_to_response(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str, db=Depends(get_database)):
    """Get a specific article by MongoDB ObjectId."""
    article_service = ArticleService(db)
    article = await article_service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return _to_response(article)


@router.get("/by-article-id/{article_id}", response_model=ArticleResponse)
async def get_article_by_article_id(article_id: str, db=Depends(get_database)):
    """Get a specific article by its custom article_id field."""
    article_service = ArticleService(db)
    article = await article_service.get_article_by_article_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return _to_response(article)


@router.post("/", response_model=ArticleResponse)
async def create_article(article: ArticleCreate, db=Depends(get_database)):
    """Create a new article from feed extraction."""
    article_service = ArticleService(db)

    # Check if article already exists
    if await article_service.article_exists(article.article_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Article with this article_id already exists",
        )

    created_article = await article_service.create_article(article)
    return _to_response(created_article)


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: str, article_update: ArticleUpdate, db=Depends(get_database)
):
    """Update an article."""
    article_service = ArticleService(db)
    updated_article = await article_service.update_article(article_id, article_update)
    if not updated_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return _to_response(updated_article)


@router.delete("/{article_id}")
async def delete_article(article_id: str, db=Depends(get_database)):
    """Delete an article."""
    article_service = ArticleService(db)
    success = await article_service.delete_article(article_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return {"message": "Article deleted successfully"}


@router.get("/source/{source_name}", response_model=List[ArticleResponse])
async def get_articles_by_source(
    source_name: str, limit: int = 100, db=Depends(get_database)
):
    """Get articles from a specific source."""
    article_service = ArticleService(db)
    articles = await article_service.get_articles_by_source(source_name, limit)
    return [_to_response(a) for a in articles]


@router.get("/search/{query}", response_model=List[ArticleResponse])
async def search_articles(query: str, limit: int = 50, db=Depends(get_database)):
    """Search articles by title and content."""
    article_service = ArticleService(db)
    articles = await article_service.search_articles(query, limit)
    return [_to_response(a) for a in articles]
