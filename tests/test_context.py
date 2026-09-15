"""
EMP-12 Contextual Intelligence Test Suite
Contains 20 automated tests validating context models, intent detection,
context builder across all five EMP-12 categories, validation rules, and end-to-end flow.
"""

from unittest.mock import MagicMock
import pytest
from pydantic import ValidationError

from src.context.context_builder import ContextBuilder
from src.context.intent import detect_query_intent
from src.context.models import (
    ContextType,
    ContextValidationResult,
    QueryIntent,
    TerminologyContext,
)
from src.context.validator import ContextValidator
from src.generator.models import GeneratedAnswer
from src.guardrails.controller import GuardrailController
from src.retrieval.models import SearchResult


# ---------------------------------------------------------------------------
# Test Fixtures: Candidates across all 5 EMP-12 categories
# ---------------------------------------------------------------------------

@pytest.fixture
def python_skill_result():
    return SearchResult(
        chunk_id="tech_python_chunk_001",
        document_id="tech_python",
        term="Python",
        category="Technical Skills",
        difficulty="Beginner",
        domain="Software Development",
        source="Python Software Foundation",
        text="Python is an interpreted, high-level language with dynamic typing used for web dev and automation.",
        score=0.74,
        rank=1,
        related_skills=["Django", "Flask"],
        related_terms=["Scripting", "Dynamic Typing", "Automation"],
    )


@pytest.fixture
def swe_role_result():
    return SearchResult(
        chunk_id="role_swe_chunk_001",
        document_id="role_swe",
        term="Software Developer",
        category="Job Roles",
        difficulty="Beginner",
        domain="Engineering",
        source="US Bureau of Labor Statistics",
        text="A software developer designs, codes, tests, and maintains applications for users.",
        score=0.78,
        rank=1,
        related_skills=["Python", "Git", "Algorithms"],
        related_terms=["Software Engineer", "Programmer"],
    )


@pytest.fixture
def internship_employment_result():
    return SearchResult(
        chunk_id="emp_internship_chunk_001",
        document_id="emp_internship",
        term="Internship",
        category="Employment Terms",
        difficulty="Beginner",
        domain="Human Resources",
        source="Fair Labor Standards Act (FLSA)",
        text="An internship provides short-term practical training and workplace experience.",
        score=0.76,
        rank=1,
        related_skills=["Mentorship"],
        related_terms=["Trainee", "Apprenticeship"],
    )


@pytest.fixture
def certification_qual_result():
    return SearchResult(
        chunk_id="qual_cert_chunk_001",
        document_id="qual_cert",
        term="Professional Certification",
        category="Professional Qualifications",
        difficulty="Intermediate",
        domain="Professional Development",
        source="ISO/IEC 17024 Standards",
        text="A professional certification demonstrates verified competency in an industry area.",
        score=0.77,
        rank=1,
        related_skills=["Continuing Education"],
        related_terms=["Credential", "Accreditation"],
    )


@pytest.fixture
def api_industry_result():
    return SearchResult(
        chunk_id="ind_api_chunk_001",
        document_id="ind_api",
        term="API",
        category="Industry Terminology",
        difficulty="Beginner",
        domain="Systems & Networking",
        source="W3C Web Services Architecture",
        text="An Application Programming Interface defines protocols and tools for software interaction.",
        score=0.79,
        rank=1,
        related_skills=["REST", "JSON"],
        related_terms=["Endpoint", "Web Service"],
    )


# ---------------------------------------------------------------------------
# Test 1: Context model validates correctly
# ---------------------------------------------------------------------------
def test_01_context_model_validation():
    ctx = TerminologyContext(
        term="Python",
        category="Technical Skills",
        domain="Software Development",
        difficulty="Beginner",
        context_type=ContextType.SKILL_CONTEXT,
        query_intent=QueryIntent.DEFINITION,
        workplace_context="Used for automation and web backends.",
        why_it_matters="Great starter language for beginners.",
        related_terms=["Scripting", "Django"],
        sources=["Python Software Foundation"],
        evidence_text="Python is high-level...",
    )
    assert ctx.term == "Python"
    assert ctx.context_type == ContextType.SKILL_CONTEXT
    assert ctx.query_intent == QueryIntent.DEFINITION


# ---------------------------------------------------------------------------
# Test 2: Empty term is rejected
# ---------------------------------------------------------------------------
def test_02_empty_term_rejected():
    with pytest.raises(ValidationError):
        TerminologyContext(
            term="",
            category="Technical Skills",
            domain="Software Development",
            difficulty="Beginner",
            context_type=ContextType.SKILL_CONTEXT,
            query_intent=QueryIntent.DEFINITION,
        )


# ---------------------------------------------------------------------------
# Test 3: Invalid category is rejected
# ---------------------------------------------------------------------------
def test_03_invalid_category_rejected():
    with pytest.raises(ValidationError):
        TerminologyContext(
            term="Python",
            category="Unsupported Category XYZ",
            domain="Software Development",
            difficulty="Beginner",
            context_type=ContextType.SKILL_CONTEXT,
            query_intent=QueryIntent.DEFINITION,
        )


