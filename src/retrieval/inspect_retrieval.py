"""
EMP-12 Retrieval Quality Inspection Tool
Runs representative terminology queries and outputs ranked retrieval performance.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.retrieval.retriever import TerminologyRetriever

SAMPLE_QUERIES = [
    "What is Python?",
    "What does a software developer do?",
    "What is machine learning?",
    "What does internship mean?",
    "What is a professional certification?",
    "What is DevOps?",
    "What is cloud computing?",
    "What is an API?",
    "What is a cybersecurity skill?",
    "What is a technical qualification?",
]


def inspect_retrieval():
    """Runs sample queries and prints top-1 and top-3 retrieval evidence."""
    retriever = TerminologyRetriever()

    print("=" * 80)
    print("           EMP-12 Semantic Retrieval Quality Inspection           ")
    print("=" * 80)

    for idx, query in enumerate(SAMPLE_QUERIES, start=1):
        results = retriever.search(query, top_k=3)
        top = results[0]

        print(f"Query {idx:02d}: \"{query}\"")
        print(f"  Top Match:  [{top.term}] (Category: {top.category})")
        print(f"  Score:      {top.score:.4f} (Cosine Similarity)")
        print(f"  Chunk ID:   {top.chunk_id}")
        print(f"  Source:     {top.source[:65]}...")
        print(f"  Runner-ups: {[r.term + ' (' + str(r.score) + ')' for r in results[1:]]}")
        print("-" * 80)


if __name__ == "__main__":
    inspect_retrieval()
