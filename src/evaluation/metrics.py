"""
EMP-12 Evaluation Metrics Module
Deterministic computation of retrieval Recall@K, classification rates,
grounding accuracy, completeness, and latency percentiles.
"""

import statistics
from typing import Any, Dict, List

from src.evaluation.models import (
    AnswerCaseResult,
    GuardrailCaseResult,
    RetrievalCaseResult,
)


def safe_percentage(numerator: float, denominator: float, decimals: int = 2) -> float:
    """
    Computes percentage safely avoiding division-by-zero errors.
    """
    if denominator <= 0:
        return 0.0
    return round((float(numerator) / float(denominator)) * 100.0, decimals)


def calculate_recall_at_k(
    results: List[RetrievalCaseResult],
    k: int = 5,
) -> float:
    """
    Calculates Recall@K across retrieval evaluation results:
    Fraction of supported cases where the expected canonical term appears in top K.
    """
    if not results:
        return 0.0

    hits = 0
    for r in results:
        if k == 1 and r.recall_at_1:
            hits += 1
        elif k == 3 and r.recall_at_3:
            hits += 1
        elif k == 5 and r.recall_at_5:
            hits += 1

    return safe_percentage(hits, len(results))


def calculate_guardrail_metrics(
    results: List[GuardrailCaseResult],
) -> Dict[str, Any]:
    """
    Computes classification summary, acceptance rates, rejection rates, and safety rates.
    """
    supported_results = [r for r in results if r.expected_type == "supported"]
    unknown_results = [r for r in results if r.expected_type == "unknown"]
    oos_results = [r for r in results if r.expected_type == "out_of_scope"]

    # Supported
    sup_allowed = sum(1 for r in supported_results if r.allowed)
    sup_blocked = sum(1 for r in supported_results if not r.allowed)
    supported_acceptance_rate = safe_percentage(sup_allowed, len(supported_results))

    # Unknown
    unk_allowed = sum(1 for r in unknown_results if r.allowed)
    unk_blocked = sum(1 for r in unknown_results if not r.allowed)
    unknown_rejection_rate = safe_percentage(unk_blocked, len(unknown_results))

    # Out of scope
    oos_allowed = sum(1 for r in oos_results if r.allowed)
    oos_blocked = sum(1 for r in oos_results if not r.allowed)
    oos_rejection_rate = safe_percentage(oos_blocked, len(oos_results))

    # Safety
    total_unsupported = len(unknown_results) + len(oos_results)
    unsupported_allowed = unk_allowed + oos_allowed
    unsupported_blocked = unk_blocked + oos_blocked

    safe_fallback_rate = safe_percentage(unsupported_blocked, total_unsupported)
    unsupported_answer_rate = safe_percentage(unsupported_allowed, total_unsupported)

    confusion_matrix = {
        "supported": {"allowed": sup_allowed, "blocked": sup_blocked},
        "unknown": {"allowed": unk_allowed, "blocked": unk_blocked},
        "out_of_scope": {"allowed": oos_allowed, "blocked": oos_blocked},
    }

    return {
        "supported_acceptance_rate": supported_acceptance_rate,
        "unknown_rejection_rate": unknown_rejection_rate,
        "out_of_scope_rejection_rate": oos_rejection_rate,
        "safe_fallback_rate": safe_fallback_rate,
        "unsupported_answer_rate": unsupported_answer_rate,
        "confusion_matrix": confusion_matrix,
    }


def calculate_answer_metrics(
    results: List[AnswerCaseResult],
) -> Dict[str, Any]:
    """
    Computes accuracy for term identification, category classification, source provenance,
    grounding validation, and field completeness availability.
    """
    if not results:
        return {
            "term_identification_accuracy": 0.0,
            "category_accuracy": 0.0,
            "source_provenance_accuracy": 0.0,
            "grounding_acceptance_rate": 0.0,
            "answer_completeness": {},
        }

    total = len(results)
    term_matches = sum(1 for r in results if r.term_matches)
    category_matches = sum(1 for r in results if r.category_matches)
    sources_valid = sum(1 for r in results if r.sources_valid)
    grounding_valid = sum(1 for r in results if r.grounding_valid)

    # Completeness breakdown
    field_names = [
        "term",
        "category",
        "simple_meaning",
        "why_it_matters",
        "job_context",
        "example",
        "related_terms",
        "sources",
    ]
    completeness: Dict[str, float] = {}
    for fn in field_names:
        present_count = sum(1 for r in results if r.completeness_scores.get(fn, False))
        completeness[fn] = safe_percentage(present_count, total)

    return {
        "term_identification_accuracy": safe_percentage(term_matches, total),
        "category_accuracy": safe_percentage(category_matches, total),
        "source_provenance_accuracy": safe_percentage(sources_valid, total),
        "grounding_acceptance_rate": safe_percentage(grounding_valid, total),
        "answer_completeness": completeness,
    }


def calculate_latency_stats(latencies_ms: List[float]) -> Dict[str, float]:
    """
    Computes min, max, mean, and median execution latencies in milliseconds.
    """
    if not latencies_ms:
        return {"min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0}

    return {
        "min": round(min(latencies_ms), 2),
        "max": round(max(latencies_ms), 2),
        "mean": round(statistics.mean(latencies_ms), 2),
        "median": round(statistics.median(latencies_ms), 2),
    }
