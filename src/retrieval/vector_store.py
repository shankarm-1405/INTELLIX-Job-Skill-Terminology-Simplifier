"""
EMP-12 FAISS Vector Store Module
Manages local FAISS index creation, persistence, loading, and cosine similarity queries.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import faiss
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import FAISS_INDEX_PATH, VECTOR_METADATA_PATH, SUPPORTED_CATEGORIES
from src.retrieval.embedder import TerminologyEmbedder
from src.retrieval.models import SearchResult


# Module-level index cache with mtime invalidation
_INDEX_CACHE = {}


class FAISSVectorStore:
    """
    Persistent local vector store utilizing FAISS IndexFlatIP for exact cosine similarity search
    over L2-normalized embeddings.
    Caches loaded indices in memory to eliminate repeated disk I/O while respecting file updates.
    """

    def __init__(self):
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: List[Dict[str, Any]] = []

    @property
    def is_loaded(self) -> bool:
        """Returns True if both index and metadata are populated."""
        return self.index is not None and len(self.metadata) > 0

    @property
    def total_vectors(self) -> int:
        """Returns the total number of indexed vectors."""
        return self.index.ntotal if self.index is not None else 0

    def build_from_chunks(
        self,
        chunks_file: Path,
        embedder: Optional[TerminologyEmbedder] = None,
    ) -> int:
        """
        Builds the FAISS vector index from a chunks JSON file:
        - Validates file existence and records
        - Enforces unique chunk IDs
        - Embeds all chunk texts into normalized vectors
        - Adds vectors to IndexFlatIP
        - Stores 1-to-1 position mapping in metadata
        """
        if not chunks_file.exists() or not chunks_file.is_file():
            raise FileNotFoundError(f"Chunks file not found at: {chunks_file}")

        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)

        if not isinstance(chunks_data, list) or len(chunks_data) == 0:
            raise ValueError(f"Chunks file '{chunks_file}' is empty or not a JSON list.")

        # Validate unique chunk IDs
        seen_ids = set()
        for idx, chunk in enumerate(chunks_data):
            chunk_id = chunk.get("chunk_id")
            if not chunk_id:
                raise ValueError(f"Chunk at index {idx} has no 'chunk_id'.")
            if chunk_id in seen_ids:
                raise ValueError(f"Duplicate chunk ID '{chunk_id}' detected in chunks data.")
            seen_ids.add(chunk_id)

        embedder_instance = embedder or TerminologyEmbedder()
        texts = [c["text"] for c in chunks_data]

        # Generate normalized vectors (N, D)
        vectors = embedder_instance.embed_texts(texts)
        num_vectors, dim = vectors.shape

        if num_vectors != len(chunks_data):
            raise ValueError(f"Vector count {num_vectors} does not match chunk count {len(chunks_data)}.")

        # Create FAISS Inner Product index (equivalent to cosine similarity on unit vectors)
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)

        self.index = index
        self.metadata = chunks_data
        return num_vectors

    def save(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
    ) -> None:
        """
        Persists the FAISS index binary and metadata JSON to disk.
        """
        if not self.is_loaded:
            raise RuntimeError("Cannot save uninitialized or empty FAISSVectorStore.")

        idx_file = index_path or FAISS_INDEX_PATH
        meta_file = metadata_path or VECTOR_METADATA_PATH

        idx_file.parent.mkdir(parents=True, exist_ok=True)
        meta_file.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(idx_file))
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

        # Invalidate / update cache
        cache_key = (str(idx_file.resolve()), str(meta_file.resolve()))
        _INDEX_CACHE[cache_key] = (self.index, self.metadata, idx_file.stat().st_mtime, meta_file.stat().st_mtime)

    def load(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
    ) -> int:
        """
        Loads the persisted FAISS index binary and metadata JSON from disk or cache.
        """
        global _INDEX_CACHE
        idx_file = (index_path or FAISS_INDEX_PATH).resolve()
        meta_file = (metadata_path or VECTOR_METADATA_PATH).resolve()

        if not idx_file.exists():
            raise FileNotFoundError(f"FAISS index file not found at: {idx_file}")
        if not meta_file.exists():
            raise FileNotFoundError(f"Vector metadata file not found at: {meta_file}")

        cache_key = (str(idx_file), str(meta_file))
        cur_idx_mtime = idx_file.stat().st_mtime
        cur_meta_mtime = meta_file.stat().st_mtime

        if cache_key in _INDEX_CACHE:
            cached_index, cached_meta, c_idx_m, c_meta_m = _INDEX_CACHE[cache_key]
            if c_idx_m == cur_idx_mtime and c_meta_m == cur_meta_mtime:
                self.index = cached_index
                self.metadata = cached_meta
                return self.index.ntotal

        loaded_index = faiss.read_index(str(idx_file))
        with open(meta_file, "r", encoding="utf-8") as f:
            loaded_metadata = json.load(f)

        if loaded_index.ntotal != len(loaded_metadata):
            raise ValueError(
                f"Index/Metadata count mismatch: {loaded_index.ntotal} vectors vs {len(loaded_metadata)} records."
            )

        self.index = loaded_index
        self.metadata = loaded_metadata
        _INDEX_CACHE[cache_key] = (self.index, self.metadata, cur_idx_mtime, cur_meta_mtime)
        return self.index.ntotal

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Executes similarity search on the FAISS index:
        - Validates query_vector
        - Searches top candidates
        - Applies optional category filtering
        - Returns ranked SearchResult objects with scores
        """
        if not self.is_loaded:
            raise RuntimeError("FAISSVectorStore is not loaded. Build or load an index first.")

        if top_k <= 0:
            raise ValueError(f"top_k must be a positive integer, got {top_k}.")

        if category is not None and category not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. Supported: {SUPPORTED_CATEGORIES}"
            )

        # Ensure query_vector is 2D float32 of shape (1, D)
        if query_vector.ndim == 1:
            q_vec = query_vector.reshape(1, -1).astype(np.float32)
        else:
            q_vec = query_vector.astype(np.float32)

        # L2-normalize query vector
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec = q_vec / norm

        total_available = self.index.ntotal
        effective_k = min(total_available, top_k if category is None else total_available)

        scores, indices = self.index.search(q_vec, effective_k)
        scores = scores[0]
        indices = indices[0]

        results: List[SearchResult] = []
        rank_counter = 1

        for score, idx in zip(scores, indices):
            if idx < 0 or idx >= len(self.metadata):
                continue

            chunk_meta = self.metadata[idx]

            # Apply category filter if specified
            if category is not None and chunk_meta.get("category") != category:
                continue

            # Ensure similarity score is non-negative and rounded cleanly
            clean_score = max(0.0, float(round(float(score), 4)))

            result = SearchResult(
                chunk_id=chunk_meta["chunk_id"],
                document_id=chunk_meta["document_id"],
                term=chunk_meta["term"],
                category=chunk_meta["category"],
                difficulty=chunk_meta["difficulty"],
                domain=chunk_meta["domain"],
                source=chunk_meta["source"],
                text=chunk_meta["text"],
                score=clean_score,
                rank=rank_counter,
                related_skills=chunk_meta.get("related_skills", []),
                related_terms=chunk_meta.get("related_terms", []),
            )
            results.append(result)
            rank_counter += 1

            if len(results) >= top_k:
                break

        return results
