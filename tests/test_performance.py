"""
EMP-12 Performance and Caching Test Suite
Benchmarks model loading, vector store caching, knowledge base caching,
warm retrieval latency, and deterministic pipeline execution.
"""

import time
import pytest

from src.ingestion.loader import load_knowledge_base, _KB_RECORDS_CACHE
from src.retrieval.embedder import TerminologyEmbedder, _MODEL_CACHE
from src.retrieval.retriever import TerminologyRetriever
from src.retrieval.vector_store import FAISSVectorStore, _INDEX_CACHE
from src.application.service import TerminologyService
from src.guardrails.controller import GuardrailController


def test_01_embedder_caching():
    """Verify that TerminologyEmbedder reuses the process-level model cache."""
    embedder1 = TerminologyEmbedder()
    _ = embedder1.dimension  # Triggers initial lazy load

    # Second instance should reuse the cached model instance
    t0 = time.perf_counter()
    embedder2 = TerminologyEmbedder()
    _ = embedder2.dimension
    t1 = time.perf_counter()

    elapsed_ms = (t1 - t0) * 1000.0
    assert embedder1.model_name in _MODEL_CACHE
    assert embedder2._model is embedder1._model
    assert elapsed_ms < 50.0  # Warm access must be near-instantaneous


def test_02_vector_store_caching():
    """Verify that FAISSVectorStore reuses cached index and metadata."""
    store1 = FAISSVectorStore()
    store1.load()

    t0 = time.perf_counter()
    store2 = FAISSVectorStore()
    count = store2.load()
    t1 = time.perf_counter()

    elapsed_ms = (t1 - t0) * 1000.0
    assert count == 60
    assert store2.index is store1.index
    assert store2.metadata is store1.metadata
    assert elapsed_ms < 50.0


def test_03_knowledge_base_loader_caching():
    """Verify that load_knowledge_base reuses cached records without disk re-reads."""
    records1 = load_knowledge_base()

    t0 = time.perf_counter()
    records2 = load_knowledge_base()
    t1 = time.perf_counter()

    elapsed_ms = (t1 - t0) * 1000.0
    assert len(records1) == 60
    assert records1 is records2
    assert elapsed_ms < 10.0


def test_04_retrieval_warm_latency():
    """Verify warm retrieval execution time is fast and within bounds."""
    retriever = TerminologyRetriever()
    # Warm-up query
    _ = retriever.search("What is Python?", top_k=5)

    test_queries = [
        "Explain Machine Learning Engineer for beginners",
        "What is an internship?",
        "What is CI/CD?",
        "What does a software developer do?",
    ]

    latencies = []
    for q in test_queries:
        t0 = time.perf_counter()
        results = retriever.search(q, top_k=5)
        t1 = time.perf_counter()
        assert len(results) > 0
        latencies.append((t1 - t0) * 1000.0)

    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 200.0, f"Average warm retrieval latency too high: {avg_latency:.2f} ms"


def test_05_deterministic_pipeline_latency():
    """Verify warm deterministic guardrail processing executes in < 150 ms."""
    controller = GuardrailController()
    # Warm-up
    _ = controller.evaluate_query("What is Python?", [])

    t0 = time.perf_counter()
    res = controller.process_query("What is today's weather?")  # Out of scope safe fallback
    t1 = time.perf_counter()

    latency_ms = (t1 - t0) * 1000.0
    assert res.is_fallback is True
    assert latency_ms < 150.0, f"Scope fallback latency too high: {latency_ms:.2f} ms"


def test_06_memory_footprint_safety():
    """Verify that repeated service instantiations do not duplicate cached resources."""
    initial_model_cache_len = len(_MODEL_CACHE)
    initial_index_cache_len = len(_INDEX_CACHE)

    for _ in range(5):
        s = TerminologyService()
        assert s.retriever is not None

    assert len(_MODEL_CACHE) == initial_model_cache_len
    assert len(_INDEX_CACHE) == initial_index_cache_len
