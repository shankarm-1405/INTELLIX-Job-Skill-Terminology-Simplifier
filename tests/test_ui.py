"""
EMP-12 User Interface & Application Layer Test Suite
Contains 20 automated tests validating UI components, presentation helpers,
application service responses across all 5 categories, error handling, and safe fallbacks.
"""

from unittest.mock import MagicMock
import pytest

from src.application.models import ApplicationResponse
from src.application.service import TerminologyService
from src.generator.models import GeneratedAnswer
from src.guardrails.controller import GuardrailController
from src.guardrails.models import SafeFallbackResponse
from src.retrieval.models import SearchResult
from src.ui.components import (
    extract_display_payload,
    format_category_badge,
    format_related_terms_list,
    format_sources_list,
    is_valid_query_input,
)


# ---------------------------------------------------------------------------
# Test Fixtures: Sample SearchResults across 5 categories
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_skill_answer():
    return GeneratedAnswer(
        query="What is Python?",
        term="Python",
        category="Technical Skills",
        simple_meaning="Python is a readable, beginner-friendly programming language.",
        why_it_matters="Learning Python opens pathways in software development and data science.",
        job_context="Software engineers use Python for building web applications and scripting automation.",
        example="Automating the renaming of 500 files with a 10-line Python script.",
        related_terms=["Django", "Scripting", "Dynamic Typing"],
        sources=["Python Software Foundation"],
    )


@pytest.fixture
def sample_role_answer():
    return GeneratedAnswer(
        query="What does a software developer do?",
        term="Software Developer",
        category="Job Roles",
        simple_meaning="A software developer designs, writes, and tests computer code.",
        why_it_matters="Helps beginners understand foundational engineering career duties.",
        job_context="Developers work in cross-functional agile engineering teams.",
        example="Building a shopping cart checkout system.",
        related_terms=["Git", "Python", "System Design"],
        sources=["US Bureau of Labor Statistics"],
    )


@pytest.fixture
def sample_employment_answer():
    return GeneratedAnswer(
        query="What does internship mean?",
        term="Internship",
        category="Employment Terms",
        simple_meaning="An internship is a period of workplace training for students or career starters.",
        why_it_matters="Crucial for understanding entry-level workplace opportunities.",
        job_context="Interns work under supervision to acquire practical job skills.",
        example="A college student interning for 3 months at a tech company.",
        related_terms=["Mentorship", "Trainee"],
        sources=["Fair Labor Standards Act (FLSA)"],
    )


@pytest.fixture
def sample_qualification_answer():
    return GeneratedAnswer(
        query="What is professional certification?",
        term="Professional Certification",
        category="Professional Qualifications",
        simple_meaning="A professional certification verifies a candidate's domain competency.",
        why_it_matters="Enables candidates to prove industry expertise without years of tenure.",
        job_context="Professionals earn certifications to meet employer credential requirements.",
        example="Earning an AWS Certified Solutions Architect credential.",
        related_terms=["Credential", "Accreditation"],
        sources=["ISO/IEC 17024 Standards"],
    )


@pytest.fixture
def sample_industry_answer():
    return GeneratedAnswer(
        query="What is an API?",
        term="API",
        category="Industry Terminology",
        simple_meaning="An API allows different computer applications to communicate with each other.",
        why_it_matters="Foundational concept for web development and software architecture.",
        job_context="Developers connect frontends to backends using REST APIs.",
        example="A weather app fetching live temperature forecasts from a remote server.",
        related_terms=["Endpoint", "Web Service", "REST"],
        sources=["W3C Web Services Architecture"],
    )


# ---------------------------------------------------------------------------
# Test 1: Application module imports successfully
# ---------------------------------------------------------------------------
def test_01_application_module_imports():
    from src.application import ApplicationResponse, TerminologyService
    assert ApplicationResponse is not None
    assert TerminologyService is not None


# ---------------------------------------------------------------------------
# Test 2: Streamlit app can initialize / imports cleanly
# ---------------------------------------------------------------------------
def test_02_streamlit_app_can_initialize():
    import app
    assert hasattr(app, "get_terminology_service")


# ---------------------------------------------------------------------------
# Test 3: Empty query is handled
# ---------------------------------------------------------------------------
def test_03_empty_query_handled():
    is_valid, msg = is_valid_query_input("")
    assert is_valid is False
    assert "enter a term" in msg

    service = TerminologyService(controller=MagicMock())
    resp = service.explain_term("")
    assert resp.success is False
    assert "enter a term" in resp.error_message


# ---------------------------------------------------------------------------
# Test 4: Whitespace query is handled
# ---------------------------------------------------------------------------
def test_04_whitespace_query_handled():
    is_valid, msg = is_valid_query_input("    \t \n  ")
    assert is_valid is False
    assert "enter a term" in msg

    service = TerminologyService(controller=MagicMock())
    resp = service.explain_term("   ")
    assert resp.success is False
    assert "enter a term" in resp.error_message


# ---------------------------------------------------------------------------
# Test 5: Valid Python query reaches application pipeline (Technical Skills)
# ---------------------------------------------------------------------------
def test_05_valid_python_query(sample_skill_answer):
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = sample_skill_answer

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("What is Python?")

    assert resp.success is True
    assert resp.is_fallback is False
    assert resp.answer.term == "Python"
    assert resp.answer.category == "Technical Skills"
    mock_controller.process_query.assert_called_once_with("What is Python?")


# ---------------------------------------------------------------------------
# Test 6: Job-role query reaches application pipeline (Job Roles)
# ---------------------------------------------------------------------------
def test_06_job_role_query(sample_role_answer):
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = sample_role_answer

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("What does a software developer do?")

    assert resp.success is True
    assert resp.answer.term == "Software Developer"
    assert resp.answer.category == "Job Roles"


