"""
EMP-12 Text Normalization & Document Processor
Converts validated TerminologyRecord objects into normalized, searchable ProcessedDocument objects.
"""

import re
from typing import List

from src.ingestion.schemas import ProcessedDocument, TerminologyRecord


def normalize_text(text: str) -> str:
    """
    Safely normalizes text without changing meaning or removing meaningful punctuation:
    - Normalizes carriage returns and line endings (\r\n -> \n)
    - Replaces non-breaking spaces with standard spaces
    - Collapses multiple horizontal spaces/tabs into a single space
    - Collapses excessive blank lines (3+ newlines -> 2 newlines)
    - Strips leading and trailing whitespace
    """
    if not text:
        return ""

    # Normalize line endings
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace non-breaking spaces and tabs
    normalized = normalized.replace("\u00a0", " ").replace("\t", " ")
    # Collapse multiple horizontal spaces on each line
    normalized = re.sub(r"[ ]{2,}", " ", normalized)
    # Strip trailing whitespace on each line
    lines = [line.strip() for line in normalized.split("\n")]
    normalized = "\n".join(lines)
    # Collapse 3 or more consecutive newlines down to 2
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def build_searchable_text(record: TerminologyRecord) -> str:
    """
    Constructs the canonical searchable document representation following
    the standard EMP-12 text format.
    """
    norm_term = normalize_text(record.term)
    norm_category = normalize_text(record.category)
    norm_def = normalize_text(record.short_definition)
    norm_exp = normalize_text(record.simple_explanation)
    norm_context = normalize_text(record.job_context)
    norm_example = normalize_text(record.example)
    norm_skills = ", ".join([normalize_text(s) for s in record.related_skills if s.strip()])
    norm_terms = ", ".join([normalize_text(t) for t in record.related_terms if t.strip()])
    norm_diff = normalize_text(record.difficulty)
    norm_domain = normalize_text(record.domain)
    norm_source = normalize_text(record.source)

    document_text = (
        f"Term: {norm_term}\n\n"
        f"Category: {norm_category}\n\n"
        f"Short Definition:\n"
        f"{norm_def}\n\n"
        f"Simple Explanation:\n"
        f"{norm_exp}\n\n"
        f"Job Context:\n"
        f"{norm_context}\n\n"
        f"Example:\n"
        f"{norm_example}\n\n"
        f"Related Skills:\n"
        f"{norm_skills}\n\n"
        f"Related Terms:\n"
        f"{norm_terms}\n\n"
        f"Difficulty:\n"
        f"{norm_diff}\n\n"
        f"Domain:\n"
        f"{norm_domain}\n\n"
        f"Source:\n"
        f"{norm_source}"
    )
    return document_text


class DocumentProcessor:
    """
    Processor responsible for transforming validated TerminologyRecords
    into normalized ProcessedDocument models with full searchable text.
    """

    @classmethod
    def process_record(cls, record: TerminologyRecord) -> ProcessedDocument:
        """Transforms a single TerminologyRecord into a ProcessedDocument."""
        searchable_text = build_searchable_text(record)
        return ProcessedDocument(
            id=normalize_text(record.id),
            term=normalize_text(record.term),
            category=record.category,
            short_definition=normalize_text(record.short_definition),
            simple_explanation=normalize_text(record.simple_explanation),
            job_context=normalize_text(record.job_context),
            example=normalize_text(record.example),
            related_skills=[normalize_text(s) for s in record.related_skills],
            related_terms=[normalize_text(t) for t in record.related_terms],
            difficulty=record.difficulty,
            domain=record.domain,
            source=normalize_text(record.source),
            searchable_text=searchable_text,
        )

    @classmethod
    def process_records(cls, records: List[TerminologyRecord]) -> List[ProcessedDocument]:
        """Batch processes a list of TerminologyRecords into ProcessedDocuments."""
        return [cls.process_record(rec) for rec in records]
