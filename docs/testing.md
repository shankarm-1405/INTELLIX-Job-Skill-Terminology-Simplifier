# EMP-12: Job & Skill Terminology Simplifier
## Automated Testing Strategy & Test Suite Specification

This document details the testing architecture, test categorization, coverage breakdown, execution commands, and final verification results for EMP-12.

---

### 1. Testing Philosophy & Framework

EMP-12 employs a test-driven development (TDD) strategy using `pytest`. The testing harness adheres to three core standards:
1. **Deterministic Execution:** Tests do not rely on live network calls, stochastic temperature variations, or volatile mock timing.
2. **Zero Mock Leakage:** Mocks for Gemini API calls validate exact Pydantic schema contracts and system instructions without calling live billable endpoints.
3. **Continuous Regression Testing:** Every new phase adds tests to the master suite without modifying prior assertions or contracts.

---

### 2. Test Suite Taxonomy & Coverage

The test suite consists of **229 automated tests** across 14 dedicated test modules in `tests/`:

| Module | Category | Test Count | Key Invariants Tested |
| :--- | :--- | :---: | :--- |
| [`test_setup.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_setup.py) | Environment & Setup | 3 | Directory structure, dependency imports, config variables. |
| [`test_knowledge_base.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_knowledge_base.py) | Data Integrity | 10 | 60 records, 5 categories, unique IDs, non-empty fields. |
| [`test_ingestion.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_ingestion.py) | Document Processing | 14 | Ingestion pipeline, document normalization, chunk schema. |
| [`test_retrieval.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_retrieval.py) | Dense Retrieval | 20 | 384-dim vectors, FAISS IndexFlatIP, Top-K ranking, score bounds. |
| [`test_generator.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_generator.py) | LLM Generation | 20 | Grounded prompts, Gemini response parsing, GeneratedAnswer model. |
| [`test_guardrails.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_guardrails.py) | Reliability & Guardrails | 20 | Scope filtering, 0.55 threshold, grounding validation, safe fallbacks. |
| [`test_context.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_context.py) | Contextual Intelligence | 20 | 7 query intents, category context builder, difficulty tags. |
| [`test_ui.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_ui.py) | UI Presentation Helpers | 20 | Badge formatting, citation cleaning, safe query validation. |
| [`test_phase9.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_phase9.py) | Usability Features | 25 | Glossary explorer, category counts, keyword search, copy format. |
| [`test_evaluation.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_evaluation.py) | Benchmark Quality | 31 | 92 benchmark cases, Recall@K formulas, confusion matrix. |
| [`test_performance.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_performance.py) | Caching & Performance | 6 | Model caching, vector caching, latency bounds, memory safety. |
| [`test_phase11.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_phase11.py) | Disambiguation & Badges | 13 | ML vs MLE re-ranking, role stability, difficulty badges, guidance. |
| [`test_security.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_security.py) | Security & Credentials | 16 | Secret scanning, error sanitization, prompt injection, path traversal. |
| [`test_deployment.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_deployment.py) | Deployment Readiness | 11 | Dockerfile syntax, Streamlit config, 300-char query limit, statelessness. |
| **Total Test Suite** | **Complete System** | **229** | **229 Passed, 0 Failed, 1 Warning (100% Success)** |

---

### 3. Execution Commands

#### Run Entire Master Test Suite
```bash
python -m pytest tests/
```

#### Run Specific Test Modules
```bash
# Run security and deployment tests
python -m pytest tests/test_security.py tests/test_deployment.py -v

# Run performance benchmark tests
python -m pytest tests/test_performance.py -v

# Run evaluation suite tests
python -m pytest tests/test_evaluation.py -v
```

#### Run End-to-End Evaluation Benchmark
```bash
python src/evaluation/evaluator.py
```

---

### 4. Test Verification Report

```text
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\shank\Downloads\SKILL_DEVELOPMENT
plugins: anyio-4.12.1
collected 229 items

tests/test_context.py ....................                               [  8%]
tests/test_deployment.py ...........                                     [ 13%]
tests/test_evaluation.py ...............................                 [ 27%]
tests/test_generator.py ....................                             [ 35%]
tests/test_guardrails.py ....................                            [ 44%]
tests/test_ingestion.py ..............                                   [ 50%]
tests/test_knowledge_base.py ..........                                  [ 55%]
tests/test_performance.py ......                                         [ 57%]
tests/test_phase11.py .............                                      [ 63%]
tests/test_phase9.py .........................                           [ 74%]
tests/test_retrieval.py ....................                             [ 82%]
tests/test_security.py ................                                  [ 89%]
tests/test_setup.py ...                                                  [ 91%]
tests/test_ui.py ....................                                    [100%]

======================= 229 passed, 1 warning in 22.40s =======================
```
