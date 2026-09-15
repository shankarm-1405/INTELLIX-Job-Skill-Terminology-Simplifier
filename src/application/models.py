"""
EMP-12 Application Response Data Models
Standardized response objects connecting the RAG pipeline to the User Interface.
"""

from typing import Optional
from pydantic import BaseModel, Field

from src.generator.models import GeneratedAnswer
from src.guardrails.models import SafeFallbackResponse


class ApplicationResponse(BaseModel):
    """
    Unified application response model delivered to the User Interface:
    Distinguishes between grounded contextual answers, safe fallbacks, and validation/error messages.
    """
    query: str = Field(..., description="Original user query")
    success: bool = Field(..., description="Whether pipeline execution finished without internal error")
    is_fallback: bool = Field(False, description="Whether the response is a deterministic safe fallback")
    answer: Optional[GeneratedAnswer] = Field(None, description="Grounded contextual answer if approved")
    fallback: Optional[SafeFallbackResponse] = Field(None, description="Safe fallback response if query was blocked or rejected")
    is_configuration_error: bool = Field(False, description="Whether failure was due to missing or invalid system configuration")
    error_message: Optional[str] = Field(None, description="User-friendly error message if an exception occurred")
