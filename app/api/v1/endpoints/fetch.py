from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.database import get_database
from app.services.ingestion_service import (
    fetch_and_store_api_articles,
    fetch_and_store_rss_articles,
)

router = APIRouter(prefix="/fetch", tags=["fetch"])


@router.post("/rss")
async def fetch_rss_articles(
    background_tasks: BackgroundTasks, db=Depends(get_database)
):
    articles = await fetch_and_store_rss_articles(db, background_tasks)
    return {"inserted": len(articles)}


@router.post("/api")
async def fetch_api_articles(
    background_tasks: BackgroundTasks, db=Depends(get_database)
):
    articles = await fetch_and_store_api_articles(db, background_tasks)
    return {"inserted": len(articles)}


@router.get("/test")
async def test():
    from app.services.fetchers.api_fetchers import get_api_sources

    result = get_api_sources()
    return {"result": result}
