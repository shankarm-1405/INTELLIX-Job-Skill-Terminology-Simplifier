"""
EMP-12 Query Intent Detection Module
Provides deterministic, explainable intent classification for user queries
to guide contextual terminology presentation.
"""

import re
from typing import Optional

from src.context.models import QueryIntent


# Deterministic pattern matchers for query intent
INTENT_PATTERNS = [
    # 1. Related terms & skills exploration
    (
        r"\b(related\s+(to|skills|terms)|similar\s+(to|skills|terms)|skills\s+related|what\s+else\s+should\s+i\s+learn)\b",
        QueryIntent.RELATED_TERMS,
    ),
    # 2. Employment & workplace context
    (
        r"\b(why\s+is\s+.*?used\s+in\s+jobs|how\s+is\s+.*?used\s+at\s+work|in\s+the\s+workplace|employment\s+context|career\s+value|internship\s+mean|what\s+does\s+internship)\b",
        QueryIntent.EMPLOYMENT_CONTEXT,
    ),
    # 3. Usage & domain application
    (
        r"\b(where\s+is\s+.*?used|where\s+do\s+people\s+use|which\s+industries\s+use|applications\s+of)\b",
        QueryIntent.USAGE_CONTEXT,
    ),
    # 4. Role & responsibility inquiry
    (
        r"\b(what\s+does\s+a\s+.*?\s+do|responsibilities\s+of|duties\s+of|role\s+of\s+a|job\s+of\s+a)\b",
        QueryIntent.ROLE_CONTEXT,
    ),
    # 5. Qualification / credential inquiry
    (
        r"\b(professional\s+certification|professional\s+qualification|certification\s+mean|qualification\s+mean|credential\s+mean)\b",
        QueryIntent.QUALIFICATION_CONTEXT,
    ),
    # 6. Industry terminology inquiry
    (
        r"\b(what\s+is\s+an?\s+api|api\s+mean|cloud\s+computing\s+mean)\b",
        QueryIntent.INDUSTRY_CONTEXT,
    ),
]


def detect_query_intent(query: str, category: Optional[str] = None) -> QueryIntent:
    """
    Detects the primary intent of a user terminology query using deterministic regex patterns,
    falling back to category-informed heuristics and canonical definition.

    Args:
        query: User input query string
        category: Optional taxonomy category of the retrieved candidate

    Returns:
        QueryIntent enum value
    """
    if not query or not isinstance(query, str):
        return QueryIntent.DEFINITION

    normalized = query.strip().lower()

    # Direct pattern checks
    for pattern, intent in INTENT_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return intent

    # Category-based heuristics if no explicit pattern fired
    if category == "Job Roles":
        if any(w in normalized for w in ["do", "role", "work as", "job", "tasks", "responsibilities"]):
            return QueryIntent.ROLE_CONTEXT

    if category == "Employment Terms":
        if any(w in normalized for w in ["job", "work", "employment", "hire", "career", "contract"]):
            return QueryIntent.EMPLOYMENT_CONTEXT

    if category == "Professional Qualifications":
        if any(w in normalized for w in ["cert", "qualification", "exam", "credential", "license"]):
            return QueryIntent.QUALIFICATION_CONTEXT

    if category == "Industry Terminology":
        if any(w in normalized for w in ["industry", "system", "technology", "standard"]):
            return QueryIntent.INDUSTRY_CONTEXT

    # Default canonical definition
    return QueryIntent.DEFINITION
