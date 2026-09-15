"""
EMP-12 Retrieval Data Models
Pydantic schemas for search queries and ranked retrieval results.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """
    Standardized, validated schema for a ranked retrieval result.
    Carries complete chunk content, similarity score, rank, and structured metadata.
    """
    chunk_id: str = Field(..., description="Unique chunk identifier, e.g. 'tech_python_chunk_001'")
    document_id: str = Field(..., description="Parent document identifier, e.g. 'tech_python'")
    term: str = Field(..., description="Terminology name")
    category: str = Field(..., description="Official EMP-12 taxonomy category")
    difficulty: str = Field(..., description="Difficulty level: Beginner, Intermediate, Advanced")
    domain: str = Field(..., description="Functional domain of terminology")
    source: str = Field(..., description="Authoritative reference and source citation")
    text: str = Field(..., description="Searchable text content of the chunk")
    score: float = Field(..., description="Cosine similarity score between query and chunk (0.0 to 1.0)")
    rank: int = Field(..., ge=1, description="1-based ranking position among retrieved results")
    related_skills: List[str] = Field(default_factory=list, description="Companion skills")
    related_terms: List[str] = Field(default_factory=list, description="Related terms")
