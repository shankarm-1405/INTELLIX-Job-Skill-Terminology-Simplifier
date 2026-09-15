"""
EMP-12 Phase 11 Functional & Regression Test Suite
Tests canonical-term re-ranking, Machine Learning vs Machine Learning Engineer disambiguation,
difficulty badges, fallback guidance, and UI presentation components.
"""

import pytest

from src.application.glossary import GlossaryService
from src.guardrails.controller import GuardrailController
from src.retrieval.retriever import TerminologyRetriever
from src.ui.components import format_fallback_guidance, render_difficulty_badge


@pytest.fixture(scope="module")
def retriever():
    return TerminologyRetriever()


@pytest.fixture(scope="module")
def glossary():
    return GlossaryService()


@pytest.fixture(scope="module")
def controller():
    return GuardrailController()


# ---------------------------------------------------------------------------
# RETRIEVAL DISAMBIGUATION TESTS
# ---------------------------------------------------------------------------


def test_01_machine_learning_engineer_retrieval(retriever):
    """Verify 'Explain Machine Learning Engineer for beginners' prioritizes Machine Learning Engineer (Job Roles)."""
    results = retriever.search("Explain Machine Learning Engineer for beginners", top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top.term == "Machine Learning Engineer"
    assert top.category == "Job Roles"


def test_02_machine_learning_skill_retrieval(retriever):
    """Verify 'What is Machine Learning?' prioritizes Machine Learning (Technical Skills)."""
    results = retriever.search("What is Machine Learning?", top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top.term == "Machine Learning"
    assert top.category == "Technical Skills"


def test_03_machine_learning_engineer_role_query(retriever):
    """Verify 'What does a Machine Learning Engineer do?' prioritizes Job Roles."""
    results = retriever.search("What does a Machine Learning Engineer do?", top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top.term == "Machine Learning Engineer"
    assert top.category == "Job Roles"


def test_04_machine_learning_usage_query(retriever):
    """Verify 'How is machine learning used?' prioritizes Technical Skills."""
    results = retriever.search("How is machine learning used?", top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top.term == "Machine Learning"
    assert top.category == "Technical Skills"


def test_05_software_developer_role_retrieval(retriever):
    """Verify 'What does a Software Developer do?' prioritizes Software Developer."""
    results = retriever.search("What does a Software Developer do?", top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top.term == "Software Developer"
    assert top.category == "Job Roles"


def test_06_devops_engineer_role_retrieval(retriever):
    """Verify 'What does a DevOps Engineer do?' prioritizes DevOps Engineer."""
    results = retriever.search("What does a DevOps Engineer do?", top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top.term == "DevOps Engineer"
    assert top.category == "Job Roles"


def test_07_cloud_engineer_role_retrieval(retriever):
    """Verify 'What does a Cloud Engineer do?' prioritizes Cloud Engineer."""
    results = retriever.search("What does a Cloud Engineer do?", top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top.term == "Cloud Engineer"
    assert top.category == "Job Roles"


def test_08_data_scientist_role_retrieval(retriever):
    """Verify 'Data Scientist role and responsibilities' prioritizes Data Scientist."""
    results = retriever.search("Data Scientist role and responsibilities", top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top.term == "Data Scientist"
    assert top.category == "Job Roles"


def test_09_cybersecurity_analyst_role_retrieval(retriever):
    """Verify 'Cybersecurity Analyst network defense' prioritizes Cybersecurity Analyst."""
    results = retriever.search("Cybersecurity Analyst network defense", top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top.term == "Cybersecurity Analyst"
    assert top.category == "Job Roles"


def test_10_unknown_query_receives_no_boost_and_fails_threshold(retriever, controller):
    """Verify that unknown queries receive no canonical match boost and remain safely blocked."""
    query = "What is quantum entanglement?"
    results = retriever.search(query, top_k=5)
    decision = controller.evaluate_query(query, results)
    assert decision.allowed is False
    assert "below the required evidence threshold" in decision.reason or decision.is_out_of_scope


# ---------------------------------------------------------------------------
# UI COMPONENT & GLOSSARY ENHANCEMENT TESTS
# ---------------------------------------------------------------------------


def test_11_render_difficulty_badge():
    """Verify render_difficulty_badge formats levels with visual indicators."""
    assert "🟢" in render_difficulty_badge("Beginner")
    assert "🟡" in render_difficulty_badge("Intermediate")
    assert "🔴" in render_difficulty_badge("Advanced")
    assert "Beginner" in render_difficulty_badge(None)


def test_12_format_fallback_guidance():
    """Verify fallback guidance includes all five official categories."""
    guidance = format_fallback_guidance()
    assert "Job Roles" in guidance
    assert "Technical Skills" in guidance
    assert "Employment Terms" in guidance
    assert "Professional Qualifications" in guidance
    assert "Industry Terminology" in guidance


def test_13_glossary_term_difficulty_lookup(glossary):
    """Verify GlossaryService.get_term_difficulty retrieves accurate difficulty levels."""
    assert glossary.get_term_difficulty("Python") == "Beginner"
    assert glossary.get_term_difficulty("Machine Learning Engineer") == "Advanced"
    assert glossary.get_term_difficulty("Full Stack Developer") == "Intermediate"
    assert glossary.get_term_difficulty("Nonexistent Term") == "Beginner"