# ---------------------------------------------------------------------------
# Test 4: Invalid difficulty is rejected
# ---------------------------------------------------------------------------
def test_04_invalid_difficulty_rejected():
    with pytest.raises(ValidationError):
        TerminologyContext(
            term="Python",
            category="Technical Skills",
            domain="Software Development",
            difficulty="SuperExpert",
            context_type=ContextType.SKILL_CONTEXT,
            query_intent=QueryIntent.DEFINITION,
        )


# ---------------------------------------------------------------------------
# Test 5: Context builder handles one result
# ---------------------------------------------------------------------------
def test_05_context_builder_single_result(python_skill_result):
    builder = ContextBuilder()
    ctx = builder.build("What is Python?", [python_skill_result])
    assert ctx.term == "Python"
    assert ctx.category == "Technical Skills"
    assert ctx.context_type == ContextType.SKILL_CONTEXT
    assert len(ctx.sources) == 1
    assert "Python Software Foundation" in ctx.sources


# ---------------------------------------------------------------------------
# Test 6: Context builder handles multiple results
# ---------------------------------------------------------------------------
def test_06_context_builder_multiple_results(python_skill_result):
    res2 = SearchResult(
        chunk_id="tech_django_chunk_001",
        document_id="tech_django",
        term="Django",
        category="Technical Skills",
        difficulty="Intermediate",
        domain="Software Development",
        source="Django Software Foundation",
        text="Django is a Python-based web framework.",
        score=0.68,
        rank=2,
        related_terms=["ORM", "MVC Framework"],
    )
    builder = ContextBuilder(max_related_terms=5)
    ctx = builder.build("What is Python?", [python_skill_result, res2])
    assert ctx.term == "Python"  # Rank 1 is primary
    assert len(ctx.sources) == 2
    assert "Django Software Foundation" in ctx.sources
    assert "Scripting" in ctx.related_terms
    assert "ORM" in ctx.related_terms


# ---------------------------------------------------------------------------
# Test 7: Highest-ranked result becomes primary term
# ---------------------------------------------------------------------------
def test_07_highest_ranked_becomes_primary_term(swe_role_result, python_skill_result):
    # Pass SWE first (rank 1)
    builder = ContextBuilder()
    ctx = builder.build("What does a software developer do?", [swe_role_result, python_skill_result])
    assert ctx.term == "Software Developer"
    assert ctx.category == "Job Roles"
    assert ctx.context_type == ContextType.JOB_CONTEXT


# ---------------------------------------------------------------------------
# Test 8: Category is preserved
# ---------------------------------------------------------------------------
def test_08_category_preserved(certification_qual_result):
    builder = ContextBuilder()
    ctx = builder.build("What is professional certification?", [certification_qual_result])
    assert ctx.category == "Professional Qualifications"
    assert ctx.context_type == ContextType.QUALIFICATION_CONTEXT


# ---------------------------------------------------------------------------
# Test 9: Domain is preserved
# ---------------------------------------------------------------------------
def test_09_domain_preserved(api_industry_result):
    builder = ContextBuilder()
    ctx = builder.build("What is an API?", [api_industry_result])
    assert ctx.domain == "Systems & Networking"


# ---------------------------------------------------------------------------
# Test 10: Difficulty is preserved
# ---------------------------------------------------------------------------
def test_10_difficulty_preserved(certification_qual_result):
    builder = ContextBuilder()
    ctx = builder.build("What is professional certification?", [certification_qual_result])
    assert ctx.difficulty == "Intermediate"


# ---------------------------------------------------------------------------
# Test 11: Workplace context is preserved
# ---------------------------------------------------------------------------
def test_11_workplace_context_preserved(python_skill_result):
    builder = ContextBuilder()
    ctx = builder.build("What is Python?", [python_skill_result])
    assert ctx.workplace_context is not None
    assert "Python" in ctx.workplace_context
    assert "Software Development" in ctx.workplace_context


# ---------------------------------------------------------------------------
# Test 12: Related terms are preserved
# ---------------------------------------------------------------------------
def test_12_related_terms_preserved(python_skill_result):
    builder = ContextBuilder()
    ctx = builder.build("What is Python?", [python_skill_result])
    assert "Scripting" in ctx.related_terms
    assert "Automation" in ctx.related_terms


# ---------------------------------------------------------------------------
# Test 13: Sources are preserved
# ---------------------------------------------------------------------------
def test_13_sources_preserved(internship_employment_result):
    builder = ContextBuilder()
    ctx = builder.build("What does internship mean?", [internship_employment_result])
    assert "Fair Labor Standards Act (FLSA)" in ctx.sources


