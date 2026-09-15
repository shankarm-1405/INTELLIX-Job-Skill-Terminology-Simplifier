# Phase 7: Contextual Intelligence

## 1. Phase 7 Objective

The objective of Phase 7 for **EMP-12: Job & Skill Terminology Simplifier** is to enhance terminology explanations by understanding the **context in which an employment or technology term is asked**. 

Rather than generating isolated, dictionary-style definitions, the system connects retrieved evidence into meaningful employment and technology relationships:
- What the term means
- Where and how it is applied in the workplace
- How it connects to specific job roles and technical skill sets
- Why the terminology matters to beginners and career transitioners
- Traceable companion terms and authoritative references

All contextual enhancements remain strictly grounded in retrieved evidence from the EMP-12 knowledge base.

---

## 2. Definition of Contextual Intelligence in EMP-12

In EMP-12, "Contextual Intelligence" does **not** mean general-purpose conversation, personality modeling, or open-ended web reasoning. 

Instead, it is defined as:
> **The systematic transformation of retrieved terminology chunks into structured, category-aware, difficulty-aware, and intent-aligned workplace explanations without introducing unverified external facts.**

### Example
When a user asks:
```text
What is Python?
```
Instead of merely stating:
```text
Python is a programming language.
```
The contextual system provides:
```text
Term: Python
Category: Technical Skills
Domain: Software Development
Difficulty: Beginner

Simple Meaning:
Python is an interpreted, high-level programming language known for readable syntax.

Why It Matters:
Learning about Python is valuable because it is a beginner-level skill frequently required in Software Development positions.

Workplace Context:
In professional environments, Python is utilized in Software Development to accomplish development, automation, and operational goals.

Related Terms:
Scripting, Automation, Dynamic Typing, Django

Sources:
Python Software Foundation
```

---

## 3. Supported Context Types

The context layer models distinct perspectives based on the terminology domain (`src/context/models.py`):

| Context Type | Applicable Domain / Category | Contextual Focus |
| :--- | :--- | :--- |
| `TERM_CONTEXT` | General Terminology | Baseline canonical definition and domain alignment |
| `JOB_CONTEXT` | Job Roles | Workplace responsibilities, team collaboration, career pathways |
| `SKILL_CONTEXT` | Technical Skills | Practical workplace application, system tools, automation tasks |
| `EMPLOYMENT_CONTEXT` | Employment Terms | Workplace arrangements, rights, contracts, career milestones |
| `QUALIFICATION_CONTEXT` | Professional Qualifications | Credential value, competency verification, standard certifications |
| `INDUSTRY_CONTEXT` | Industry Terminology | Standard architectural concepts, protocols, technical infrastructure |
| `RELATED_TERMS_CONTEXT`| Companion Terms Exploration | Traceable prerequisite or adjacent concepts |

---

## 4. Context Extraction from Evidence

The contextual layer consumes the output of Phase 4 Retrieval (`SearchResult` objects). It:
1. **Never queries raw JSON files directly** during query execution.
2. **Never executes external web search**.
3. **Never creates a secondary database**.

The extraction flow:
```text
Phase 4 Retrieval Results (SearchResult list)
                ↓
    Extract Primary Candidate (Rank 1)
                ↓
    Aggregate Distinct Related Terms & Sources
                ↓
    Consolidate Passive Evidence Excerpts
                ↓
    Construct Structured TerminologyContext
```

---

## 5. Intent Detection Rules

Query intent is detected deterministically in `src/context/intent.py` using high-precision regex pattern matching and category heuristics without machine learning models:

| User Query Pattern | Classified Intent | Target Context Presentation |
| :--- | :--- | :--- |
| *"What is Python?"* | `DEFINITION` | Simple beginner meaning and primary concept |
| *"Why is Python used in jobs?"* | `EMPLOYMENT_CONTEXT` | How the skill functions in workplace tasks |
| *"Where is Python used?"* | `USAGE_CONTEXT` | Industry domains and practical applications |
| *"What does a software developer do?"* | `ROLE_CONTEXT` | Responsibilities and team role duties |
| *"What does internship mean?"* | `EMPLOYMENT_CONTEXT` | Workplace training and contract context |
| *"What is professional certification?"* | `QUALIFICATION_CONTEXT` | Credential recognition and standard competency |
| *"What is an API?"* | `INDUSTRY_CONTEXT` | Systems interaction and software standards |
| *"What skills are related to Python?"* | `RELATED_TERMS` | Curated companion skills and concepts |

---

## 6. Category-Aware Contextual Behavior

The system tailors its contextual representation across all five EMP-12 taxonomy categories:

1. **Job Roles (e.g., Software Developer, DevOps Engineer):**
   Focuses on core workplace duties, collaborative tasks, and day-to-day responsibilities in the industry.
2. **Technical Skills (e.g., Python, Git, Docker):**
   Focuses on how the skill is practically utilized in engineering and automation workflows.
3. **Employment Terms (e.g., Internship, Full-Time, Severance):**
   Focuses on workplace agreements, employee-employer arrangements, and career development milestones.
4. **Professional Qualifications (e.g., Professional Certification, PMP):**
   Focuses on verified competency standards, credentials, and professional development without claiming employment guarantees.
5. **Industry Terminology (e.g., Cloud Computing, API, Microservices):**
   Focuses on architectural standards and technical communication across cross-functional engineering teams.

---

## 7. Domain-Aware Context

Every retrieved chunk includes an authoritative functional domain (e.g., *Software Development*, *Information Technology*, *Human Resources*, *Professional Development*, *Systems & Networking*). 

