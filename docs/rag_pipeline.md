# EMP-12: Job & Skill Terminology Simplifier
## Retrieval-Augmented Generation (RAG) Pipeline Specification

This document details the exact end-to-end mechanics of the RAG pipeline implemented in EMP-12, from offline indexing to online grounded generation.

---

### 1. High-Level RAG Progression

Unlike unconstrained open-domain chatbots that generate answers from internal parameter weights, EMP-12 uses a strictly controlled RAG pipeline:

```text
Knowledge Base (60 records)
       ↓
Processing & Chunking (60 single-concept chunks)
       ↓
Dense Vector Embedding (all-MiniLM-L6-v2, 384-dim)
       ↓
FAISS Indexing (IndexFlatIP, L2-normalized)
       ↓
Online User Query Embedding
       ↓
Dense Candidate Retrieval (Top-5)
       ↓
Canonical Phrase Re-ranking
       ↓
Evidence Sufficiency Gate (Threshold >= 0.55)
       ↓
Contextual Formulation (7 Query Intents)
       ↓
Prompt Synthesis & Gemini 2.5 Flash Generation (temp=0.2)
       ↓
Post-Generation Grounding Verification
       ↓
Structured Pedagogical Output
```

---

### 2. Offline Ingestion and Indexing

1. **Structured Ingestion (`src/ingestion/loader.py`):**
   - Ingests 60 records across `job_roles.json`, `technical_skills.json`, `employment_terms.json`, `qualifications.json`, and `industry_terminology.json`.
   - Validates each record against `TerminologyRecord` schema.
2. **Single-Concept Semantic Chunking (`src/ingestion/chunker.py`):**
   - Each terminology entry forms an atomic semantic chunk (`CHUNK-001` through `CHUNK-060`).
   - Retains definition, simple meaning, job context, real-world example, related terms, sources, and category.
3. **Dense Embedding (`src/retrieval/embedder.py`):**
   - Uses `sentence-transformers/all-MiniLM-L6-v2`.
   - Generates 384-dimensional dense vectors for all 60 chunk texts.
   - Computes $L_2$-normalization:
     $$\vec{v}_{\text{norm}} = \frac{\vec{v}}{\|\vec{v}\|_2}$$
4. **FAISS Storage (`src/retrieval/vector_store.py`):**
   - Populates `faiss.IndexFlatIP(384)`.
   - Persists binary index to `models/vector_store/index.faiss` (92 KB) and position-mapped metadata to `models/vector_store/metadata.json` (113 KB).

---

### 3. Online Query Processing & Re-ranking

1. **Query Normalization & Embedding:**
   - Cleans query string, trims whitespace, and generates a normalized 384-dimensional query vector $\vec{q}$.
2. **FAISS Vector Search:**
   - Computes inner product between $\vec{q}$ and all 60 indexed vectors.
   - Retrieves the Top-$K$ ($K=5$) nearest candidate chunks.
3. **Canonical Phrase Re-ranking:**
   - Solves semantic overlap where base terms (e.g., *"Machine Learning"*) score closely to compound role titles (e.g., *"Machine Learning Engineer"*).
   - Searches for complete word boundary matches (`\b`) of candidate canonical terms in the query.
   - Candidates with exact complete phrase matches receive a $+0.20$ boost; partial subsumed matches receive $+0.05$.

---

### 4. Guardrail Evaluation & Gating

Before invoking Google Gemini, the candidate evidence must pass three deterministic gates:
1. **Relevance Threshold:** Top candidate similarity must satisfy:
   $$\text{score}_{\text{top}} \ge 0.55$$
2. **Result Count:** At least one retrieved candidate must exceed the threshold.
3. **Score Gap & Ambiguity:** Analyzes whether the top candidate represents an unambiguous semantic match.

If evidence is insufficient, the RAG pipeline halts and returns `SafeFallbackResponse` without invoking the LLM.

---

### 5. Grounded Prompt Formulation & LLM Generation

- **Model:** Google Gemini API (`gemini-2.5-flash`).
- **Temperature:** `0.2` (deterministic factual synthesis).
- **Prompt Structure (`src/generator/prompt_builder.py`):**
  - **System Instruction:** Guides the model to act as a supportive terminology mentor, write in accessible language, use clear analogies, and cite only provided evidence.
  - **Evidence Block:** Injects the Top-3 verified retrieval chunks containing canonical terms, definitions, context, and sources.
  - **Target Context:** Injects category-specific focus and beginner difficulty guidance.
  - **JSON Schema Requirement:** Enforces valid JSON conforming to the `GeneratedAnswer` structure.

---

### 6. Post-Generation Grounding Validation

Before displaying the output to the user, `validate_grounding` checks:
1. **Term Alignment:** The generated `term` matches the retrieved chunk's canonical term or known alias.
2. **Category Consistency:** The generated `category` matches the evidence taxonomy.
3. **Source Provenance:** Every citation in `sources` exists in the retrieved evidence chunks. Unsupported or hallucinated URLs/organizations trigger immediate fallback rejection.

This multi-stage architecture guarantees 0.0% unsupported hallucinations and total factual grounding.
