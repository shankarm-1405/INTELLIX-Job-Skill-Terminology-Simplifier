"""
EMP-12 Retrieval System Comprehensive Test Suite
Validates embedding generation, FAISS indexing, similarity metrics, metadata mapping,
ranking, category-aware queries, and error boundaries.
"""

import json
import sys
import tempfile
from pathlib import Path
import pytest
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    CHUNKS_PATH,
    FAISS_INDEX_PATH,
    SUPPORTED_CATEGORIES,
    VECTOR_METADATA_PATH,
)
from src.retrieval.embedder import TerminologyEmbedder
from src.retrieval.models import SearchResult
from src.retrieval.retriever import TerminologyRetriever
from src.retrieval.vector_store import FAISSVectorStore


@pytest.fixture(scope="module")
def shared_embedder():
    """Shared TerminologyEmbedder instance to avoid redundant model reloads."""
    return TerminologyEmbedder()


@pytest.fixture(scope="module")
def active_retriever(shared_embedder):
    """Shared TerminologyRetriever with loaded FAISS index."""
    retriever = TerminologyRetriever(embedder=shared_embedder, auto_load=True)
    if not retriever.vector_store.is_loaded:
        retriever.rebuild_index()
    return retriever


def test_01_embedding_model_loads_successfully(shared_embedder):
    """Test 1: Embedding model loads and reports expected 384 dimensions."""
    assert shared_embedder.dimension == 384


def test_02_all_60_chunks_can_be_embedded(shared_embedder):
    """Test 2: Embeds all 60 text strings from chunks.json."""
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    assert len(chunks) == 60
    texts = [c["text"] for c in chunks]
    vectors = shared_embedder.embed_texts(texts)
    assert vectors.shape == (60, 384)


def test_03_embedding_dimensions_are_consistent(shared_embedder):
    """Test 3: Single query embedding has identical dimension to chunk embeddings."""
    q_vec = shared_embedder.embed_text("software developer")
    assert q_vec.ndim == 1
    assert q_vec.shape[0] == shared_embedder.dimension
    # Verify L2 normalization
    norm = np.linalg.norm(q_vec)
    assert pytest.approx(norm, rel=1e-3) == 1.0


def test_04_vector_count_equals_chunk_count(active_retriever):
    """Test 4: Vector index contains exactly 60 vectors matching the 60 chunks."""
    assert active_retriever.vector_store.total_vectors == 60
    assert len(active_retriever.vector_store.metadata) == 60


def test_05_faiss_index_can_be_saved(active_retriever):
    """Test 5: FAISS index and metadata can be saved to disk."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_idx = Path(tmp_dir) / "test.faiss"
        tmp_meta = Path(tmp_dir) / "test_meta.json"
        active_retriever.vector_store.save(tmp_idx, tmp_meta)
        assert tmp_idx.exists()
        assert tmp_meta.exists()
        assert tmp_idx.stat().st_size > 1000
        assert tmp_meta.stat().st_size > 1000


def test_06_faiss_index_can_be_loaded(shared_embedder):
    """Test 6: Persisted FAISS index can be reloaded and queried."""
    store = FAISSVectorStore()
    count = store.load(FAISS_INDEX_PATH, VECTOR_METADATA_PATH)
    assert count == 60
    assert store.is_loaded is True
    assert store.total_vectors == 60


def test_07_every_indexed_vector_maps_to_valid_chunk_id(active_retriever):
    """Test 7: Every metadata entry has a non-empty chunk_id and valid document_id."""
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    expected_ids = {c["chunk_id"] for c in chunks}

    for idx, meta in enumerate(active_retriever.vector_store.metadata):
        cid = meta["chunk_id"]
        assert cid in expected_ids
        assert meta["document_id"] in cid


def test_08_duplicate_chunk_ids_are_rejected(shared_embedder):
    """Test 8: VectorStore raises ValueError if duplicate chunk IDs are present."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        bad_chunks = Path(tmp_dir) / "bad_chunks.json"
        data = [
            {"chunk_id": "dup_001", "text": "sample text one"},
            {"chunk_id": "dup_001", "text": "sample text two"},
        ]
        with open(bad_chunks, "w", encoding="utf-8") as f:
            json.dump(data, f)

        store = FAISSVectorStore()
        with pytest.raises(ValueError, match="Duplicate chunk ID"):
            store.build_from_chunks(bad_chunks, shared_embedder)