# ---------------------------------------------------------------------------
# Test 7: Employment-term query reaches application pipeline (Employment Terms)
# ---------------------------------------------------------------------------
def test_07_employment_term_query(sample_employment_answer):
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = sample_employment_answer

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("What does internship mean?")

    assert resp.success is True
    assert resp.answer.term == "Internship"
    assert resp.answer.category == "Employment Terms"


# ---------------------------------------------------------------------------
# Test 8: Qualification query reaches application pipeline (Professional Qualifications)
# ---------------------------------------------------------------------------
def test_08_qualification_query(sample_qualification_answer):
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = sample_qualification_answer

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("What is professional certification?")

    assert resp.success is True
    assert resp.answer.term == "Professional Certification"
    assert resp.answer.category == "Professional Qualifications"


# ---------------------------------------------------------------------------
# Test 9: Industry-terminology query reaches application pipeline (Industry Terminology)
# ---------------------------------------------------------------------------
def test_09_industry_term_query(sample_industry_answer):
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = sample_industry_answer

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("What is an API?")

    assert resp.success is True
    assert resp.answer.term == "API"
    assert resp.answer.category == "Industry Terminology"


# ---------------------------------------------------------------------------
# Test 10: Successful response is rendered correctly
# ---------------------------------------------------------------------------
def test_10_successful_response_structure(sample_skill_answer):
    payload = extract_display_payload(sample_skill_answer)
    assert payload["term"] == "Python"
    assert payload["category"] == "Technical Skills"
    assert "programming language" in payload["simple_meaning"]
    assert len(payload["sources"]) == 1


# ---------------------------------------------------------------------------
# Test 11: Safe fallback response is rendered correctly
# ---------------------------------------------------------------------------
def test_11_safe_fallback_response_structure():
    fallback = SafeFallbackResponse(
        query="What is quantum entanglement?",
        message="I don't have enough information in the EMP-12 knowledge base to explain this term reliably.",
        reason="Score below threshold",
        is_fallback=True,
    )
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = fallback

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("What is quantum entanglement?")

    assert resp.success is True
    assert resp.is_fallback is True
    assert resp.fallback is not None
    assert "I don't have enough information" in resp.fallback.message


# ---------------------------------------------------------------------------
# Test 12: Unknown query does not produce a fake answer
# ---------------------------------------------------------------------------
def test_12_unknown_query_does_not_produce_fake_answer():
    fallback = SafeFallbackResponse(
        query="What is quantum entanglement?",
        message="I don't have enough information in the EMP-12 knowledge base to explain this term reliably.",
        reason="Low score",
    )
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = fallback

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("What is quantum entanglement?")

    assert resp.answer is None
    assert resp.is_fallback is True


# ---------------------------------------------------------------------------
# Test 13: Out-of-scope query remains controlled
# ---------------------------------------------------------------------------
def test_13_out_of_scope_query_remains_controlled():
    fallback = SafeFallbackResponse(
        query="What is the weather today?",
        message="I don't have enough information in the EMP-12 knowledge base to explain this term reliably.",
        reason="Out of scope",
    )
    mock_controller = MagicMock()
    mock_controller.process_query.return_value = fallback

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("What is the weather today?")

    assert resp.is_fallback is True
    assert resp.answer is None


# ---------------------------------------------------------------------------
# Test 14: Generated term is displayed
# ---------------------------------------------------------------------------
def test_14_generated_term_displayed(sample_skill_answer):
    payload = extract_display_payload(sample_skill_answer)
    assert payload["term"] == "Python"


# ---------------------------------------------------------------------------
# Test 15: Category is displayed
# ---------------------------------------------------------------------------
def test_15_category_displayed(sample_skill_answer):
    badge = format_category_badge(sample_skill_answer.category)
    assert badge == "Category: Technical Skills"


# ---------------------------------------------------------------------------
# Test 16: Simple meaning is displayed
# ---------------------------------------------------------------------------
def test_16_simple_meaning_displayed(sample_role_answer):
    payload = extract_display_payload(sample_role_answer)
    assert "designs, writes, and tests" in payload["simple_meaning"]


# ---------------------------------------------------------------------------
# Test 17: Why-it-matters field is displayed when available
# ---------------------------------------------------------------------------
def test_17_why_it_matters_displayed_when_available(sample_skill_answer):
    payload = extract_display_payload(sample_skill_answer)
    assert payload["why_it_matters"] is not None
    assert "software development" in payload["why_it_matters"].lower()


# ---------------------------------------------------------------------------
# Test 18: Related terms are displayed when available
# ---------------------------------------------------------------------------
def test_18_related_terms_displayed_when_available(sample_industry_answer):
    formatted = format_related_terms_list(sample_industry_answer.related_terms)
    assert "Endpoint" in formatted
    assert "REST" in formatted


# ---------------------------------------------------------------------------
# Test 19: Sources are displayed when available
# ---------------------------------------------------------------------------
def test_19_sources_displayed_when_available(sample_qualification_answer):
    sources = format_sources_list(sample_qualification_answer.sources)
    assert len(sources) == 1
    assert "ISO/IEC 17024 Standards" in sources


# ---------------------------------------------------------------------------
# Test 20: Backend errors are handled without exposing sensitive details
# ---------------------------------------------------------------------------
def test_20_backend_errors_handled_gracefully():
    mock_controller = MagicMock()
    mock_controller.process_query.side_effect = RuntimeError("Critical secret internal database failed")

    service = TerminologyService(controller=mock_controller)
    resp = service.explain_term("What is Python?")

    assert resp.success is False
    assert resp.error_message == "Sorry, I couldn't process the explanation right now. Please try again."
    # Assert sensitive internal message is not leaked in user-facing message
    assert "Critical secret" not in resp.error_message
