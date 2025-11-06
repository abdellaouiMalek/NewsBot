import re
from typing import Dict, List

from app.core.models.nlp_model import nlp


def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
    """
    Extract key phrases from text using NLP (noun chunks + frequency filtering).

    Args:
        text (str): Input text.
        max_phrases (int): Maximum number of key phrases to return.

    Returns:
        List[str]: List of key phrases.
    """
    if not text:
        return []

    # Clean text a bit
    text = re.sub(r"\s+", " ", text.strip())

    doc = nlp(text)
    phrases = [chunk.text.lower() for chunk in doc.noun_chunks]

    # Deduplicate while preserving order
    seen = set()
    unique_phrases = []
    for phrase in phrases:
        if phrase not in seen:
            seen.add(phrase)
            unique_phrases.append(phrase)

    return unique_phrases[:max_phrases]


def format_entities(entities: Dict[str, List[str]]) -> str:
    """
    Convert an entities dictionary into a structured, human-readable string.

    Args:
        entities (Dict[str, List[str]]): {
            "persons": [...],
            "organizations": [...],
            "locations": [...],
            "dates": [...],
            "events": [...]
        }

    Returns:
        str: Concatenated string of all entity types, ready for embedding.
    """
    parts = []
    for key, values in entities.items():
        if values:
            # Join unique values to avoid duplicates
            unique_values = list(dict.fromkeys(values))
            parts.append(f"{key.upper()}: {', '.join(unique_values)}")
    return " | ".join(parts)
