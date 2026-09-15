"""
EMP-12 Application Layer Module
Connects the User Interface to the underlying RAG, Context, Guardrail, and Glossary pipelines.
"""

from src.application.glossary import GlossaryItem, GlossaryService
from src.application.models import ApplicationResponse
from src.application.service import TerminologyService

__all__ = [
    "ApplicationResponse",
    "GlossaryItem",
    "GlossaryService",
    "TerminologyService",
]
