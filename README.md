# EMP-12 — Job & Skill Terminology Simplifier

> **Domain-Specific Glossary & RAG System for Employment & Technical Terminology**
> Designed for Beginners, Fresh Graduates, and Career Switchers.

---

## 📌 Problem Overview

Entering the modern technical workforce requires navigating a dense barrier of jargon: job advertisements, employment contracts, and technical tools are laden with acronyms, hierarchical skills, and nuanced conditions.

**EMP-12** is an AI/RAG-powered **Contextual Terminology Assistant** that translates complex employment and technology vocabulary into plain, accessible, and grounded explanations.

### Key Capabilities
- **5 Core Terminology Domains**: Job Roles, Technical Skills, Employment Terms, Professional Qualifications, Industry Terminology.
- **Contextual Intelligence**: Explains terms through specific career lenses (e.g., *Software Developer* vs. *Cloud/DevOps Engineer*).
- **9-Part Structured Response**: Delivers definitions, beginner-friendly analogies, workplace usage, concrete examples, companion skills, and verified source citations.
- **Anti-Hallucination Guardrails**: Detects out-of-scope or unverified queries and provides polite, controlled fallbacks.

---

## 📂 Project Architecture

```
SKILL_DEVELOPMENT/
├── data/
│   ├── knowledge_base/         # Curated domain terminology JSON records
│   └── raw/                    # Reference documents & sources
├── models/
│   └── vector_store/           # Serialized FAISS indices & metadata
├── src/
│   ├── __init__.py             # Package initializer
│   ├── config.py               # Centralized configuration & environment paths
│   ├── query/                  # Query preprocessing & intent classification
│   ├── ingestion/              # Ingestion, validation & chunking engine
│   ├── retrieval/              # Vector embedder & similarity search
│   ├── generator/              # Prompt templates & LLM generation chain
│   ├── guardrails/             # Similarity threshold & fallback control
│   └── ui/                     # Streamlit user interface
├── tests/
│   ├── __init__.py
│   └── test_setup.py           # Environment sanity & dependency test suite
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Locked project dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Git

### 2. Environment Setup
```bash
# Clone the repository
git clone <repo-url>
cd SKILL_DEVELOPMENT

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

### 3. Verify Installation
```bash
pytest tests/test_setup.py
```

---

## 🛠️ Technology Stack

