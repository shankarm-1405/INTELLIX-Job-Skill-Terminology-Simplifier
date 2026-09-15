# EMP-12: Job & Skill Terminology Simplifier
## System Requirements Specification

---

### 1. Functional Requirements (FR)

| ID | Title | Description | Implementation Module |
| :---: | :--- | :--- | :--- |
| **FR-01** | Query Acceptance | Accept natural language terminology queries from the web UI or Python service. | `src/application/service.py` |
| **FR-02** | Input Sanitization & Bounds | Enforce non-empty input, minimum length (2 characters), and maximum length (`MAX_QUERY_LENGTH = 300`). | `src/ui/components.py`, `src/config.py` |
| **FR-03** | Scope Pre-Filtering | Detect gibberish or clear out-of-domain queries before calling vector retrieval. | `src/guardrails/scope.py` |
| **FR-04** | Semantic Dense Retrieval | Embed query into 384-dimensional vector and retrieve Top-$K$ (default 5) candidates. | `src/retrieval/retriever.py` |
| **FR-05** | Canonical Phrase Re-ranking | Apply canonical boundary re-ranking to prioritize exact role/term phrases over subsumed substrings. | `src/retrieval/retriever.py` |
| **FR-06** | Evidence Sufficiency Evaluation | Enforce similarity threshold ($\ge 0.55$), score gap analysis, and category consistency. | `src/guardrails/relevance.py` |
| **FR-07** | Contextual Intelligence Formulation | Infer query intent and inject workplace usage, difficulty guidance, and related terms into generation prompt. | `src/context/context_builder.py` |
| **FR-08** | Grounded Answer Generation | Synthesize structured beginner-friendly explanations via Google Gemini 2.5 Flash at temperature 0.2. | `src/generator/generator.py` |
| **FR-09** | Post-Generation Grounding Check | Verify that term, category, and citations match retrieved evidence chunks. | `src/guardrails/grounding.py` |
| **FR-10** | Deterministic Safe Fallback | Deliver structured, safe fallback responses with category recommendations when evidence is insufficient. | `src/guardrails/controller.py` |
| **FR-11** | Glossary Browsing & Filtering | Allow browsing of all 60 terms, filtered by category and sorted alphabetically. | `src/application/glossary.py` |
| **FR-12** | Keyword & Alias Search | Provide deterministic, instant search over terms, definitions, and aliases. | `src/application/glossary.py` |
| **FR-13** | Study Card Export | Format clean Markdown summary cards for student note-taking omitting credentials or diagnostics. | `src/ui/components.py` |
| **FR-14** | One-Click Related Navigation | Enable clicking companion term chips to trigger grounded RAG pipeline directly. | `app.py` |
| **FR-15** | Instant Reset / Clear | Reset active search, explanation card, and UI state without leaving residual history. | `app.py` |

---

### 2. Non-Functional Requirements (NFR)

- **NFR-01 (Factuality & Hallucination Resistance):** 0.0% unsupported hallucinations on verified concepts.
- **NFR-02 (Performance & Latency):** Sub-second warm response times (< 20 ms for local retrieval and guardrails).
- **NFR-03 (Security & Secret Protection):** 0 hardcoded credentials; all error messages redact API keys and system paths.
- **NFR-04 (Privacy & Statelessness):** Single-turn architecture; no user tracking or cross-session persistence.
- **NFR-05 (Deterministic Reproducibility):** Zero stochastic drift in retrieval, chunking, or guardrail decisions.
- **NFR-06 (Software Quality & Maintainability):** 100% automated test pass rate across 229 unit, integration, and security tests.

---

### 3. Software and Hardware Baseline

#### Software Environment
- **Operating System:** Tested on Microsoft Windows (Windows 11 / PowerShell) and Linux container compatible (`python:3.11-slim`).
- **Python Runtime:** Python `3.14.3` (compatible with Python 3.10 through 3.14).
- **Package Management:** `pip` with locked requirements in `requirements.txt`.
- **Core Libraries:** `streamlit`, `pydantic`, `sentence-transformers`, `faiss-cpu`, `google-genai`, `torch`, `pytest`.

#### Hardware Specifications
- **CPU:** Standard multi-core x86_64 or ARM64 processor.
- **RAM:** Minimum 2 GB recommended (~450 MB resident memory for model, FAISS index, and Streamlit runtime).
- **Disk Storage:** Minimum 500 MB free space for virtual environment, models, and dependencies.
- **GPU:** *Not required* (all vector indexing and embeddings run efficiently on CPU).
- *(Note: Exact hardware scaling limits for concurrent multi-user load were not measured as EMP-12 is designed as a single-tenant academic demonstration).*

---

### 4. Environment Variables

| Variable | Required | Default | Purpose |
| :--- | :---: | :---: | :--- |
| `GEMINI_API_KEY` | Optional for glossary / Required for LLM | `""` | Google Gemini API key for grounded generation |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` | Gemini model variant |
| `DEFAULT_GENERATION_TEMPERATURE` | No | `0.2` | Generation temperature for factual determinism |
| `MAX_QUERY_LENGTH` | No | `300` | Safety limit for user query characters |
| `EMBEDDING_MODEL_NAME` | No | `all-MiniLM-L6-v2` | SentenceTransformer model identifier |
| `RETRIEVAL_SCORE_THRESHOLD` | No | `0.55` | Minimum cosine similarity threshold |
| `TOP_K_RETRIEVAL` | No | `3` | Number of chunks supplied to LLM context |
| `APP_ENV` | No | `development` | Application execution mode |

---

### 5. Deployment Requirements
- **Containerization:** `Dockerfile` based on `python:3.11-slim` with non-root user execution (`emp12user`).
- **Port Binding:** Expose TCP port 8501 for Streamlit HTTP traffic.
- **Health Verification:** Built-in HTTP healthcheck endpoint at `/_stcore/health`.
