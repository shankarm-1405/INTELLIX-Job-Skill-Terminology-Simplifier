"""
EMP-12 Guardrail Data Models
Pydantic schemas for guardrail decisions, grounding validation, and safe fallbacks.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class GuardrailDecision(BaseModel):
    """
    Structured, explainable evaluation of query relevance, evidence sufficiency,
    and permission to invoke Phase 5 generation.
    """
    allowed: bool = Field(..., description="Whether the query is permitted to proceed to generation")
    reason: str = Field(..., description="Explainable rationale for the decision")
    confidence: str = Field(..., description="Qualitative confidence band: HIGH, MEDIUM, or LOW (evidence strength)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Quantitative evidence strength score (0.0 to 1.0)")
    matched_terms: List[str] = Field(default_factory=list, description="Terminology terms recognized in evidence or query")
    top_score: float = Field(0.0, description="Highest similarity score among retrieved results")
    second_score: Optional[float] = Field(None, description="Similarity score of second-highest result if available")
    score_gap: Optional[float] = Field(None, description="Separation gap between top_score and second_score")
    category: Optional[str] = Field(None, description="Dominant or matched taxonomy category")
    is_out_of_scope: bool = Field(False, description="Flag indicating query was flagged as outside EMP-12 domain scope")
    relevant_result_count: int = Field(0, description="Number of retrieved results meeting relevance threshold")


class GroundingValidationResult(BaseModel):
    """
    Outcome of post-generation deterministic validation checking term, category,
    sources, and completeness against retrieved evidence.
    """
    is_valid: bool = Field(..., description="Whether generated answer strictly complies with retrieved evidence")
    reason: str = Field(..., description="Explainable rationale for grounding pass or rejection")
    term_matches: bool = Field(..., description="Whether generated term corresponds to retrieved evidence")
    category_matches: bool = Field(..., description="Whether generated category matches retrieved evidence")
    sources_valid: bool = Field(..., description="Whether all cited sources exist in retrieved evidence")
    unsupported_sources: List[str] = Field(default_factory=list, description="Citations present in answer but missing from evidence")


class SafeFallbackResponse(BaseModel):
    """
    Deterministic, structured fallback response returned when query is out-of-scope,
    evidence is insufficient, or generated answer fails grounding validation.
    """
    query: str = Field(..., description="Original user query")
    message: str = Field(..., description="Deterministic user-facing explanation")
    reason: str = Field(..., description="Underlying reason for fallback")
    is_fallback: bool = Field(True, description="Identifies this response as a fallback")
    confidence: str = Field("LOW", description="Confidence tier for fallback responses")
