"""
EMP-12 Evaluation Models Module
Pydantic schemas for evaluation cases, results, diagnostic records, and summary scorecards.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvaluationCase(BaseModel):
    """
    Schema for a single standardized evaluation benchmark case.
    """
    case_id: str = Field(..., description="Unique case identifier, e.g. 'eval_sup_job_01'")
    query: str = Field(..., description="Input query string to evaluate")
    expected_type: str = Field(..., description="Classification type: 'supported', 'unknown', or 'out_of_scope'")
    expected_category: Optional[str] = Field(None, description="Expected taxonomy category if supported")
    expected_term: Optional[str] = Field(None, description="Expected canonical terminology name if supported")
    difficulty: Optional[str] = Field(None, description="Difficulty band: Beginner, Intermediate, Advanced")
    variation_type: Optional[str] = Field(None, description="Query formulation style")


class RetrievalCaseResult(BaseModel):
    """
    Per-case evaluation record for Phase 4 dense FAISS retrieval.
    """
    case_id: str
    query: str
    expected_term: Optional[str] = None
    retrieved_terms: List[str] = Field(default_factory=list)
    top_score: float = 0.0
    recall_at_1: bool = False
    recall_at_3: bool = False
    recall_at_5: bool = False
    latency_ms: float = 0.0


class GuardrailCaseResult(BaseModel):
    """
    Per-case evaluation record for Phase 6 guardrail scope and evidence verification.
    """
    case_id: str
    query: str
    expected_type: str
    allowed: bool
    is_fallback: bool
    reason: str
    top_score: float = 0.0
    classification: str = Field(..., description="'TP', 'FP', 'TN', or 'FN'")


class AnswerCaseResult(BaseModel):
    """
    Per-case evaluation record for Phase 5 LLM generation and Phase 6 grounding.
    """
    case_id: str
    query: str
    expected_term: Optional[str] = None
    expected_category: Optional[str] = None
    generated_term: Optional[str] = None
    generated_category: Optional[str] = None
    term_matches: bool = False
    category_matches: bool = False
    sources_valid: bool = False
    grounding_valid: bool = False
    completeness_scores: Dict[str, bool] = Field(default_factory=dict)


class EndToEndCaseResult(BaseModel):
    """
    Holistic end-to-end evaluation record across the full pipeline.
    """
    case_id: str
    query: str
    expected_type: str
    expected_term: Optional[str] = None
    expected_category: Optional[str] = None
    retrieval_success: bool = False
    guardrail_decision: bool = False
    is_fallback: bool = False
    final_status: str = Field(..., description="'SUCCESS', 'SAFE_FALLBACK', 'FALSE_ACCEPT', 'FALSE_REJECT', or 'ERROR'")
    generated_term: Optional[str] = None
    generated_category: Optional[str] = None
    total_latency_ms: float = 0.0


class CategoryMetrics(BaseModel):
    """
    Taxonomy category breakdown scorecard.
    """
    category: str
    total_cases: int = 0
    recall_at_1: float = 0.0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    term_accuracy: float = 0.0
    category_accuracy: float = 0.0
    end_to_end_success_rate: float = 0.0


class EvaluationMetricsSummary(BaseModel):
    """
    Comprehensive benchmark summary containing all measured metrics.
    """
    timestamp: str
    dataset_version: str = "1.0.0"
    total_cases: int = 0
    supported_cases: int = 0
    unknown_cases: int = 0
    out_of_scope_cases: int = 0
    
    # Retrieval metrics
    recall_at_1: float = 0.0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    category_recall_at_5: Dict[str, float] = Field(default_factory=dict)
    
    # Guardrail metrics
    supported_acceptance_rate: float = 0.0
    unknown_rejection_rate: float = 0.0
    out_of_scope_rejection_rate: float = 0.0
    safe_fallback_rate: float = 0.0
    unsupported_answer_rate: float = 0.0
    confusion_matrix: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    
    # Generation & Grounding metrics
    term_identification_accuracy: float = 0.0
    category_accuracy: float = 0.0
    source_provenance_accuracy: float = 0.0
    grounding_acceptance_rate: float = 0.0
    answer_completeness: Dict[str, float] = Field(default_factory=dict)
    
    # End-to-End
    end_to_end_success_rate: float = 0.0
    category_breakdown: Dict[str, CategoryMetrics] = Field(default_factory=dict)
    
    # Performance & Resources
    latency_stats: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    resource_metrics: Dict[str, Any] = Field(default_factory=dict)
