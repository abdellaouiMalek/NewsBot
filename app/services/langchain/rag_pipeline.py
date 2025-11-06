import logging

from app.services.langchain.context_builder import ContextBuilder
from app.services.langchain.langchain_vectorstore import LangchainQdrantConnector
from app.services.llm.llm_client import LLMClient

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.
    """

    def __init__(self):
        self.retriever = LangchainQdrantConnector()
        self.llm = LLMClient()

    async def generate_answer(self, query: str, k: int = 5) -> dict:
        # Step 1: Retrieve relevant documents
        docs = await self.retriever.search(query=query, k=k)
        serialized_docs = [d.metadata | {"snippet": d.page_content} for d in docs]

        # Step 2: Build context
        context = ContextBuilder.build_context(query, serialized_docs)

        # Step 3: Construct prompt
        prompt = (
            "You are a helpful news assistant. Use ONLY the provided context to answer "
            "the user's question factually.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n"
            "Answer in a concise, journalistic tone:\n"
        )

        # Step 4: Generate answer (LLMClient provides an async interface)
        # Use the async generate if available
        if hasattr(self.llm, "generate_async"):
            answer = await self.llm.generate_async(prompt)
        else:
            # fallback to sync generate (run in thread to avoid blocking)
            import asyncio

            answer = await asyncio.to_thread(self.llm.generate, prompt)

        return {
            "query": query,
            "context": context,
            "answer": answer,
            "sources": [d["article_id"] for d in serialized_docs],
        }
