"""
EMP-12 LLM Answer Generation Test Suite
Validates prompt construction, schema validation, mock Gemini integration,
metadata/source preservation, and boundary error handling.
"""

import inspect
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    DEFAULT_GENERATION_TEMPERATURE,
    GEMINI_MODEL,
    SUPPORTED_CATEGORIES,
)
from src.generator.generator import TerminologyGenerator, extract_json_payload
from src.generator.models import GeneratedAnswer
from src.generator.prompt_builder import SYSTEM_INSTRUCTION, PromptBuilder
from src.retrieval.models import SearchResult


def create_sample_search_results() -> list[SearchResult]:
    """Helper creating representative SearchResult items for test fixtures."""
    return [
        SearchResult(
            chunk_id="tech_python_chunk_001",
            document_id="tech_python",
            term="Python",
            category="Technical Skills",
            difficulty="Beginner",
            domain="Software Development",
            source="Python Software Foundation Official Documentation (python.org)",
            text="Term: Python\nCategory: Technical Skills\nShort Definition: A versatile programming language.",
            score=0.8850,
            rank=1,
            related_skills=["Programming", "SQL", "Git"],
            related_terms=["Data Science", "Machine Learning"],
        ),
        SearchResult(
            chunk_id="role_software_developer_chunk_001",
            document_id="role_software_developer",
            term="Software Developer",
            category="Job Roles",
            difficulty="Beginner",
            domain="Software Development",
            source="U.S. Bureau of Labor Statistics (BLS)",
            text="Term: Software Developer\nCategory: Job Roles\nShort Definition: An engineer who builds software.",
            score=0.6200,
            rank=2,
            related_skills=["Programming", "Problem Solving"],
            related_terms=["Backend Developer", "Full Stack Developer"],
        ),
    ]


def test_01_generator_configuration_loads_correctly():
    """Test 1: Generator configuration parameters load with expected defaults."""
    assert GEMINI_MODEL is not None
    assert len(GEMINI_MODEL.strip()) > 0
    assert 0.0 <= DEFAULT_GENERATION_TEMPERATURE <= 1.0


def test_02_missing_api_key_handled_correctly():
    """Test 2: Missing client and API key raises clear descriptive error."""
    gen = TerminologyGenerator(api_key="", client=None)
    results = create_sample_search_results()
    with pytest.raises(ValueError, match="Gemini API client is not configured"):
        gen.generate("What is Python?", results)


def test_03_prompt_builder_includes_query():
    """Test 3: PromptBuilder user prompt contains the exact user query."""
    query = "Explain Docker to a beginner."
    results = create_sample_search_results()
    sys_inst, user_prompt = PromptBuilder.build_prompt(query, results)

    assert query in user_prompt
    assert "USER QUERY:" in user_prompt
    assert sys_inst == SYSTEM_INSTRUCTION


def test_04_prompt_builder_includes_retrieved_evidence():
    """Test 4: PromptBuilder user prompt includes the retrieved chunk texts."""
    query = "What is Python?"
    results = create_sample_search_results()
    _, user_prompt = PromptBuilder.build_prompt(query, results)

    assert "RETRIEVED EMP-12 EVIDENCE:" in user_prompt
    assert "tech_python_chunk_001" not in user_prompt  # IDs not cluttering prompt
    assert "Python Software Foundation" in user_prompt
    assert "A versatile programming language" in user_prompt


def test_05_prompt_builder_includes_category_and_source_metadata():
    """Test 5: PromptBuilder formats category, difficulty, domain, and source clearly."""
    results = create_sample_search_results()
    _, user_prompt = PromptBuilder.build_prompt("Query", results)

    assert "Category: Technical Skills" in user_prompt
    assert "Source: Python Software Foundation" in user_prompt
    assert "Difficulty: Beginner" in user_prompt
    assert "Similarity Score: 0.8850" in user_prompt


def test_06_prompt_builder_does_not_discard_evidence():
    """Test 6: All passed SearchResult items appear in the formatted evidence block."""
    results = create_sample_search_results()
    evidence_block = PromptBuilder.format_evidence_block(results)

    assert "[Source 1]" in evidence_block
    assert "[Source 2]" in evidence_block
    assert "Software Developer" in evidence_block
    assert "Python" in evidence_block


