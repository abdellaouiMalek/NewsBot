import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def get_embedding_model(preferred_device: Optional[str] = None):
    """
    Lazily load and return the SentenceTransformer embedding model.

    - preferred_device: Optional override (e.g. 'cpu' or 'cuda'). If not
      provided the function will try CUDA if available and fall back to CPU on
      failure (OOM or other errors).

    This avoids importing and allocating large models during module import,
    and handles environments with limited GPU memory gracefully.
    """
    # Local import to avoid heavy dependencies during top-level import
    try:
        import torch
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        logger.error("Failed to import sentence-transformers or torch: %s", e)
        raise

    # Respect explicit env override first
    env_device = os.environ.get("EMBEDDING_DEVICE")
    if preferred_device:
        device = preferred_device
    elif env_device:
        device = env_device
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    model_name = os.environ.get(
        "EMBEDDING_MODEL_NAME", "sentence-transformers/all-mpnet-base-v2"
    )

    # Try to load on the chosen device, but gracefully fall back to CPU on OOM
    try:
        logger.info(f"[EmbeddingModel] Loading '{model_name}' on device={device}")
        model = SentenceTransformer(model_name, device=device)
        logger.info(f"[EmbeddingModel] Loaded '{model_name}' on {device}")
        return model
    except Exception as e:
        # If CUDA OOM or any other error occurs, fallback to CPU
        logger.warning(
            "[EmbeddingModel] Failed to load on %s (%s). Falling back to CPU.",
            device,
            e,
        )
        try:
            model = SentenceTransformer(model_name, device="cpu")
            logger.info(f"[EmbeddingModel] Loaded '{model_name}' on cpu")
            return model
        except Exception as e2:
            logger.error("[EmbeddingModel] Failed to load model on CPU: %s", e2)
            raise


__all__ = ["get_embedding_model"]
