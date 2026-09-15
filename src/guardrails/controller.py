"""
EMP-12 Guardrail Controller Module
Coordinates pre-retrieval scope checks, evidence sufficiency evaluation,
and post-generation grounding validation around Phases 4 and 5.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from src.config import SAFE_FALLBACK_MESSAGE
from src.generator.generator import TerminologyGenerator
from src.generator.models import GeneratedAnswer
from src.guardrails.grounding import validate_grounding
from src.guardrails.models import (
    GroundingValidationResult,
    GuardrailDecision,
    SafeFallbackResponse,
)
from src.guardrails.relevance import evaluate_evidence
from src.guardrails.scope import validate_query_scope
from src.retrieval.models import SearchResult
from src.retrieval.retriever import TerminologyRetriever

logger = logging.getLogger("emp12.guardrails")


class GuardrailController:
    """
    Central reliability and hallucination control coordinator for EMP-12:
    - Pre-retrieval query validation & domain scope detection
    - Post-retrieval evidence sufficiency & relevance evaluation
    - Post-generation grounding validation (term, category, sources)
    - Deterministic safe fallback generation
    """

    def __init__(
        self,
        retriever: Optional[TerminologyRetriever] = None,
        generator: Optional[TerminologyGenerator] = None,
        context_builder: Optional[Any] = None,
        threshold: Optional[float] = None,
    ):
        self.retriever = retriever
        self.generator = generator
        self.context_builder = context_builder
        self.threshold = threshold

    def evaluate_query(
        self,
        query: str,
        retrieved_results: List[SearchResult],
    ) -> GuardrailDecision:
        """
        Evaluates query domain scope and retrieval evidence quality:
        1. Checks query structure and scope.
        2. Evaluates retrieved evidence relevance, result counts, and consistency.
        """
        # Step 1: Query scope check
        in_scope, scope_reason = validate_query_scope(query)
        if not in_scope:
            decision = GuardrailDecision(
                allowed=False,
                reason=scope_reason,
                confidence="LOW",
                confidence_score=0.0,
                matched_terms=[],
                top_score=0.0,
                second_score=None,
                score_gap=None,
                category=None,
                is_out_of_scope=True,
                relevant_result_count=0,
            )
            self._log_decision(query, decision)
            return decision

        # Step 2: Evidence sufficiency check
        decision = evaluate_evidence(
            query=query,
            retrieved_results=retrieved_results,
            threshold=self.threshold,
        )
        self._log_decision(query, decision)
        return decision

    def validate_answer(
        self,
        answer: GeneratedAnswer,
        retrieved_results: List[SearchResult],
    ) -> GroundingValidationResult:
        """
        Validates that a generated answer strictly aligns with retrieved evidence.
        """
        validation = validate_grounding(answer, retrieved_results)
        logger.info(
            "Grounding validation: is_valid=%s, reason='%s', term_matches=%s, category_matches=%s, sources_valid=%s",
            validation.is_valid,
            validation.reason,
            validation.term_matches,
            validation.category_matches,
            validation.sources_valid,
        )
        return validation

    def get_safe_fallback(self, query: str, reason: str) -> SafeFallbackResponse:
        """
        Generates a deterministic safe fallback response without invoking an LLM.
        """
        logger.info("Triggered safe fallback for query='%s' (reason='%s')", query, reason)
        return SafeFallbackResponse(
            query=query,
            message=SAFE_FALLBACK_MESSAGE,
            reason=reason,
            is_fallback=True,
            confidence="LOW",
        )

    def process_query(
        self,
        query: str,
        top_k: int = 5,
    ) -> Union[GeneratedAnswer, SafeFallbackResponse]:
        """
        Full end-to-end controlled RAG pipeline:
        Query -> Scope Check -> Retrieval -> Evidence Eval -> Generation -> Grounding Check -> Result
        """
        # 1. Pre-retrieval scope check
        in_scope, scope_reason = validate_query_scope(query)
        if not in_scope:
            return self.get_safe_fallback(query, scope_reason)

        # Ensure retriever is available
        if self.retriever is None:
            self.retriever = TerminologyRetriever()

        # 2. Retrieval
        try:
            results = self.retriever.search(query=query, top_k=top_k)
        except Exception as e:
            return self.get_safe_fallback(query, f"Retrieval failed: {str(e)}")

        # 3. Evidence sufficiency check
        decision = self.evaluate_query(query, results)
        if not decision.allowed:
            return self.get_safe_fallback(query, decision.reason)

        # 4. Contextual Intelligence (Phase 7)
        context = None
        if self.context_builder is not None:
            try:
                context = self.context_builder.build(query=query, retrieved_results=results)
            except Exception as e:
                logger.warning("Context building failed, proceeding with basic retrieval: %s", str(e))

        # Ensure generator is available
        if self.generator is None:
            self.generator = TerminologyGenerator()

        # 5. LLM Generation
        try:
            answer = self.generator.generate(query=query, retrieved_results=results, context=context)
        except Exception as e:
            return self.get_safe_fallback(query, f"Answer generation failed: {str(e)}")

        # 6. Post-generation grounding validation
        validation = self.validate_answer(answer, results)
        if not validation.is_valid:
            return self.get_safe_fallback(query, f"Grounding validation rejected answer: {validation.reason}")

        # 7. Return verified, grounded answer
        return answer

    def _log_decision(self, query: str, decision: GuardrailDecision) -> None:
        """
        Logs structured diagnostics for internal debugging without exposing sensitive data.
        """
        logger.info(
            "Guardrail Decision: query='%s', allowed=%s, confidence=%s(%.4f), top_score=%.4f, gap=%s, category=%s, reason='%s'",
            query,
            decision.allowed,
            decision.confidence,
            decision.confidence_score,
            decision.top_score,
            f"{decision.score_gap:.4f}" if decision.score_gap is not None else "None",
            decision.category,
            decision.reason,
        )
