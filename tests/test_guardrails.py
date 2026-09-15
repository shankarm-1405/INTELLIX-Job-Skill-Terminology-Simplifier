"""
EMP-12 Guardrail & Hallucination Control Test Suite
Contains 20 automated tests validating query scope checks, relevance thresholds,
evidence sufficiency, post-generation grounding validation, and deterministic fallbacks.
"""

from unittest.mock import MagicMock
import pytest

from src.config import RETRIEVAL_SCORE_THRESHOLD, SAFE_FALLBACK_MESSAGE
from src.generator.models import GeneratedAnswer
from src.guardrails.controller import GuardrailController
from src.guardrails.grounding import validate_grounding, validate_sources_against_evidence
from src.guardrails.models import (
    GroundingValidationResult,
    GuardrailDecision,
    SafeFallbackResponse,
)
from src.guardrails.relevance import (
    calculate_similarity_gap,
    classify_confidence,
    evaluate_category_consistency,
    evaluate_evidence,
    extract_matched_terms,
)
from src.guardrails.scope import normalize_query, validate_query_scope
from src.retrieval.models import SearchResult


# ---------------------------------------------------------------------------
# Test Fixtures: Sample SearchResults & Answers across all 5 EMP-12 Categories
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_python_result():
    return SearchResult(
        chunk_id="tech_python_chunk_001",
        document_id="tech_python",
        term="Python",
        category="Technical Skills",
        difficulty="Beginner",
        domain="Software Development",
        source="Python Software Foundation",
        text="Python is an interpreted, high-level, general-purpose programming language.",
        score=0.72,
        rank=1,
        related_skills=["Django", "Flask", "Pandas"],
        related_terms=["Programming Language", "Scripting", "Dynamic Typing"],
    )


@pytest.fixture
def sample_job_role_result():
    return SearchResult(
        chunk_id="role_swe_chunk_001",
        document_id="role_swe",
        term="Software Developer",
        category="Job Roles",
        difficulty="Beginner",
        domain="Engineering",
        source="US Bureau of Labor Statistics",
        text="A software developer designs, codes, and maintains computer software applications.",
        score=0.75,
        rank=1,
        related_skills=["Python", "Git", "System Design"],
        related_terms=["Software Engineer", "Programmer", "Full-Stack Developer"],
    )


@pytest.fixture
def sample_employment_term_result():
    return SearchResult(
        chunk_id="emp_internship_chunk_001",
        document_id="emp_internship",
        term="Internship",
        category="Employment Terms",
        difficulty="Beginner",
        domain="Human Resources",
        source="Fair Labor Standards Act (FLSA)",
        text="An internship is a period of work experience offered by an organization for students.",
        score=0.78,
        rank=1,
        related_skills=["Mentorship", "Networking"],
        related_terms=["Apprenticeship", "Trainee", "Stipend"],
    )


@pytest.fixture
def sample_qualification_result():
    return SearchResult(
        chunk_id="qual_cert_chunk_001",
        document_id="qual_cert",
        term="Professional Certification",
        category="Professional Qualifications",
        difficulty="Beginner",
        domain="Professional Development",
        source="ISO/IEC 17024 Standards",
        text="A professional certification is a credential earned to demonstrate proficiency.",
        score=0.76,
        rank=1,
        related_skills=["Exam Preparation", "Continuing Education"],
        related_terms=["Credential", "Accreditation", "License"],
    )


@pytest.fixture
def sample_industry_term_result():
    return SearchResult(
        chunk_id="ind_cloud_chunk_001",
        document_id="ind_cloud",
        term="Cloud Computing",
        category="Industry Terminology",
        difficulty="Beginner",
        domain="Information Technology",
        source="NIST SP 800-145",
        text="Cloud computing is a model for enabling ubiquitous on-demand network access to shared pools of computing resources.",
        score=0.77,
        rank=1,
        related_skills=["AWS", "Azure", "GCP"],
        related_terms=["SaaS", "IaaS", "Virtualization"],
    )


@pytest.fixture
def valid_python_answer():
    return GeneratedAnswer(
        query="What is Python?",
        term="Python",
        category="Technical Skills",
        simple_meaning="Python is a beginner-friendly programming language used for building websites, data analysis, and automation.",
        job_context="Software developers and data scientists use Python to build scalable web services and train machine learning models.",
        example="Writing a script to automatically process daily spreadsheet reports.",
        related_terms=["Django", "Scripting", "Dynamic Typing"],
        sources=["Python Software Foundation"],
    )


