"""
EMP-12 Guardrails & Hallucination Control Module
Responsible for query scope validation, evidence sufficiency evaluation,
post-generation grounding validation, and deterministic safe fallbacks.
"""

from src.guardrails.controller import GuardrailController
from src.guardrails.grounding import validate_grounding
from src.guardrails.models import (
    GroundingValidationResult,
    GuardrailDecision,
    SafeFallbackResponse,
)
from src.guardrails.relevance import evaluate_evidence
from src.guardrails.scope import validate_query_scope

__all__ = [
    "GuardrailController",
    "GuardrailDecision",
    "GroundingValidationResult",
    "SafeFallbackResponse",
    "evaluate_evidence",
    "validate_grounding",
    "validate_query_scope",
]
