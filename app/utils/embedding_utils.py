import re
from typing import Dict, List

from app.core.models.embedding_model import EMBEDDING_MODEL
from app.utils.nlp_utils import extract_key_phrases


def prepare_embedding_text(article: Dict) -> Dict:
    """
    Generate optimized text fields for embedding generation.

    Args:
        article (Dict): A single article record containing fields like 'title',
                        'content', 'summary', 'category', 'entities', etc.

    Returns:
        Dict: Original article dict augmented with
                'embedding_title_text', 'embedding_primary_text', and 'embedding_secondary_text'.
    """

    # --- Title embedding text ---
    title_text = article.get("title") or ""

    # --- Primary embedding text: core semantic information ---
    primary_text = _build_primary_text(article)

    # --- Secondary embedding text: metadata / context ---
    secondary_text = _build_secondary_text(article)

    # --- Clean the text for embeddings ---
    article["embedding_title_text"] = _clean_text_for_embedding(title_text)
    article["embedding_primary_text"] = _clean_text_for_embedding(primary_text)
    article["embedding_secondary_text"] = _clean_text_for_embedding(secondary_text)

    return article


# ==============================================================
# Internal Helpers
# ==============================================================


def _build_primary_text(article: Dict) -> str:
    """
    Construct the primary embedding text, combining:
    title, content, formatted entities, and source.
    """
    entities_text = article.get("entities") or ""

    primary_template = (
        f"TITLE: {article.get('title', '')}\n"
        f"CONTENT: {article.get('content', '')}\n"
        f"ENTITIES: {entities_text}\n"
        f"SOURCE: {article.get('source_name', '')}"
    )

    return primary_template


def _build_secondary_text(article: Dict) -> str:
    """
    Construct secondary embedding text combining summary, category, and key phrases.
    Useful for contextual or hybrid search embeddings.
    """
    summary = article.get("summary") or ""
    category = article.get("category") or ""
    content = article.get("content") or ""

    key_phrases = extract_key_phrases(content)
    key_phrases_text = ", ".join(key_phrases)

    secondary_template = (
        f"SUMMARY: {summary}\n"
        f"CATEGORY: {category}\n"
        f"KEY_PHRASES: {key_phrases_text}"
    )

    return secondary_template


def _clean_text_for_embedding(text: str) -> str:
    """
    Normalize text for embedding models:
    - Keep only useful punctuation.
    - Normalize whitespace.
    """
    text = re.sub(r"[^\w\s.,!?;:()\-]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ==============================================================
# Embedding Computation
# ==============================================================


def compute_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Compute embeddings for a list of texts using the configured embedding model.

    Supports GPU acceleration automatically if EMBEDDING_MODEL is on CUDA.
    """
    if not texts:
        return []

    # Use the sentence-transformers model
    return EMBEDDING_MODEL.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
    ).tolist()


def compute_article_embeddings(article: Dict) -> Dict:
    """
    Compute all embeddings (title, primary, secondary) and return them as vectors.

    Returns:
        Dict with keys: 'title_embedding', 'primary_embedding', 'secondary_embedding'
    """
    # Ensure embedding texts are prepared
    article = prepare_embedding_text(article)

    # Compute embeddings
    title_vector = (
        compute_embeddings([article["embedding_title_text"]])[0]
        if article.get("embedding_title_text")
        else None
    )
    primary_vector = (
        compute_embeddings([article["embedding_primary_text"]])[0]
        if article.get("embedding_primary_text")
        else None
    )
    secondary_vector = (
        compute_embeddings([article["embedding_secondary_text"]])[0]
        if article.get("embedding_secondary_text")
        else None
    )

    return {
        "title_embedding": title_vector,
        "primary_embedding": primary_vector,
        "secondary_embedding": secondary_vector,
    }
