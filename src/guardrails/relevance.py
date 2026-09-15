"""
EMP-12 Evidence Quality and Relevance Evaluation Module
Inspects retrieved evidence using multi-signal heuristics to decide whether
Phase 5 generation is permitted.
"""

from collections import Counter
import re
from typing import List, Optional, Tuple

from src.config import (
    MIN_RELEVANT_RESULTS,
    RETRIEVAL_SCORE_THRESHOLD,
    USE_CATEGORY_CONSISTENCY,
    USE_TERM_MATCH_SIGNAL,
)
from src.guardrails.models import GuardrailDecision
from src.guardrails.scope import normalize_query
from src.retrieval.models import SearchResult


def extract_matched_terms(query: str, results: List[SearchResult]) -> List[str]:
    """
    Identifies terminology terms and aliases from retrieved evidence that appear
    in the normalized user query.
    """
    normalized_q = normalize_query(query)
    matched = []

    for res in results:
        res_term = res.term.strip()
        norm_term = normalize_query(res_term)
        if not norm_term:
            continue

        # Exact substring or word boundary match
        pattern = r"\b" + re.escape(norm_term) + r"\b"
        if re.search(pattern, normalized_q):
            if res_term not in matched:
                matched.append(res_term)

        # Also check related terms
        for rel in res.related_terms:
            norm_rel = normalize_query(rel)
            if norm_rel and re.search(r"\b" + re.escape(norm_rel) + r"\b", normalized_q):
                if rel not in matched:
                    matched.append(rel)

    return matched


def evaluate_category_consistency(results: List[SearchResult], top_n: int = 3) -> Optional[str]:
    """
    Checks if a dominant category exists among the top N retrieved results.
    Returns the dominant category name if frequency >= 50%, else None.
    """
    subset = results[:top_n]
    if not subset:
        return None

    categories = [res.category for res in subset if res.category]
    if not categories:
        return None

    counts = Counter(categories)
    most_common, freq = counts.most_common(1)[0]
    if freq >= (len(subset) / 2):
        return most_common
    return None


def calculate_similarity_gap(results: List[SearchResult]) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculates the second-best score and the gap between top_score and second_score.
    Returns:
        (second_score, score_gap)
    """
    if len(results) < 2:
        return None, None

    top_score = results[0].score
    second_score = results[1].score
    gap = round(top_score - second_score, 4)
    return second_score, gap


def classify_confidence(
    top_score: float,
    has_term_match: bool,
    relevant_count: int,
    threshold: float,
) -> Tuple[str, float]:
    """
    Computes an interpretable evidence-strength score (0.0 to 1.0) and qualitative band
    (HIGH, MEDIUM, LOW).

    Note: This measures retrieval evidence strength and candidate relevance,
    NOT mathematical factual certainty or absolute truth probability.
    """
    if top_score < threshold:
        return "LOW", round(max(0.0, top_score), 4)

    # Base confidence is the top cosine similarity score
    strength = top_score

    # Multi-signal adjustment
    if has_term_match:
        strength += 0.05
    if relevant_count >= 2:
        strength += 0.03

    strength = min(1.0, max(0.0, round(strength, 4)))

    if top_score >= 0.65 and (has_term_match or relevant_count >= 2):
        tier = "HIGH"
    elif top_score >= threshold:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    return tier, strength


def evaluate_evidence(
    query: str,
    retrieved_results: List[SearchResult],
    threshold: Optional[float] = None,
) -> GuardrailDecision:
    """
    Executes multi-signal evidence evaluation over retrieved search results:
    1. Checks for empty results
    2. Inspects top similarity score against threshold
    3. Counts relevant results
    4. Extracts matched terminology
    5. Computes category consistency and similarity gap
    6. Produces an explainable GuardrailDecision
    """
    active_threshold = threshold if threshold is not None else RETRIEVAL_SCORE_THRESHOLD

    # Handle missing / empty results
    if not retrieved_results:
        return GuardrailDecision(
            allowed=False,
            reason="No relevant evidence was retrieved from the knowledge base.",
            confidence="LOW",
            confidence_score=0.0,
            matched_terms=[],
            top_score=0.0,
            second_score=None,
            score_gap=None,
            category=None,
            is_out_of_scope=False,
            relevant_result_count=0,
        )

    top_result = retrieved_results[0]
    top_score = round(top_result.score, 4)
    second_score, score_gap = calculate_similarity_gap(retrieved_results)

    # Count results meeting relevance floor (at least 0.45 or 85% of threshold)
    relevance_floor = min(0.45, active_threshold * 0.85)
    relevant_results = [r for r in retrieved_results if r.score >= relevance_floor]
    relevant_count = len(relevant_results)

    # Term matching
    matched_terms = []
    if USE_TERM_MATCH_SIGNAL:
        matched_terms = extract_matched_terms(query, retrieved_results)

    has_term_match = len(matched_terms) > 0

    # Category consistency
    dominant_category = top_result.category
    if USE_CATEGORY_CONSISTENCY:
        consistent_cat = evaluate_category_consistency(retrieved_results)
        if consistent_cat:
            dominant_category = consistent_cat

    # Confidence classification
    confidence_tier, confidence_score = classify_confidence(
        top_score=top_score,
        has_term_match=has_term_match,
        relevant_count=relevant_count,
        threshold=active_threshold,
    )

    # Decision logic
    if top_score < active_threshold:
        return GuardrailDecision(
            allowed=False,
            reason=(
                f"Top retrieval similarity score ({top_score:.4f}) is below the required "
                f"evidence threshold ({active_threshold:.4f}). Evidence is insufficient."
            ),
            confidence=confidence_tier,
            confidence_score=confidence_score,
            matched_terms=matched_terms,
            top_score=top_score,
            second_score=second_score,
            score_gap=score_gap,
            category=dominant_category,
            is_out_of_scope=False,
            relevant_result_count=relevant_count,
        )

    if relevant_count < MIN_RELEVANT_RESULTS:
        return GuardrailDecision(
            allowed=False,
            reason=(
                f"Number of relevant results ({relevant_count}) is below minimum "
                f"requirement ({MIN_RELEVANT_RESULTS})."
            ),
            confidence=confidence_tier,
            confidence_score=confidence_score,
            matched_terms=matched_terms,
            top_score=top_score,
            second_score=second_score,
            score_gap=score_gap,
            category=dominant_category,
            is_out_of_scope=False,
            relevant_result_count=relevant_count,
        )

    # Sufficient evidence
    return GuardrailDecision(
        allowed=True,
        reason=(
            f"Evidence is sufficient (top score: {top_score:.4f} >= {active_threshold:.4f}, "
            f"confidence: {confidence_tier}, relevant items: {relevant_count})."
        ),
        confidence=confidence_tier,
        confidence_score=confidence_score,
        matched_terms=matched_terms,
        top_score=top_score,
        second_score=second_score,
        score_gap=score_gap,
        category=dominant_category,
        is_out_of_scope=False,
        relevant_result_count=relevant_count,
    )
