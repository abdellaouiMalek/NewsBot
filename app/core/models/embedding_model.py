import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Global cache for the embedding model (singleton pattern)
_embedding_model_cache = None


def get_embedding_model(preferred_device: Optional[str] = None):
    """
    Lazily load and return the SentenceTransformer embedding model.
    Returns a cached instance on subsequent calls to avoid reloading.

    - preferred_device: Optional override (e.g. 'cpu' or 'cuda'). If not
      provided, respects EMBEDDING_DEVICE env var, otherwise uses CPU as
      safe default (since GPU may be occupied by Ollama).

    This avoids importing and allocating large models during module import,
    and handles environments with limited GPU memory gracefully.
    """
    global _embedding_model_cache

    # Return cached model if already loaded
    if _embedding_model_cache is not None:
        return _embedding_model_cache

    # Local import to avoid heavy dependencies during top-level import
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        logger.error("Failed to import sentence-transformers: %s", e)
        raise

    # Respect explicit env override first, default to CPU to avoid GPU OOM
    env_device = os.environ.get("EMBEDDING_DEVICE", "cpu")
    if preferred_device:
        device = preferred_device
    else:
        device = env_device

    model_name = os.environ.get(
        "EMBEDDING_MODEL_NAME", "sentence-transformers/all-mpnet-base-v2"
    )

    # Load on the chosen device
    try:
        logger.info(f"[EmbeddingModel] Loading '{model_name}' on device={device}")
        model = SentenceTransformer(model_name, device=device)
        logger.info(f"[EmbeddingModel] Successfully loaded '{model_name}' on {device}")
        _embedding_model_cache = model
        return model
    except Exception as e:
        # If loading fails and we tried CUDA, fallback to CPU
        if device != "cpu":
            logger.warning(
                "[EmbeddingModel] Failed to load on %s (%s). Falling back to CPU.",
                device,
                e,
            )
            try:
                model = SentenceTransformer(model_name, device="cpu")
                logger.info(
                    f"[EmbeddingModel] Successfully loaded '{model_name}' on cpu"
                )
                _embedding_model_cache = model
                return model
            except Exception as e2:
                logger.error("[EmbeddingModel] Failed to load model on CPU: %s", e2)
                raise
        else:
            logger.error("[EmbeddingModel] Failed to load model on %s: %s", device, e)
            raise


__all__ = ["get_embedding_model"]
