"""
EMP-12 Knowledge Base Comprehensive Test Suite
Validates schema conformance, data integrity, uniqueness, and structural constraints.
"""

import json
import sys
from pathlib import Path
import pytest

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import KNOWLEDGE_BASE_DIR, SUPPORTED_CATEGORIES
from src.ingestion.schemas import TerminologyRecord

EXPECTED_FILES = {
    "job_roles.json": "Job Roles",
    "technical_skills.json": "Technical Skills",
    "employment_terms.json": "Employment Terms",
    "professional_qualifications.json": "Professional Qualifications",
    "industry_terminology.json": "Industry Terminology",
}


@pytest.fixture(scope="module")
def loaded_kb():
    """Fixture loading all 5 JSON files and parsed records."""
    kb_data = {}
    all_records = []
    for filename, expected_category in EXPECTED_FILES.items():
        filepath = KNOWLEDGE_BASE_DIR / filename
        assert filepath.exists(), f"Missing expected file: {filepath}"
        with open(filepath, "r", encoding="utf-8") as f:
            records = json.load(f)
            kb_data[filename] = records
            all_records.extend(records)
    return {"by_file": kb_data, "all_records": all_records}


def test_01_all_files_exist():
    """Test 8: Verify all five category JSON files exist."""
    for filename in EXPECTED_FILES.keys():
        filepath = KNOWLEDGE_BASE_DIR / filename
        assert filepath.is_file(), f"File does not exist: {filepath}"


def test_02_all_json_files_are_valid(loaded_kb):
    """Test 1: Verify all JSON files are valid and contain lists of dicts."""
    for filename, records in loaded_kb["by_file"].items():
        assert isinstance(records, list), f"{filename} does not contain a JSON list."
        assert len(records) > 0, f"{filename} is empty."
        for item in records:
            assert isinstance(item, dict), f"Item in {filename} is not a dictionary."


def test_03_every_record_follows_pydantic_schema(loaded_kb):
    """Test 2: Verify every record validates successfully against TerminologyRecord schema."""
    for record_data in loaded_kb["all_records"]:
        parsed = TerminologyRecord(**record_data)
        assert parsed.id == record_data["id"]
        assert parsed.term == record_data["term"]


def test_04_all_ids_are_unique(loaded_kb):
    """Test 3: Verify all IDs are globally unique across the entire knowledge base."""
    seen_ids = set()
    duplicates = []
    for record in loaded_kb["all_records"]:
        rec_id = record["id"]
        if rec_id in seen_ids:
            duplicates.append(rec_id)
        seen_ids.add(rec_id)
    assert len(duplicates) == 0, f"Duplicate IDs detected: {duplicates}"


def test_05_all_categories_are_valid_and_match_file(loaded_kb):
    """Test 4: Verify categories match supported set and match their respective file."""
    for filename, expected_category in EXPECTED_FILES.items():
        records = loaded_kb["by_file"][filename]
        for record in records:
            assert record["category"] == expected_category, (
                f"Record '{record['id']}' has category '{record['category']}' "
                f"but is in file '{filename}' expecting '{expected_category}'"
            )
            assert record["category"] in SUPPORTED_CATEGORIES


def test_06_all_difficulty_values_are_valid(loaded_kb):
    """Test 5: Verify all difficulty values are strictly Beginner, Intermediate, or Advanced."""
    allowed_difficulties = {"Beginner", "Intermediate", "Advanced"}
    for record in loaded_kb["all_records"]:
        diff = record.get("difficulty")
        assert diff in allowed_difficulties, f"Record '{record['id']}' has invalid difficulty '{diff}'"


def test_07_required_fields_are_not_empty(loaded_kb):
    """Test 6: Verify required fields contain meaningful, non-whitespace content."""
    string_fields = ["id", "term", "category", "short_definition", "simple_explanation", "job_context", "example", "source"]
    for record in loaded_kb["all_records"]:
        for field in string_fields:
            val = record.get(field, "")
            assert isinstance(val, str), f"Field '{field}' in '{record['id']}' is not a string."
            assert len(val.strip()) >= 3, f"Field '{field}' in '{record['id']}' is too short or empty."


def test_08_no_duplicate_terms(loaded_kb):
    """Test 7: Verify there are no duplicate terms across the dataset."""
    seen_terms = set()
    duplicates = []
    for record in loaded_kb["all_records"]:
        normalized = record["term"].strip().lower()
        if normalized in seen_terms:
            duplicates.append(record["term"])
        seen_terms.add(normalized)
    assert len(duplicates) == 0, f"Duplicate terms detected: {duplicates}"


def test_09_total_record_count_meets_target(loaded_kb):
    """Test 9: Verify total record count is within target range (55-65 records)."""
    total = len(loaded_kb["all_records"])
    assert 55 <= total <= 65, f"Total record count {total} is outside target range 55-65."


def test_10_related_skills_and_terms_valid(loaded_kb):
    """Test 10: Verify related_skills and related_terms are valid non-empty lists of strings."""
    for record in loaded_kb["all_records"]:
        for list_field in ["related_skills", "related_terms"]:
            items = record.get(list_field)
            assert isinstance(items, list), f"Field '{list_field}' in '{record['id']}' is not a list."
            assert len(items) >= 2, f"Field '{list_field}' in '{record['id']}' has fewer than 2 items."
            for item in items:
                assert isinstance(item, str) and len(item.strip()) > 0, (
                    f"Item in '{list_field}' of record '{record['id']}' is not a non-empty string."
                )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
