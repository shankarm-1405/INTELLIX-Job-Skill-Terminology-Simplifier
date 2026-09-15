"""
EMP-12 Evaluation Runner and Benchmark Evaluator Module
Executes deterministic retrieval, guardrail, grounding, and end-to-end evaluations
across the 92-case benchmark dataset.
"""

import sys
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    BASE_DIR,
    CHUNKS_PATH,
    FAISS_INDEX_PATH,
    KNOWLEDGE_BASE_DIR,
    SUPPORTED_CATEGORIES,
    VECTOR_METADATA_PATH,
)
from src.context.context_builder import ContextBuilder
from src.evaluation.dataset_loader import (
    DEFAULT_DATASET_PATH,
    filter_by_category,
    filter_by_type,
    load_evaluation_dataset,
    validate_evaluation_dataset,
)
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
from src.generator.generator import TerminologyGenerator
from src.generator.models import GeneratedAnswer
from src.guardrails.controller import GuardrailController
from src.guardrails.grounding import is_term_compatible, validate_grounding
from src.guardrails.models import SafeFallbackResponse
from src.guardrails.scope import normalize_query, validate_query_scope
from src.retrieval.models import SearchResult
from src.retrieval.retriever import TerminologyRetriever

logger = logging.getLogger("emp12.evaluation")

DEFAULT_RESULTS_PATH = BASE_DIR / "data" / "evaluation" / "results.json"


class MockDeterministicGenerator:
    """
    Deterministic offline generator creating structured explanations directly
    from retrieved evidence without making live external API calls.
    Ensures offline reproducibility for automated evaluation and CI testing.
    """

    def generate(
        self,
        query: str,
        retrieved_results: List[SearchResult],
        context: Optional[Any] = None,
    ) -> GeneratedAnswer:
        if not retrieved_results:
            raise ValueError("No retrieved evidence provided for generation.")

        top = retrieved_results[0]
        return GeneratedAnswer(
            query=query,
            term=top.term,
            category=top.category,
            simple_meaning=f"{top.term} is a key concept in {top.domain}.",
            why_it_matters=f"Understanding {top.term} is valuable for employment and technical proficiency.",
            job_context=f"{top.term} is frequently required in modern workplace settings.",
            example=f"A practical workplace application of {top.term}.",
            related_terms=top.related_terms[:3] if top.related_terms else [],
            sources=[top.source] if top.source else ["EMP-12 Knowledge Base"],
        )


