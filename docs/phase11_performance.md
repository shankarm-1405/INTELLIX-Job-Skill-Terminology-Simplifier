# EMP-12: Phase 11 Performance & Retrieval Quality Report

**Project:** EMP-12 — Job & Skill Terminology Simplifier  
**Phase:** 11 — UI/UX & Performance Improvement  
**Evaluation Date:** 2026-09-15  
**Baseline Reference:** Phase 10 Evaluation Report  

---

## 1. Executive Summary

Phase 11 addresses two core engineering challenges identified during Phase 10 benchmarking:
1. **Cold-Start & Re-Initialization Latency:** Repeated disk I/O and transformer model instantiations across pipeline components.
2. **Retrieval Semantic Ambiguity (Machine Learning vs Machine Learning Engineer):** Score competition in dense embedding space where a compound role term (`Machine Learning Engineer`) was ranked second behind its base skill (`Machine Learning`) by a margin of only `0.0067`, causing a category mismatch.

Through controlled, explainable in-memory caching and canonical-term-aware re-ranking, both challenges were resolved **without replacing the embedding model or vector store index**.

---

## 2. Bottleneck Analysis & Profiling

Profiling the Phase 10 baseline pipeline revealed the following latency drivers:
1. **Model Initialization:** Instantiating `TerminologyEmbedder()` without a process-level cache caused PyTorch to reload weights and rebuild the transformer compute graph on new worker invocations (taking ~2,500 ms to ~3,200 ms per instantiation).
2. **FAISS File I/O:** Reading `index.faiss` (92 KB) and parsing `metadata.json` (113 KB) on every retriever lifecycle consumed 20–35 ms of unnecessary disk I/O.
3. **JSON Knowledge-Base Loading:** Reading and validating 5 separate category files (79 KB) during every glossary search or count operation introduced 10–18 ms of repeated disk reads.
4. **Token Overlap Score Bias:** In pure cosine similarity space, short general skill definitions often exhibit slightly tighter token density than multi-word job role descriptions, causing base terms to outscore specific compound titles when queries contain both.

---

## 3. Optimizations Implemented

### 3.1 Process-Level SentenceTransformer Model Cache
- **Location:** `src/retrieval/embedder.py`
- **Mechanism:** Implemented module-level caches `_MODEL_CACHE` and `_DIMENSION_CACHE`. When `_load_model()` is called for `sentence-transformers/all-MiniLM-L6-v2`, it checks `_MODEL_CACHE`. If present, it returns the shared in-memory instance immediately.
- **Impact:** Warm model access dropped from **~3,000 ms to < 1 ms** (a >99.9% initialization speedup).

### 3.2 In-Memory Index & Metadata Cache with mtime Invalidation
- **Location:** `src/retrieval/vector_store.py`
- **Mechanism:** Implemented `_INDEX_CACHE` mapping file paths to `(faiss_index, metadata, idx_mtime, meta_mtime)`. If the modification timestamp on disk has not changed, the in-memory index is returned without disk I/O.
- **Impact:** Vector store loading dropped from **~25 ms to < 0.1 ms**.

### 3.3 Knowledge Base Records Cache
- **Location:** `src/ingestion/loader.py`
- **Mechanism:** Implemented `_KB_RECORDS_CACHE` with file-level timestamp verification. `load_knowledge_base()` reuses parsed `TerminologyRecord` objects for subsequent requests.
- **Impact:** Repeated glossary access dropped from **~15 ms to < 0.1 ms**.

### 3.4 Canonical-Term-Aware Retrieval Re-Ranking
- **Location:** `src/retrieval/retriever.py`
- **Mechanism:**
  - Expanded the vector search candidate pool to $K_{\text{pool}} = \max(2 \times \text{top\_k}, 10)$.
  - Normalized the query using `_normalize_query()`.
  - Identified word-bounded matches for candidate canonical terms (`r"\b" + re.escape(t_norm) + r"\b"`).
  - Computed **maximal canonical matches** (terms not contained as a proper sub-phrase of another matching term).
  - Applied a deterministic, explainable boost:
    - **+0.20** for maximal canonical term matches.
    - **+0.05** for subsumed sub-phrase matches.
    - **0.00** for non-matching candidates (pure semantic similarity preserved).
  - Clamped adjusted scores to $\le 1.0$ and re-sorted descending.
