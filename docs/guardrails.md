# Phase 6: Hallucination & Unknown Query Control

## 1. Phase 6 Objective

The primary objective of Phase 6 for **EMP-12: Job & Skill Terminology Simplifier** is to establish an explainable, deterministic reliability and guardrail layer surrounding the Phase 4 Retrieval and Phase 5 LLM Generation modules. 

The system prevents the LLM from producing confident, unsupported explanations when retrieved evidence is:
- Irrelevant
- Insufficient or too weak
- Missing
- Contradictory
- Outside the project's employment and technology terminology scope

When evidence is inadequate, the system prefers:
> *"I don't have enough information in the EMP-12 knowledge base to explain this term reliably."*

rather than fabricating an answer.

---

## 2. Why Hallucination Control Is Required

In domain-specific retrieval-augmented generation (RAG) applications for beginners, unconstrained LLMs exhibit several failure modes:
1. **Hallucinated Definitions:** Inventing plausible-sounding but technically inaccurate definitions for rare or unknown acronyms.
2. **Fabricated Citations:** Hallucinating fake organizations, documentation titles, or standards bodies when evidence is absent.
3. **Out-of-Scope Creep:** Answering arbitrary general knowledge questions (weather, politics, creative writing) that dilute the specialized focus of the EMP-12 assistant.
4. **Category Drift:** Confusing job roles with technical skills or qualifications (e.g., claiming "Python" is a "Job Role" rather than a "Technical Skill").

Phase 6 enforces strict evidence bounds before and after generation without modifying Phase 4 retrieval or Phase 5 generation logic.

---

## 3. High-Level Guardrail Architecture

```text
                       USER QUERY
                           │
                           ▼
                  ┌─────────────────┐
                  │ Query Validation│ (Format, length >= 2, domain scope)
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Phase 4         │
                  │ RAG Retrieval   │ (Dense FAISS search, cosine similarity)
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Evidence        │ (Threshold >= 0.55, term matching,
                  │ Evaluation      │  result count, category consistency)
                  └────────┬────────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
             SUFFICIENT          INSUFFICIENT
                 │                   │
                 ▼                   ▼
        ┌─────────────────┐    ┌──────────────┐
        │ Phase 5         │    │ Safe         │
        │ LLM Generation  │    │ Fallback     │
        └────────┬────────┘    └──────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Grounding       │ (Term match, category match,
        │ Validation      │  source citation provenance)
        └────────┬────────┘
                 │
           ┌─────┴─────┐
           │           │
         VALID       INVALID
           │           │
           ▼           ▼
       Final Answer  Fallback
```

---

## 4. Query Validation & Domain Scope Detection

The pre-retrieval validation layer (`src/guardrails/scope.py`) inspects incoming user queries before executing expensive vector embeddings or similarity searches.

### Validation Rules
1. **Non-Null & Non-Empty:** Empty strings or whitespace-only queries are blocked.
2. **Length Floor:** Queries must be at least 2 characters long.
3. **Domain Scope Alignment:** Non-employment intents are intercepted using lightweight, high-precision pattern matching:
   - Creative writing requests (poems, jokes, stories)
   - Weather and meteorological queries
   - Sports scores and live entertainment
   - Travel reservations (flights, hotels)
   - Personal financial calculations (mortgage, tax)
   - Commercial shopping recommendations (phones, electronics)
   - Culinary recipes
   - General political officeholders outside professional glossaries

Queries flagged as out-of-scope are immediately routed to the deterministic safe fallback without invoking retrieval or LLM generation.

---

## 5. Relevance Threshold Rationale

The configurable threshold `RETRIEVAL_SCORE_THRESHOLD` resides in `src/config.py`.

### Empirical Determination (0.55)
During Phase 4 and Phase 6 retrieval evaluation across our 60-chunk vector index, cosine similarity scores exhibited clear distribution separation:

| Query Type | Query Example | Cosine Score Range | Observed Mean |
| :--- | :--- | :--- | :--- |
| **Known In-Domain** | *"What is Python?"* | `0.6864` | `0.7423` |
| **Known In-Domain** | *"What does a software developer do?"* | `0.6974` | `0.7423` |
| **Known In-Domain** | *"What is machine learning?"* | `0.7134` | `0.7423` |
| **Known In-Domain** | *"What does internship mean?"* | `0.7576` | `0.7423` |
| **Known In-Domain** | *"What is cybersecurity analyst?"* | `0.8062` | `0.7423` |
| **Unknown / Out-of-Domain** | *"How to bake a chocolate cake?"* | `0.0952` | `0.0779` |
| **Unknown / Out-of-Domain** | *"Book me a flight to London"* | `0.0606` | `0.0779` |

### Trade-Off Analysis
- **Setting threshold > 0.65:** Risk of false rejections on valid queries with non-canonical phrasing (e.g., *"Professional Qualification"* scored `0.6392` in early baseline queries).
- **Setting threshold < 0.45:** Risk of allowing semantically weak noise to trigger LLM hallucinations.
- **Selected Value (0.55):** Provides a robust buffer below legitimate queries (min `0.6864`) while standing more than 5x higher than the highest out-of-domain noise (`0.0952`).

---

## 6. Multi-Signal Evidence Evaluation

A single scalar score can occasionally mislead in edge cases. `src/guardrails/relevance.py` computes multiple supporting signals:

1. **Top Cosine Similarity Score:** Compares the top candidate's cosine similarity against `RETRIEVAL_SCORE_THRESHOLD`.
2. **Relevant Result Count:** Counts how many retrieved chunks satisfy `score >= min(0.45, threshold * 0.85)`. At least `MIN_RELEVANT_RESULTS` (default: 1) is required.
3. **Terminology Overlap (Term Matching):** Extracts whether any normalized term or related terms from the top retrieved results appear in the user query.
4. **Category Consistency:** Detects whether the majority of top retrieved results share a unified taxonomy category (e.g., Job Roles).
5. **Similarity Separation Gap:** Measures the distance between the top score and the runner-up score.