def test_09_normal_terminology_query_returns_results(active_retriever):
    """Test 9: Normal terminology query returns valid ranked SearchResult items."""
    results = active_retriever.search("What is Python?", top_k=3)
    assert len(results) == 3
    for r in results:
        assert isinstance(r, SearchResult)
        assert r.score > 0.0
    assert results[0].term == "Python"


def test_10_job_role_query_returns_relevant_terminology(active_retriever):
    """Test 10: Query for software developer retrieves role_software_developer top."""
    results = active_retriever.search("What does a software developer do?", top_k=3)
    assert results[0].term == "Software Developer"
    assert results[0].category == "Job Roles"


def test_11_technical_skill_query_returns_relevant_terminology(active_retriever):
    """Test 11: Query for machine learning retrieves Machine Learning as top result."""
    results = active_retriever.search("What is machine learning?", top_k=3)
    assert results[0].term == "Machine Learning"
    assert results[0].category == "Technical Skills"


def test_12_employment_term_query_returns_relevant_terminology(active_retriever):
    """Test 12: Query for internship retrieves Internship as top result."""
    results = active_retriever.search("What does internship mean in a job offer?", top_k=3)
    assert results[0].term == "Internship"
    assert results[0].category == "Employment Terms"


def test_13_professional_qualification_query_returns_relevant_terminology(active_retriever):
    """Test 13: Query for professional certification retrieves certification results."""
    results = active_retriever.search("What is a professional certification?", top_k=3)
    top_terms = [r.term for r in results]
    assert "Professional Certification" in top_terms
    assert results[0].category == "Professional Qualifications"


def test_14_industry_terminology_query_returns_relevant_terminology(active_retriever):
    """Test 14: Query for API retrieves API and REST API in top results."""
    results = active_retriever.search("What is an API?", top_k=3)
    assert results[0].term == "API"
    assert results[0].category == "Industry Terminology"


def test_15_results_are_sorted_by_descending_similarity_score(active_retriever):
    """Test 15: Search results are strictly sorted by score descending."""
    results = active_retriever.search("cloud computing deployment servers", top_k=5)
    for i in range(len(results) - 1):
        assert results[i].score >= results[i + 1].score
        assert results[i].rank == i + 1


def test_16_top_k_works_correctly(active_retriever):
    """Test 16: Retriever respects different top_k values (1, 3, 5, 10)."""
    for k in [1, 3, 5, 10]:
        results = active_retriever.search("Python programming database", top_k=k)
        assert len(results) == k


def test_17_empty_query_is_handled_correctly(active_retriever):
    """Test 17: Empty or whitespace query raises clear ValueError."""
    with pytest.raises(ValueError, match="empty or whitespace"):
        active_retriever.search("")

    with pytest.raises(ValueError, match="empty or whitespace"):
        active_retriever.search("   ")

    with pytest.raises(ValueError, match="at least 2 characters"):
        active_retriever.search("a")


def test_18_invalid_category_is_handled_correctly(active_retriever):
    """Test 18: Non-existent category filter raises clear ValueError."""
    with pytest.raises(ValueError, match="Category .* is invalid"):
        active_retriever.search("Python", category="NonExistentCategory")

    # Valid category filtering works
    filtered = active_retriever.search("Python", top_k=3, category="Technical Skills")
    for r in filtered:
        assert r.category == "Technical Skills"


def test_19_retrieved_metadata_matches_original_chunk(active_retriever):
    """Test 19: Retrieved SearchResult fields match chunks.json verbatim."""
    results = active_retriever.search("What is Docker?", top_k=1)
    top = results[0]

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    matching_chunk = next(c for c in chunks if c["chunk_id"] == top.chunk_id)

    assert top.term == matching_chunk["term"]
    assert top.category == matching_chunk["category"]
    assert top.difficulty == matching_chunk["difficulty"]
    assert top.domain == matching_chunk["domain"]
    assert top.source == matching_chunk["source"]
    assert top.text == matching_chunk["text"]
    assert top.related_skills == matching_chunk["related_skills"]
    assert top.related_terms == matching_chunk["related_terms"]


def test_20_index_can_be_rebuilt_successfully(active_retriever):
    """Test 20: Index can be rebuilt deterministically without error."""
    count = active_retriever.rebuild_index()
    assert count == 60
    assert active_retriever.vector_store.total_vectors == 60


if __name__ == "__main__":
    pytest.main(["-v", __file__])
