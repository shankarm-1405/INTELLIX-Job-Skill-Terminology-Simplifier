"""
EMP-12 Generated Answer Data Models
Pydantic schemas enforcing validated, structured beginner-friendly explanations.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from src.config import SUPPORTED_CATEGORIES


class GeneratedAnswer(BaseModel):
    """
    Structured, beginner-friendly terminology explanation synthesized by the LLM
    from retrieved EMP-12 evidence.
    """
    query: str = Field(..., description="Original user query")
    term: str = Field(..., description="Canonical terminology name being explained")
    category: str = Field(..., description="Taxonomy category of the term")
    simple_meaning: str = Field(..., description="Beginner-friendly explanation using plain language")
    why_it_matters: Optional[str] = Field(None, description="Why this term is important in employment or beginner learning context")
    job_context: Optional[str] = Field(None, description="How the term is used in workplace/industry settings")
    example: Optional[str] = Field(None, description="Realistic practical example")
    related_terms: List[str] = Field(default_factory=list, description="Related skills or terminology")
    sources: List[str] = Field(default_factory=list, description="Authoritative reference sources from evidence")

    @field_validator("query", "term", "simple_meaning", mode="before")
    @classmethod
    def validate_non_empty_strings(cls, v: str, info) -> str:
        if not isinstance(v, str):
            raise ValueError(f"Field '{info.field_name}' must be a string.")
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError(f"Field '{info.field_name}' must be at least 2 characters long.")
        return trimmed

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Category must be a non-empty string.")
        trimmed = v.strip()
        if trimmed not in SUPPORTED_CATEGORIES:
            raise ValueError(f"Category '{trimmed}' is not in supported categories: {SUPPORTED_CATEGORIES}")
        return trimmed

    @field_validator("sources", mode="before")
    @classmethod
    def validate_sources(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            raise ValueError("Sources must be a list of strings.")
        cleaned = [s.strip() for s in v if isinstance(s, str) and s.strip()]
        if len(cleaned) == 0:
            raise ValueError("Generated answer must cite at least one authoritative source.")
        return cleaned