---

## 7. Confidence Classification (Evidence Strength)

Confidence is categorized into three qualitative tiers:
- **`HIGH`:** `top_score >= 0.65` with explicit term overlap or multiple high-relevance chunks.
- **`MEDIUM`:** `0.55 <= top_score < 0.65`, or `top_score >= 0.65` with weak term overlap.
- **`LOW`:** `top_score < 0.55` or no retrieved evidence.

> [!NOTE]
> **Academic Integrity Statement:** Confidence represents **retrieval evidence strength** and similarity density, NOT a calibrated mathematical probability of factual truth.

---

## 8. Similarity Gap Analysis

The similarity gap is calculated as:
$$\text{Gap} = \text{Top Score} - \text{Second Score}$$

- **Large Gap ($\text{Gap} \ge 0.15$):** Indicates sharp separation and strong distinct candidate identification (e.g., *"What is Python?"* has $\text{Gap} = 0.2807$).
- **Small Gap ($\text{Gap} < 0.05$):** Indicates candidate competition or polysemy across multiple related entries (e.g., *"What is professional certification?"* vs *"What is professional qualification?"* has $\text{Gap} = 0.0551$). A small gap does not disqualify an answer if both candidates meet the relevance threshold.

---

## 9. Post-Generation Grounding Validation

Even when retrieved evidence is sufficient, generative models can introduce hallucinations during synthesis. `src/guardrails/grounding.py` applies deterministic post-generation validation before returning the explanation to the user.

---

## 10. Source Citation Validation

The model is strictly prohibited from inventing reference sources:
- Every citation listed in `GeneratedAnswer.sources` must correspond (via token-level or substring matching) to a source present in the retrieved evidence chunks.
- If the generator outputs citations not found in retrieved chunks (e.g., `"Random Tech Blog"`), grounding validation fails, and the response defaults to safe fallback.

---

## 11. Term Alignment Validation

The canonical `term` explained in `GeneratedAnswer` must correspond to the term or related terms of the retrieved chunks. If the generator drifts to an unrelated term (e.g., generating an explanation of "Quantum Cryptography" when evidence is for "Python"), the answer is rejected.

---

## 12. Category Alignment Validation

The taxonomy category asserted by `GeneratedAnswer` must match the category associated with the retrieved evidence chunk:
- Supported categories: `Job Roles`, `Technical Skills`, `Employment Terms`, `Professional Qualifications`, `Industry Terminology`.
- Contradictory assertions (e.g., claiming "Python" belongs to "Job Roles") trigger an immediate grounding rejection.

---

## 13. Deterministic Safe Fallback

When any pre-retrieval check, evidence sufficiency check, or post-generation grounding check fails, the system returns a structured `SafeFallbackResponse`:

```python
class SafeFallbackResponse(BaseModel):
    query: str
    message: str
    reason: str
    is_fallback: bool = True
    confidence: str = "LOW"
```

The fallback message is deterministic and fixed:
```text
I don't have enough information in the EMP-12 knowledge base to explain this term reliably.

Please ask about a job role, technical skill, employment term, professional qualification, or industry terminology covered by the knowledge base.
```
No LLM calls are made to construct the fallback response.

---

## 14. Testing Methodology

The testing architecture (`tests/test_guardrails.py`) contains 20 automated tests:
- **Test 1:** Valid known terminology query is allowed.
- **Test 2:** Unknown terminology query is rejected when evidence is insufficient.
- **Test 3:** Out-of-scope query is rejected.
- **Test 4:** Empty query is rejected.
- **Test 5:** Whitespace-only query is rejected.
- **Test 6:** Low similarity result triggers fallback.
- **Test 7:** Strong similarity result allows generation.
- **Test 8:** Retrieved term is recognized correctly.
- **Test 9:** Category consistency is checked.
- **Test 10:** Source consistency is checked.
- **Test 11:** Generated answer with valid source passes validation.
- **Test 12:** Generated answer with invented source fails validation.
- **Test 13:** Generated answer with unrelated term fails validation.
- **Test 14:** Generated answer with mismatched category fails validation.
- **Test 15:** Empty generated answer fails validation.
- **Test 16:** Confidence classification works (`HIGH`, `MEDIUM`, `LOW`).
- **Test 17:** Similarity gap is calculated correctly.
- **Test 18:** Multiple relevant results strengthen evidence.
- **Test 19:** Safe fallback is deterministic.
- **Test 20:** Complete controlled pipeline works end-to-end with mock generation.

All tests run locally without making live Gemini API calls, preventing rate limits or external dependencies.

---

## 15. Known Limitations

> [!WARNING]
> **Academic Disclaimer:** Phase 6 significantly reduces hallucination risk by blocking low-evidence queries and deterministically validating generated answers against retrieved evidence. It **does not provide a formal mathematical guarantee of zero hallucinations**. 
> 
> Potential residual failure modes include:
> - Phrasing variations where an LLM synthesizes an inaccurate nuance while using only approved terminology and sources.
> - Polysemous terms where two concepts share identical names across different domains.

---

## 16. Future Improvements (Phase 7+ Roadmap)

1. **Contextual Disambiguation:** Differentiating terms whose meanings shift depending on user career context (e.g., "Pipeline" in DevOps vs Data Engineering).
2. **Dynamic Threshold Tuning:** Adapting the threshold dynamically based on query length and specificity.
3. **Cross-Encoder Reranking:** Adding a lightweight cross-encoder stage prior to the guardrail check for higher semantic precision.
