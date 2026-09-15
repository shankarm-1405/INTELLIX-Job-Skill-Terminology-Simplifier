"""
EMP-12 Scope and Query Validation Module
Provides deterministic, lightweight pre-retrieval validation for user queries.
"""

import re
from typing import Tuple

# High-precision patterns indicating non-employment intent
OUT_OF_SCOPE_PATTERNS = [
    # Creative writing & entertainment
    (r"\b(write|compose|generate)\b.*?\b(poem|poetry|song|lyrics|story|joke|novel|haiku)\b", "Creative writing request"),
    (r"\b(tell\s+me\s+a\s+joke|make\s+me\s+laugh)\b", "Entertainment / humor request"),
    
    # Weather and climate
    (r"\b(weather|temperature|forecast|rain|humidity|snowing|umbrella)\b", "Weather or meteorological inquiry"),
    
    # Sports and live entertainment
    (r"\b(cricket|football|soccer|baseball|basketball|nba|ipl|fifa|tournament)\b", "Sports inquiry"),
    
    # Travel and reservations
    (r"\b(book|reserve)\b.*?\b(flight|hotel|ticket|train|bus|table|cab|uber)\b", "Travel / reservation booking request"),
    
    # Personal transactions & calculations
    (r"\b(calculate\s+my|mortgage\s+calculator|tax\s+calculator|bmi\s+calculator)\b", "Personal finance calculation"),
    
    # Consumer shopping / product recommendations
    (r"\b(best\s+(phone|mobile|smartphone|camera|car|bike|television|tv)\s+to\s+buy)\b", "Consumer product purchasing recommendation"),
    (r"\b(buy|purchase)\s+(an?\s+)?(iphone|android|samsung|car|shoes|clothes)\b", "Commercial purchase request"),
    
    # Cooking and culinary recipes
    (r"\b(recipe\s+for|how\s+to\s+(cook|bake|make))\b.*?\b(cake|pizza|pasta|bread|curry|soup|food|cookie)\b", "Culinary recipe inquiry"),
    
    # General trivia / political officeholders outside professional glossary
    (r"\b(who\s+is\s+the\s+prime\s+minister|who\s+is\s+the\s+president\s+of)\b", "General political / geopolitical inquiry"),
    
    # Unrelated scientific phenomena
    (r"\bquantum\s+entanglement\b", "Quantum physics topic outside employment glossary"),
]


def normalize_query(query: str) -> str:
    """
    Normalizes query string for uniform inspection:
    lowercased, collapsed whitespace, trimmed surrounding punctuation.
    """
    if not query:
        return ""
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", query.strip().lower())
    # Remove leading/trailing non-alphanumeric chars (except trailing question marks)
    cleaned = re.sub(r"^[^\w\s]+", "", cleaned)
    cleaned = re.sub(r"[^\w\s\?]+$", "", cleaned)
    return cleaned.strip()


def validate_query_scope(query: str) -> Tuple[bool, str]:
    """
    Validates query structure and verifies it does not belong to obvious out-of-scope domains.
    Returns:
        (is_valid: bool, reason: str)
    """
    if query is None:
        return False, "Query cannot be None."

    if not isinstance(query, str):
        return False, "Query must be a string."

    trimmed = query.strip()
    if not trimmed:
        return False, "Query string cannot be empty or whitespace-only."

    if len(trimmed) < 2:
        return False, "Query string must be at least 2 characters long."

    normalized = normalize_query(trimmed)

    # Check out-of-scope regular expressions
    for pattern, description in OUT_OF_SCOPE_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return False, f"Query is outside EMP-12 domain scope ({description})."

    return True, "Query structure and initial domain scope are valid."
