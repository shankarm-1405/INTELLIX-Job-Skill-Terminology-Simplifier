"""
EMP-12 Knowledge Base Schemas
Pydantic data models enforcing strict schema validation for terminology records.
"""

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


# Allowed Categories strictly following EMP-12 taxonomy
CategoryLiteral = Literal[
    "Job Roles",
    "Technical Skills",
    "Employment Terms",
    "Professional Qualifications",
    "Industry Terminology",
]

# Allowed Difficulty Levels
DifficultyLiteral = Literal[
    "Beginner",
    "Intermediate",
    "Advanced",
]

# Controlled Domain Vocabulary
DomainLiteral = Literal[
    "Software Development",
    "Data Science",
    "Cloud Computing",
    "Cybersecurity",
    "DevOps",
    "Employment",
    "Education",
    "Professional Development",
    "Web Development",
    "Systems & Networking",
]


class TerminologyRecord(BaseModel):
    """
    Standardized schema for an EMP-12 Knowledge Base record.
    Every terminology item must satisfy all validation constraints.
    """
    id: str = Field(
        ...,
        description="Globally unique identifier, e.g. 'tech_python' or 'role_data_analyst'"
    )
    term: str = Field(
        ...,
        description="The canonical terminology name"
    )
    category: CategoryLiteral = Field(
        ...,
        description="One of the 5 official EMP-12 terminology categories"
    )
    short_definition: str = Field(
        ...,
        description="A concise, accurate definition (1-2 sentences)"
    )
    simple_explanation: str = Field(
        ...,
        description="Beginner-friendly explanation using plain language and analogies (2-4 sentences)"
    )
    job_context: str = Field(
        ...,
        description="Explanation of how the term appears in real workplace and employment settings"
    )
    example: str = Field(
        ...,
        description="Concrete, practical workplace scenario or usage example"
    )
    related_skills: List[str] = Field(
        ...,
        description="Meaningfully connected technical or professional skills"
    )
    related_terms: List[str] = Field(
        ...,
        description="Meaningfully connected terminology within the domain"
    )
    difficulty: DifficultyLiteral = Field(
        ...,
        description="Target beginner audience difficulty level"
    )
    domain: DomainLiteral = Field(
        ...,
        description="Controlled functional domain of the terminology"
    )
    source: str = Field(
        ...,
        description="Verifiable, authoritative source name and reference"
    )

    @field_validator(
        "id", "term", "short_definition", "simple_explanation",
        "job_context", "example", "source",
        mode="before"
    )
    @classmethod
    def validate_non_empty_string(cls, v: str, info) -> str:
        if not isinstance(v, str):
            raise ValueError(f"Field '{info.field_name}' must be a string.")
        trimmed = v.strip()
        if len(trimmed) < 3:
            raise ValueError(f"Field '{info.field_name}' must contain at least 3 characters.")
        # Disallow generic placeholder values
        placeholders = {"tbd", "todo", "example text", "lorem ipsum", "unknown", "n/a"}
        if trimmed.lower() in placeholders:
            raise ValueError(f"Field '{info.field_name}' cannot contain placeholder '{trimmed}'.")
        return trimmed

    @field_validator("related_skills", "related_terms", mode="before")
    @classmethod
    def validate_string_list(cls, v: List[str], info) -> List[str]:
        if not isinstance(v, list):
            raise ValueError(f"Field '{info.field_name}' must be a list of strings.")
        if len(v) == 0:
            raise ValueError(f"Field '{info.field_name}' cannot be empty; provide at least one related item.")
        cleaned = []
        for idx, item in enumerate(v):
            if not isinstance(item, str):
                raise ValueError(f"Item {idx} in '{info.field_name}' must be a string.")
            trimmed = item.strip()
            if not trimmed:
                raise ValueError(f"Item {idx} in '{info.field_name}' cannot be blank.")
            cleaned.append(trimmed)
        return cleaned


class ProcessedDocument(BaseModel):
    """
    Normalized, formatted document representation ready for retrieval indexing.
    Preserves all structured fields from TerminologyRecord plus full searchable text.
    """
    id: str = Field(..., description="Original record ID")
    term: str = Field(..., description="Terminology name")
    category: CategoryLiteral = Field(..., description="Category")
    short_definition: str = Field(..., description="Short definition")
    simple_explanation: str = Field(..., description="Beginner explanation")
    job_context: str = Field(..., description="Job context")
    example: str = Field(..., description="Practical example")
    related_skills: List[str] = Field(..., description="List of related skills")
    related_terms: List[str] = Field(..., description="List of related terms")
    difficulty: DifficultyLiteral = Field(..., description="Difficulty level")
    domain: DomainLiteral = Field(..., description="Functional domain")
    source: str = Field(..., description="Source reference")
    searchable_text: str = Field(..., description="Consistently formatted full-text representation")

    @field_validator("searchable_text", mode="before")
    @classmethod
    def validate_searchable_text(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 20:
            raise ValueError("searchable_text must be at least 20 characters.")
        return trimmed


class DocumentChunk(BaseModel):
    """
    Final retrieval-ready text chunk with rich metadata and deterministic IDs.
    """
    chunk_id: str = Field(..., description="Deterministic chunk identifier, e.g. 'tech_python_chunk_001'")
    document_id: str = Field(..., description="Parent document identifier")
    term: str = Field(..., description="Terminology name")
    category: CategoryLiteral = Field(..., description="Category")
    difficulty: DifficultyLiteral = Field(..., description="Difficulty level")
    domain: DomainLiteral = Field(..., description="Domain")
    source: str = Field(..., description="Authoritative source citation")
    chunk_index: int = Field(..., ge=1, description="1-based chunk index")
    total_chunks: int = Field(..., ge=1, description="Total chunks for parent document")
    related_skills: List[str] = Field(..., description="Related skills")
    related_terms: List[str] = Field(..., description="Related terms")
    text: str = Field(..., description="Retrieval-ready chunk text")

    @field_validator("text", mode="before")
    @classmethod
    def validate_chunk_text(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 20:
            raise ValueError("Chunk text must be at least 20 characters.")
        return trimmed