# ---------------------------------------------------------------------------
# Test 1: Valid known terminology query is allowed
# ---------------------------------------------------------------------------
def test_01_valid_known_terminology_allowed(sample_python_result):
    query = "What is Python?"
    decision = evaluate_evidence(query=query, retrieved_results=[sample_python_result], threshold=0.55)
    assert decision.allowed is True
    assert decision.confidence in ["HIGH", "MEDIUM"]
    assert "Python" in decision.matched_terms
    assert decision.top_score == 0.72


# ---------------------------------------------------------------------------
# Test 2: Unknown terminology query is rejected when evidence is insufficient
# ---------------------------------------------------------------------------
def test_02_unknown_query_rejected(sample_python_result):
    query = "What is ancient pottery dating?"
    # Simulate weak retrieval match with low similarity score
    low_res = SearchResult(
        chunk_id=sample_python_result.chunk_id,
        document_id=sample_python_result.document_id,
        term=sample_python_result.term,
        category=sample_python_result.category,
        difficulty=sample_python_result.difficulty,
        domain=sample_python_result.domain,
        source=sample_python_result.source,
        text=sample_python_result.text,
        score=0.32,
        rank=1,
    )
    decision = evaluate_evidence(query=query, retrieved_results=[low_res], threshold=0.55)
    assert decision.allowed is False
    assert decision.confidence == "LOW"
    assert "below the required evidence threshold" in decision.reason


# ---------------------------------------------------------------------------
# Test 3: Out-of-scope query is rejected
# ---------------------------------------------------------------------------
def test_03_out_of_scope_query_rejected():
    controller = GuardrailController(threshold=0.55)
    out_of_scope_queries = [
        "What is the weather today?",
        "Write a poem about nature",
        "Book me a flight to New York",
        "Who won today's cricket match?",
        "How to bake a chocolate cake?",
        "Tell me a joke",
    ]
    for q in out_of_scope_queries:
        decision = controller.evaluate_query(q, [])
        assert decision.allowed is False
        assert decision.is_out_of_scope is True
        assert "outside EMP-12 domain scope" in decision.reason


# ---------------------------------------------------------------------------
# Test 4: Empty query is rejected
# ---------------------------------------------------------------------------
def test_04_empty_query_rejected():
    is_valid, reason = validate_query_scope("")
    assert is_valid is False
    assert "empty or whitespace-only" in reason


# ---------------------------------------------------------------------------
# Test 5: Whitespace-only query is rejected
# ---------------------------------------------------------------------------
def test_05_whitespace_query_rejected():
    is_valid, reason = validate_query_scope("   \t  \n  ")
    assert is_valid is False
    assert "empty or whitespace-only" in reason


# ---------------------------------------------------------------------------
# Test 6: Low similarity result triggers fallback
# ---------------------------------------------------------------------------
def test_06_low_similarity_triggers_fallback(sample_python_result):
    sample_python_result.score = 0.48
    controller = GuardrailController(threshold=0.55)
    decision = controller.evaluate_query("What is Python?", [sample_python_result])
    assert decision.allowed is False
    fallback = controller.get_safe_fallback("What is Python?", decision.reason)
    assert isinstance(fallback, SafeFallbackResponse)
    assert fallback.is_fallback is True
    assert fallback.message == SAFE_FALLBACK_MESSAGE


# ---------------------------------------------------------------------------
# Test 7: Strong similarity result allows generation
# ---------------------------------------------------------------------------
def test_07_strong_similarity_allows_generation(sample_job_role_result):
    decision = evaluate_evidence(
        query="What does a software developer do?",
        retrieved_results=[sample_job_role_result],
        threshold=0.55,
    )
    assert decision.allowed is True
    assert decision.top_score >= 0.55
    assert "Software Developer" in decision.matched_terms


# ---------------------------------------------------------------------------
# Test 8: Retrieved term is recognized correctly
# ---------------------------------------------------------------------------
def test_08_retrieved_term_recognized(sample_employment_term_result):
    matched = extract_matched_terms(
        query="Can you explain what an internship entails?",
        results=[sample_employment_term_result],
    )
    assert "Internship" in matched


