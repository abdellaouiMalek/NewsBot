from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.database import get_database
from app.schemas.article import ArticleResponse
from app.services.article.article_service import ArticleService
from app.services.langchain.rag_pipeline import RAGPipeline

router = APIRouter(prefix="", tags=["Generate"])
rag_pipeline = RAGPipeline()


class GenerateRequest(BaseModel):
    query: str
    k: int = 5


class GenerateResponse(BaseModel):
    query: str
    context: str
    answer: str
    sources: List[str]
    articles: List[ArticleResponse]


def _to_response(article) -> ArticleResponse:
    """Helper to normalize Article objects/dicts to ArticleResponse schema."""
    if hasattr(article, "model_dump"):
        article_dict = article.model_dump()
    else:
        article_dict = dict(article)

    # Convert ObjectId fields to strings
    for field in ["id", "embedding_id"]:
        if field in article_dict and article_dict[field] is not None:
            article_dict[field] = str(article_dict[field])

    return ArticleResponse(**article_dict)


@router.post("/", response_model=GenerateResponse)
async def generate_answer(request: GenerateRequest, db=Depends(get_database)):
    """
    Generate an AI-augmented news answer for a given query.
    Returns the answer along with full article details for the sources used.
    """
    try:
        # Get RAG pipeline result
        result = await rag_pipeline.generate_answer(query=request.query, k=request.k)

        # Fetch full articles for the sources
        article_service = ArticleService(db)
        article_ids = result.get("sources", [])
        articles = await article_service.get_articles_by_ids(article_ids)

        # Convert articles to response format
        article_responses = [_to_response(article) for article in articles]

        return GenerateResponse(
            query=result["query"],
            context=result["context"],
            answer=result["answer"],
            sources=article_ids,
            articles=article_responses,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
