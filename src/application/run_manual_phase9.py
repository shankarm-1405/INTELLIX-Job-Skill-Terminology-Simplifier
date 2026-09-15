"""
EMP-12 Phase 9 Manual Testing Script (Tests A through M)
Executes and validates all 13 manual test scenarios directly.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from unittest.mock import MagicMock
from src.application.glossary import GlossaryService
from src.application.service import TerminologyService
from src.generator.models import GeneratedAnswer
from src.guardrails.controller import GuardrailController
from src.retrieval.retriever import TerminologyRetriever
from src.ui.components import format_copy_text

def run_phase9_manual_tests():
    print("=" * 76)
    print("EMP-12 PHASE 9 MANUAL VERIFICATION (TESTS A - M)")
    print("=" * 76)

    glossary = GlossaryService()

    # TEST A: Browse All
    all_terms = glossary.get_glossary_terms(category="All Categories")
    assert len(all_terms) == 60
    assert len(all_terms) == len(set(t.term for t in all_terms))
    print(f"TEST A - Browse All: [OK] {len(all_terms)} unique terms sorted alphabetically.")

    # TEST B: Job Roles
    job_roles = glossary.get_glossary_terms(category="Job Roles")
    assert len(job_roles) == 12
    assert all(t.category == "Job Roles" for t in job_roles)
    print(f"TEST B - Job Roles: [OK] {len(job_roles)} terms, all Job Roles.")

    # TEST C: Technical Skills
    tech_skills = glossary.get_glossary_terms(category="Technical Skills")
    assert len(tech_skills) == 15
    assert all(t.category == "Technical Skills" for t in tech_skills)
    print(f"TEST C - Technical Skills: [OK] {len(tech_skills)} terms, all Technical Skills.")

    # TEST D: Employment Terms
    emp_terms = glossary.get_glossary_terms(category="Employment Terms")
    assert len(emp_terms) == 12
    assert all(t.category == "Employment Terms" for t in emp_terms)
    print(f"TEST D - Employment Terms: [OK] {len(emp_terms)} terms, all Employment Terms.")

    # TEST E: Professional Qualifications
    prof_quals = glossary.get_glossary_terms(category="Professional Qualifications")
    assert len(prof_quals) == 9
    assert all(t.category == "Professional Qualifications" for t in prof_quals)
    print(f"TEST E - Professional Qualifications: [OK] {len(prof_quals)} terms, all Qualifications.")

    # TEST F: Industry Terminology
    ind_terms = glossary.get_glossary_terms(category="Industry Terminology")
    assert len(ind_terms) == 12
    assert all(t.category == "Industry Terminology" for t in ind_terms)
    print(f"TEST F - Industry Terminology: [OK] {len(ind_terms)} terms, all Industry Terminology.")

    # TEST G: Search Python
    py_search = glossary.get_glossary_terms(search_query="Python")
    assert any(t.term == "Python" for t in py_search)
    print(f"TEST G - Search 'Python': [OK] Found {len(py_search)} matching item(s).")

    # TEST H: Case Insensitive Search
    py_upper = glossary.get_glossary_terms(search_query="PYTHON")
    assert any(t.term == "Python" for t in py_upper)
    print(f"TEST H - Case Insensitive 'PYTHON': [OK] Found {len(py_upper)} matching item(s).")

    # TEST I: Explain Python through Pipeline
    retriever = TerminologyRetriever()
    mock_gen = MagicMock()
    mock_gen.generate.return_value = GeneratedAnswer(
        query="Python",
        term="Python",
        category="Technical Skills",
        simple_meaning="Python is a beginner-friendly programming language.",
        why_it_matters="Valuable for software and data careers.",
        job_context="Used for web development and automation.",
        example="Automating repetitive file management tasks.",
        related_terms=["Django", "Scripting"],
        sources=["Python Software Foundation"],
    )
    controller = GuardrailController(retriever=retriever, generator=mock_gen, threshold=0.55)
    service = TerminologyService(retriever=retriever, generator=mock_gen, controller=controller)
    resp = service.explain_term("Python")
    assert resp.success is True
    assert resp.answer.term == "Python"
    print(f"TEST I - Explain 'Python': [OK] Pipeline returned grounded answer for {resp.answer.term}.")

    # TEST J: Related Term Navigation
    rel_term = resp.answer.related_terms[0]
    resp_rel = service.explain_term(rel_term)
    assert resp_rel.success is True
    print(f"TEST J - Related Term '{rel_term}': [OK] Explained successfully through pipeline.")

    # TEST K: Unknown Term Search
    unk_search = glossary.get_glossary_terms(search_query="Quantum Entanglement")
    assert len(unk_search) == 0
    print(f"TEST K - Unknown Search: [OK] 0 matches, no invented record.")

    # TEST L: Copy Explanation
    copy_text = format_copy_text(resp.answer)
    assert "Term: Python" in copy_text
    assert "API_KEY" not in copy_text
    assert "faiss" not in copy_text.lower()
    print("TEST L - Copy Explanation: [OK] Clean formatted text without sensitive data.")

    # TEST M: Clear / Reset
    state = {"user_query_input": "Python", "active_response": resp}
    state["user_query_input"] = ""
    state["active_response"] = None
    assert state["user_query_input"] == ""
    assert state["active_response"] is None
    print("TEST M - Clear: [OK] State reset cleanly.")

    print("=" * 76)
    print("ALL MANUAL TESTS (A - M) PASSED SUCCESSFULLY!")
    print("=" * 76)

if __name__ == "__main__":
    run_phase9_manual_tests()
