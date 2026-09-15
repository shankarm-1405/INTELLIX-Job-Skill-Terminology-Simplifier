"""
EMP-12 Knowledge Base Statistics & Integrity Inspector
Analyzes and reports quantitative breakdown and integrity metrics for the knowledge base.
"""

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any

# Ensure project root is accessible
import sys
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import KNOWLEDGE_BASE_DIR, SUPPORTED_CATEGORIES
from src.ingestion.schemas import TerminologyRecord


def load_all_records() -> List[Dict[str, Any]]:
    """Load all JSON records across all category files in KNOWLEDGE_BASE_DIR."""
    all_records = []
    category_files = [
        "job_roles.json",
        "technical_skills.json",
        "employment_terms.json",
        "professional_qualifications.json",
        "industry_terminology.json",
    ]
    for filename in category_files:
        filepath = KNOWLEDGE_BASE_DIR / filename
        if not filepath.exists():
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            records = json.load(f)
            all_records.extend(records)
    return all_records


def generate_statistics_report() -> Dict[str, Any]:
    """Calculate and display statistics and data integrity checks."""
    all_raw_records = load_all_records()
    total_records = len(all_raw_records)

    categories_counter = Counter()
    difficulty_counter = Counter()
    domain_counter = Counter()
    seen_ids = set()
    seen_terms = set()
    duplicate_ids = []
    duplicate_terms = []
    validation_errors = []

    validated_records = []

    for idx, raw in enumerate(all_raw_records):
        rec_id = raw.get("id", f"record_{idx}")
        rec_term = raw.get("term", f"term_{idx}")

        # Duplicate ID check
        if rec_id in seen_ids:
            duplicate_ids.append(rec_id)
        seen_ids.add(rec_id)

        # Duplicate Term check
        normalized_term = rec_term.strip().lower()
        if normalized_term in seen_terms:
            duplicate_terms.append(rec_term)
        seen_terms.add(normalized_term)

        # Pydantic schema validation
        try:
            record = TerminologyRecord(**raw)
            validated_records.append(record)
            categories_counter[record.category] += 1
            difficulty_counter[record.difficulty] += 1
            domain_counter[record.domain] += 1
        except Exception as e:
            validation_errors.append(f"Record '{rec_id}' failed validation: {str(e)}")

    report = {
        "total_records": total_records,
        "valid_records": len(validated_records),
        "invalid_records": len(validation_errors),
        "duplicate_ids": duplicate_ids,
        "duplicate_terms": duplicate_terms,
        "categories": dict(categories_counter),
        "difficulties": dict(difficulty_counter),
        "domains": dict(domain_counter),
        "validation_errors": validation_errors,
    }

    # Print clean formatted report to console
    print("=" * 60)
    print("       EMP-12 Knowledge Base Statistics Report       ")
    print("=" * 60)
    print(f"Total Records: {total_records}")
    print(f"Valid Records: {len(validated_records)}")
    print(f"Invalid Records: {len(validation_errors)}")
    print(f"Duplicate IDs: {len(duplicate_ids)}")
    print(f"Duplicate Terms: {len(duplicate_terms)}")
    print("-" * 60)
    print("Records per Category:")
    for cat in SUPPORTED_CATEGORIES:
        print(f"  - {cat}: {categories_counter.get(cat, 0)}")
    print("-" * 60)
    print("Records per Difficulty:")
    for diff in ["Beginner", "Intermediate", "Advanced"]:
        print(f"  - {diff}: {difficulty_counter.get(diff, 0)}")
    print("-" * 60)
    print("Records per Domain:")
    for dom, count in domain_counter.most_common():
        print(f"  - {dom}: {count}")
    print("=" * 60)

    if validation_errors:
        print("\n[WARNING] Validation Errors Detected:")
        for err in validation_errors:
            print(f"  ! {err}")
    else:
        print("\n[SUCCESS] 100% of records conform to TerminologyRecord schema.")

    return report


if __name__ == "__main__":
    generate_statistics_report()