# ---------------------------------------------------------------------------
# Test 9: Category consistency is checked
# ---------------------------------------------------------------------------
def test_09_category_consistency_checked(sample_job_role_result):
    res2 = SearchResult(
        chunk_id="role_devops_chunk_001",
        document_id="role_devops",
        term="DevOps Engineer",
        category="Job Roles",
        difficulty="Intermediate",
        domain="Engineering",
        source="DevOps Research Assessment",
        text="A DevOps engineer bridges development and operations.",
        score=0.71,
        rank=2,
    )
    res3 = SearchResult(
        chunk_id="tech_git_chunk_001",
        document_id="tech_git",
        term="Git",
        category="Technical Skills",
        difficulty="Beginner",
        domain="Engineering",
        source="Git Documentation",
        text="Git is a distributed version control system.",
        score=0.68,
        rank=3,
    )
    # 2 out of 3 are Job Roles
    dominant = evaluate_category_consistency([sample_job_role_result, res2, res3], top_n=3)
    assert dominant == "Job Roles"


# ---------------------------------------------------------------------------
# Test 10: Source consistency is checked
# ---------------------------------------------------------------------------
def test_10_source_consistency_checked(sample_python_result):
    valid, unsupp = validate_sources_against_evidence(
        generated_sources=["Python Software Foundation"],
        retrieved_results=[sample_python_result],
    )
    assert valid is True
    assert len(unsupp) == 0


# ---------------------------------------------------------------------------
# Test 11: Generated answer with valid source passes validation
# ---------------------------------------------------------------------------
def test_11_valid_generated_sources_pass(valid_python_answer, sample_python_result):
    result = validate_grounding(
        answer=valid_python_answer,
        retrieved_results=[sample_python_result],
    )
    assert result.is_valid is True
    assert result.term_matches is True
    assert result.category_matches is True
    assert result.sources_valid is True


# ---------------------------------------------------------------------------
# Test 12: Generated answer with invented source fails validation
# ---------------------------------------------------------------------------
def test_12_invented_source_rejected(valid_python_answer, sample_python_result):
    fake_answer = valid_python_answer.model_copy(
        update={"sources": ["Random Hallucinated Blog Inc."]}
    )
    result = validate_grounding(
        answer=fake_answer,
        retrieved_results=[sample_python_result],
    )
    assert result.is_valid is False
    assert result.sources_valid is False
    assert "unsupported sources" in result.reason
    assert "Random Hallucinated Blog Inc." in result.unsupported_sources


# ---------------------------------------------------------------------------
# Test 13: Generated answer with unrelated term fails validation
# ---------------------------------------------------------------------------
def test_13_unrelated_term_rejected(valid_python_answer, sample_python_result):
    unrelated_answer = valid_python_answer.model_copy(
        update={"term": "Quantum Cryptography"}
    )
    result = validate_grounding(
        answer=unrelated_answer,
        retrieved_results=[sample_python_result],
    )
    assert result.is_valid is False
    assert result.term_matches is False
    assert "does not correspond to any term" in result.reason


# ---------------------------------------------------------------------------
# Test 14: Generated answer with mismatched category fails validation
# ---------------------------------------------------------------------------
def test_14_mismatched_category_rejected(valid_python_answer, sample_python_result):
    # Python is Technical Skills, but answer claims Job Roles
    mismatched_cat_answer = valid_python_answer.model_copy(
        update={"category": "Job Roles"}
    )
    result = validate_grounding(
        answer=mismatched_cat_answer,
        retrieved_results=[sample_python_result],
    )
    assert result.is_valid is False
    assert result.category_matches is False
    assert "conflicts with evidence category" in result.reason


# ---------------------------------------------------------------------------
# Test 15: Empty generated answer fails validation
# ---------------------------------------------------------------------------
def test_15_empty_generated_answer_rejected(sample_python_result):
    # Create an answer with too short meaning (bypassing model validator with whitespace)
    # Using object with empty simple_meaning
    mock_answer = MagicMock(spec=GeneratedAnswer)
    mock_answer.term = "Python"
    mock_answer.category = "Technical Skills"
    mock_answer.simple_meaning = "Short"
    mock_answer.sources = ["Python Software Foundation"]

    result = validate_grounding(
        answer=mock_answer,
        retrieved_results=[sample_python_result],
    )
    assert result.is_valid is False
    assert "overly short explanation" in result.reason


