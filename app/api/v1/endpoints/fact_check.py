from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.database import get_database
from app.services.fact_checking.fact_check_service import FactCheckService

router = APIRouter(prefix="", tags=["Fact Check"])


class FactCheckRequest(BaseModel):
    article_id: str = Field(..., description="The article ID to fact-check")
    headline: str = Field(..., description="The headline of the article")
    summary: str = Field(..., description="The summary/content of the article")
    source: str = Field(..., description="The original source name")


class SourceComparison(BaseModel):
    source: str
    article_id: str
    headline: str
    summary: str
    trust_score: int
    credibility: str  # "high", "medium", "low"
    fact_accuracy: int
    bias_level: str  # "low", "medium", "high"
    reasoning: str


class FactCheckResponse(BaseModel):
    original_article_id: str
    original_source: str
    original_headline: str
    comparisons: List[SourceComparison]
    overall_assessment: str
    recommendation: str
    total_sources_found: int


@router.post("/", response_model=FactCheckResponse)
async def fact_check_article(request: FactCheckRequest, db=Depends(get_database)):
    """
    Perform fact-checking by finding similar articles from different sources
    and comparing them using LLM analysis.

    Note: This endpoint can take 3-5 minutes due to:
    - Semantic search in vector database
    - Multiple LLM calls for filtering and analysis
    - MongoDB queries for full article content

    By default, analyzes up to 3 similar articles to balance quality and speed.
    """
    try:
        fact_check_service = FactCheckService(db)
        # Use k=3 for faster results (3 comparisons instead of 5)
        result = await fact_check_service.fact_check_article(
            article_id=request.article_id,
            headline=request.headline,
            summary=request.summary,
            source=request.source,
            k=3,  # Reduced from default 5 to speed up processing
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
