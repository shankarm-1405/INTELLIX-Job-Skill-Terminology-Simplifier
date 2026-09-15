"""
EMP-12 Setup & Dependency Sanity Test Suite
Validates that all required libraries and project modules import cleanly.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def test_core_dependencies():
    """Verify core third-party dependencies can be imported."""
    import streamlit
    import google.genai
    import sentence_transformers
    import faiss
    import pydantic
    import dotenv
    import numpy
    import sklearn

    assert streamlit.__version__ is not None
    assert sentence_transformers.__version__ is not None
    assert faiss.__version__ is not None
    assert pydantic.__version__ is not None
    assert numpy.__version__ is not None
    assert sklearn.__version__ is not None


def test_project_modules():
    """Verify internal project module structure imports cleanly."""
    import src
    import src.config as config
    import src.query
    import src.ingestion
    import src.retrieval
    import src.generator
    import src.guardrails
    import src.ui

    assert src.__problem_id__ == "EMP-12"
    assert config.SUPPORTED_CATEGORIES is not None
    assert len(config.SUPPORTED_CATEGORIES) == 5
    assert len(config.SUPPORTED_CONTEXTS) >= 5


def test_directory_structure():
    """Verify expected project directories exist."""
    import src.config as config

    assert config.KNOWLEDGE_BASE_DIR.exists()
    assert config.VECTOR_STORE_DIR.exists()
    assert config.DOCS_DIR.exists()


if __name__ == "__main__":
    print("Running EMP-12 setup sanity tests...")
    test_core_dependencies()
    print("[OK] Core dependencies verified.")
    test_project_modules()
    print("[OK] Internal project modules verified.")
    test_directory_structure()
    print("[OK] Directory structure verified.")
    print("\nALL PHASE 1 SANITY CHECKS PASSED.")
