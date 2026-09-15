"""
EMP-12 Contextual Intelligence Data Models
Pydantic schemas for structured terminology context, intent classification, and validation.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from src.config import SUPPORTED_CATEGORIES


class ContextType(str, Enum):
    """Context types representing the domain perspective of terminology."""
    TERM_CONTEXT = "TERM_CONTEXT"
    JOB_CONTEXT = "JOB_CONTEXT"
    SKILL_CONTEXT = "SKILL_CONTEXT"
    EMPLOYMENT_CONTEXT = "EMPLOYMENT_CONTEXT"
    QUALIFICATION_CONTEXT = "QUALIFICATION_CONTEXT"
    INDUSTRY_CONTEXT = "INDUSTRY_CONTEXT"
    RELATED_TERMS_CONTEXT = "RELATED_TERMS_CONTEXT"


class QueryIntent(str, Enum):
    """Classified user intent regarding the terminology inquiry."""
    DEFINITION = "DEFINITION"
    EMPLOYMENT_CONTEXT = "EMPLOYMENT_CONTEXT"
    USAGE_CONTEXT = "USAGE_CONTEXT"
    ROLE_CONTEXT = "ROLE_CONTEXT"
    QUALIFICATION_CONTEXT = "QUALIFICATION_CONTEXT"
    INDUSTRY_CONTEXT = "INDUSTRY_CONTEXT"
    RELATED_TERMS = "RELATED_TERMS"


class TerminologyContext(BaseModel):
    """
    Structured contextual representation synthesized from Phase 4 retrieved evidence,
    preserving domain, category, difficulty, workplace usage, and source traceability.
    """
    term: str = Field(..., description="Canonical primary terminology name")
    category: str = Field(..., description="Taxonomy category: Job Roles, Technical Skills, etc.")
    domain: str = Field(..., description="Functional domain, e.g. Software Development, Human Resources")
    difficulty: str = Field(..., description="Difficulty level: Beginner, Intermediate, or Advanced")
    context_type: ContextType = Field(..., description="Perspective type for contextual explanation")
    query_intent: QueryIntent = Field(..., description="Detected user intent")
    workplace_context: Optional[str] = Field(None, description="How the term is applied in workplace environments")
    why_it_matters: Optional[str] = Field(None, description="Why this term is important for beginners or career transitioners")
    related_terms: List[str] = Field(default_factory=list, description="Related terms traceable to retrieved evidence")
    sources: List[str] = Field(default_factory=list, description="Authoritative sources preserved from evidence")
    evidence_text: str = Field("", description="Consolidated excerpt of retrieved evidence chunks")

    @field_validator("term", mode="before")
    @classmethod
    def validate_term(cls, v: str) -> str:
        if not isinstance(v, str) or len(v.strip()) < 2:
            raise ValueError("Term must be a non-empty string of at least 2 characters.")
        return v.strip()

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Category cannot be empty.")
        trimmed = v.strip()
        if trimmed not in SUPPORTED_CATEGORIES:
            raise ValueError(f"Category '{trimmed}' is not in supported categories: {SUPPORTED_CATEGORIES}")
        return trimmed

    @field_validator("difficulty", mode="before")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Difficulty cannot be empty.")
        trimmed = v.strip()
        allowed = {"Beginner", "Intermediate", "Advanced"}
        if trimmed not in allowed:
            raise ValueError(f"Difficulty '{trimmed}' must be one of {allowed}")
        return trimmed

    @field_validator("domain", mode="before")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        if not isinstance(v, str) or len(v.strip()) < 2:
            raise ValueError("Domain must be a non-empty string of at least 2 characters.")
        return v.strip()


class ContextValidationResult(BaseModel):
    """
    Deterministic evaluation result for a TerminologyContext instance.
    """
    is_valid: bool = Field(..., description="Whether context conforms to all data integrity requirements")
    reason: str = Field(..., description="Rationale for validity decision")
    missing_fields: List[str] = Field(default_factory=list, description="List of required fields that are missing or empty")
    invalid_values: List[str] = Field(default_factory=list, description="List of fields with invalid or unsupported values")
