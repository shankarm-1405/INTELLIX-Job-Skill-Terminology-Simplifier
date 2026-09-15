"""
EMP-12 Contextual Intelligence Module
Synthesizes grounded terminology context, connects employment relationships,
and guides category-aware, difficulty-aware beginner explanations.
"""

from src.context.context_builder import ContextBuilder
from src.context.intent import detect_query_intent
from src.context.models import (
    ContextType,
    ContextValidationResult,
    QueryIntent,
    TerminologyContext,
)
from src.context.validator import ContextValidator

__all__ = [
    "ContextBuilder",
    "TerminologyContext",
    "ContextType",
    "QueryIntent",
    "ContextValidator",
    "ContextValidationResult",
    "detect_query_intent",
]
