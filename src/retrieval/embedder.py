"""
EMP-12 Vector Embedder Module
Wraps Sentence-Transformers to generate unit-normalized vector embeddings for chunks and queries.
"""

import sys
from pathlib import Path
from typing import List, Optional
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import EMBEDDING_MODEL_NAME


# Module-level model cache to prevent expensive repeated model initializations
_MODEL_CACHE = {}
_DIMENSION_CACHE = {}


class TerminologyEmbedder:
    """
    Handles local dense embedding generation using Sentence-Transformers.
    Applies L2 normalization so dot product / inner product equals cosine similarity.
    Reuses cached model instances within the process to optimize performance.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or EMBEDDING_MODEL_NAME
        self._model = None
        self._dimension: Optional[int] = None

    def _load_model(self):
        """Lazy loader for SentenceTransformer model with process-level caching."""
        global _MODEL_CACHE, _DIMENSION_CACHE
        if self.model_name in _MODEL_CACHE:
            self._model = _MODEL_CACHE[self.model_name]
            self._dimension = _DIMENSION_CACHE.get(self.model_name)
            return self._model

        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            # Determine output embedding dimension dynamically
            sample_embedding = self._model.encode(["sample text"], convert_to_numpy=True)
            self._dimension = int(sample_embedding.shape[1])
            _MODEL_CACHE[self.model_name] = self._model
            _DIMENSION_CACHE[self.model_name] = self._dimension

        return self._model

    @property
    def dimension(self) -> int:
        """Returns the embedding vector dimensionality (e.g. 384 for all-MiniLM-L6-v2)."""
        if self._dimension is None:
            self._load_model()
        return self._dimension

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embeds a single query or text string into a normalized 1D float32 vector.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text for embedding cannot be empty or whitespace.")

        model = self._load_model()
        raw_embedding = model.encode(text.strip(), convert_to_numpy=True)

        # Cast to float32
        vec = raw_embedding.astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Batch embeds a list of text strings into a normalized 2D float32 numpy matrix (N, D).
        """
        if not isinstance(texts, list) or len(texts) == 0:
            raise ValueError("texts must be a non-empty list of strings.")

        for idx, t in enumerate(texts):
            if not isinstance(t, str) or not t.strip():
                raise ValueError(f"Text at index {idx} cannot be empty or non-string.")

        model = self._load_model()
        cleaned_texts = [t.strip() for t in texts]
        raw_embeddings = model.encode(cleaned_texts, batch_size=32, convert_to_numpy=True)

        # Cast to float32 and L2 normalize each vector
        matrix = raw_embeddings.astype(np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0  # Prevent division by zero
        normalized_matrix = matrix / norms
        return normalized_matrix
