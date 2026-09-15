"""
EMP-12 Knowledge Base Loader
Safely discovers, loads, and validates all five primary knowledge base files.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from src.config import KNOWLEDGE_BASE_DIR, SUPPORTED_CATEGORIES
from src.ingestion.schemas import TerminologyRecord

# Mapping of canonical filename to expected category
EXPECTED_KB_FILES: Dict[str, str] = {
    "job_roles.json": "Job Roles",
    "technical_skills.json": "Technical Skills",
    "employment_terms.json": "Employment Terms",
    "professional_qualifications.json": "Professional Qualifications",
    "industry_terminology.json": "Industry Terminology",
}


# Module-level knowledge base cache with mtime invalidation
_KB_RECORDS_CACHE = {}


class KnowledgeBaseLoader:
    """
    Loader responsible for reading, validating, and returning all records
    from the curated Phase 2 knowledge base.
    Uses in-memory caching with mtime checking to eliminate redundant disk reads.
    """

    def __init__(self, kb_dir: Optional[Path] = None):
        self.kb_dir = kb_dir or KNOWLEDGE_BASE_DIR

    def discover_files(self) -> Dict[str, Path]:
        """
        Verify that all five required category JSON files exist.
        Raises FileNotFoundError if any file is missing.
        """
        found_files = {}
        missing_files = []
        for filename in EXPECTED_KB_FILES.keys():
            filepath = self.kb_dir / filename
            if not filepath.exists() or not filepath.is_file():
                missing_files.append(filename)
            else:
                found_files[filename] = filepath

        if missing_files:
            raise FileNotFoundError(
                f"Knowledge Base loading failed. Missing required files in {self.kb_dir}: {missing_files}"
            )
        return found_files

    def load_file(self, filename: str, filepath: Path) -> List[TerminologyRecord]:
        """
        Load and validate records from a single category JSON file.
        Enforces JSON validity, non-emptiness, and Pydantic schema conformance.
        """
        expected_category = EXPECTED_KB_FILES.get(filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Malformed JSON in file '{filename}': {str(e)}") from e
        except Exception as e:
            raise IOError(f"Unable to read file '{filename}': {str(e)}") from e

        if not isinstance(data, list):
            raise ValueError(f"File '{filename}' must contain a JSON array of records.")

        if len(data) == 0:
            raise ValueError(f"File '{filename}' is empty; at least one record is required.")

        validated_records: List[TerminologyRecord] = []
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Item at index {idx} in '{filename}' is not an object/dict.")

            try:
                record = TerminologyRecord(**item)
            except Exception as e:
                rec_id = item.get("id", f"index_{idx}")
                raise ValueError(
                    f"Validation error in '{filename}' for record '{rec_id}': {str(e)}"
                ) from e

            if expected_category and record.category != expected_category:
                raise ValueError(
                    f"Category mismatch in '{filename}' for record '{record.id}': "
                    f"Expected '{expected_category}', found '{record.category}'."
                )

            validated_records.append(record)

        return validated_records

    def load_all(self) -> List[TerminologyRecord]:
        """
        Load all records across all five categories.
        Performs global uniqueness validation across all IDs.
        Reuses cached records if underlying files have not been modified.
        """
        global _KB_RECORDS_CACHE
        files = self.discover_files()
        cache_key = str(self.kb_dir.resolve())
        current_mtimes = tuple(files[fn].stat().st_mtime for fn in sorted(files.keys()))

        if cache_key in _KB_RECORDS_CACHE:
            cached_records, cached_mtimes = _KB_RECORDS_CACHE[cache_key]
            if cached_mtimes == current_mtimes:
                return cached_records

        all_records: List[TerminologyRecord] = []
        seen_ids = set()

        for filename, filepath in files.items():
            records = self.load_file(filename, filepath)
            for record in records:
                if record.id in seen_ids:
                    raise ValueError(
                        f"Duplicate record ID '{record.id}' detected in '{filename}'."
                    )
                seen_ids.add(record.id)
                all_records.append(record)

        _KB_RECORDS_CACHE[cache_key] = (all_records, current_mtimes)
        return all_records


def load_knowledge_base(kb_dir: Optional[Path] = None) -> List[TerminologyRecord]:
    """Convenience helper function to load and validate all KB records."""
    loader = KnowledgeBaseLoader(kb_dir=kb_dir)
    return loader.load_all()
