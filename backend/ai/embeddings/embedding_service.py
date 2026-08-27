"""
SevaSetu AI — Embedding Service
Author: Rahul Jha | Made in India 🇮🇳

Singleton wrapper around Sentence-Transformers for
consistent embedding generation across the app.

Model: all-MiniLM-L6-v2 (384 dimensions)
- 14x faster than BERT base
- Strong semantic similarity performance
- Works well for English + partial Hindi
"""
import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generates dense vector embeddings for text using Sentence-BERT.
    Used by RAG engine for both document indexing and query embedding.
    """
    _instance = None
    _model    = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, model_name: str = "all-MiniLM-L6-v2"):
        """Lazy-load the embedding model once at startup."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"📊 Loading embedding model: {model_name}")
                self._model = SentenceTransformer(model_name)
                logger.info(f"✅ Embedding model loaded — dim={self._model.get_sentence_embedding_dimension()}")
            except ImportError:
                logger.warning("⚠️ sentence-transformers not installed — using zero vectors")

    def embed(self, text: str) -> List[float]:
        """Embed a single text → normalised 384-dim vector."""
        if self._model is None:
            self.load()
        if self._model:
            return self._model.encode(text, normalize_embeddings=True).tolist()
        # Fallback for testing without the model installed
        return (np.zeros(384) + 1e-6).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Efficiently embed a list of texts in batches."""
        if self._model is None:
            self.load()
        if self._model:
            return self._model.encode(
                texts,
                normalize_embeddings=True,
                batch_size=32,
                show_progress_bar=False,
            ).tolist()
        return [(np.zeros(384) + 1e-6).tolist() for _ in texts]

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Cosine similarity between two vectors (range −1 to 1)."""
        a = np.array(vec_a)
        b = np.array(vec_b)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    @property
    def dim(self) -> int:
        """Return embedding dimension."""
        if self._model:
            return self._model.get_sentence_embedding_dimension()
        return 384


# Singleton — import and use across the app
embedding_service = EmbeddingService()
