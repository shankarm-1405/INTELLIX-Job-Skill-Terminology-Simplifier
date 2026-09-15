"""
EMP-12 Post-Generation Grounding Validation Module
Performs deterministic verification of generated answers against retrieved evidence
to detect unsupported terminology, mismatched categories, and hallucinated citations.
"""

from typing import List, Set, Tuple
from src.config import SUPPORTED_CATEGORIES
from src.generator.models import GeneratedAnswer
from src.guardrails.models import GroundingValidationResult
from src.guardrails.scope import normalize_query
from src.retrieval.models import SearchResult

# Type alias helper
Tuple_Sources = Tuple[bool, List[str]]


def is_term_compatible(gen_term: str, res_term: str) -> bool:
    """
    Checks whether the generated term aligns with the retrieved term
    (case-insensitive, exact match or token containment).
    """
    norm_gen = normalize_query(gen_term)
    norm_res = normalize_query(res_term)

    if not norm_gen or not norm_res:
        return False

    if norm_gen == norm_res:
        return True

    # Token-level containment (e.g. "DevOps Engineer" and "DevOps")
    gen_tokens = set(norm_gen.split())
    res_tokens = set(norm_res.split())
    if gen_tokens and res_tokens:
        overlap = gen_tokens.intersection(res_tokens)
        if len(overlap) == min(len(gen_tokens), len(res_tokens)):
            return True

    return False


def validate_sources_against_evidence(
    generated_sources: List[str],
    retrieved_results: List[SearchResult],
) -> Tuple_Sources:
    """
    Verifies that every citation in generated_sources exists within the retrieved evidence.
    Returns:
        (is_valid: bool, unsupported: List[str])
    """
    # Collect all authoritative sources from retrieved evidence
    valid_evidence_sources = {
        normalize_query(res.source) for res in retrieved_results if res.source and res.source.strip()
    }

    unsupported = []
    for src in generated_sources:
        norm_src = normalize_query(src)
        if not norm_src:
            continue

        # Check exact or partial match with any valid evidence source
        matched = False
        for ev_src in valid_evidence_sources:
            if norm_src == ev_src or norm_src in ev_src or ev_src in norm_src:
                matched = True
                break

        if not matched:
            unsupported.append(src)

    return len(unsupported) == 0, unsupported


def validate_grounding(
    answer: GeneratedAnswer,
    retrieved_results: List[SearchResult],
) -> GroundingValidationResult:
    """
    Validates a Phase 5 GeneratedAnswer against Phase 4 retrieved evidence:
    1. Validates answer non-emptiness
    2. Validates term compatibility
    3. Validates category alignment
    4. Validates source citation provenance
    """
    if answer is None:
        return GroundingValidationResult(
            is_valid=False,
            reason="Generated answer is None.",
            term_matches=False,
            category_matches=False,
            sources_valid=False,
            unsupported_sources=[],
        )

    if not retrieved_results:
        return GroundingValidationResult(
            is_valid=False,
            reason="Cannot validate answer without retrieved evidence.",
            term_matches=False,
            category_matches=False,
            sources_valid=False,
            unsupported_sources=[],
        )

    # 1. Non-emptiness check
    if not answer.simple_meaning or len(answer.simple_meaning.strip()) < 15:
        return GroundingValidationResult(
            is_valid=False,
            reason="Generated answer has an empty or overly short explanation.",
            term_matches=False,
            category_matches=False,
            sources_valid=False,
            unsupported_sources=[],
        )

    # 2. Term compatibility check
    matched_results = []
    for res in retrieved_results:
        if is_term_compatible(answer.term, res.term):
            matched_results.append(res)
            continue
        # Also check related terms
        for rel in res.related_terms:
            if is_term_compatible(answer.term, rel):
                matched_results.append(res)
                break

    term_matches = len(matched_results) > 0
    if not term_matches:
        return GroundingValidationResult(
            is_valid=False,
            reason=(
                f"Generated term '{answer.term}' does not correspond to any term "
                f"present in the retrieved evidence."
            ),
            term_matches=False,
            category_matches=False,
            sources_valid=False,
            unsupported_sources=[],
        )

    # 3. Category alignment check
    allowed_categories = {res.category for res in matched_results if res.category}
    category_matches = answer.category in allowed_categories
    if not category_matches:
        return GroundingValidationResult(
            is_valid=False,
            reason=(
                f"Generated category '{answer.category}' conflicts with evidence category "
                f"{list(allowed_categories)} for term '{answer.term}'."
            ),
            term_matches=True,
            category_matches=False,
            sources_valid=False,
            unsupported_sources=[],
        )

    # 4. Source provenance check
    sources_valid, unsupported_sources = validate_sources_against_evidence(
        generated_sources=answer.sources,
        retrieved_results=retrieved_results,
    )
    if not sources_valid:
        return GroundingValidationResult(
            is_valid=False,
            reason=(
                f"Generated citations contain unsupported sources not present in retrieved evidence: "
                f"{unsupported_sources}"
            ),
            term_matches=True,
            category_matches=True,
            sources_valid=False,
            unsupported_sources=unsupported_sources,
        )

    # All checks passed
    return GroundingValidationResult(
        is_valid=True,
        reason="Answer is fully grounded in retrieved evidence (term, category, and sources verified).",
        term_matches=True,
        category_matches=True,
        sources_valid=True,
        unsupported_sources=[],
    )
