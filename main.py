import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import close_mongo_connection, connect_to_mongo
from app.core.scheduler import configure_jobs, start_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="NewsBot AI API with MongoDB & APScheduler",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting NewsBot AI API...")
    await connect_to_mongo()
    configure_jobs()
    start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down NewsBot AI API...")
    await close_mongo_connection()


@app.get("/")
async def root():
    return {
        "message": "Welcome to NewsBot AI API",
        "version": settings.version,
        "docs": f"{settings.api_v1_prefix}/docs",
    }
