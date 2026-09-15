"""
EMP-12 Terminology Retriever Module
High-level interface for semantic terminology queries against the FAISS vector store.
"""

import sys
from pathlib import Path
from typing import List, Optional

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    CHUNKS_PATH,
    DEFAULT_TOP_K,
    FAISS_INDEX_PATH,
    SUPPORTED_CATEGORIES,
    VECTOR_METADATA_PATH,
)
from src.retrieval.embedder import TerminologyEmbedder
from src.retrieval.models import SearchResult
from src.retrieval.vector_store import FAISSVectorStore


import re


def _normalize_query(query: str) -> str:
    """Normalizes query for uniform matching: lowercased, collapsed whitespace, stripped punctuation."""
    if not query:
        return ""
    cleaned = re.sub(r"\s+", " ", query.strip().lower())
    cleaned = re.sub(r"^[^\w\s]+", "", cleaned)
    cleaned = re.sub(r"[^\w\s\?]+$", "", cleaned)
    return cleaned.strip()


class TerminologyRetriever:
    """
    High-level query retrieval service for EMP-12:
    Validates terminology queries, computes dense embeddings, executes similarity search,
    and applies canonical-term-aware re-ranking to prioritize complete terminology phrases.
    """

    def __init__(
        self,
        embedder: Optional[TerminologyEmbedder] = None,
        vector_store: Optional[FAISSVectorStore] = None,
        auto_load: bool = True,
    ):
        self.embedder = embedder or TerminologyEmbedder()
        self.vector_store = vector_store or FAISSVectorStore()

        if auto_load and not self.vector_store.is_loaded:
            if FAISS_INDEX_PATH.exists() and VECTOR_METADATA_PATH.exists():
                self.vector_store.load(FAISS_INDEX_PATH, VECTOR_METADATA_PATH)

    def rebuild_index(self, chunks_path: Optional[Path] = None) -> int:
        """
        Rebuilds the FAISS vector index from chunks.json and saves to disk.
        """
        target_chunks = chunks_path or CHUNKS_PATH
        if not target_chunks.exists():
            raise FileNotFoundError(f"Cannot build vector index. Chunks file not found: {target_chunks}")

        count = self.vector_store.build_from_chunks(target_chunks, self.embedder)
        self.vector_store.save(FAISS_INDEX_PATH, VECTOR_METADATA_PATH)
        return count

    def _re_rank_candidates(
        self,
        query: str,
        candidates: List[SearchResult],
        top_k: int,
    ) -> List[SearchResult]:
        """
        Applies explainable, deterministic canonical-term-aware re-ranking.
        Prioritizes complete, specific canonical terminology matches over shorter base terms
        when both are present in the query (e.g., 'Machine Learning Engineer' over 'Machine Learning').
        """
        if not candidates:
            return []

        norm_q = _normalize_query(query)
        matching_terms = set()

        for c in candidates:
            norm_term = _normalize_query(c.term)
            if not norm_term:
                continue
            pattern = r"\b" + re.escape(norm_term) + r"\b"
            if re.search(pattern, norm_q):
                matching_terms.add(norm_term)

        # Identify maximal matches (terms not contained as sub-phrases within another matching term)
        maximal_terms = {
            m for m in matching_terms
            if not any(m != other and m in other for other in matching_terms)
        }

        adjusted_candidates = []
        for c in candidates:
            norm_term = _normalize_query(c.term)
            boost = 0.0
            if norm_term in maximal_terms:
                boost = 0.20
            elif any(norm_term in m for m in maximal_terms):
                boost = 0.05

            new_score = round(min(1.0, c.score + boost), 4)
            adjusted_candidates.append((new_score, c.score, c))

        # Sort descending by adjusted score, then by original dense score
        adjusted_candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)

        final_results: List[SearchResult] = []
        for rank_idx, (adj_score, _, original_result) in enumerate(adjusted_candidates[:top_k], start=1):
            updated_result = original_result.model_copy(
                update={
                    "score": adj_score,
                    "rank": rank_idx,
                }
            )
            final_results.append(updated_result)

        return final_results

    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        category: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Executes semantic retrieval with canonical re-ranking for a user terminology query:
        1. Validates query input
        2. Validates top_k and category parameters
        3. Encodes query into dense unit-vector
        4. Performs cosine similarity search on FAISS across candidate pool
        5. Re-ranks candidates giving controlled priority to maximal canonical matches
        6. Returns ranked list of SearchResult items
        """
        # Query validation
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query string cannot be empty or whitespace.")

        cleaned_query = query.strip()
        if len(cleaned_query) < 2:
            raise ValueError("Query string must be at least 2 characters long.")

        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError(f"top_k must be a positive integer, got: {top_k}")

        if category is not None and category not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Category '{category}' is invalid. Supported categories: {SUPPORTED_CATEGORIES}"
            )

        if not self.vector_store.is_loaded:
            raise RuntimeError(
                "Vector store is not loaded. Build the index first with rebuild_index() or ensure index.faiss exists."
            )

        # Generate query vector
        query_vector = self.embedder.embed_text(cleaned_query)

        # Search expanded candidate pool from vector store
        pool_k = max(top_k * 2, 10)
        raw_candidates = self.vector_store.search(
            query_vector=query_vector,
            top_k=pool_k,
            category=category,
        )

        # Apply canonical re-ranking
        results = self._re_rank_candidates(
            query=cleaned_query,
            candidates=raw_candidates,
            top_k=top_k,
        )
        return results
