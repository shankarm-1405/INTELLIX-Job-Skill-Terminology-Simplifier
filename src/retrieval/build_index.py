"""
EMP-12 Vector Index Builder CLI
Builds and serializes the local FAISS index from data/processed/chunks.json.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import CHUNKS_PATH, FAISS_INDEX_PATH, VECTOR_METADATA_PATH
from src.retrieval.retriever import TerminologyRetriever


def build_and_save_index():
    """Builds and serializes the FAISS index and metadata."""
    print("=" * 60)
    print("         EMP-12 Vector Index Building Service        ")
    print("=" * 60)
    print(f"Reading chunks from: {CHUNKS_PATH}")

    retriever = TerminologyRetriever(auto_load=False)
    indexed_count = retriever.rebuild_index(CHUNKS_PATH)

    print(f"[SUCCESS] Successfully indexed {indexed_count} vectors.")
    print(f"FAISS index saved to:    {FAISS_INDEX_PATH}")
    print(f"Metadata saved to:       {VECTOR_METADATA_PATH}")
    print("=" * 60)
    return indexed_count


if __name__ == "__main__":
    build_and_save_index()
