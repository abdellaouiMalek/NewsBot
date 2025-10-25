from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.services.fetchers.api_fetchers import get_api_sources
from app.services.ingestion_service import (
    fetch_and_store_api_articles,
    fetch_and_store_rss_articles,
)

router = APIRouter(prefix="/fetch", tags=["fetch"])


@router.post("/rss")
async def fetch_rss_articles(db=Depends(get_database)):
    count = await fetch_and_store_rss_articles(db)
    return {"inserted": count}


@router.post("/api")
async def fetch_api_articles(db=Depends(get_database)):
    count = await fetch_and_store_api_articles(db)
    return {"inserted": count}


@router.get("/test")
async def test():
    result = get_api_sources()
    return {"result: ": result}
