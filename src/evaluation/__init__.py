"""
EMP-12 Evaluation Package
Provides tools and modules for reproducible benchmarking, metric calculation,
and validation of the EMP-12 Job & Skill Terminology Simplifier.
"""

from src.evaluation.dataset_loader import (
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
    CategoryMetrics,
    EndToEndCaseResult,
    EvaluationCase,
    EvaluationMetricsSummary,
    GuardrailCaseResult,
    RetrievalCaseResult,
)

__all__ = [
    "EvaluationCase",
    "RetrievalCaseResult",
    "GuardrailCaseResult",
    "AnswerCaseResult",
    "EndToEndCaseResult",
    "CategoryMetrics",
    "EvaluationMetricsSummary",
    "load_evaluation_dataset",
    "validate_evaluation_dataset",
    "filter_by_type",
    "filter_by_category",
    "calculate_recall_at_k",
    "calculate_guardrail_metrics",
    "calculate_answer_metrics",
    "calculate_latency_stats",
    "safe_percentage",
    "TerminologyEvaluator",
    "MockDeterministicGenerator",
]
