from fastapi import APIRouter

from app.api.v1.endpoints.articles import router as articles_router
from app.api.v1.endpoints.bot import router as bot_router
from app.api.v1.endpoints.fetch import router as fetch_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.scheduler import router as scheduler_router

router = APIRouter()

router.include_router(articles_router, prefix="/articles", tags=["Articles"])
router.include_router(bot_router, prefix="/bot", tags=["Bot"])
router.include_router(health_router, prefix="/health", tags=["Health"])
router.include_router(fetch_router, prefix="/fetch", tags=["fetch_articles"])
router.include_router(scheduler_router, prefix="/scheduler", tags=["scheduler"])
