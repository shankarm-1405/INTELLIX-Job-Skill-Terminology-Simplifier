"""
EMP-12 Manual UI Test Runner
Tests the 5 manual UI verification queries through TerminologyService
with full real Retrieval (Phase 4), real Guardrails (Phase 6), real Context Builder (Phase 7),
and deterministic generator synthesis.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Ensure project root is in sys.path
BASE_DIR = Path("C:/Users/shank/Downloads/SKILL_DEVELOPMENT")
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.application.service import TerminologyService
from src.context.context_builder import ContextBuilder
from src.generator.models import GeneratedAnswer
from src.guardrails.controller import GuardrailController
from src.retrieval.retriever import TerminologyRetriever

def create_test_service():
    retriever = TerminologyRetriever()
    context_builder = ContextBuilder()

    # Mock generator to avoid network API calls while exercising 100% of pipeline
    mock_generator = MagicMock()
    def mock_generate(query, retrieved_results, context=None):
        primary = retrieved_results[0]
        return GeneratedAnswer(
            query=query,
            term=primary.term,
            category=primary.category,
            simple_meaning=f"{primary.term} is an important {primary.category.lower()} concept in {primary.domain}.",
            why_it_matters=context.why_it_matters if context else "Foundational career knowledge.",
            job_context=context.workplace_context if context else f"Used in {primary.domain}.",
            example=f"A professional in {primary.domain} applying {primary.term} to solve a practical task.",
            related_terms=primary.related_terms[:3],
            sources=[primary.source],
        )
    mock_generator.generate.side_effect = mock_generate

    controller = GuardrailController(
        retriever=retriever,
        generator=mock_generator,
        context_builder=context_builder,
        threshold=0.55,
    )

    return TerminologyService(
        retriever=retriever,
        generator=mock_generator,
        context_builder=context_builder,
        controller=controller,
    )

def main():
    service = create_test_service()
    
    test_cases = [
        ("Test A — Technical Skill", "What is Python?"),
        ("Test B — Job Role", "What does a software developer do?"),
        ("Test C — Employment Term", "What does internship mean?"),
        ("Test D — Unknown Term", "What is quantum entanglement?"),
        ("Test E — Out-of-Scope", "What is the weather today?"),
    ]

    print("=" * 76)
    print("MANUAL UI VERIFICATION RESULTS (Phases 4 - 8 Pipeline)")
    print("=" * 76)

    for label, query in test_cases:
        print(f"\n>>> {label}: \"{query}\"")
        resp = service.explain_term(query)
        if resp.is_fallback:
            print("  [STATUS] SAFE FALLBACK TRIGGERED")
            print(f"  [MESSAGE] {resp.fallback.message}")
            print(f"  [REASON]  {resp.fallback.reason}")
        elif resp.success and resp.answer:
            ans = resp.answer
            print(f"  [STATUS]  ANSWER GENERATED & GROUNDED")
            print(f"  [TERM]    {ans.term}")
            print(f"  [CATEGORY]{ans.category}")
            print(f"  [MEANING] {ans.simple_meaning}")
            print(f"  [WHY]     {ans.why_it_matters}")
            print(f"  [WORK]    {ans.job_context}")
            print(f"  [EXAMPLE] {ans.example}")
            print(f"  [RELATED] {ans.related_terms}")
            print(f"  [SOURCES] {ans.sources}")
        else:
            print(f"  [ERROR]   {resp.error_message}")

    print("\n" + "=" * 76)

if __name__ == "__main__":
    main()