# ---------------------------------------------------------------------------
# Test 14: Job-role context is generated correctly from evidence
# ---------------------------------------------------------------------------
def test_14_job_role_context_generated(swe_role_result):
    builder = ContextBuilder()
    ctx = builder.build("What does a software developer do?", [swe_role_result])
    assert ctx.context_type == ContextType.JOB_CONTEXT
    assert "Software Developer" in ctx.workplace_context
    assert "Engineering" in ctx.why_it_matters


# ---------------------------------------------------------------------------
# Test 15: Technical-skill context is generated correctly from evidence
# ---------------------------------------------------------------------------
def test_15_technical_skill_context_generated(python_skill_result):
    builder = ContextBuilder()
    ctx = builder.build("What is Python?", [python_skill_result])
    assert ctx.context_type == ContextType.SKILL_CONTEXT
    assert "skill" in ctx.why_it_matters.lower()


# ---------------------------------------------------------------------------
# Test 16: Employment-term context is generated correctly from evidence
# ---------------------------------------------------------------------------
def test_16_employment_term_context_generated(internship_employment_result):
    builder = ContextBuilder()
    ctx = builder.build("What does internship mean?", [internship_employment_result])
    assert ctx.context_type == ContextType.EMPLOYMENT_CONTEXT
    assert "contracts" in ctx.why_it_matters.lower() or "workplace" in ctx.why_it_matters.lower()


# ---------------------------------------------------------------------------
# Test 17: Qualification context is generated correctly from evidence
# ---------------------------------------------------------------------------
def test_17_qualification_context_generated(certification_qual_result):
    builder = ContextBuilder()
    ctx = builder.build("What is professional certification?", [certification_qual_result])
    assert ctx.context_type == ContextType.QUALIFICATION_CONTEXT
    assert "credential" in ctx.why_it_matters.lower() or "professional" in ctx.why_it_matters.lower()


# ---------------------------------------------------------------------------
# Test 18: Industry terminology context is generated correctly from evidence
# ---------------------------------------------------------------------------
def test_18_industry_terminology_context_generated(api_industry_result):
    builder = ContextBuilder()
    ctx = builder.build("What is an API?", [api_industry_result])
    assert ctx.context_type == ContextType.INDUSTRY_CONTEXT
    assert "technical literacy" in ctx.why_it_matters.lower() or "collaborate" in ctx.why_it_matters.lower()


# ---------------------------------------------------------------------------
# Test 19: Intent detection patterns
# ---------------------------------------------------------------------------
def test_19_intent_detection_patterns():
    # Definition
    assert detect_query_intent("What is Python?") == QueryIntent.DEFINITION
    # Employment context
    assert detect_query_intent("Why is Python used in jobs?") == QueryIntent.EMPLOYMENT_CONTEXT
    assert detect_query_intent("What does internship mean?") == QueryIntent.EMPLOYMENT_CONTEXT
    # Usage context
    assert detect_query_intent("Where is Python used?") == QueryIntent.USAGE_CONTEXT
    # Role context
    assert detect_query_intent("What does a software developer do?") == QueryIntent.ROLE_CONTEXT
    # Qualification context
    assert detect_query_intent("What is professional certification?") == QueryIntent.QUALIFICATION_CONTEXT
    # Industry context
    assert detect_query_intent("What is an API?") == QueryIntent.INDUSTRY_CONTEXT
    # Related terms
    assert detect_query_intent("What skills are related to Python?") == QueryIntent.RELATED_TERMS


# ---------------------------------------------------------------------------
# Test 20: End-to-end flow works with mocked Phase 4/5/6 components
# ---------------------------------------------------------------------------
def test_20_end_to_end_contextual_pipeline_mocked(swe_role_result):
    mock_retriever = MagicMock()
    mock_retriever.search.return_value = [swe_role_result]

    mock_generator = MagicMock()
    mock_generator.generate.return_value = GeneratedAnswer(
        query="What does a software developer do?",
        term="Software Developer",
        category="Job Roles",
        simple_meaning="A software developer creates, tests, and maintains applications.",
        why_it_matters="Understanding this role helps beginners explore software engineering careers.",
        job_context="Software developers collaborate in agile engineering teams.",
        example="Building a customer checkout feature for an e-commerce website.",
        related_terms=["Python", "Git"],
        sources=["US Bureau of Labor Statistics"],
    )

    context_builder = ContextBuilder()

    controller = GuardrailController(
        retriever=mock_retriever,
        generator=mock_generator,
        context_builder=context_builder,
        threshold=0.55,
    )

    answer = controller.process_query("What does a software developer do?")
    assert isinstance(answer, GeneratedAnswer)
    assert answer.term == "Software Developer"
    assert answer.why_it_matters is not None
    assert "US Bureau of Labor Statistics" in answer.sources

    # Verify context builder was called
    mock_generator.generate.assert_called_once()
    call_kwargs = mock_generator.generate.call_args.kwargs
    assert "context" in call_kwargs
    assert call_kwargs["context"] is not None
    assert call_kwargs["context"].term == "Software Developer"
