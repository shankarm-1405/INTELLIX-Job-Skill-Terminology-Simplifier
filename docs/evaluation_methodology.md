# EMP-12: Evaluation Methodology

## 1. Overview and Purpose

The evaluation framework for **EMP-12: Job & Skill Terminology Simplifier** provides a reproducible, empirical, and rigorous methodology to measure:
- Retrieval quality of the dense FAISS vector search across domain terminology.
- Effectiveness of Phase 6 guardrails in accepting in-scope queries and blocking unsupported or out-of-scope queries.
- Accuracy of canonical terminology identification and category classification.
- Strictness of post-generation grounding and source citation provenance.
- Field completeness of generated structured explanations.
- Qualitative beginner friendliness, workplace contextual relevance, and explanatory clarity.
- Computational latency and resource efficiency.

The evaluation is designed to be **deterministic, offline-executable, and completely isolated** from production datasets.

---

## 2. Dataset Design & Taxonomy Distribution

The evaluation dataset is permanently stored at `data/evaluation/evaluation_dataset.json` and strictly segregated from `data/knowledge_base/`.

### 2.1 Case Composition
The benchmark comprises **92 structured evaluation cases**:

| Partition | Target Count | Actual Count | Description |
| :--- | :---: | :---: | :--- |
| **Supported Queries** | $\ge 50$ | **52** | In-scope terminology queries spanning all 5 official EMP-12 taxonomy categories. |
| **Unknown Terminology** | $\ge 20$ | **20** | Valid natural language queries about terminology outside the EMP-12 glossary (e.g., physics, biology, geology). |
| **Out-of-Scope Queries** | $\ge 20$ | **20** | Non-employment inquiries (weather, jokes, creative writing, cooking recipes, travel booking, shopping). |
| **Total Benchmark** | $\ge 90$ | **92** | Comprehensive evaluation suite. |

### 2.2 Supported Category Distribution
Supported queries are balanced across all five official EMP-12 taxonomy categories:

| Taxonomy Category | Minimum Required | Case Count in Benchmark | Representative Concepts |
| :--- | :---: | :---: | :--- |
| **Job Roles** | $\ge 10$ | **11** | Software Developer, Full Stack Developer, Frontend Developer, Backend Developer, Data Analyst, Data Scientist, Machine Learning Engineer, Cloud Engineer, DevOps Engineer, Cybersecurity Analyst, UI/UX Designer |
| **Technical Skills** | $\ge 10$ | **11** | Python, Java, JavaScript, SQL, HTML, CSS, Git, Docker, Kubernetes, AWS, REST API |
| **Employment Terms** | $\ge 10$ | **10** | Internship, Full-Time Employment, Part-Time Employment, Probation, Notice Period, Job Offer, Work Experience, Job Description, Employment Contract, Remote Work |
| **Professional Qualifications** | $\ge 10$ | **10** | Bachelor's Degree, Master's Degree, Diploma, Professional Certification, Technical Certification, Degree Qualification, Professional Qualification, Vocational Qualification, Industry Certification |
| **Industry Terminology** | $\ge 10$ | **10** | API, CI/CD, Deployment, Framework, Repository, Open Source, Cloud Computing, Version Control, Database, Agile |

### 2.3 Query Variations & Difficulty Levels
To assess system resilience, queries are formulated across four distinct variation types:
1. **Direct Queries:** Formal, dictionary-style inquiries (e.g., *"What is Python?"*, *"What is an internship?"*).
2. **Natural Beginner Queries:** Plain-language questions requesting simplicity (e.g., *"Can you explain SQL in simple words?"*, *"Tell me about full stack developer in simple words"*).
3. **Workplace Context Questions:** Inquiries targeting practical application on the job (e.g., *"How is Git used in the workplace for team collaboration?"*, *"What is a notice period when leaving a company?"*).
4. **Role / Action Questions:** Functional inquiries on responsibilities and operations (e.g., *"Backend developer role description and responsibilities"*, *"What does a UI/UX designer do?"*).
5. **Advanced Wording / Lexical Complexity:** Complex phrasing (e.g., *"Explain the role of a Cybersecurity Analyst in enterprise defense"*, *"Explain Kubernetes cluster orchestration in production systems"*).
6. **Whitespace and Casing Robustness:** Testing tolerance to leading/trailing whitespace and uppercase strings (e.g., `" python "`, `"BACHELOR'S DEGREE"`).

---

## 3. Evaluation Schema

Each test case adheres to the `EvaluationCase` Pydantic model (`src/evaluation/models.py`):

```python
class EvaluationCase(BaseModel):
    case_id: str                   # e.g., "eval_sup_job_01"
    query: str                     # e.g., "What is a Software Developer?"
    expected_type: str             # "supported", "unknown", or "out_of_scope"
    expected_category: Optional[str] = None
    expected_term: Optional[str] = None
    difficulty: Optional[str] = None  # "Beginner", "Intermediate", "Advanced"
    variation_type: Optional[str] = None
```

---

## 4. Evaluation Metrics & Formulas

### 4.1 Retrieval Quality Metrics (Phase 4)
Evaluated over all supported queries against the FAISS dense vector store (`sentence-transformers/all-MiniLM-L6-v2`):