# ---------------------------------------------------------------------------
# Test 16: Confidence classification works
# ---------------------------------------------------------------------------
def test_16_confidence_classification():
    # High confidence: score >= 0.65 with term match
    tier_high, score_high = classify_confidence(0.72, has_term_match=True, relevant_count=2, threshold=0.55)
    assert tier_high == "HIGH"
    assert score_high > 0.72

    # Medium confidence: between 0.55 and 0.65
    tier_med, score_med = classify_confidence(0.58, has_term_match=False, relevant_count=1, threshold=0.55)
    assert tier_med == "MEDIUM"

    # Low confidence: below 0.55
    tier_low, score_low = classify_confidence(0.42, has_term_match=False, relevant_count=0, threshold=0.55)
    assert tier_low == "LOW"


# ---------------------------------------------------------------------------
# Test 17: Similarity gap is calculated correctly
# ---------------------------------------------------------------------------
def test_17_similarity_gap_calculation(sample_python_result, sample_job_role_result):
    sample_python_result.score = 0.75
    sample_job_role_result.score = 0.65
    second_score, gap = calculate_similarity_gap([sample_python_result, sample_job_role_result])
    assert second_score == 0.65
    assert gap == 0.10


# ---------------------------------------------------------------------------
# Test 18: Multiple relevant results strengthen evidence
# ---------------------------------------------------------------------------
def test_18_multiple_relevant_results_strengthen_evidence(sample_qualification_result):
    res2 = SearchResult(
        chunk_id="qual_cert_chunk_002",
        document_id="qual_cert",
        term="Professional Certification",
        category="Professional Qualifications",
        difficulty="Intermediate",
        domain="Professional Development",
        source="ISO/IEC 17024 Standards",
        text="Certification requires recertification and continuing professional development units.",
        score=0.74,
        rank=2,
    )
    decision = evaluate_evidence(
        query="What is professional certification?",
        retrieved_results=[sample_qualification_result, res2],
        threshold=0.55,
    )
    assert decision.allowed is True
    assert decision.relevant_result_count >= 2
    assert decision.confidence == "HIGH"


# ---------------------------------------------------------------------------
# Test 19: Safe fallback is deterministic
# ---------------------------------------------------------------------------
def test_19_safe_fallback_is_deterministic():
    controller = GuardrailController(threshold=0.55)
    fb1 = controller.get_safe_fallback("Unknown Query 1", "Low score")
    fb2 = controller.get_safe_fallback("Unknown Query 2", "Out of scope")

    assert fb1.message == fb2.message
    assert fb1.message == SAFE_FALLBACK_MESSAGE
    assert fb1.is_fallback is True
    assert fb1.confidence == "LOW"


# ---------------------------------------------------------------------------
# Test 20: Complete controlled pipeline works (Query -> Retrieval -> Guardrail -> Mock Gen -> Grounding -> Result)
# ---------------------------------------------------------------------------
def test_20_complete_controlled_pipeline(sample_industry_term_result):
    # Mock retriever
    mock_retriever = MagicMock()
    mock_retriever.search.return_value = [sample_industry_term_result]

    # Mock generator
    mock_generator = MagicMock()
    mock_generator.generate.return_value = GeneratedAnswer(
        query="What is cloud computing?",
        term="Cloud Computing",
        category="Industry Terminology",
        simple_meaning="Cloud computing is on-demand access to computer services like storage and servers over the internet.",
        job_context="Cloud engineers build and manage infrastructure on AWS, Azure, and Google Cloud.",
        example="Storing photos on Google Drive rather than on your phone's internal storage.",
        related_terms=["SaaS", "IaaS", "Virtualization"],
        sources=["NIST SP 800-145"],
    )

    controller = GuardrailController(
        retriever=mock_retriever,
        generator=mock_generator,
        threshold=0.55,
    )

    result = controller.process_query("What is cloud computing?")
    assert isinstance(result, GeneratedAnswer)
    assert result.term == "Cloud Computing"
    assert result.category == "Industry Terminology"
    assert "NIST SP 800-145" in result.sources
    mock_retriever.search.assert_called_once()
    mock_generator.generate.assert_called_once()
