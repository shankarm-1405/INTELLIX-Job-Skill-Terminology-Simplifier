"""
EMP-12 Generator Package
Synthesizes grounded beginner-friendly explanations from retrieved evidence using Google Gemini API.
"""

from src.generator.generator import TerminologyGenerator
from src.generator.models import GeneratedAnswer
from src.generator.prompt_builder import PromptBuilder

__all__ = [
    "TerminologyGenerator",
    "GeneratedAnswer",
    "PromptBuilder",
]