| Layer | Component | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core runtime and data processing |
| **User Interface** | Streamlit | Fast, responsive, pure-Python UI |
| **Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`) | Local, CPU-friendly 384-dimensional embeddings |
| **Vector Index** | FAISS (`faiss-cpu`) | High-speed local similarity search |
| **LLM Engine** | Google Gemini API (`gemini-2.5-flash`) | Grounded answer generation and analogy synthesis |
| **Data Format** | Structured JSON + Markdown | Version-controlled, schema-validated terminology repository |

---

## 📋 Master Roadmap Status

- [x] **PHASE 0**: Project Definition, Planning & Architecture *(Complete)*
- [x] **PHASE 1**: Project Setup & Environment Initialization *(Complete)*
- [x] **PHASE 2**: Knowledge Base Design & Creation *(Complete)*
- [x] **PHASE 3**: Document Processing & Ingestion Pipeline *(Complete)*
- [x] **PHASE 4**: RAG Retrieval System *(Complete)*
- [x] **PHASE 5**: LLM Answer Generation *(Complete)*
- [x] **PHASE 6**: Hallucination & Unknown Query Control *(Complete)*
- [x] **PHASE 7**: Contextual Intelligence Engine *(Complete)*
- [x] **PHASE 8**: User Interface Development *(Complete)*
- [x] **PHASE 9**: Useful EMP-12 Features *(Complete)*
- [x] **PHASE 10**: Evaluation & Testing *(Complete)*
- [x] **PHASE 11**: UI/UX & Performance Improvement *(Complete)*
- [x] **PHASE 12**: Security & Deployment *(Complete)*
- [x] **PHASE 13**: Documentation *(Complete)*
- [x] **PHASE 14**: Final Presentation, Demo & Viva *(Complete - 100% Finished)*

---

## 📚 Project Documentation Package

EMP-12 includes an exhaustive, verified academic documentation suite:

- 🎓 **[Phase 14 Presentation & Slide Outline](docs/phase14_presentation.md)**: 18-slide academic presentation structure.
- 🎙️ **[Phase 14 1-Minute Elevator Pitch](docs/phase14_one_minute_explanation.md)** & **[5-Minute Spoken Script](docs/phase14_five_minute_explanation.md)**: Timed presentation scripts.
- 🖥️ **[Phase 14 Demo Script](docs/phase14_demo_script.md)** & **[Offline Contingency Guide](docs/phase14_demo_backup.md)**: 10-step demo script and offline fallback guide.
- 🗣️ **[Phase 14 Comprehensive Viva Voce (69 Q&As)](docs/phase14_viva.md)** & **[Tricky Viva Defense](docs/phase14_tricky_viva.md)**: Examiner defense handbooks.
- 📋 **[Phase 14 Final Checklist](docs/phase14_final_checklist.md)** & **[Evidence Catalog](docs/phase14_evidence_checklist.md)**: Operational checklist and screenshot specifications.
- 📘 **[Master Project Report (Chapters 1–28)](docs/EMP12_Project_Report.md)**: The comprehensive academic project report covering problem definition, objectives, architecture, knowledge base, RAG, evaluation, security, and future scope.
- 📋 **[Project Overview](docs/project_overview.md)**: Executive summary, problem statement, and scope boundaries.
- 📐 **[System Architecture](docs/system_architecture.md)**: Mermaid diagrams, subsystem boundaries, and data flow.
- 📑 **[System Requirements](docs/requirements.md)**: Functional, non-functional, runtime, and deployment requirements.
- 🔍 **[RAG Pipeline Specification](docs/rag_pipeline.md)**: Dense retrieval, FAISS vector search, and Gemini generation mechanics.
- 🖥️ **[UI & Usability Features](docs/ui_features.md)**: Screen layouts, difficulty badges, Glossary Explorer, and study cards.
- 📊 **[Evaluation Benchmark Report](docs/evaluation.md)**: 92-case evaluation methodology, metrics, and disambiguation analysis.
- ⚡ **[Performance & Caching](docs/performance.md)**: In-memory model/vector caching benchmarks and latency profiles.
- 🔒 **[Security Architecture](docs/security.md)**: Threat model, secret isolation, input bounds, and error sanitization.
- 🐳 **[Deployment & Operations](docs/deployment.md)**: Local execution, Docker containerization, and configuration reference.
- 🧪 **[Testing Strategy](docs/testing.md)**: Test suite taxonomy covering 229 automated tests.
- 📖 **[Technical Reference](docs/technical_reference.md)**: Codebase directory and module reference.
- 🔮 **[Limitations & Future Scope](docs/limitations_and_future_scope.md)**: System boundaries and future academic milestones.
- 🏆 **[Final Executive Project Summary](docs/phase14_final_summary.md)**: Final executive sign-off and milestone summary.

---

## 🔒 Security & Deployment

EMP-12 is hardened for secure, reproducible deployment:

- **Secret Protection:** Google Gemini API keys are loaded solely via `GEMINI_API_KEY` from environment/.env and never logged, printed, or saved.
- **Input Hardening:** Queries are bounded by `MAX_QUERY_LENGTH = 300` characters, and file paths are fully protected from path traversal.
- **Diagnostic Sanitization:** All error messages and logs redact API keys (`AIza...`), tokens, and local directory paths via `sanitize_error_message`.
- **Reproducible Docker:** Includes a hardened, non-root `Dockerfile` and `.dockerignore` for containerized execution.
- **Production Streamlit Config:** Configured in `.streamlit/config.toml` with headless mode, CORS/XSRF protection, and port 8501.

### Quick Start Deployment:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env

# 3. Run Streamlit
streamlit run app.py
```

---

## 📊 Evaluation & Testing

EMP-12 includes a comprehensive automated test suite with **229 tests** and a reproducible 92-case evaluation benchmark:

```bash
# Run all unit, security, and deployment tests
python -m pytest tests/

# Run deterministic benchmark evaluation
python src/evaluation/evaluator.py
```


