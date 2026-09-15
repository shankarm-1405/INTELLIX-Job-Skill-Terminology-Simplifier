"""
EMP-12 Deployment Test Suite (Phase 12)
Validates deployment configuration artifacts, Dockerfile structure, .dockerignore safety,
Streamlit settings, query length bounds, configuration failure containment, and stateless behavior.
"""

import sys
from pathlib import Path
import tomllib
import pytest

from src.config import (
    BASE_DIR,
    FAISS_INDEX_PATH,
    MAX_QUERY_LENGTH,
    VECTOR_METADATA_PATH,
)
from src.application.service import TerminologyService
from src.generator.generator import TerminologyGenerator
from src.retrieval.embedder import _MODEL_CACHE
from src.retrieval.vector_store import _INDEX_CACHE
from src.ui.components import is_valid_query_input


def test_01_dockerfile_exists_and_has_valid_instructions():
    """Verifies Dockerfile exists and contains required deployment instructions."""
    dockerfile = BASE_DIR / "Dockerfile"
    assert dockerfile.exists(), "Dockerfile must exist in project root"
    content = dockerfile.read_text(encoding="utf-8")
    assert "FROM python:" in content
    assert "WORKDIR /app" in content
    assert "COPY requirements.txt" in content
    assert "EXPOSE 8501" in content
    assert "CMD" in content or "ENTRYPOINT" in content


def test_02_dockerfile_contains_no_secrets():
    """Verifies Dockerfile contains no baked-in API keys or secrets."""
    dockerfile = BASE_DIR / "Dockerfile"
    content = dockerfile.read_text(encoding="utf-8")
    assert "AIza" not in content
    assert "GEMINI_API_KEY=" not in content or "your_" in content


def test_03_dockerignore_protects_sensitive_files():
    """Verifies .dockerignore excludes credentials, caches, and test artifacts."""
    dockerignore = BASE_DIR / ".dockerignore"
    assert dockerignore.exists(), ".dockerignore must exist in project root"
    content = dockerignore.read_text(encoding="utf-8")
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
    assert any(".env" in l for l in lines)
    assert any("__pycache__" in l for l in lines)
    assert any(".pytest_cache" in l for l in lines)


def test_04_streamlit_config_exists_and_safe():
    """Verifies .streamlit/config.toml exists and specifies secure production defaults."""
    config_path = BASE_DIR / ".streamlit" / "config.toml"
    assert config_path.exists(), ".streamlit/config.toml must exist"
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    assert config.get("server", {}).get("headless") is True
    assert config.get("server", {}).get("port") == 8501
    assert config.get("server", {}).get("enableCORS") is False


def test_05_required_deployment_artifacts_exist():
    """Verifies that all files required to run the application exist."""
    assert (BASE_DIR / "app.py").exists(), "app.py must exist"
    assert (BASE_DIR / "requirements.txt").exists(), "requirements.txt must exist"
    assert FAISS_INDEX_PATH.exists(), f"FAISS index missing at {FAISS_INDEX_PATH}"
    assert VECTOR_METADATA_PATH.exists(), f"Vector metadata missing at {VECTOR_METADATA_PATH}"


def test_06_query_length_limit_enforced_in_service():
    """Verifies that queries exceeding MAX_QUERY_LENGTH are rejected safely."""
    service = TerminologyService()
    oversized_query = "What is " + "A" * (MAX_QUERY_LENGTH + 20)
    response = service.explain_term(oversized_query)
    assert response.success is False
    assert "too long" in response.error_message.lower()
    assert str(MAX_QUERY_LENGTH) in response.error_message


def test_07_query_length_limit_enforced_in_ui_component():
    """Verifies UI input validation rejects oversized queries before processing."""
    valid_query = "a" * (MAX_QUERY_LENGTH - 5)
    is_valid, msg = is_valid_query_input(valid_query)
    assert is_valid is True

    oversized_query = "a" * (MAX_QUERY_LENGTH + 5)
    is_valid_over, msg_over = is_valid_query_input(oversized_query)
    assert is_valid_over is False
    assert "too long" in msg_over.lower()


def test_08_application_service_handles_missing_api_key_gracefully():
    """Verifies that unconfigured Gemini client produces a clean configuration error without uncaught exceptions."""
    # TerminologyGenerator with api_key="" and client=None
    unconfigured_gen = TerminologyGenerator(api_key="", client=None)
    service = TerminologyService(generator=unconfigured_gen)

    # Calling a supported query that reaches generator
    response = service.explain_term("Python")
    assert response.success is False
    assert response.is_configuration_error is True
    assert "GEMINI_API_KEY" in response.error_message or "configuration" in response.error_message.lower()


def test_09_caching_preserved_in_deployment():
    """Verifies in-memory caching for model and vector index remains functional."""
    service = TerminologyService()
    # Trigger retrieval to ensure cache is populated
    res = service.retriever.search("Python", top_k=2)
    assert len(res) > 0

    # Caches must hold entries
    assert len(_MODEL_CACHE) > 0
    assert len(_INDEX_CACHE) > 0


def test_10_statelessness_preserved():
    """Verifies system does not retain query state between separate requests."""
    service = TerminologyService()
    resp1 = service.explain_term("Python")
    resp2 = service.explain_term("Quantum Entanglement")

    assert resp1.query == "Python"
    assert resp2.query == "Quantum Entanglement"
    # Fallback should not mention Python
    if resp2.is_fallback:
        assert resp2.fallback.query == "Quantum Entanglement"


def test_11_python_environment_compatibility():
    """Verifies Python version and core library presence."""
    assert sys.version_info >= (3, 10), "Requires Python 3.10+"
    import streamlit
    import pydantic
    import sentence_transformers
    import faiss
    assert streamlit is not None
    assert pydantic is not None
    assert sentence_transformers is not None
    assert faiss is not None
