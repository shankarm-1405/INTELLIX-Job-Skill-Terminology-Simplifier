"""
EMP-12 Evaluation Dataset Loader Module
Loads, validates, and partitions the curated evaluation benchmark dataset.
"""

import json
from pathlib import Path
from typing import List, Optional, Tuple

from src.config import BASE_DIR, SUPPORTED_CATEGORIES
from src.evaluation.models import EvaluationCase

DEFAULT_DATASET_PATH = BASE_DIR / "data" / "evaluation" / "evaluation_dataset.json"


def load_evaluation_dataset(path: Optional[Path] = None) -> List[EvaluationCase]:
    """
    Loads and parses the evaluation dataset JSON file into EvaluationCase models.
    """
    dataset_file = path or DEFAULT_DATASET_PATH
    if not dataset_file.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at: {dataset_file}")

    with open(dataset_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Evaluation dataset root must be a JSON list.")

    cases = [EvaluationCase(**item) for item in data]
    return cases


def validate_evaluation_dataset(cases: List[EvaluationCase]) -> Tuple[bool, List[str]]:
    """
    Validates evaluation dataset integrity according to Phase 10 constraints:
    - Minimum 90 total cases
    - Minimum 50 supported cases
    - Minimum 20 unknown cases
    - Minimum 20 out-of-scope cases
    - All 5 official categories represented with at least 10 cases each
    - Unique case IDs
    - Valid query strings (non-empty)
    - Valid expected_types and expected_categories
    """
    errors: List[str] = []

    if len(cases) < 90:
        errors.append(f"Total evaluation cases ({len(cases)}) is below minimum requirement of 90.")

    seen_ids = set()
    supported_count = 0
    unknown_count = 0
    oos_count = 0
    category_counts = {cat: 0 for cat in SUPPORTED_CATEGORIES}

    valid_types = {"supported", "unknown", "out_of_scope"}

    for idx, case in enumerate(cases):
        # ID check
        if not case.case_id or not case.case_id.strip():
            errors.append(f"Case at index {idx} has an empty case_id.")
        elif case.case_id in seen_ids:
            errors.append(f"Duplicate case_id found: '{case.case_id}'")
        else:
            seen_ids.add(case.case_id)

        # Query check
        if not case.query or not case.query.strip():
            errors.append(f"Case '{case.case_id}' has an empty or whitespace query.")

        # Type check
        if case.expected_type not in valid_types:
            errors.append(
                f"Case '{case.case_id}' has invalid expected_type '{case.expected_type}'. Must be one of {valid_types}."
            )

        if case.expected_type == "supported":
            supported_count += 1
            if not case.expected_term:
                errors.append(f"Supported case '{case.case_id}' is missing expected_term.")
            if not case.expected_category:
                errors.append(f"Supported case '{case.case_id}' is missing expected_category.")
            elif case.expected_category not in SUPPORTED_CATEGORIES:
                errors.append(
                    f"Supported case '{case.case_id}' has unknown category '{case.expected_category}'."
                )
            else:
                category_counts[case.expected_category] += 1

        elif case.expected_type == "unknown":
            unknown_count += 1

        elif case.expected_type == "out_of_scope":
            oos_count += 1

    # Count checks
    if supported_count < 50:
        errors.append(f"Supported cases count ({supported_count}) is below minimum of 50.")

    if unknown_count < 20:
        errors.append(f"Unknown terminology cases count ({unknown_count}) is below minimum of 20.")

    if oos_count < 20:
        errors.append(f"Out-of-scope cases count ({oos_count}) is below minimum of 20.")

    # Category checks
    for cat, count in category_counts.items():
        if count < 10:
            errors.append(f"Category '{cat}' has {count} cases, below minimum requirement of 10.")

    return (len(errors) == 0, errors)


def filter_by_type(cases: List[EvaluationCase], expected_type: str) -> List[EvaluationCase]:
    """Filters evaluation cases by expected type ('supported', 'unknown', 'out_of_scope')."""
    return [c for c in cases if c.expected_type == expected_type]


def filter_by_category(cases: List[EvaluationCase], category: str) -> List[EvaluationCase]:
    """Filters supported evaluation cases by taxonomy category."""
    return [c for c in cases if c.expected_category == category]
