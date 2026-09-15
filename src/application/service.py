"""
EMP-12 Application Service Module
High-level service interface wrapping the RAG retrieval, contextualization,
generation, and guardrails pipeline for presentation in the User Interface.
"""

import logging
from typing import Optional

from src.application.models import ApplicationResponse
from src.context.context_builder import ContextBuilder
from src.generator.generator import TerminologyGenerator
from src.generator.models import GeneratedAnswer
from src.guardrails.controller import GuardrailController
from src.guardrails.models import SafeFallbackResponse
from src.config import MAX_QUERY_LENGTH, sanitize_error_message
from src.retrieval.retriever import TerminologyRetriever

logger = logging.getLogger("emp12.application")


class TerminologyService:
    """
    Application service coordinator for EMP-12:
    Provides a clean, single-call interface for the UI without exposing internal
    FAISS, embedding, or prompt engineering complexities.
    """

    def __init__(
        self,
        retriever: Optional[TerminologyRetriever] = None,
        generator: Optional[TerminologyGenerator] = None,
        context_builder: Optional[ContextBuilder] = None,
        controller: Optional[GuardrailController] = None,
    ):
        self.retriever = retriever or TerminologyRetriever()
        self.generator = generator or TerminologyGenerator()
        self.context_builder = context_builder or ContextBuilder()
        self.controller = controller or GuardrailController(
            retriever=self.retriever,
            generator=self.generator,
            context_builder=self.context_builder,
        )

    def explain_term(self, query: str) -> ApplicationResponse:
        """
        Executes the full controlled RAG pipeline for a user query:
        1. Pre-validates non-empty input
        2. Dispatches to GuardrailController
        3. Wraps response in clean ApplicationResponse model
        4. Handles exceptions safely without exposing credentials or internal traces
        """
        if query is None or not isinstance(query, str) or not query.strip():
            return ApplicationResponse(
                query=query or "",
                success=False,
                is_fallback=False,
                error_message="Please enter a term or question to continue.",
            )

        cleaned_query = query.strip()
        if len(cleaned_query) < 2:
            return ApplicationResponse(
                query=cleaned_query,
                success=False,
                is_fallback=False,
                error_message="Query is too short. Please enter a complete term or question.",
            )

        if len(cleaned_query) > MAX_QUERY_LENGTH:
            return ApplicationResponse(
                query=cleaned_query[:60] + "...",
                success=False,
                is_fallback=False,
                error_message=f"Query is too long (maximum {MAX_QUERY_LENGTH} characters). Please enter a concise term or question.",
            )

        try:
            result = self.controller.process_query(cleaned_query)

            if isinstance(result, SafeFallbackResponse):
                # Detect if fallback was triggered by configuration failure (e.g. missing API key)
                if "GEMINI_API_KEY" in result.reason or "client is not configured" in result.reason:
                    return ApplicationResponse(
                        query=cleaned_query,
                        success=False,
                        is_fallback=False,
                        is_configuration_error=True,
                        error_message="Grounded generation is unavailable because GEMINI_API_KEY is not configured in the environment.",
                    )
                return ApplicationResponse(
                    query=cleaned_query,
                    success=True,
                    is_fallback=True,
                    fallback=result,
                )

            elif isinstance(result, GeneratedAnswer):
                return ApplicationResponse(
                    query=cleaned_query,
                    success=True,
                    is_fallback=False,
                    answer=result,
                )

            else:
                logger.error("Unexpected result type from controller: %s", type(result))
                return ApplicationResponse(
                    query=cleaned_query,
                    success=False,
                    is_fallback=False,
                    error_message="Sorry, I couldn't process the explanation right now. Please try again.",
                )

        except Exception as e:
            raw_msg = str(e)
            clean_err = sanitize_error_message(raw_msg)
            is_config_err = "GEMINI_API_KEY" in raw_msg or "client is not configured" in raw_msg

            if is_config_err:
                logger.warning("Configuration issue in TerminologyService: %s", clean_err)
                return ApplicationResponse(
                    query=cleaned_query,
                    success=False,
                    is_fallback=False,
                    is_configuration_error=True,
                    error_message="Grounded generation is unavailable because GEMINI_API_KEY is not configured in the environment.",
                )
            else:
                logger.error("Unexpected error in TerminologyService: %s", clean_err)
                return ApplicationResponse(
                    query=cleaned_query,
                    success=False,
                    is_fallback=False,
                    error_message="Sorry, I couldn't process the explanation right now. Please try again.",
                )
