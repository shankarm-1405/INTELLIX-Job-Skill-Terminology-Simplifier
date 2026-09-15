"""
EMP-12 Context Validator Module
Deterministic verification of TerminologyContext instances ensuring source traceability,
category consistency, and absence of invented terminology.
"""

from typing import List, Optional
from src.config import SUPPORTED_CATEGORIES
from src.context.models import ContextValidationResult, TerminologyContext
from src.guardrails.scope import normalize_query
from src.retrieval.models import SearchResult


class ContextValidator:
    """
    Deterministic validator verifying that a TerminologyContext instance adheres
    to structural integrity rules and stays strictly grounded in retrieved evidence.
    """

    @classmethod
    def validate(
        cls,
        context: TerminologyContext,
        retrieved_results: Optional[List[SearchResult]] = None,
    ) -> ContextValidationResult:
        """
        Validates a TerminologyContext instance:
        - Structural non-emptiness checks
        - Category and difficulty validity
        - Source preservation
        - Evidence traceability (if retrieved_results provided)
        """
        missing_fields = []
        invalid_values = []

        if not context:
            return ContextValidationResult(
                is_valid=False,
                reason="Context object is None.",
                missing_fields=["context"],
                invalid_values=[],
            )

        # 1. Structural checks
        if not context.term or len(context.term.strip()) < 2:
            missing_fields.append("term")

        if not context.category or context.category not in SUPPORTED_CATEGORIES:
            invalid_values.append(f"category: {context.category}")

        if not context.difficulty or context.difficulty not in {"Beginner", "Intermediate", "Advanced"}:
            invalid_values.append(f"difficulty: {context.difficulty}")

        if not context.domain or len(context.domain.strip()) < 2:
            missing_fields.append("domain")

        if not context.sources or len(context.sources) == 0:
            missing_fields.append("sources")

        # 2. Evidence traceability checks (if evidence is supplied)
        if retrieved_results:
            # Check canonical term correspondence
            evidence_terms = {normalize_query(r.term) for r in retrieved_results}
            norm_ctx_term = normalize_query(context.term)
            if norm_ctx_term not in evidence_terms:
                invalid_values.append(f"unsupported term: {context.term}")

            # Check category alignment
            matching_results = [r for r in retrieved_results if normalize_query(r.term) == norm_ctx_term]
            if matching_results:
                expected_category = matching_results[0].category
                if context.category != expected_category:
                    invalid_values.append(
                        f"category mismatch: expected '{expected_category}', got '{context.category}'"
                    )

            # Check source traceability
            evidence_sources = {normalize_query(r.source) for r in retrieved_results if r.source}
            for src in context.sources:
                norm_src = normalize_query(src)
                matched = any(norm_src == ev_s or norm_src in ev_s or ev_s in norm_src for ev_s in evidence_sources)
                if not matched:
                    invalid_values.append(f"unsupported source: {src}")

        if missing_fields or invalid_values:
            reason = f"Context validation failed. Missing: {missing_fields}, Invalid: {invalid_values}"
            return ContextValidationResult(
                is_valid=False,
                reason=reason,
                missing_fields=missing_fields,
                invalid_values=invalid_values,
            )

        return ContextValidationResult(
            is_valid=True,
            reason="Context is fully valid and traceable to retrieved evidence.",
            missing_fields=[],
            invalid_values=[],
        )