def test_07_generated_answer_schema_validates_correctly():
    """Test 7: Valid data structure successfully instantiates GeneratedAnswer."""
    answer = GeneratedAnswer(
        query="What is Python?",
        term="Python",
        category="Technical Skills",
        simple_meaning="Python is a beginner-friendly programming language used for building applications.",
        job_context="Frequently required in software engineering and data science roles.",
        example="A developer writes a script to automate spreadsheet reports.",
        related_terms=["Programming", "Data Science"],
        sources=["Python Software Foundation (python.org)"],
    )
    assert answer.term == "Python"
    assert answer.category == "Technical Skills"
    assert len(answer.sources) == 1


def test_08_malformed_generated_output_is_rejected():
    """Test 8: Incomplete or malformed JSON payloads fail Pydantic validation."""
    with pytest.raises(Exception):
        # Missing required simple_meaning and sources
        GeneratedAnswer(
            query="What is Python?",
            term="Python",
            category="Technical Skills",
        )

    with pytest.raises(ValueError, match="Category 'InvalidCategory' is not in supported"):
        GeneratedAnswer(
            query="What is Python?",
            term="Python",
            category="InvalidCategory",
            simple_meaning="Meaningful explanation here.",
            sources=["Valid Source"],
        )


def test_09_empty_query_is_rejected():
    """Test 9: Empty or whitespace query raises ValueError."""
    mock_client = MagicMock()
    gen = TerminologyGenerator(client=mock_client)
    results = create_sample_search_results()

    with pytest.raises(ValueError, match="Query string cannot be empty"):
        gen.generate("", results)

    with pytest.raises(ValueError, match="Query string cannot be empty"):
        gen.generate("   ", results)


def test_10_empty_retrieved_evidence_handled_safely():
    """Test 10: Empty retrieved_results list raises ValueError without calling API."""
    mock_client = MagicMock()
    gen = TerminologyGenerator(client=mock_client)

    with pytest.raises(ValueError, match="Cannot generate explanation without retrieved evidence"):
        gen.generate("What is Python?", [])
    assert mock_client.models.generate_content.call_count == 0


def test_11_multiple_retrieved_results_passed_to_generator():
    """Test 11: Generator formats and delivers multiple SearchResult objects."""
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "term": "Python",
        "category": "Technical Skills",
        "simple_meaning": "Python is a clean, readable programming language.",
        "job_context": "Used in web development and data analytics.",
        "example": "Automating reports with pandas.",
        "related_terms": ["SQL", "Git"],
        "sources": ["Python Software Foundation"],
    })
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp

    gen = TerminologyGenerator(client=mock_client)
    results = create_sample_search_results()
    answer = gen.generate("What is Python?", results)

    assert mock_client.models.generate_content.call_count == 1
    call_args = mock_client.models.generate_content.call_args
    assert "Python" in call_args.kwargs["contents"]
    assert "Software Developer" in call_args.kwargs["contents"]
    assert isinstance(answer, GeneratedAnswer)


def test_12_sources_are_preserved():
    """Test 12: Cited sources in LLM response are retained on GeneratedAnswer."""
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "term": "Python",
        "category": "Technical Skills",
        "simple_meaning": "Python is an easy-to-read programming language.",
        "sources": ["Python Software Foundation (python.org)"],
    })
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp

    gen = TerminologyGenerator(client=mock_client)
    answer = gen.generate("Python", create_sample_search_results())
    assert "Python Software Foundation (python.org)" in answer.sources


def test_13_category_information_preserved():
    """Test 13: Returned category must match one of EMP-12's 5 official categories."""
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "term": "Software Developer",
        "category": "Job Roles",
        "simple_meaning": "Builds applications and systems.",
        "sources": ["BLS Handbook"],
    })
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp

    gen = TerminologyGenerator(client=mock_client)
    answer = gen.generate("Software Developer", create_sample_search_results())
    assert answer.category == "Job Roles"
    assert answer.category in SUPPORTED_CATEGORIES


def test_14_generator_does_not_access_raw_kb_files():
    """Test 14: Inspect source code to verify generator never imports or reads data/knowledge_base."""
    gen_source = inspect.getsource(TerminologyGenerator)
    assert "knowledge_base" not in gen_source
    assert "job_roles.json" not in gen_source
    assert "technical_skills.json" not in gen_source


