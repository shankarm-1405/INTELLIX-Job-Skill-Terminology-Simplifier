# EMP-12: Job & Skill Terminology Simplifier
## Demonstration Contingency & Offline Backup Plan

This document provides step-by-step procedures for conducting a successful project evaluation if internet connectivity is lost, Google Gemini API endpoints are unreachable, or API quotas are exhausted during the live review.

---

### 1. Transparency Rule
> **Do not attempt to disguise an API outage or fabricate live generation.**
> State clearly to the committee:
> *“The external Google Gemini API endpoint is currently unreachable or unconfigured. However, the core architecture of EMP-12—including local dense vector embeddings, FAISS similarity search, the 60-record glossary, and deterministic guardrails—operates 100% offline and locally on our machine.”*

---

### 2. Offline Demonstration Flow

#### Backup Step 1: Demonstrate the Local Knowledge Base & Taxonomy
- Show the 5 structured JSON datasets in `data/knowledge_base/`:
  - `job_roles.json` (12 records)
  - `technical_skills.json` (15 records)
  - `employment_terms.json` (12 records)
  - `qualifications.json` (9 records)
  - `industry_terminology.json` (12 records)
- Open any record and demonstrate the Pydantic schema: canonical term, category, simple meaning, job context, example, related terms, sources, and difficulty level.

#### Backup Step 2: Demonstrate the Interactive Glossary Explorer
- In the Streamlit UI, scroll to the **Glossary Explorer**:
  - Show that browsing all 60 terms operates completely offline without network calls.
  - Filter by **Professional Qualifications** (showing 9 terms).
  - Search for `"AWS"` to show real-time alias and keyword matching.
  - Expand the card to show verified plain-English explanations and citations.

#### Backup Step 3: Demonstrate Vector Search via Python CLI
- Run the offline vector inspection script:
  ```powershell
  python src/retrieval/inspect_retrieval.py
  ```
- Demonstrate that `all-MiniLM-L6-v2` embeds queries into 384 dimensions and queries `models/vector_store/index.faiss` on CPU in < 5 ms, returning exact cosine similarity scores.

#### Backup Step 4: Demonstrate Deterministic Guardrails
- Run the guardrail threshold evaluation script:
  ```powershell
  python src/guardrails/evaluate_threshold.py
  ```
- Show the committee the empirical cosine separation: supported queries average **0.7026** while unsupported queries average **0.1603**, proving the mathematical validity of the 0.55 threshold without calling external LLMs.

#### Backup Step 5: Demonstrate the 92-Case Benchmark Suite
- Run the automated evaluation suite:
  ```powershell
  python src/evaluation/evaluator.py
  ```
- Show the real-time execution across 92 benchmark cases confirming **100% Recall@1, 100% Category Accuracy, and 100% Guardrail Rejection**.

#### Backup Step 6: Demonstrate the 229 Automated Tests
- Run the pytest suite:
  ```powershell
  python -m pytest tests/
  ```
- Show **229 passed tests** demonstrating complete code health and test-driven rigor across all 12 prior phases.
