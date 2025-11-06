from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.langchain.rag_pipeline import RAGPipeline

router = APIRouter(prefix="/generate", tags=["Generate"])
rag_pipeline = RAGPipeline()


class GenerateRequest(BaseModel):
    query: str
    k: int = 5


@router.post("/generate/")
async def generate_answer(request: GenerateRequest):
    """
    Generate an AI-augmented news answer for a given query.
    """
    try:
        result = await rag_pipeline.generate_answer(query=request.query, k=request.k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