The context builder incorporates this domain directly into the explanation, contextualizing where a beginner will encounter the term in real organizations.

---

## 8. Difficulty-Aware Explanations

Each term carries an empirical difficulty rating:
- **Beginner:** Emphasizes simple language, minimal jargon, short declarative sentences, and concrete analogies.
- **Intermediate:** Introduces practical domain vocabulary and realistic system contexts while keeping the explanation accessible.
- **Advanced:** Explains specialized architectural or operational concepts while breaking them down into beginner-friendly components.

The overall system remains strictly beginner-oriented.

---

## 9. Related Terminology Handling

Related terms are preserved from retrieved candidate metadata:
- Capped at `CONTEXT_MAX_RELATED_TERMS = 5` to avoid overwhelming beginners.
- Only terms explicitly present in the retrieved evidence are included.
- No external or hallucinated terminology relationships are added.

---

## 10. Employment Context & "Why It Matters"

To assist beginners and career transitioners, Phase 7 generates a dedicated `why_it_matters` guidance field grounded in the evidence:
- Connects the terminology to career pathways.
- Clarifies workplace relevance without making unsubstantiated promises (e.g., never promises specific salaries or guaranteed hiring).

---

## 11. Context Merging Across Multiple Results

When multiple search results are retrieved:
1. **Rank 1 Candidate:** Determines the primary canonical term, primary domain, and primary category.
2. **Supporting Candidates:** Merged for additional related terms and authoritative source citations only if they align with the canonical record.
3. **Noise Filtering:** Results with divergent categories or low relevance scores are excluded from context synthesis.

---

## 12. Ambiguity Handling

For polysemous terms or terms appearing across multiple contexts:
- The system resolves the term according to the highest-quality retrieved evidence chunk.
- If evidence is genuinely contradictory or ambiguous, Phase 6 guardrails trigger a safe fallback rather than guessing alternative definitions.

---

## 13. Source Traceability

Source provenance is strictly preserved throughout the contextual transformation:
- All source citations from retrieved evidence are preserved in `TerminologyContext.sources`.
- Post-generation grounding validation (`src/guardrails/grounding.py`) verifies that every citation in the generated response matches retrieved evidence.

---

## 14. Context Validation

Deterministic quality assurance is performed by `ContextValidator` (`src/context/validator.py`):
- Term non-emptiness ($\ge 2$ characters).
- Category membership in `SUPPORTED_CATEGORIES`.
- Difficulty membership in `{"Beginner", "Intermediate", "Advanced"}`.
- Domain non-emptiness.
- Cross-verification against retrieved evidence chunks (ensuring canonical term, category, and sources match).

---

## 15. Integration with Phase 6 Guardrails

Phase 7 sits between Phase 6 Evidence Checking and Phase 5 LLM Generation:

```text
                    USER QUERY
                        │
                        ▼
              ┌───────────────────┐
              │ Phase 6           │
              │ Query Validation  │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Phase 4           │
              │ Retrieval         │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Phase 6           │
              │ Evidence Check    │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Phase 7           │
              │ Context Builder   │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Phase 5           │
              │ LLM Generation    │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Phase 6           │
              │ Grounding Check   │
              └─────────┬─────────┘
                        │
                        ▼
                 CONTEXTUAL ANSWER
```

Phase 6 guardrails are never bypassed:
- Low-evidence queries are blocked before reaching the context builder.
- Generated outputs are verified for term, category, and source provenance before delivery.

---

## 16. Testing Methodology

The test suite (`tests/test_context.py`) comprises 20 automated tests:
1. `test_01_context_model_validation`: Verifies schema constraints.
2. `test_02_empty_term_rejected`: Asserts validation error on empty term.
3. `test_03_invalid_category_rejected`: Asserts rejection of unsupported categories.
4. `test_04_invalid_difficulty_rejected`: Asserts rejection of unapproved difficulty levels.
5. `test_05_context_builder_single_result`: Asserts context synthesis with single candidate.
6. `test_06_context_builder_multiple_results`: Asserts aggregation across multiple chunks.
7. `test_07_highest_ranked_becomes_primary_term`: Asserts rank-1 canonical dominance.
8. `test_08_category_preserved`: Asserts category integrity.
9. `test_09_domain_preserved`: Asserts domain integrity.
10. `test_10_difficulty_preserved`: Asserts difficulty level integrity.
11. `test_11_workplace_context_preserved`: Asserts workplace context derivation.
12. `test_12_related_terms_preserved`: Asserts related terms matching.
13. `test_13_sources_preserved`: Asserts source preservation.
14. `test_14_job_role_context_generated`: Validates Job Roles contextualization.
15. `test_15_technical_skill_context_generated`: Validates Technical Skills contextualization.
16. `test_16_employment_term_context_generated`: Validates Employment Terms contextualization.
17. `test_17_qualification_context_generated`: Validates Professional Qualifications contextualization.
18. `test_18_industry_terminology_context_generated`: Validates Industry Terminology contextualization.
19. `test_19_intent_detection_patterns`: Validates all 7 intent types.
20. `test_20_end_to_end_contextual_pipeline_mocked`: Validates full mocked RAG execution with context layer.

All tests run locally using mocks with zero live Gemini API dependencies.

---

## 17. Known Limitations

> [!NOTE]
> Contextual intelligence improves the presentation, structure, and workplace relevance of terminology, but **does not create new factual knowledge**.
> 
> If a specific nuance, tool, or relationship is not present in the EMP-12 knowledge base, the system will not fabricate it.
