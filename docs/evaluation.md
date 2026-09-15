# EMP-12: Job & Skill Terminology Simplifier
## Evaluation Methodology & Quality Benchmark Report (Phase 10 & 11)

This document provides complete documentation of the empirical evaluation methodology, benchmark dataset composition, mathematical metric formulas, baseline performance, error analysis, and final verified results for EMP-12.

---

### 1. Benchmark Dataset Design

The evaluation benchmark is strictly segregated from the training/knowledge base records to prevent data contamination. It is stored at `data/evaluation/evaluation_dataset.json` and comprises **92 cases**:

| Test Group | Case Count | Distribution & Criteria | Expected Behavior |
| :--- | :---: | :--- | :--- |
| **Supported Queries** | **52** | 11 Job Roles, 11 Technical Skills, 10 Employment Terms, 10 Qualifications, 10 Industry Terms | Top-1 retrieval match, category alignment, grounded answer synthesis |
| **Unknown Queries** | **20** | Plausible professional concepts not in knowledge base (e.g. *"Actuary"*, *"Underwriter"*) | Intercepted by relevance guardrails ($\text{score} < 0.55$); safe fallback |
| **Out-of-Scope Queries**| **20** | Non-employment queries (e.g. weather, geography, cooking, arithmetic) | Intercepted by domain scope filter; safe fallback |
| **Total Benchmark** | **92** | Comprehensive representation of normal, edge, and adversarial queries | Deterministic, verifiable behavior |

---

### 2. Evaluation Metrics & Mathematical Formulations

1. **Retrieval Recall@K:**
   Fraction of supported evaluation queries where the expected canonical term appears within the Top-$K$ retrieved candidates:
   $$\text{Recall}@K = \frac{1}{|Q_{\text{supported}}|} \sum_{q \in Q_{\text{supported}}} \mathbb{I}(\text{expected\_term}(q) \in \text{Top-}K(q))$$
2. **Guardrail Acceptance & Rejection Rates:**
   $$\text{Unknown Rejection Rate} = \frac{\text{Correctly Rejected Unknown Queries}}{|Q_{\text{unknown}}|}$$
   $$\text{Out-of-Scope Rejection Rate} = \frac{\text{Correctly Rejected Out-of-Scope Queries}}{|Q_{\text{out\_of\_scope}}|}$$
   $$\text{Unsupported Answer Rate} = \frac{\text{Hallucinated Answers Produced on Non-KB Queries}}{|Q_{\text{unknown}}| + |Q_{\text{out\_of\_scope}}|}$$
3. **Category & Grounding Accuracy:**
   $$\text{Category Accuracy} = \frac{\text{Queries with Matched Ground-Truth Category}}{|Q_{\text{supported}}|}$$
   $$\text{Source Provenance Accuracy} = \frac{\text{Answers with 100\% Verified Sources}}{|Q_{\text{grounded\_answers}}|}$$

---

### 3. Quantitative Benchmark Results

The benchmark was executed via `python src/evaluation/evaluator.py` against the full 92-case dataset.

| Metric | Phase 10 Baseline | Phase 11 / Phase 12 Final | Target | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Recall@1** | 100.0% | **100.0%** | $\ge 90.0\%$ | ✅ Exceeded |
| **Recall@3** | 100.0% | **100.0%** | $\ge 95.0\%$ | ✅ Exceeded |
| **Recall@5** | 100.0% | **100.0%** | $\ge 98.0\%$ | ✅ Exceeded |
| **Supported Acceptance Rate** | 100.0% | **100.0%** | $\ge 95.0\%$ | ✅ Exceeded |
| **Unknown Rejection Rate** | 100.0% | **100.0%** | $100.0\%$ | ✅ Perfect |
| **Out-of-Scope Rejection Rate**| 100.0% | **100.0%** | $100.0\%$ | ✅ Perfect |
| **Safe Fallback Trigger Rate** | 100.0% | **100.0%** | $100.0\%$ | ✅ Perfect |
| **Unsupported Answer Rate** | 0.0% | **0.0%** | $0.0\%$ | ✅ Zero Hallucinations |
| **Term Identification Accuracy**| 100.0% | **100.0%** | $\ge 95.0\%$ | ✅ Exceeded |
| **Category Accuracy** | 98.08% | **100.0%** | $\ge 95.0\%$ | ✅ Resolved |
| **Source Provenance Accuracy** | 100.0% | **100.0%** | $100.0\%$ | ✅ Perfect |
| **End-to-End Success Rate** | 98.08% | **100.0%** | $\ge 95.0\%$ | ✅ Perfect |

---

### 4. Baseline Error Analysis & Resolution

#### The Phase 10 Baseline Issue:
During Phase 10 evaluation, one single case out of 52 supported cases produced a category mismatch:
- **Query:** *"Explain Machine Learning Engineer for beginners"*
- **Expected Term:** `Machine Learning Engineer` (Category: `Job Roles`)
- **Retrieved Top-1 Candidate:** `Machine Learning` (Category: `Technical Skills`, Score: `0.7719`)
- **Retrieved Top-2 Candidate:** `Machine Learning Engineer` (Category: `Job Roles`, Score: `0.7652`)
- **Root Cause:** In dense embedding space (`all-MiniLM-L6-v2`), the subphrase *"Machine Learning"* had an inner product similarity `0.0067` higher than the full compound title, causing the system to classify the term as Technical Skills rather than Job Roles.

#### The Phase 11 Resolution:
In Phase 11, canonical phrase-aware re-ranking was introduced in `TerminologyRetriever._re_rank_candidates`:
- Complete word-boundary matches for candidate titles in the query receive $+0.20$.
- Subsumed subphrases receive $+0.05$.
- As a result, *"Machine Learning Engineer"* now scores `0.7618` at Rank 1, while *"What is Machine Learning?"* preserves *"Machine Learning"* at Rank 1 (`0.9134`).
- Category Accuracy and End-to-End Success Rate both improved from 98.08% to **100.0%**.

---

### 5. Similarity Score Distribution Analysis

Evaluating the 92 benchmark cases demonstrated clear separation between supported knowledge and unsupported queries:

| Metric | Supported Queries (52 cases) | Unknown / OOS Queries (40 cases) | Separation Margin |
| :--- | :---: | :---: | :---: |
| **Mean Cosine Similarity** | **0.7026** | **0.1603** | **+0.5423** |
| **Minimum Similarity** | **0.5836** | 0.0000 | — |
| **Maximum Similarity** | 0.9412 | **0.2851** | — |
| **Guardrail Threshold** | **0.5500** | **0.5500** | **+0.2985 above threshold** |

Because the highest scoring unknown term (`0.2851`) is well below the `0.5500` threshold, the system exhibits **zero false acceptances**.
