from typing import Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.langchain.langchain_vectorstore import LangchainQdrantConnector

router = APIRouter(prefix="/semantic-search", tags=["Semantic Search"])


class SearchRequest(BaseModel):
    query: str
    k: int = 5
    vector_type: str = "primary_embedding"
    filters: Optional[Dict] = None


@router.post("/")
async def semantic_search(request: SearchRequest):
    # Compute embedding for query text

    # Connect to Qdrant via LangChain wrapper
    vector_connector = LangchainQdrantConnector(vector_name=request.vector_type)

    # Perform similarity search
    results = vector_connector.search(
        query=request.query,
        k=request.k,
        filters=request.filters,
    )

    return {
        "query": request.query,
        "results": [
            {
                "article_id": doc.metadata.get("article_id"),
                "category": doc.metadata.get("category"),
                "source_name": doc.metadata.get("source_name"),
                "published_at": doc.metadata.get("published_at"),
                "score": doc.metadata.get("score"),
                "snippet": doc.page_content[:400],
            }
            for doc in results
        ],
    }
