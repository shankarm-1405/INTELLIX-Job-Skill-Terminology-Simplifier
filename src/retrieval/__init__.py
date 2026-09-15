"""
EMP-12 Retrieval Engine Package
Provides embedding generation, FAISS indexing, and semantic terminology retrieval.
"""

from src.retrieval.embedder import TerminologyEmbedder
from src.retrieval.models import SearchResult
from src.retrieval.retriever import TerminologyRetriever
from src.retrieval.vector_store import FAISSVectorStore

__all__ = [
    "TerminologyEmbedder",
    "FAISSVectorStore",
    "TerminologyRetriever",
    "SearchResult",
]