- **Result:**
  - For *"Explain Machine Learning Engineer for beginners"*, `Machine Learning Engineer` receives +0.20 (maximal match), achieving score `0.7618` and ranking **#1** (`Job Roles`).
  - For *"What is Machine Learning?"*, `Machine Learning` receives +0.20 (maximal match), achieving score `0.9134` and ranking **#1** (`Technical Skills`).
  - For unknown queries (*"What is quantum entanglement?"*), no canonical term matches; boost is 0.0, and guardrails reject the query safely.

---

## 4. Before vs After Performance Comparison

Empirical comparison between Phase 10 Baseline and Phase 11:

| Metric | Phase 10 Baseline | Phase 11 Result | Net Change |
| :--- | :---: | :---: | :---: |
| **Retrieval Recall@1** | 100.0% | **100.0%** | Maintained (Perfect) |
| **Retrieval Recall@3** | 100.0% | **100.0%** | Maintained (Perfect) |
| **Retrieval Recall@5** | 100.0% | **100.0%** | Maintained (Perfect) |
| **Supported Acceptance Rate** | 100.0% | **100.0%** | Maintained (Perfect) |
| **Unknown Rejection Rate** | 100.0% | **100.0%** | Maintained (Perfect) |
| **Out-of-Scope Rejection Rate** | 100.0% | **100.0%** | Maintained (Perfect) |
| **Safe Fallback Rate** | 100.0% | **100.0%** | Maintained (Perfect) |
| **Unsupported Answer Rate** | 0.0% | **0.0%** | Maintained (Zero Hallucination) |
| **Term Identification Accuracy** | 100.0% | **100.0%** | Maintained (Perfect) |
| **Category Classification Accuracy** | 98.08% | **100.0%** | **+1.92% (All 52 Correct)** |
| **Job Roles Category Accuracy** | 90.91% | **100.0%** | **+9.09% (All 11 Correct)** |
| **Source Provenance Accuracy** | 100.0% | **100.0%** | Maintained (Perfect) |
| **End-to-End Success Rate** | 98.08% | **100.0%** | **+1.92% (All 52 Successful)** |
| **Warm Embedder Re-initialization** | ~3,000 ms | **< 1 ms** | **>99.9% Faster** |
| **Warm Vector Store Loading** | ~25 ms | **< 0.1 ms** | **>99% Faster** |
| **Warm Knowledge Base Loading** | ~15 ms | **< 0.1 ms** | **>99% Faster** |
| **Warm Pipeline Latency (Median)** | 47.56 ms | **~42 ms** | **Faster** |

---

## 5. Regression Testing

A dedicated test suite was created and verified:
- **`tests/test_performance.py` (6 tests):** Validates embedder cache, vector store cache, knowledge base cache, warm retrieval bounds (< 200 ms), and memory footprint safety.
- **`tests/test_phase11.py` (13 tests):** Validates exact canonical re-ranking across:
  - `Machine Learning` vs `Machine Learning Engineer`
  - `Software Developer`
  - `DevOps Engineer`
  - `Cloud Engineer`
  - `Data Scientist`
  - `Cybersecurity Analyst`
  - Unknown query safety without artificial boost
  - UI difficulty badges and fallback guidance formatting.

### Full Test Suite Execution Summary:
```text
======================= 202 passed, 1 warning in 22.06s =======================
```
- Total Tests: **202 passed, 0 failed (100%)**.
- Zero regression across all prior Phases (Phases 1 through 10).

---

## 6. Limitations

1. **Cold Start PyTorch Overhead:** The very first query of an application process still requires loading the PyTorch library and SentenceTransformer weights from disk (~2.5s). Caching eliminates this overhead for all subsequent operations.
2. **External Gemini API Latency:** While local vector search and guardrail evaluation complete in $< 50$ ms, end-to-end generation calling the external Gemini API is subject to internet round-trip latency (~1.2s to 2.8s).
3. **Lexical Boundary Assumption:** The canonical re-ranking algorithm relies on word-bounded token matching; unconventional typographical distortions (e.g. extreme typos) rely purely on dense semantic vector similarity.
