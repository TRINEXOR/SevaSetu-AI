"""
SevaSetu AI — Embedding Service (lightweight ONNX version)
Uses chromadb's built-in ONNX embedding — no torch required.
"""
import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    _instance = None
    _fn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, model_name: str = "all-MiniLM-L6-v2"):
        if self._fn is None:
            try:
                from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
                self._fn = ONNXMiniLM_L6_V2()
                logger.info("✅ ONNX embedding model loaded")
            except Exception as e:
                logger.warning(f"⚠️ Could not load ONNX embeddings: {e}")

    def embed(self, text: str) -> List[float]:
        if self._fn is None:
            self.load()
        if self._fn:
            try:
                return self._fn([text])[0]
            except Exception:
                pass
        return (np.zeros(384) + 1e-6).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if self._fn is None:
            self.load()
        if self._fn:
            try:
                return self._fn(texts)
            except Exception:
                pass
        return [(np.zeros(384) + 1e-6).tolist() for _ in texts]

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        a = np.array(vec_a)
        b = np.array(vec_b)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    @property
    def dim(self) -> int:
        return 384


embedding_service = EmbeddingService()
