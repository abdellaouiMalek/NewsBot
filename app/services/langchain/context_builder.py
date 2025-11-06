from datetime import datetime
from typing import Dict, List, Optional


class ContextBuilder:
    """
    Builds a clean, LLM-friendly context from retrieved articles.

    Contract / small spec:
    - build_context(query, results, max_docs, role, skills, tones) -> str
        - query: user's question (string)
        - results: list of article dicts (each may contain source_name, published_at, category, article_id, snippet)
        - max_docs: how many articles to include
        - role: optional assistant role string (e.g. "You are a professional news agent")
        - skills: optional list of skill strings (e.g. ["fact-checking", "concise summaries"]) that the assistant should apply
        - tones: optional list of tones to adopt (e.g. ["neutral", "authoritative"])

    The resulting context is a single string suitable for prepending to an LLM prompt. It places
    role/skills/tones as a short instruction block before the retrieved documents and the user query.
    """

    @staticmethod
    def format_article(article: Dict) -> str:
        """
        Format a single article entry into readable text.
        """
        source = article.get("source_name", "Unknown Source")
        date = article.get("published_at")
        category = article.get("category", "Uncategorized")

        # Format publication date
        if date:
            try:
                date = datetime.fromisoformat(date).strftime("%B %d, %Y")
            except Exception:
                pass

        snippet = article.get("snippet") or ""
        article_id = article.get("article_id", "")

        return (
            f"Source: {source}\n"
            f"Date: {date}\n"
            f"Category: {category}\n"
            f"URL: {article_id}\n"
            f"Summary: {snippet.strip()}\n"
        )

    @classmethod
    def build_context(
        cls,
        query: str,
        results: List[Dict],
        max_docs: Optional[int] = 5,
        role: Optional[str] = None,
        skills: Optional[List[str]] = None,
        tones: Optional[List[str]] = None,
    ) -> str:
        """
        Combine multiple article entries into a single context block.
        """
        if not results:
            base = "No related context found."
            # still include small role/skill/tones header if provided
            header_parts = []
            if role:
                header_parts.append(f"Role: {role}")
            if skills:
                header_parts.append("Skills: " + ", ".join(skills))
            if tones:
                header_parts.append("Tones: " + ", ".join(tones))

            if header_parts:
                return "\n".join(header_parts) + "\n\n" + base

            return "No related context found."

        selected = results[:max_docs]

        formatted_articles = [cls.format_article(article) for article in selected]

        context_text = "\n\n---\n\n".join(formatted_articles)

        # Build instruction header (role / skills / tones) with defaults when appropriate
        header_lines: List[str] = []
        if role:
            header_lines.append(f"Role instruction: {role.strip()}")
        else:
            # sensible default role that helps the assistant stay focused
            header_lines.append(
                "Role instruction: You are a professional news agent. Provide factual, concise, and well-sourced answers."
            )

        if skills:
            header_lines.append(
                "Skills to apply: " + ", ".join(s.strip() for s in skills if s)
            )

        if tones:
            header_lines.append(
                "Tones to adopt: " + ", ".join(t.strip() for t in tones if t)
            )

        header = "\n".join(header_lines) + "\n\n"

        return (
            f"{header}The following articles may help answer the user's question:\n\n"
            f"{context_text}\n\n"
            f"User Query: {query}\n"
        )
