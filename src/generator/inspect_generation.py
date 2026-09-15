"""
EMP-12 Generation Quality Inspection Tool
Demonstrates the complete Retriever -> Prompt Builder -> Generator flow across representative queries.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import GEMINI_API_KEY
from src.generator.generator import TerminologyGenerator
from src.retrieval.retriever import TerminologyRetriever

SAMPLE_QUERIES = [
    "What is Python?",
    "What does a software developer do?",
    "What is machine learning?",
    "What does internship mean?",
    "What is a professional certification?",
]


def create_mock_client_response(term: str, category: str, meaning: str, context: str, example: str, source: str):
    """Creates a mock response for offline verification."""
    mock_resp = MagicMock()
    mock_resp.text = f"""{{
        "term": "{term}",
        "category": "{category}",
        "simple_meaning": "{meaning}",
        "job_context": "{context}",
        "example": "{example}",
        "related_terms": ["Skill A", "Skill B"],
        "sources": ["{source}"]
    }}"""
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp
    return mock_client


def inspect_generation():
    """Demonstrates prompt assembly and answer synthesis."""
    retriever = TerminologyRetriever()

    print("=" * 80)
    print("        EMP-12 Grounded Generation Quality Inspection        ")
    print("=" * 80)

    for idx, query in enumerate(SAMPLE_QUERIES, start=1):
        results = retriever.search(query, top_k=3)
        top = results[0]

        # Use mock client if GEMINI_API_KEY is not configured
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
            mock_client = create_mock_client_response(
                term=top.term,
                category=top.category,
                meaning=f"{top.term} is a fundamental concept explained in beginner-friendly terms.",
                context=f"In the workplace, {top.term} is commonly referenced in job descriptions and daily duties.",
                example=f"A junior specialist applies {top.term} to complete a real-world task.",
                source=top.source,
            )
            generator = TerminologyGenerator(client=mock_client)
        else:
            generator = TerminologyGenerator()

        answer = generator.generate(query, results)

        print(f"Query {idx}: \"{query}\"")
        print(f"  Term:           {answer.term} (Category: {answer.category})")
        print(f"  Simple Meaning: {answer.simple_meaning}")
        print(f"  Job Context:    {answer.job_context}")
        print(f"  Example:        {answer.example}")
        print(f"  Related Terms:  {answer.related_terms}")
        print(f"  Sources:        {answer.sources}")
        print("-" * 80)


if __name__ == "__main__":
    inspect_generation()