def test_15_generator_does_not_perform_retrieval_internally():
    """Test 15: Generator does not invoke FAISS or sentence-transformers directly."""
    gen_source = inspect.getsource(TerminologyGenerator)
    assert "FAISS" not in gen_source
    assert "SentenceTransformer" not in gen_source
    assert "faiss" not in gen_source


def test_16_generation_configuration_loaded():
    """Test 16: Custom temperature and model parameters are honored."""
    gen = TerminologyGenerator(api_key="mock_key", model_name="custom-model", temperature=0.0)
    assert gen.model_name == "custom-model"
    assert gen.temperature == 0.0


def test_17_api_errors_handled_cleanly():
    """Test 17: Runtime errors from the Gemini client are wrapped gracefully."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("API connection timeout")

    gen = TerminologyGenerator(client=mock_client)
    with pytest.raises(RuntimeError, match="Gemini API generation failed: API connection timeout"):
        gen.generate("What is Python?", create_sample_search_results())


def test_18_mock_successful_gemini_response():
    """Test 18: Mock Gemini response with markdown code block parses cleanly."""
    mock_resp = MagicMock()
    mock_resp.text = """```json
    {
      "term": "Internship",
      "category": "Employment Terms",
      "simple_meaning": "A supervised period of practical work experience.",
      "job_context": "Commonly offered to students during summer terms.",
      "example": "A student works for 10 weeks at a software company.",
      "related_terms": ["On-the-Job Training", "Full-Time Employment"],
      "sources": ["U.S. Department of Labor (DOL)"]
    }
    ```"""
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp

    gen = TerminologyGenerator(client=mock_client)
    answer = gen.generate("What is an internship?", create_sample_search_results())

    assert answer.term == "Internship"
    assert answer.category == "Employment Terms"
    assert "practical work experience" in answer.simple_meaning


def test_19_generated_answer_contains_beginner_friendly_fields():
    """Test 19: GeneratedAnswer provides structured access to beginner-friendly explanation fields."""
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "term": "CI/CD",
        "category": "Industry Terminology",
        "simple_meaning": "Continuous integration and deployment automated pipeline.",
        "job_context": "Daily duty of DevOps engineers.",
        "example": "Code tests and deploys automatically on commit.",
        "related_terms": ["DevOps", "Git"],
        "sources": ["IEEE Software Engineering Guide"],
    })
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp

    gen = TerminologyGenerator(client=mock_client)
    answer = gen.generate("Explain CI/CD", create_sample_search_results())

    assert answer.term == "CI/CD"
    assert answer.category == "Industry Terminology"
    assert answer.job_context is not None
    assert answer.example is not None


def test_20_end_to_end_pipeline_integration(monkeypatch):
    """Test 20: Controlled integration test from SearchResult to GeneratedAnswer."""
    # Build a controlled SearchResult from Phase 4
    sample_result = SearchResult(
        chunk_id="ind_ci_cd_chunk_001",
        document_id="ind_ci_cd",
        term="CI/CD",
        category="Industry Terminology",
        difficulty="Intermediate",
        domain="DevOps",
        source="IEEE Software Engineering Best Practices for Continuous Delivery",
        text="Term: CI/CD\nCategory: Industry Terminology\nShort Definition: Automated software delivery.",
        score=0.8200,
        rank=1,
        related_skills=["Git", "Docker"],
        related_terms=["DevOps", "Deployment"],
    )

    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "term": "CI/CD",
        "category": "Industry Terminology",
        "simple_meaning": "CI/CD is like an automated assembly line for code.",
        "job_context": "Used continuously by DevOps engineers to test and deploy builds.",
        "example": "A developer saves code and an automated server runs tests immediately.",
        "related_terms": ["DevOps", "Deployment"],
        "sources": ["IEEE Software Engineering Best Practices for Continuous Delivery"],
    })
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp

    gen = TerminologyGenerator(client=mock_client)
    answer = gen.generate("What is CI/CD?", [sample_result])

    assert answer.query == "What is CI/CD?"
    assert answer.term == "CI/CD"
    assert answer.category == "Industry Terminology"
    assert "automated assembly line" in answer.simple_meaning
    assert answer.sources == ["IEEE Software Engineering Best Practices for Continuous Delivery"]


if __name__ == "__main__":
    pytest.main(["-v", __file__])
