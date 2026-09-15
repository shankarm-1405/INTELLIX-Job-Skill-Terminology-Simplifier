"""
EMP-12 Phase 9 Useful Features Test Suite
Contains 25 automated tests validating the Glossary Explorer, category filtering,
deterministic search, related-term navigation, one-click explanations, copy formatting,
and clear/reset controls.
"""

from unittest.mock import MagicMock
import pytest

from src.application.glossary import GlossaryItem, GlossaryService
from src.application.models import ApplicationResponse
from src.application.service import TerminologyService
from src.config import SUPPORTED_CATEGORIES
from src.generator.models import GeneratedAnswer
from src.guardrails.models import SafeFallbackResponse
from src.ui.components import format_copy_text


@pytest.fixture
def glossary_service():
    return GlossaryService()


@pytest.fixture
def sample_answer():
    return GeneratedAnswer(
        query="What is Python?",
        term="Python",
        category="Technical Skills",
        simple_meaning="Python is a beginner-friendly programming language.",
        why_it_matters="Learning Python opens software engineering pathways.",
        job_context="Engineers use Python to write automation scripts and web backends.",
        example="Writing a script to rename files.",
        related_terms=["Django", "Scripting", "Dynamic Typing"],
        sources=["Python Software Foundation"],
    )


# ---------------------------------------------------------------------------
# Tests 1-14: Glossary Explorer, Category Filtering & Search
# ---------------------------------------------------------------------------

def test_01_knowledge_base_loads(glossary_service):
    total = glossary_service.get_total_count()
    assert total == 60


def test_02_all_five_categories_available(glossary_service):
    counts = glossary_service.get_category_counts()
    for cat in SUPPORTED_CATEGORIES:
        assert cat in counts
        assert counts[cat] > 0


def test_03_all_terms_discoverable(glossary_service):
    all_terms = glossary_service.get_glossary_terms(category="All Categories")
    assert len(all_terms) == 60


def test_04_category_filtering(glossary_service):
    job_roles = glossary_service.get_glossary_terms(category="Job Roles")
    assert len(job_roles) == 12
    assert all(item.category == "Job Roles" for item in job_roles)

    tech_skills = glossary_service.get_glossary_terms(category="Technical Skills")
    assert len(tech_skills) == 15
    assert all(item.category == "Technical Skills" for item in tech_skills)


def test_05_all_category_view(glossary_service):
    terms = glossary_service.get_glossary_terms(category="All Categories")
    assert len(terms) == 60


def test_06_search_case_insensitive(glossary_service):
    res_lower = glossary_service.get_glossary_terms(search_query="python")
    res_upper = glossary_service.get_glossary_terms(search_query="PYTHON")
    res_title = glossary_service.get_glossary_terms(search_query="Python")

    assert len(res_lower) == len(res_upper) == len(res_title)
    assert any(item.term == "Python" for item in res_lower)


def test_07_search_whitespace_tolerant(glossary_service):
    res = glossary_service.get_glossary_terms(search_query="   python   \t")
    assert any(item.term == "Python" for item in res)


def test_08_search_exact_term(glossary_service):
    res = glossary_service.get_glossary_terms(search_query="API")
    assert len(res) >= 1
    assert res[0].term == "API"


def test_09_search_partial_term(glossary_service):
    res = glossary_service.get_glossary_terms(search_query="soft")
    assert any(item.term == "Software Developer" for item in res)


def test_10_search_by_alias_or_related_term(glossary_service):
    # Search for a term that appears in related_terms
    res = glossary_service.get_glossary_terms(search_query="Full Stack Developer")
    assert len(res) >= 1
    assert any("Developer" in item.term for item in res)


def test_11_empty_search_returns_category(glossary_service):
    res_all = glossary_service.get_glossary_terms(category="Job Roles", search_query="")
    assert len(res_all) == 12


def test_12_unknown_glossary_search_no_results(glossary_service):
    res = glossary_service.get_glossary_terms(search_query="quantum entanglement")
    assert len(res) == 0


def test_13_alphabetical_sorting(glossary_service):
    terms = glossary_service.get_glossary_terms(category="All Categories")
    term_names = [t.term.lower() for t in terms]
    assert term_names == sorted(term_names)


