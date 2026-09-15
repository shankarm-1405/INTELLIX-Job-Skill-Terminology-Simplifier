"""
EMP-12 Document Processing & Ingestion Test Suite
Validates the end-to-end ingestion pipeline, normalization, chunking, and metadata integrity.
"""

import json
import sys
from pathlib import Path
import pytest

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import KNOWLEDGE_BASE_DIR, PROCESSED_DATA_DIR, SUPPORTED_CATEGORIES
from src.ingestion.loader import KnowledgeBaseLoader, EXPECTED_KB_FILES
from src.ingestion.pipeline import IngestionPipeline
from src.ingestion.schemas import DocumentChunk, ProcessedDocument, TerminologyRecord


@pytest.fixture(scope="module")
def pipeline_output():
    """Executes the ingestion pipeline and returns in-memory results and persisted files."""
    pipeline = IngestionPipeline()
    stats = pipeline.run()

    docs_file = PROCESSED_DATA_DIR / "documents.json"
    chunks_file = PROCESSED_DATA_DIR / "chunks.json"

    with open(docs_file, "r", encoding="utf-8") as f:
        docs_data = json.load(f)

    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)

    return {
        "stats": stats,
        "docs_data": docs_data,
        "chunks_data": chunks_data,
        "docs_file": docs_file,
        "chunks_file": chunks_file,
    }


def test_01_all_five_input_files_can_be_loaded():
    """Test 1: Verify all five category JSON files can be discovered and loaded."""
    loader = KnowledgeBaseLoader()
    discovered = loader.discover_files()
    assert len(discovered) == 5
    for filename in EXPECTED_KB_FILES:
        assert filename in discovered


def test_02_all_input_records_pass_schema():
    """Test 2: Verify all raw knowledge base records pass TerminologyRecord validation."""
    loader = KnowledgeBaseLoader()
    records = loader.load_all()
    assert len(records) == 60
    for record in records:
        assert isinstance(record, TerminologyRecord)
        assert len(record.id.strip()) >= 3
        assert len(record.term.strip()) >= 2


def test_03_expected_number_of_records_preserved(pipeline_output):
    """Test 3: Expected number of source records is preserved (60 records)."""
    assert pipeline_output["stats"]["source_records"] == 60
    assert len(pipeline_output["docs_data"]) == 60
    assert len(pipeline_output["chunks_data"]) >= 60


def test_04_no_duplicate_document_ids(pipeline_output):
    """Test 4: Verify no duplicate document IDs exist in processed documents."""
    doc_ids = [doc["id"] for doc in pipeline_output["docs_data"]]
    assert len(doc_ids) == len(set(doc_ids))
    assert pipeline_output["stats"]["duplicate_document_ids"] == 0


def test_05_processed_documents_are_non_empty(pipeline_output):
    """Test 5: Verify processed documents contain meaningful searchable text and fields."""
    for doc in pipeline_output["docs_data"]:
        parsed = ProcessedDocument(**doc)
        assert len(parsed.searchable_text.strip()) > 100
        assert len(parsed.short_definition.strip()) > 10
        assert len(parsed.simple_explanation.strip()) > 20
        assert len(parsed.job_context.strip()) > 20
        assert len(parsed.example.strip()) > 20


def test_06_chunks_are_non_empty(pipeline_output):
    """Test 6: Verify all generated chunks have non-empty retrieval text."""
    for chunk in pipeline_output["chunks_data"]:
        parsed = DocumentChunk(**chunk)
        assert len(parsed.text.strip()) > 50
        assert parsed.text.startswith("Term: ")


def test_07_no_duplicate_chunk_ids(pipeline_output):
    """Test 7: Verify all chunk IDs are globally unique."""
    chunk_ids = [chunk["chunk_id"] for chunk in pipeline_output["chunks_data"]]
    assert len(chunk_ids) == len(set(chunk_ids))
    assert pipeline_output["stats"]["duplicate_chunk_ids"] == 0


def test_08_every_chunk_maps_to_valid_document(pipeline_output):
    """Test 8: Verify every chunk references a valid, existing document ID."""
    valid_doc_ids = {doc["id"] for doc in pipeline_output["docs_data"]}
    for chunk in pipeline_output["chunks_data"]:
        assert chunk["document_id"] in valid_doc_ids


def test_09_required_metadata_exists(pipeline_output):
    """Test 9: Verify required metadata attributes exist on all chunks."""
    required_keys = [
        "chunk_id", "document_id", "term", "category",
        "difficulty", "domain", "source", "chunk_index",
        "total_chunks", "related_skills", "related_terms", "text"
    ]
    for chunk in pipeline_output["chunks_data"]:
        for key in required_keys:
            assert key in chunk, f"Missing key '{key}' in chunk {chunk.get('chunk_id')}"
            assert chunk[key] is not None


def test_10_category_and_term_information_preserved(pipeline_output):
    """Test 10: Verify category and term match exactly between documents and chunks."""
    doc_map = {doc["id"]: doc for doc in pipeline_output["docs_data"]}
    for chunk in pipeline_output["chunks_data"]:
        parent_doc = doc_map[chunk["document_id"]]
        assert chunk["term"] == parent_doc["term"]
        assert chunk["category"] == parent_doc["category"]
        assert chunk["category"] in SUPPORTED_CATEGORIES


def test_11_source_information_preserved(pipeline_output):
    """Test 11: Verify authoritative source string is preserved without modification."""
    doc_map = {doc["id"]: doc for doc in pipeline_output["docs_data"]}
    for chunk in pipeline_output["chunks_data"]:
        parent_doc = doc_map[chunk["document_id"]]
        assert chunk["source"] == parent_doc["source"]
        assert len(chunk["source"].strip()) > 5


def test_12_chunk_indices_are_valid(pipeline_output):
    """Test 12: Verify 1-based chunk indices are within [1, total_chunks]."""
    for chunk in pipeline_output["chunks_data"]:
        idx = chunk["chunk_index"]
        total = chunk["total_chunks"]
        assert 1 <= idx <= total


def test_13_total_chunk_count_is_consistent(pipeline_output):
    """Test 13: Verify total chunk count equals sum of chunks produced across all documents."""
    total_chunks = len(pipeline_output["chunks_data"])
    assert total_chunks == pipeline_output["stats"]["generated_chunks"]
    assert total_chunks >= 60


def test_14_reproducibility():
    """Verify running ingestion twice yields identical outputs byte-for-byte."""
    pipeline = IngestionPipeline()
    stats1 = pipeline.run()
    stats2 = pipeline.run()

    assert stats1["source_records"] == stats2["source_records"]
    assert stats1["processed_documents"] == stats2["processed_documents"]
    assert stats1["generated_chunks"] == stats2["generated_chunks"]


if __name__ == "__main__":
    pytest.main(["-v", __file__])
