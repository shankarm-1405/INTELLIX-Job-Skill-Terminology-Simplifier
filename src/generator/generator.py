"""
EMP-12 LLM Answer Generator Module
Consumes retrieved SearchResult evidence and synthesizes grounded, beginner-friendly explanations
using Google Gemini API via the official google-genai SDK.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    DEFAULT_GENERATION_TEMPERATURE,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    get_gemini_api_key,
    sanitize_error_message,
)
from src.generator.models import GeneratedAnswer
from src.generator.prompt_builder import PromptBuilder
from src.retrieval.models import SearchResult


def extract_json_payload(raw_text: str) -> Dict[str, Any]:
    """
    Safely extracts and parses JSON payload from raw LLM output,
    handling markdown code blocks if present.
    """
    cleaned = raw_text.strip()
    # Remove markdown code blocks if wrapped
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object/dict, got: {type(data)}")
        return data
    except Exception as e:
        raise ValueError(f"Failed to parse JSON from LLM response: {str(e)} | Raw: {raw_text[:200]}") from e


class TerminologyGenerator:
    """
    Grounded LLM answer generator for EMP-12:
    Takes user queries and retrieved SearchResult evidence to synthesize structured,
    beginner-friendly explanations strictly anchored in the knowledge base.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        client: Optional[Any] = None,
    ):
        self.api_key = api_key or get_gemini_api_key() or GEMINI_API_KEY
        self.model_name = model_name or GEMINI_MODEL
        self.temperature = temperature if temperature is not None else DEFAULT_GENERATION_TEMPERATURE
        self.client = client

        if self.client is None and self.api_key:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)

    def generate(
        self,
        query: str,
        retrieved_results: List[SearchResult],
        context: Optional[Any] = None,
    ) -> GeneratedAnswer:
        """
        Synthesizes a structured beginner explanation for a query using retrieved evidence:
        1. Validates inputs
        2. Builds grounded prompt with optional contextual metadata
        3. Calls Gemini API
        4. Validates and returns GeneratedAnswer
        """
        # Validate query
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query string cannot be empty or whitespace.")

        cleaned_query = query.strip()
        if len(cleaned_query) < 2:
            raise ValueError("Query string must be at least 2 characters long.")

        # Validate retrieved results
        if not isinstance(retrieved_results, list) or len(retrieved_results) == 0:
            raise ValueError(
                "Cannot generate explanation without retrieved evidence. "
                "retrieved_results must be a non-empty list of SearchResult items."
            )

        for idx, res in enumerate(retrieved_results):
            if not isinstance(res, SearchResult):
                raise ValueError(
                    f"Item {idx} in retrieved_results is not a SearchResult instance."
                )

        # Ensure Gemini client or API key is available
        if self.client is None:
            raise ValueError(
                "Gemini API client is not configured. Please set GEMINI_API_KEY in your .env file "
                "or pass an initialized client to TerminologyGenerator."
            )

        # Build prompt
        system_instruction, user_prompt = PromptBuilder.build_prompt(
            cleaned_query, retrieved_results, context=context
        )

        # Execute generation via google-genai SDK
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=self.temperature,
                response_mime_type="application/json",
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )
        except Exception as e:
            clean_err = sanitize_error_message(str(e))
            raise RuntimeError(f"Gemini API generation failed: {clean_err}") from e

        if not response or not hasattr(response, "text") or not response.text:
            raise RuntimeError("Gemini API returned an empty or invalid response.")

        # Parse and validate response JSON
        payload = extract_json_payload(response.text)

        # Ensure query is bound
        payload["query"] = cleaned_query

        # Fallback for sources if empty or omitted in LLM payload
        if not payload.get("sources") or len(payload["sources"]) == 0:
            payload["sources"] = list({r.source for r in retrieved_results if r.source})

        try:
            answer = GeneratedAnswer(**payload)
        except Exception as e:
            clean_val_err = sanitize_error_message(str(e))
            raise ValueError(f"LLM output failed GeneratedAnswer schema validation: {clean_val_err}") from e

        return answer
