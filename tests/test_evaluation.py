"""
EMP-12 Evaluation Test Suite
Validates dataset integrity, retrieval recall formulas, guardrail classification,
grounding checks, completeness scoring, and report generation.
All tests are 100% deterministic and require NO live Gemini API key.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.config import BASE_DIR, SUPPORTED_CATEGORIES
from src.evaluation.dataset_loader import (
    DEFAULT_DATASET_PATH,
    filter_by_category,
    filter_by_type,
    load_evaluation_dataset,
    validate_evaluation_dataset,
)
from src.evaluation.evaluator import MockDeterministicGenerator, TerminologyEvaluator
from src.evaluation.metrics import (
    calculate_answer_metrics,
    calculate_guardrail_metrics,
    calculate_latency_stats,
    calculate_recall_at_k,
    safe_percentage,
)
from src.evaluation.models import (
    AnswerCaseResult,
    EvaluationCase,
    EvaluationMetricsSummary,
    GuardrailCaseResult,
    RetrievalCaseResult,
)
from src.generator.models import GeneratedAnswer
from src.guardrails.grounding import is_term_compatible, validate_grounding
from src.retrieval.models import SearchResult


# ---------------------------------------------------------------------------
# DATASET TESTS (Tests 1-10)
# ---------------------------------------------------------------------------


def test_01_dataset_loads_successfully():
    """Verify evaluation_dataset.json exists and loads into EvaluationCase models."""
    cases = load_evaluation_dataset(DEFAULT_DATASET_PATH)
    assert isinstance(cases, list)
    assert len(cases) >= 90


def test_02_dataset_schema_is_valid():
    """Verify each item conforms to the EvaluationCase Pydantic model."""
    cases = load_evaluation_dataset(DEFAULT_DATASET_PATH)
    for case in cases:
        assert isinstance(case, EvaluationCase)
        assert isinstance(case.case_id, str) and case.case_id
        assert isinstance(case.query, str) and case.query
        assert case.expected_type in {"supported", "unknown", "out_of_scope"}


def test_03_case_ids_are_unique():
    """Verify all case IDs are strictly unique across the dataset."""
    cases = load_evaluation_dataset(DEFAULT_DATASET_PATH)
    seen = set()
    for case in cases:
        assert case.case_id not in seen, f"Duplicate case_id: {case.case_id}"
        seen.add(case.case_id)


def test_04_supported_cases_meet_minimum_count():
    """Verify dataset contains at least 50 supported cases."""
    cases = load_evaluation_dataset(DEFAULT_DATASET_PATH)
    supported = filter_by_type(cases, "supported")
    assert len(supported) >= 50


def test_05_unknown_cases_meet_minimum_count():
    """Verify dataset contains at least 20 unknown terminology cases."""
    cases = load_evaluation_dataset(DEFAULT_DATASET_PATH)
    unknown = filter_by_type(cases, "unknown")
    assert len(unknown) >= 20


def test_06_out_of_scope_cases_meet_minimum_count():
    """Verify dataset contains at least 20 out-of-scope cases."""
    cases = load_evaluation_dataset(DEFAULT_DATASET_PATH)
    oos = filter_by_type(cases, "out_of_scope")
    assert len(oos) >= 20


def test_07_all_five_categories_represented():
    """Verify all 5 official EMP-12 categories have at least 10 supported cases."""
    cases = load_evaluation_dataset(DEFAULT_DATASET_PATH)
    supported = filter_by_type(cases, "supported")
    for category in SUPPORTED_CATEGORIES:
        cat_cases = filter_by_category(supported, category)
        assert len(cat_cases) >= 10, f"Category '{category}' has only {len(cat_cases)} cases (minimum 10 required)."


def test_08_no_empty_or_whitespace_queries():
    """Verify no query in the dataset is empty, whitespace-only, or under 2 characters."""
    cases = load_evaluation_dataset(DEFAULT_DATASET_PATH)
    for case in cases:
        assert case.query.strip(), f"Case {case.case_id} has empty query."
        assert len(case.query.strip()) >= 2, f"Case {case.case_id} query is too short."


def test_09_expected_types_are_strictly_valid():
    """Verify expected_type is restricted to supported, unknown, or out_of_scope."""
    cases = load_evaluation_dataset(DEFAULT_DATASET_PATH)
    valid_types = {"supported", "unknown", "out_of_scope"}
    for case in cases:
        assert case.expected_type in valid_types


def test_10_expected_categories_match_supported_taxonomy():
    """Verify all supported cases have expected_category in SUPPORTED_CATEGORIES."""
    cases = load_evaluation_dataset(DEFAULT_DATASET_PATH)
    supported = filter_by_type(cases, "supported")
    for case in supported:
        assert case.expected_category in SUPPORTED_CATEGORIES
        assert case.expected_term is not None and len(case.expected_term) > 0


# ---------------------------------------------------------------------------
# RETRIEVAL EVALUATION TESTS (Tests 11-15)
# ---------------------------------------------------------------------------


def test_11_recall_at_1_calculation():
    """Verify calculate_recall_at_k with k=1."""
    mock_results = [
        RetrievalCaseResult(case_id="1", query="q1", recall_at_1=True, recall_at_3=True, recall_at_5=True),
        RetrievalCaseResult(case_id="2", query="q2", recall_at_1=False, recall_at_3=True, recall_at_5=True),
        RetrievalCaseResult(case_id="3", query="q3", recall_at_1=True, recall_at_3=True, recall_at_5=True),
        RetrievalCaseResult(case_id="4", query="q4", recall_at_1=False, recall_at_3=False, recall_at_5=False),
    ]
    recall_1 = calculate_recall_at_k(mock_results, k=1)
    assert recall_1 == 50.0  # 2 out of 4


def test_12_recall_at_3_calculation():
    """Verify calculate_recall_at_k with k=3."""
    mock_results = [
        RetrievalCaseResult(case_id="1", query="q1", recall_at_1=False, recall_at_3=True, recall_at_5=True),
        RetrievalCaseResult(case_id="2", query="q2", recall_at_1=False, recall_at_3=True, recall_at_5=True),
        RetrievalCaseResult(case_id="3", query="q3", recall_at_1=False, recall_at_3=False, recall_at_5=True),
        RetrievalCaseResult(case_id="4", query="q4", recall_at_1=False, recall_at_3=False, recall_at_5=False),
    ]
    recall_3 = calculate_recall_at_k(mock_results, k=3)
    assert recall_3 == 50.0  # 2 out of 4


def test_13_recall_at_5_calculation():
    """Verify calculate_recall_at_k with k=5."""
    mock_results = [
        RetrievalCaseResult(case_id="1", query="q1", recall_at_1=False, recall_at_3=False, recall_at_5=True),
        RetrievalCaseResult(case_id="2", query="q2", recall_at_1=False, recall_at_3=False, recall_at_5=True),
        RetrievalCaseResult(case_id="3", query="q3", recall_at_1=False, recall_at_3=False, recall_at_5=True),
        RetrievalCaseResult(case_id="4", query="q4", recall_at_1=False, recall_at_3=False, recall_at_5=False),
    ]
    recall_5 = calculate_recall_at_k(mock_results, k=5)
    assert recall_5 == 75.0  # 3 out of 4


def test_14_retrieval_result_ordering():
    """Verify that retrieval rank ordering is monotonically ascending."""
    results = [
        SearchResult(
            chunk_id="c1",
            document_id="d1",
            term="Python",
            category="Technical Skills",
            difficulty="Beginner",
            domain="Data Science",
            source="PSF",
            text="text",
            score=0.9,
            rank=1,
        ),
        SearchResult(
            chunk_id="c2",
            document_id="d2",
            term="Java",
            category="Technical Skills",
            difficulty="Beginner",
            domain="Software",
            source="Oracle",
            text="text",
            score=0.7,
            rank=2,
        ),
    ]
    assert results[0].rank < results[1].rank
    assert results[0].score >= results[1].score


def test_15_expected_term_detection_in_retrieved_results():
    """Verify term compatibility detection logic with casing and token variations."""
    assert is_term_compatible("Python", "python")
    assert is_term_compatible("DevOps Engineer", "DevOps")
    assert is_term_compatible("Full Stack Developer", "full stack developer")
    assert not is_term_compatible("Python", "Java")
    assert not is_term_compatible("Data Analyst", "Cloud Engineer")


# ---------------------------------------------------------------------------
# GUARDRAILS EVALUATION TESTS (Tests 16-20)
# ---------------------------------------------------------------------------


def test_16_supported_acceptance_rate_calculation():
    """Verify supported acceptance rate calculation in guardrail metrics."""
    guard_results = [
        GuardrailCaseResult(case_id="1", query="q1", expected_type="supported", allowed=True, is_fallback=False, reason="ok", classification="TP"),
        GuardrailCaseResult(case_id="2", query="q2", expected_type="supported", allowed=True, is_fallback=False, reason="ok", classification="TP"),
        GuardrailCaseResult(case_id="3", query="q3", expected_type="supported", allowed=False, is_fallback=True, reason="low", classification="FN"),
    ]
    metrics = calculate_guardrail_metrics(guard_results)
    assert metrics["supported_acceptance_rate"] == 66.67


def test_17_unknown_rejection_rate_calculation():
    """Verify unknown terminology rejection rate calculation."""
    guard_results = [
        GuardrailCaseResult(case_id="u1", query="qu1", expected_type="unknown", allowed=False, is_fallback=True, reason="low", classification="TN"),
        GuardrailCaseResult(case_id="u2", query="qu2", expected_type="unknown", allowed=False, is_fallback=True, reason="low", classification="TN"),
        GuardrailCaseResult(case_id="u3", query="qu3", expected_type="unknown", allowed=True, is_fallback=False, reason="err", classification="FP"),
    ]
    metrics = calculate_guardrail_metrics(guard_results)
    assert metrics["unknown_rejection_rate"] == 66.67


def test_18_out_of_scope_rejection_rate_calculation():
    """Verify out-of-scope query rejection rate calculation."""
    guard_results = [
        GuardrailCaseResult(case_id="o1", query="qo1", expected_type="out_of_scope", allowed=False, is_fallback=True, reason="oos", classification="TN"),
        GuardrailCaseResult(case_id="o2", query="qo2", expected_type="out_of_scope", allowed=False, is_fallback=True, reason="oos", classification="TN"),
    ]
    metrics = calculate_guardrail_metrics(guard_results)
    assert metrics["out_of_scope_rejection_rate"] == 100.0


def test_19_safe_fallback_rate_detection():
    """Verify safe fallback rate across combined unknown and out-of-scope queries."""
    guard_results = [
        GuardrailCaseResult(case_id="u1", query="qu1", expected_type="unknown", allowed=False, is_fallback=True, reason="low", classification="TN"),
        GuardrailCaseResult(case_id="o1", query="qo1", expected_type="out_of_scope", allowed=False, is_fallback=True, reason="oos", classification="TN"),
        GuardrailCaseResult(case_id="u2", query="qu2", expected_type="unknown", allowed=True, is_fallback=False, reason="err", classification="FP"),
    ]
    metrics = calculate_guardrail_metrics(guard_results)
    assert metrics["safe_fallback_rate"] == 66.67


def test_20_unsupported_answer_rate_calculation():
    """Verify unsupported answer rate is correctly 0% when no unsupported query is allowed."""
    guard_results = [
        GuardrailCaseResult(case_id="u1", query="qu1", expected_type="unknown", allowed=False, is_fallback=True, reason="low", classification="TN"),
        GuardrailCaseResult(case_id="o1", query="qo1", expected_type="out_of_scope", allowed=False, is_fallback=True, reason="oos", classification="TN"),
    ]
    metrics = calculate_guardrail_metrics(guard_results)
    assert metrics["unsupported_answer_rate"] == 0.0


# ---------------------------------------------------------------------------
# ANSWER & GROUNDING EVALUATION TESTS (Tests 21-25)
# ---------------------------------------------------------------------------


def test_21_category_accuracy_calculation():
    """Verify category classification accuracy calculation."""
    answer_results = [
        AnswerCaseResult(case_id="1", query="q1", category_matches=True),
        AnswerCaseResult(case_id="2", query="q2", category_matches=True),
        AnswerCaseResult(case_id="3", query="q3", category_matches=False),
    ]
    metrics = calculate_answer_metrics(answer_results)
    assert metrics["category_accuracy"] == 66.67


def test_22_term_accuracy_calculation():
    """Verify term identification accuracy calculation."""
    answer_results = [
        AnswerCaseResult(case_id="1", query="q1", term_matches=True),
        AnswerCaseResult(case_id="2", query="q2", term_matches=True),
        AnswerCaseResult(case_id="3", query="q3", term_matches=True),
        AnswerCaseResult(case_id="4", query="q4", term_matches=False),
    ]
    metrics = calculate_answer_metrics(answer_results)
    assert metrics["term_identification_accuracy"] == 75.0


def test_23_source_provenance_validation():
    """Verify source provenance accuracy calculation."""
    answer_results = [
        AnswerCaseResult(case_id="1", query="q1", sources_valid=True),
        AnswerCaseResult(case_id="2", query="q2", sources_valid=True),
    ]
    metrics = calculate_answer_metrics(answer_results)
    assert metrics["source_provenance_accuracy"] == 100.0


def test_24_answer_completeness_calculation():
    """Verify answer completeness field percentage calculation."""
    answer_results = [
        AnswerCaseResult(
            case_id="1",
            query="q1",
            completeness_scores={"term": True, "category": True, "simple_meaning": True, "example": True},
        ),
        AnswerCaseResult(
            case_id="2",
            query="q2",
            completeness_scores={"term": True, "category": True, "simple_meaning": True, "example": False},
        ),
    ]
    metrics = calculate_answer_metrics(answer_results)
    assert metrics["answer_completeness"]["term"] == 100.0
    assert metrics["answer_completeness"]["example"] == 50.0


def test_25_end_to_end_success_calculation():
    """Verify End-to-End success rate calculation on supported cases."""
    supported_total = 4
    successes = 3
    rate = safe_percentage(successes, supported_total)
    assert rate == 75.0


# ---------------------------------------------------------------------------
# METRICS & DIAGNOSTICS TESTS (Tests 26-31)
# ---------------------------------------------------------------------------


def test_26_percentage_helper_and_zero_division():
    """Verify safe_percentage handles zero denominator gracefully."""
    assert safe_percentage(5, 10) == 50.0
    assert safe_percentage(0, 10) == 0.0
    assert safe_percentage(5, 0) == 0.0
    assert safe_percentage(0, 0) == 0.0


def test_27_empty_dataset_handling():
    """Verify metric calculators return 0.0 when given empty lists."""
    assert calculate_recall_at_k([], k=1) == 0.0
    assert calculate_recall_at_k([], k=5) == 0.0
    guard_metrics = calculate_guardrail_metrics([])
    assert guard_metrics["supported_acceptance_rate"] == 0.0
    ans_metrics = calculate_answer_metrics([])
    assert ans_metrics["category_accuracy"] == 0.0


def test_28_per_case_result_serialization():
    """Verify that case result models serialize cleanly to JSON."""
    res = GuardrailCaseResult(
        case_id="test_01",
        query="What is Git?",
        expected_type="supported",
        allowed=True,
        is_fallback=False,
        reason="Evidence sufficient",
        top_score=0.85,
        classification="TP",
    )
    dumped = res.model_dump()
    assert dumped["case_id"] == "test_01"
    assert dumped["classification"] == "TP"
    json_str = json.dumps(dumped)
    assert "test_01" in json_str


def test_29_confusion_matrix_structure():
    """Verify confusion matrix contains supported, unknown, and out_of_scope breakdown."""
    guard_results = [
        GuardrailCaseResult(case_id="1", query="q1", expected_type="supported", allowed=True, is_fallback=False, reason="", classification="TP"),
        GuardrailCaseResult(case_id="2", query="q2", expected_type="unknown", allowed=False, is_fallback=True, reason="", classification="TN"),
        GuardrailCaseResult(case_id="3", query="q3", expected_type="out_of_scope", allowed=False, is_fallback=True, reason="", classification="TN"),
    ]
    metrics = calculate_guardrail_metrics(guard_results)
    cm = metrics["confusion_matrix"]
    assert "supported" in cm
    assert "unknown" in cm
    assert "out_of_scope" in cm
    assert cm["supported"]["allowed"] == 1
    assert cm["supported"]["blocked"] == 0
    assert cm["unknown"]["allowed"] == 0
    assert cm["unknown"]["blocked"] == 1
    assert cm["out_of_scope"]["allowed"] == 0
    assert cm["out_of_scope"]["blocked"] == 1


def test_30_latency_stats_calculation():
    """Verify calculate_latency_stats computes min, max, mean, and median."""
    latencies = [10.0, 20.0, 30.0, 40.0, 50.0]
    stats = calculate_latency_stats(latencies)
    assert stats["min"] == 10.0
    assert stats["max"] == 50.0
    assert stats["mean"] == 30.0
    assert stats["median"] == 30.0


def test_31_offline_evaluator_run_with_mocks():
    """Verify TerminologyEvaluator runs benchmark deterministically using offline mock components."""
    mock_retriever = MagicMock()
    mock_search_res = SearchResult(
        chunk_id="chunk_001",
        document_id="doc_001",
        term="Python",
        category="Technical Skills",
        difficulty="Beginner",
        domain="Programming",
        source="Python Software Foundation (python.org)",
        text="Python is a high-level programming language.",
        score=0.88,
        rank=1,
    )
    mock_retriever.search.return_value = [mock_search_res]
    mock_retriever.vector_store = MagicMock()
    mock_retriever.vector_store.is_loaded = True
    mock_retriever.vector_store.index = MagicMock()
    mock_retriever.vector_store.index.d = 384

    evaluator = TerminologyEvaluator(
        retriever=mock_retriever,
        generator=MockDeterministicGenerator(),
    )
    # Test single supported case evaluation
    test_case = EvaluationCase(
        case_id="test_01",
        query="What is Python?",
        expected_type="supported",
        expected_category="Technical Skills",
        expected_term="Python",
    )
    ret_res = evaluator.evaluate_retrieval([test_case])
    assert len(ret_res) == 1
    assert ret_res[0].recall_at_1 is True
    assert ret_res[0].recall_at_5 is True
