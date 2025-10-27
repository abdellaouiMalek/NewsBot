import torch
from sentence_transformers import SentenceTransformer

# Automatically detect device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load the model once and keep it in memory
EMBEDDING_MODEL = SentenceTransformer(
    "sentence-transformers/all-mpnet-base-v2", device=DEVICE
)

print(f"[EmbeddingModel] Loaded on {DEVICE.upper()}")
