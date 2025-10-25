from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_database
from app.schemas.article import ArticleCreate, ArticleResponse, ArticleUpdate
from app.services.article.article_service import ArticleService

router = APIRouter()


@router.get("/articles", response_model=List[ArticleResponse])
async def get_articles(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    source_name: Optional[str] = None,
    fetch_method: Optional[str] = None,
    language: Optional[str] = None,
    country: Optional[str] = None,
    db=Depends(get_database),
):
    """Get articles with optional filtering."""
    article_service = ArticleService(db)
    articles = await article_service.get_articles(
        skip=skip,
        limit=limit,
        category=category,
        source_name=source_name,
        fetch_method=fetch_method,
        language=language,
        country=country,
    )
    return articles


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str, db=Depends(get_database)):
    """Get a specific article by MongoDB ObjectId."""
    article_service = ArticleService(db)
    article = await article_service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return article


@router.get("/articles/by-article-id/{article_id}", response_model=ArticleResponse)
async def get_article_by_article_id(article_id: str, db=Depends(get_database)):
    """Get a specific article by its custom article_id field."""
    article_service = ArticleService(db)
    article = await article_service.get_article_by_article_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return article


@router.post("/articles", response_model=ArticleResponse)
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
    return created_article


@router.put("/articles/{article_id}", response_model=ArticleResponse)
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
    return updated_article


@router.delete("/articles/{article_id}")
async def delete_article(article_id: str, db=Depends(get_database)):
    """Delete an article."""
    article_service = ArticleService(db)
    success = await article_service.delete_article(article_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return {"message": "Article deleted successfully"}


@router.get("/articles/source/{source_name}", response_model=List[ArticleResponse])
async def get_articles_by_source(
    source_name: str, limit: int = 100, db=Depends(get_database)
):
    """Get articles from a specific source."""
    article_service = ArticleService(db)
    articles = await article_service.get_articles_by_source(source_name, limit)
    return articles


@router.get("/articles/search/{query}", response_model=List[ArticleResponse])
async def search_articles(query: str, limit: int = 50, db=Depends(get_database)):
    """Search articles by title and content."""
    article_service = ArticleService(db)
    articles = await article_service.search_articles(query, limit)
    return articles