class TerminologyEvaluator:
    """
    Comprehensive evaluation engine for EMP-12:
    - Measures dense FAISS retrieval performance (Recall@1, 3, 5)
    - Measures guardrail scope checks and evidence thresholds
    - Evaluates post-generation grounding and source provenance
    - Records detailed latency distributions and resource footprints
    - Exports machine-readable benchmark results
    """

    def __init__(
        self,
        retriever: Optional[TerminologyRetriever] = None,
        generator: Optional[Any] = None,
        controller: Optional[GuardrailController] = None,
        dataset_path: Optional[Path] = None,
        results_path: Optional[Path] = None,
    ):
        self.dataset_path = dataset_path or DEFAULT_DATASET_PATH
        self.results_path = results_path or DEFAULT_RESULTS_PATH
        
        self.retriever = retriever or TerminologyRetriever()
        self.generator = generator or MockDeterministicGenerator()
        self.context_builder = ContextBuilder()
        self.controller = controller or GuardrailController(
            retriever=self.retriever,
            generator=self.generator,
            context_builder=self.context_builder,
        )

    def _term_matches(self, expected_term: Optional[str], retrieved_term: str) -> bool:
        """Determines if a retrieved term matches the expected canonical term."""
        if not expected_term:
            return False
        return is_term_compatible(expected_term, retrieved_term)

    def evaluate_retrieval(
        self,
        cases: List[EvaluationCase],
        top_k: int = 5,
    ) -> List[RetrievalCaseResult]:
        """
        Evaluates Phase 4 dense FAISS retrieval for all supported cases.
        """
        results: List[RetrievalCaseResult] = []

        for case in cases:
            # Measure latency
            t0 = time.perf_counter()
            try:
                search_results = self.retriever.search(query=case.query, top_k=top_k)
            except Exception as e:
                logger.warning("Retrieval failed for case '%s': %s", case.case_id, str(e))
                search_results = []
            t1 = time.perf_counter()
            latency_ms = round((t1 - t0) * 1000.0, 2)

            retrieved_terms = [r.term for r in search_results]
            top_score = round(search_results[0].score, 4) if search_results else 0.0

            recall_1 = False
            recall_3 = False
            recall_5 = False

            if case.expected_term and search_results:
                # Recall@1
                if self._term_matches(case.expected_term, search_results[0].term):
                    recall_1 = True
                # Recall@3
                for r in search_results[:3]:
                    if self._term_matches(case.expected_term, r.term):
                        recall_3 = True
                        break
                # Recall@5
                for r in search_results[:5]:
                    if self._term_matches(case.expected_term, r.term):
                        recall_5 = True
                        break

            results.append(
                RetrievalCaseResult(
                    case_id=case.case_id,
                    query=case.query,
                    expected_term=case.expected_term,
                    retrieved_terms=retrieved_terms,
                    top_score=top_score,
                    recall_at_1=recall_1,
                    recall_at_3=recall_3,
                    recall_at_5=recall_5,
                    latency_ms=latency_ms,
                )
            )

        return results

    def evaluate_guardrails(
        self,
        cases: List[EvaluationCase],
    ) -> List[GuardrailCaseResult]:
        """
        Evaluates Phase 6 guardrail scope and evidence sufficiency checks.
        """
        results: List[GuardrailCaseResult] = []

        for case in cases:
            # 1. Scope check
            in_scope, scope_reason = validate_query_scope(case.query)
            if not in_scope:
                is_allowed = False
                reason = scope_reason
                top_score = 0.0
            else:
                # 2. Retrieval & evidence evaluation
                try:
                    search_results = self.retriever.search(query=case.query, top_k=5)
                    decision = self.controller.evaluate_query(case.query, search_results)
                    is_allowed = decision.allowed
                    reason = decision.reason
                    top_score = decision.top_score
                except Exception as e:
                    is_allowed = False
                    reason = f"Evaluation error: {str(e)}"
                    top_score = 0.0

            # Classification
            classification = "UNKNOWN"
            if case.expected_type == "supported":
                classification = "TP" if is_allowed else "FN"  # TP: Correct accept, FN: False reject
            else:
                classification = "FP" if is_allowed else "TN"  # TN: Correct reject, FP: False accept

            results.append(
                GuardrailCaseResult(
                    case_id=case.case_id,
                    query=case.query,
                    expected_type=case.expected_type,
                    allowed=is_allowed,
                    is_fallback=not is_allowed,
                    reason=reason,
                    top_score=top_score,
                    classification=classification,
                )
            )

        return results

    def evaluate_answers(
        self,
        supported_cases: List[EvaluationCase],
    ) -> List[AnswerCaseResult]:
        """
        Evaluates post-generation answer alignment, grounding, and field completeness.
        """
        results: List[AnswerCaseResult] = []

        for case in supported_cases:
            try:
                search_results = self.retriever.search(query=case.query, top_k=5)
                if not search_results:
                    results.append(
                        AnswerCaseResult(
                            case_id=case.case_id,
                            query=case.query,
                            expected_term=case.expected_term,
                            expected_category=case.expected_category,
                        )
                    )
                    continue

                # Generate answer using configured generator
                answer = self.generator.generate(
                    query=case.query,
                    retrieved_results=search_results,
                )

                # Validate grounding
                val = validate_grounding(answer, search_results)

                # Term matches
                term_matches = is_term_compatible(case.expected_term, answer.term) if case.expected_term else False
                category_matches = (
                    normalize_query(case.expected_category) == normalize_query(answer.category)
                    if case.expected_category
                    else False
                )

                completeness = {
                    "term": bool(answer.term and answer.term.strip()),
                    "category": bool(answer.category and answer.category.strip()),
                    "simple_meaning": bool(answer.simple_meaning and answer.simple_meaning.strip()),
                    "why_it_matters": bool(answer.why_it_matters and answer.why_it_matters.strip()),
                    "job_context": bool(answer.job_context and answer.job_context.strip()),
                    "example": bool(answer.example and answer.example.strip()),
                    "related_terms": bool(answer.related_terms and len(answer.related_terms) > 0),
                    "sources": bool(answer.sources and len(answer.sources) > 0),
                }

                results.append(
                    AnswerCaseResult(
                        case_id=case.case_id,
                        query=case.query,
                        expected_term=case.expected_term,
                        expected_category=case.expected_category,
                        generated_term=answer.term,
                        generated_category=answer.category,
                        term_matches=term_matches,
                        category_matches=category_matches,
                        sources_valid=val.sources_valid,
                        grounding_valid=val.is_valid,
                        completeness_scores=completeness,
                    )
                )

            except Exception as e:
                logger.warning("Answer evaluation error for '%s': %s", case.case_id, str(e))
                results.append(
                    AnswerCaseResult(
                        case_id=case.case_id,
                        query=case.query,
                        expected_term=case.expected_term,
                        expected_category=case.expected_category,
                    )
                )

        return results

    def evaluate_end_to_end(
        self,
        cases: List[EvaluationCase],
    ) -> List[EndToEndCaseResult]:
        """
        Executes complete end-to-end evaluation across the full RAG pipeline.
        """
        results: List[EndToEndCaseResult] = []

        for case in cases:
            t0 = time.perf_counter()
            try:
                outcome = self.controller.process_query(case.query)
            except Exception as e:
                logger.error("Controller process_query exception for '%s': %s", case.case_id, str(e))
                outcome = SafeFallbackResponse(
                    query=case.query,
                    message="Pipeline error occurred.",
                    reason=str(e),
                    is_fallback=True,
                    confidence="LOW",
                )
            t1 = time.perf_counter()
            total_latency_ms = round((t1 - t0) * 1000.0, 2)

            is_fallback = isinstance(outcome, SafeFallbackResponse)
            guardrail_decision = not is_fallback
            generated_term = outcome.term if isinstance(outcome, GeneratedAnswer) else None
            generated_category = outcome.category if isinstance(outcome, GeneratedAnswer) else None

            final_status = "UNKNOWN"
            if case.expected_type == "supported":
                if isinstance(outcome, GeneratedAnswer):
                    term_ok = is_term_compatible(case.expected_term, outcome.term) if case.expected_term else True
                    cat_ok = (
                        normalize_query(case.expected_category) == normalize_query(outcome.category)
                        if case.expected_category
                        else True
                    )
                    final_status = "SUCCESS" if (term_ok and cat_ok) else "ERROR"
                else:
                    final_status = "FALSE_REJECT"
            else:
                if is_fallback:
                    final_status = "SAFE_FALLBACK"
                else:
                    final_status = "FALSE_ACCEPT"

            results.append(
                EndToEndCaseResult(
                    case_id=case.case_id,
                    query=case.query,
                    expected_type=case.expected_type,
                    expected_term=case.expected_term,
                    expected_category=case.expected_category,
                    retrieval_success=not is_fallback,
                    guardrail_decision=guardrail_decision,
                    is_fallback=is_fallback,
                    final_status=final_status,
                    generated_term=generated_term,
                    generated_category=generated_category,
                    total_latency_ms=total_latency_ms,
                )
            )

        return results

    def get_resource_metrics(self) -> Dict[str, Any]:
        """
        Profiles existing repository data resources and vector store dimensions.
        """
        kb_files = list(KNOWLEDGE_BASE_DIR.glob("*.json"))
        kb_size_bytes = sum(f.stat().st_size for f in kb_files if f.is_file())
        
        chunk_count = 0
        if CHUNKS_PATH.exists():
            with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
                chunks_data = json.load(f)
                chunk_count = len(chunks_data)

        faiss_size_bytes = FAISS_INDEX_PATH.stat().st_size if FAISS_INDEX_PATH.exists() else 0
        vector_dim = (
            self.retriever.vector_store.index.d
            if (self.retriever.vector_store.is_loaded and self.retriever.vector_store.index is not None)
            else 384
        )
        index_type = "IndexFlatIP (Cosine via L2-normalized vectors)"

        return {
            "knowledge_base_records": 60,
            "knowledge_base_size_bytes": kb_size_bytes,
            "processed_chunks": chunk_count,
            "vector_dimension": vector_dim,
            "index_type": index_type,
            "faiss_file_size_bytes": faiss_size_bytes,
            "categories_supported": len(SUPPORTED_CATEGORIES),
        }

    def run_benchmark(self) -> EvaluationMetricsSummary:
        """
        Executes full benchmark evaluation across dataset and returns structured summary.
        """
        cases = load_evaluation_dataset(self.dataset_path)
        is_valid, validation_errors = validate_evaluation_dataset(cases)
        if not is_valid:
            raise ValueError(f"Evaluation dataset validation failed: {validation_errors}")

        supported_cases = filter_by_type(cases, "supported")
        unknown_cases = filter_by_type(cases, "unknown")
        oos_cases = filter_by_type(cases, "out_of_scope")

        # 1. Retrieval evaluation (supported cases)
        retrieval_results = self.evaluate_retrieval(supported_cases)
        recall_1 = calculate_recall_at_k(retrieval_results, k=1)
        recall_3 = calculate_recall_at_k(retrieval_results, k=3)
        recall_5 = calculate_recall_at_k(retrieval_results, k=5)

        # Category level retrieval Recall@5
        cat_retrieval: Dict[str, float] = {}
        category_breakdown: Dict[str, CategoryMetrics] = {}

        for cat in SUPPORTED_CATEGORIES:
            cat_cases = filter_by_category(supported_cases, cat)
            cat_ids = {c.case_id for c in cat_cases}
            cat_ret_res = [r for r in retrieval_results if r.case_id in cat_ids]
            
            c_rec_1 = calculate_recall_at_k(cat_ret_res, k=1)
            c_rec_3 = calculate_recall_at_k(cat_ret_res, k=3)
            c_rec_5 = calculate_recall_at_k(cat_ret_res, k=5)
            cat_retrieval[cat] = c_rec_5

            category_breakdown[cat] = CategoryMetrics(
                category=cat,
                total_cases=len(cat_cases),
                recall_at_1=c_rec_1,
                recall_at_3=c_rec_3,
                recall_at_5=c_rec_5,
            )

        # 2. Guardrail evaluation (all cases)
        guardrail_results = self.evaluate_guardrails(cases)
        guardrail_metrics = calculate_guardrail_metrics(guardrail_results)

        # 3. Answer & Grounding evaluation (supported cases)
        answer_results = self.evaluate_answers(supported_cases)
        answer_metrics = calculate_answer_metrics(answer_results)

        # 4. End-to-end evaluation (all cases)
        e2e_results = self.evaluate_end_to_end(cases)
        e2e_supported = [r for r in e2e_results if r.expected_type == "supported"]
        e2e_successes = sum(1 for r in e2e_supported if r.final_status == "SUCCESS")
        end_to_end_success_rate = safe_percentage(e2e_successes, len(e2e_supported))

        # Update category breakdown with term/cat accuracy and e2e success
        for cat in SUPPORTED_CATEGORIES:
            cat_cases = filter_by_category(supported_cases, cat)
            cat_ids = {c.case_id for c in cat_cases}
            
            cat_ans_res = [r for r in answer_results if r.case_id in cat_ids]
            c_term_acc = safe_percentage(sum(1 for r in cat_ans_res if r.term_matches), len(cat_ans_res))
            c_cat_acc = safe_percentage(sum(1 for r in cat_ans_res if r.category_matches), len(cat_ans_res))

            cat_e2e_res = [r for r in e2e_results if r.case_id in cat_ids]
            c_e2e_succ = safe_percentage(sum(1 for r in cat_e2e_res if r.final_status == "SUCCESS"), len(cat_e2e_res))

            cm = category_breakdown[cat]
            cm.term_accuracy = c_term_acc
            cm.category_accuracy = c_cat_acc
            cm.end_to_end_success_rate = c_e2e_succ

        # 5. Latency profiling
        retrieval_latencies = [r.latency_ms for r in retrieval_results]
        e2e_latencies = [r.total_latency_ms for r in e2e_results]

        latency_stats = {
            "retrieval": calculate_latency_stats(retrieval_latencies),
            "end_to_end": calculate_latency_stats(e2e_latencies),
        }

        # 6. Resources
        resource_metrics = self.get_resource_metrics()

        summary = EvaluationMetricsSummary(
            timestamp=datetime.now(timezone.utc).isoformat(),
            dataset_version="1.0.0",
            total_cases=len(cases),
            supported_cases=len(supported_cases),
            unknown_cases=len(unknown_cases),
            out_of_scope_cases=len(oos_cases),
            recall_at_1=recall_1,
            recall_at_3=recall_3,
            recall_at_5=recall_5,
            category_recall_at_5=cat_retrieval,
            supported_acceptance_rate=guardrail_metrics["supported_acceptance_rate"],
            unknown_rejection_rate=guardrail_metrics["unknown_rejection_rate"],
            out_of_scope_rejection_rate=guardrail_metrics["out_of_scope_rejection_rate"],
            safe_fallback_rate=guardrail_metrics["safe_fallback_rate"],
            unsupported_answer_rate=guardrail_metrics["unsupported_answer_rate"],
            confusion_matrix=guardrail_metrics["confusion_matrix"],
            term_identification_accuracy=answer_metrics["term_identification_accuracy"],
            category_accuracy=answer_metrics["category_accuracy"],
            source_provenance_accuracy=answer_metrics["source_provenance_accuracy"],
            grounding_acceptance_rate=answer_metrics["grounding_acceptance_rate"],
            answer_completeness=answer_metrics["answer_completeness"],
            end_to_end_success_rate=end_to_end_success_rate,
            category_breakdown=category_breakdown,
            latency_stats=latency_stats,
            resource_metrics=resource_metrics,
        )

        # Save to results_path
        self._save_results(summary, retrieval_results, guardrail_results, answer_results, e2e_results)

        return summary

    def _save_results(
        self,
        summary: EvaluationMetricsSummary,
        retrieval_results: List[RetrievalCaseResult],
        guardrail_results: List[GuardrailCaseResult],
        answer_results: List[AnswerCaseResult],
        e2e_results: List[EndToEndCaseResult],
    ) -> None:
        """
        Serializes summary metrics and per-case results to data/evaluation/results.json.
        """
        self.results_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "summary": summary.model_dump(),
            "per_case_results": {
                "retrieval": [r.model_dump() for r in retrieval_results],
                "guardrails": [r.model_dump() for r in guardrail_results],
                "answers": [r.model_dump() for r in answer_results],
                "end_to_end": [r.model_dump() for r in e2e_results],
            },
        }

        with open(self.results_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        logger.info("Saved evaluation results to %s", self.results_path)


if __name__ == "__main__":
    print("Running EMP-12 Full Benchmark Evaluation...")
    evaluator = TerminologyEvaluator()
    summary = evaluator.run_benchmark()
    print("\n--- BENCHMARK RESULTS SUMMARY ---")
    print(f"Total Cases: {summary.total_cases}")
    print(f"Recall@1: {summary.recall_at_1:.2f}%")
    print(f"Recall@3: {summary.recall_at_3:.2f}%")
    print(f"Recall@5: {summary.recall_at_5:.2f}%")
    print(f"Guardrail Rejection Rate: {summary.unknown_rejection_rate:.2f}%")
    print(f"Out-of-Scope Rejection Rate: {summary.out_of_scope_rejection_rate:.2f}%")
    print(f"Safe Fallback Rate: {summary.safe_fallback_rate:.2f}%")
    print(f"Term Accuracy: {summary.term_identification_accuracy:.2f}%")
    print(f"Category Accuracy: {summary.category_accuracy:.2f}%")
    print(f"End-to-End Success Rate: {summary.end_to_end_success_rate:.2f}%")