- **Recall@K:** Percentage of supported queries where the expected canonical term (or a compatible token-equivalent) appears in the top $K$ retrieved search results:
  $$\text{Recall@K} = \frac{\sum_{i=1}^{N_{\text{supported}}} \mathbb{I}(\text{expected\_term} \in \text{Top-K}(q_i))}{N_{\text{supported}}} \times 100\%$$
  Measured for $K \in \{1, 3, 5\}$.
- **Category-Level Recall@5:** Recall@5 calculated independently for each of the five categories.
- **Top Score Distribution:** Minimum, maximum, and mean cosine similarity scores across partitions.

### 4.2 Guardrail & Safety Metrics (Phase 6)
Evaluated across all 92 cases to assess query classification and unknown term refusal:

- **Supported Acceptance Rate:**
  $$\text{Supported Acceptance Rate} = \frac{\text{Correctly Allowed Supported Cases}}{N_{\text{supported}}} \times 100\%$$
- **Unknown Rejection Rate:**
  $$\text{Unknown Rejection Rate} = \frac{\text{Correctly Blocked Unknown Cases}}{N_{\text{unknown}}} \times 100\%$$
- **Out-of-Scope Rejection Rate:**
  $$\text{OOS Rejection Rate} = \frac{\text{Correctly Blocked OOS Cases}}{N_{\text{oos}}} \times 100\%$$
- **Safe Fallback Rate:**
  $$\text{Safe Fallback Rate} = \frac{\text{Correct Fallbacks on Unsupported Cases}}{N_{\text{unknown}} + N_{\text{oos}}} \times 100\%$$
- **Unsupported Answer Rate:**
  $$\text{Unsupported Answer Rate} = \frac{\text{Unsupported Cases Producing Generated Answer}}{N_{\text{unknown}} + N_{\text{oos}}} \times 100\% \quad (\text{Target: } 0\%)$$
- **Guardrail Classification Matrix:**
  | Expected Partition | Predicted Allowed | Predicted Blocked |
  | :--- | :---: | :---: |
  | **Supported** | True Positive (TP) | False Negative (FN / False Reject) |
  | **Unknown** | False Positive (FP / False Accept) | True Negative (TN / Correct Reject) |
  | **Out-of-Scope** | False Positive (FP / False Accept) | True Negative (TN / Correct Reject) |

### 4.3 Answer & Grounding Metrics (Phase 5 & 6)
Evaluated on supported cases to ensure generated explanations remain strictly faithful to retrieved evidence:

- **Term Identification Accuracy:**
  $$\text{Term Accuracy} = \frac{\text{Answers with Correct Canonical Term}}{N_{\text{supported}}} \times 100\%$$
- **Category Accuracy:**
  $$\text{Category Accuracy} = \frac{\text{Answers with Correct Official Category}}{N_{\text{supported}}} \times 100\%$$
- **Source Provenance Accuracy:**
  $$\text{Source Provenance} = \frac{\text{Answers where All Citations Exist in Evidence}}{N_{\text{supported}}} \times 100\%$$
- **Grounding Acceptance Rate:**
  $$\text{Grounding Rate} = \frac{\text{Answers Passing Deterministic Grounding Validator}}{N_{\text{generated}}} \times 100\%$$
- **Field Completeness:** Availability percentage across 8 schema fields:
  `term`, `category`, `simple_meaning`, `why_it_matters`, `job_context`, `example`, `related_terms`, `sources`.

### 4.4 End-to-End Success Rate
A query is considered an **End-to-End Success** if and only if:
1. It is correctly accepted by the pre-retrieval scope check.
2. Retrieved evidence satisfies the similarity score threshold ($\ge 0.55$).
3. Context is constructed successfully.
4. Structured answer is generated.
5. Grounding validation passes (term, category, sources).
6. Canonical term and category align with expected ground truth.

---

## 5. Qualitative Manual Review Protocol

In addition to automated metrics, a representative sample of **35 cases** (25 supported across all 5 categories, 5 unknown, 5 out-of-scope) was qualitatively scored using a standardized 4-point rubric (0–3) and recorded in `data/evaluation/manual_review.json`.

### Rubric Criteria:
1. **Relevance (0–3):**
   - 0: Irrelevant / off-topic
   - 1: Partially relevant
   - 2: Relevant to the query
   - 3: Highly relevant, addressing the core term directly
2. **Beginner Clarity (0–3):**
   - 0: Unclear, confusing, or circular
   - 1: Difficult, excessive uncontextualized jargon
   - 2: Understandable and accessible to newcomers
   - 3: Very clear, intuitive analogies, plain English
3. **Workplace Context Usefulness (0–3):**
   - 0: Missing workplace context
   - 1: Weak or generic context
   - 2: Useful practical context (tools, duties, workflows)
   - 3: Strong, actionable workplace context directly applicable to job seekers
4. **Grounding & Evidence Alignment (0–3):**
   - 0: Unsupported or hallucinated facts
   - 1: Partially supported
   - 2: Strongly supported by retrieved chunks
   - 3: Clearly grounded with authoritative, traceable citations

---

## 6. Reproducibility & Test Execution

The evaluation suite is 100% automated and deterministic.

### Run Automated Unit & Evaluation Tests:
```powershell
python -m pytest tests/test_evaluation.py -v
```

### Run Benchmark Execution:
```powershell
python -c "from src.evaluation.evaluator import TerminologyEvaluator; TerminologyEvaluator().run_benchmark()"
```

Results are automatically saved to `data/evaluation/results.json`.
