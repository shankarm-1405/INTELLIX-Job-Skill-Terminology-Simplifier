"""
EMP-12 UI Presentation Helpers and Formatting Components
Provides reusable, isolated presentation functions for Streamlit rendering.
"""

from typing import Any, Dict, List, Optional, Tuple

from src.config import MAX_QUERY_LENGTH
from src.generator.models import GeneratedAnswer


def is_valid_query_input(query: Optional[str], max_length: int = MAX_QUERY_LENGTH) -> Tuple[bool, str]:
    """
    Validates user query input before dispatching to backend.
    Enforces non-empty string, minimum length of 2 characters, and maximum length.
    """
    if query is None or not isinstance(query, str):
        return False, "Please enter a term or question to continue."

    trimmed = query.strip()
    if not trimmed:
        return False, "Please enter a term or question to continue."

    if len(trimmed) < 2:
        return False, "Query is too short. Please enter a complete term or question."

    if len(trimmed) > max_length:
        return False, f"Query is too long (maximum {max_length} characters). Please enter a concise term or question."

    return True, ""


def format_category_badge(category: str) -> str:
    """
    Returns a clean category label for display.
    """
    return f"Category: {category.strip()}" if category else "Category: General"


def format_related_terms_list(related_terms: Optional[List[str]]) -> List[str]:
    """
    Cleans and deduplicates related terms for list presentation.
    """
    if not related_terms:
        return []
    cleaned = []
    for t in related_terms:
        t_clean = t.strip()
        if t_clean and t_clean not in cleaned:
            cleaned.append(t_clean)
    return cleaned


def format_sources_list(sources: Optional[List[str]]) -> List[str]:
    """
    Formats authoritative reference source citations for display.
    """
    if not sources:
        return []
    cleaned = []
    for s in sources:
        s_clean = s.strip()
        if s_clean and s_clean not in cleaned:
            cleaned.append(s_clean)
    return cleaned


def extract_display_payload(answer: GeneratedAnswer) -> Dict[str, Any]:
    """
    Converts a GeneratedAnswer instance into a presentation-ready dictionary.
    """
    if not answer:
        return {}

    return {
        "term": answer.term,
        "category": answer.category,
        "simple_meaning": answer.simple_meaning,
        "why_it_matters": answer.why_it_matters,
        "job_context": answer.job_context,
        "example": answer.example,
        "related_terms": format_related_terms_list(answer.related_terms),
        "sources": format_sources_list(answer.sources),
    }


def format_copy_text(answer: GeneratedAnswer) -> str:
    """
    Formats a clean, comprehensive plaintext representation of a GeneratedAnswer
    for user study and clipboard copying, strictly omitting internal diagnostics.
    """
    if not answer:
        return ""

    sections = [
        f"Term: {answer.term}",
        f"Category: {answer.category}",
        "",
        "Simple Meaning:",
        answer.simple_meaning.strip(),
    ]

    if answer.why_it_matters:
        sections.extend(["", "Why It Matters:", answer.why_it_matters.strip()])

    if answer.job_context:
        sections.extend(["", "Where It Fits in Work:", answer.job_context.strip()])

    if answer.example:
        sections.extend(["", "Beginner Example:", answer.example.strip()])

    if answer.related_terms:
        rel_lines = "\n".join(f"- {t}" for t in format_related_terms_list(answer.related_terms))
        sections.extend(["", "Related Terms:", rel_lines])

    if answer.sources:
        src_lines = "\n".join(f"- {s}" for s in format_sources_list(answer.sources))
        sections.extend(["", "Authoritative Sources:", src_lines])

    return "\n".join(sections)


def render_difficulty_badge(difficulty: Optional[str]) -> str:
    """
    Renders an accessible visual badge for terminology difficulty.
    """
    if not difficulty:
        return "Difficulty: Beginner"
    diff_clean = difficulty.strip().capitalize()
    if diff_clean == "Beginner":
        return "🟢 Beginner"
    elif diff_clean == "Intermediate":
        return "🟡 Intermediate"
    elif diff_clean == "Advanced":
        return "🔴 Advanced"
    return f"Difficulty: {diff_clean}"


def format_fallback_guidance() -> str:
    """
    Formats beginner-friendly structured guidance when a query is outside the knowledge base.
    """
    return (
        "**This term is not currently covered by the EMP-12 knowledge base.**\n\n"
        "EMP-12 is dedicated to explaining employment and technology concepts. "
        "Try exploring terms from our five official categories:\n"
        "- 💼 **Job Roles** (e.g., *Software Developer*, *Cloud Engineer*, *Data Analyst*)\n"
        "- 💻 **Technical Skills** (e.g., *Python*, *SQL*, *Docker*, *Git*)\n"
        "- 📄 **Employment Terms** (e.g., *Internship*, *Probation*, *Notice Period*)\n"
        "- 🎓 **Professional Qualifications** (e.g., *Bachelor's Degree*, *Technical Certification*)\n"
        "- ⚙️ **Industry Terminology** (e.g., *API*, *CI/CD*, *Agile*, *Cloud Computing*)\n\n"
        "Or browse our full collection using the **Glossary Explorer** below!"
    )