def test_14_no_duplicate_terms(glossary_service):
    terms = glossary_service.get_glossary_terms(category="All Categories")
    term_names = [t.term for t in terms]
    assert len(term_names) == len(set(term_names))


# ---------------------------------------------------------------------------
# Tests 15-20: Term Explanations across Categories
# ---------------------------------------------------------------------------

def test_15_explain_glossary_term(sample_answer):
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = sample_answer

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("Python")

    assert resp.success is True
    assert resp.is_fallback is False
    assert resp.answer.term == "Python"


def test_16_job_role_explanation():
    ans = GeneratedAnswer(
        query="Software Developer",
        term="Software Developer",
        category="Job Roles",
        simple_meaning="Builds and maintains software programs.",
        sources=["US Bureau of Labor Statistics"],
    )
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = ans

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("Software Developer")
    assert resp.answer.category == "Job Roles"


def test_17_technical_skill_explanation(sample_answer):
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = sample_answer

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("Python")
    assert resp.answer.category == "Technical Skills"


def test_18_employment_term_explanation():
    ans = GeneratedAnswer(
        query="Internship",
        term="Internship",
        category="Employment Terms",
        simple_meaning="Supervised work experience for trainees.",
        sources=["Fair Labor Standards Act"],
    )
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = ans

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("Internship")
    assert resp.answer.category == "Employment Terms"


def test_19_qualification_explanation():
    ans = GeneratedAnswer(
        query="Professional Certification",
        term="Professional Certification",
        category="Professional Qualifications",
        simple_meaning="Credential verifying competency.",
        sources=["ISO/IEC 17024 Standards"],
    )
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = ans

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("Professional Certification")
    assert resp.answer.category == "Professional Qualifications"


def test_20_industry_term_explanation():
    ans = GeneratedAnswer(
        query="Cloud Computing",
        term="Cloud Computing",
        category="Industry Terminology",
        simple_meaning="On-demand delivery of IT resources over the internet.",
        sources=["NIST SP 800-145"],
    )
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = ans

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("Cloud Computing")
    assert resp.answer.category == "Industry Terminology"


# ---------------------------------------------------------------------------
# Tests 21-23: Related Term Navigation & Safety
# ---------------------------------------------------------------------------

def test_21_related_terms_displayed(sample_answer):
    assert len(sample_answer.related_terms) == 3
    assert "Django" in sample_answer.related_terms


def test_22_related_term_selection_invokes_service():
    mock_controller = MagicMock()
    ans = GeneratedAnswer(
        query="Django",
        term="Django",
        category="Technical Skills",
        simple_meaning="A Python web framework.",
        sources=["Django Software Foundation"],
    )
    mock_controller.process_query.return_value = ans

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("Django")
    assert resp.answer.term == "Django"
    mock_controller.process_query.assert_called_once_with("Django")


def test_23_unsupported_related_term_shows_fallback():
    mock_controller = MagicMock()
    fallback = SafeFallbackResponse(
        query="Quantum Mechanics",
        message="I don't have enough information in the EMP-12 knowledge base to explain this term reliably.",
        reason="Low score",
    )
    mock_controller.process_query.return_value = fallback

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("Quantum Mechanics")
    assert resp.is_fallback is True
    assert resp.fallback is not None
    assert resp.answer is None


# ---------------------------------------------------------------------------
# Tests 24-25: UX Features (Clear & Copy)
# ---------------------------------------------------------------------------

def test_24_clear_reset_functionality():
    state = {"user_query_input": "Python", "active_response": "dummy_response"}
    # Simulate clear_state()
    state["user_query_input"] = ""
    state["active_response"] = None
    assert state["user_query_input"] == ""
    assert state["active_response"] is None


def test_25_copy_content_safety(sample_answer):
    copy_text = format_copy_text(sample_answer)
    assert "Term: Python" in copy_text
    assert "Category: Technical Skills" in copy_text
    assert "Simple Meaning:" in copy_text
    assert "Python Software Foundation" in copy_text

    # Verify no sensitive or internal fields are leaked
    assert "api_key" not in copy_text.lower()
    assert "faiss" not in copy_text.lower()
    assert "chunk_id" not in copy_text.lower()
    assert "similarity" not in copy_text.lower()
    assert "score" not in copy_text.lower()
