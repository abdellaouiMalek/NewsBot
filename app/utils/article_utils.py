import re
from typing import Dict, List

import pandas as pd
from langdetect import LangDetectException, detect

from app.core.models.nlp_model import nlp
from app.models.article import Article
from app.schemas.article import ArticleCreate
from app.schemas.article_embedding import ArticleEmbeddingCreate
from app.services.article.article_service import ArticleService
from app.services.embedding.embedding_service import EmbeddingService
from app.utils.embedding_utils import (
    compute_article_embeddings,
    compute_embeddings,
    prepare_embedding_text,
)


def deduplicate(new_records: List[Dict], existing_df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates from new_records based on 'article_id' against existing_df."""
    new_df = pd.DataFrame(new_records)
    if existing_df.empty:
        return new_df

    deduped_df = new_df[~new_df["article_id"].isin(existing_df["article_id"])]
    return deduped_df


def clean_rss_text(text):
    """Enhanced content cleaning pipeline"""
    # Remove RSS-specific artifacts
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def enhance_metadata(article: ArticleCreate) -> ArticleCreate:
    """Fill missing metadata"""
    if not article.language:
        if article.content:
            try:
                article.language = detect(article.content)
            except LangDetectException:
                article.language = "unknown"
            except Exception:
                article.language = "unknown"
        else:
            article.language = "unknown"
    return article


def format_entities(entities: dict) -> str:
    """Convert a dict of entities into a compact readable string."""
    if not entities or not isinstance(entities, dict):
        return ""
    parts = []
    for key, values in entities.items():
        if values:
            formatted_values = ", ".join(sorted(set(values)))
            parts.append(f"{key}: {formatted_values}")
    return " | ".join(parts)


async def extract_entities(articles: List[Article], db):
    """
    Extract entities for a list of Article instances and update the DB.
    """
    print(
        f"🚀 Running background entities extraction task for {len(articles)} articles"
    )
    article_service = ArticleService(db)
    updated_articles = []

    for article in articles:
        doc = nlp(f"{article.title}: {article.content or ''}")

        entities_dict = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "events": [],
        }

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities_dict["persons"].append(ent.text)
            elif ent.label_ == "ORG":
                entities_dict["organizations"].append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:
                entities_dict["locations"].append(ent.text)
            elif ent.label_ in ["DATE", "TIME"]:
                entities_dict["dates"].append(ent.text)
            elif ent.label_ == "EVENT":
                entities_dict["events"].append(ent.text)

        # Format entities before saving
        formatted_entities = format_entities(entities_dict)

        article_dict = {
            "article_id": article.article_id,
            "entities": formatted_entities,
        }
        updated_articles.append(article_dict)

    # Bulk update
    await article_service.update_entities_bulk(updated_articles)


async def extract_embeddings(articles: List[Article], db):
    """
    Extract primary and secondary embeddings for a list of Article instances
    and update the database in bulk.

    This function mirrors the `extract_entities` logic, but for embeddings.
    """
    print(
        f"🚀 Running background embedding extraction task for {len(articles)} articles"
    )
    article_service = ArticleService(db)

    updated_articles = []

    for article in articles:
        # Prepare text for embeddings
        article_dict = article.dict()
        article_dict = prepare_embedding_text(article_dict)

        embeddings = compute_embeddings(
            [
                article_dict.get("embedding_primary_text"),
                article_dict.get("embedding_secondary_text"),
            ]
        )

        # Collect fields to update
        update_data = {
            "embedding_primary_text": article_dict.get("embedding_primary_text"),
            "embedding_secondary_text": article_dict.get("embedding_secondary_text"),
            "embedding_primary": embeddings[0],
            "embedding_secondary": embeddings[1],
        }

        updated_articles.append({"article_id": article.article_id, **update_data})

    # Update all embeddings in bulk
    await article_service.update_embeddings_bulk(updated_articles)


async def extract_embeddings_qdrant(articles: List[Article], db):
    """
    Extract embeddings for articles and save them into Qdrant.

    Works similarly to extract_embeddings, but persists directly in Qdrant.
    """
    print(f"🚀 Running background Qdrant embedding task for {len(articles)} articles")

    embedding_service = EmbeddingService()
    embeddings_to_upsert = []

    for article in articles:
        article_dict = article.dict()
        # Prepare the text for embeddings
        article_dict = prepare_embedding_text(article_dict)

        # Compute vectors
        vectors = compute_article_embeddings(article_dict)

        # Build Qdrant schema
        embedding = ArticleEmbeddingCreate(
            article_id=article.article_id,
            vectors=vectors,
            category=getattr(article, "category", None),
            source_name=getattr(article, "source_name", None),
            published_at=getattr(article, "published_at", None),
        )

        embeddings_to_upsert.append(embedding)

    # Batch upsert into Qdrant
    embedding_service.batch_upsert(embeddings_to_upsert)
    print(f"✅ Finished Qdrant embedding task for {len(articles)} articles")
