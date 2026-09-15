# EMP-12: Job & Skill Terminology Simplifier
## Project Overview & Executive Summary

---

### 1. Executive Summary
**EMP-12: Job & Skill Terminology Simplifier** is a domain-specific conversational terminology assistant and Retrieval-Augmented Generation (RAG) system. It is engineered to demystify complex workplace jargon, technical programming concepts, hiring conditions, professional credentials, and industry methodologies for beginners, college students, and career changers.

### 2. Official Problem Statement
> “Develop a domain-specific glossary and RAG system for employment terminology such as job roles, technical skills, professional qualifications, employment terms, and industry-specific terminology.”

### 3. Required Outcome
> “A contextual terminology assistant that explains unfamiliar employment and technology terms to beginners.”

### 4. Core Pillars of EMP-12
1. **Authoritative Domain Glossary:** 60 structured, expert-curated records across five mandatory employment categories.
2. **Dense Vector Search:** High-speed semantic search using `sentence-transformers/all-MiniLM-L6-v2` and `FAISS IndexFlatIP`.
3. **Grounded Generation:** Low-temperature (0.2) explanation synthesis via Google Gemini 2.5 Flash strictly bound to retrieved evidence.
4. **Zero-Hallucination Guardrails:** Dual-scope validation, relevance thresholds (cosine $\ge 0.55$), and 1-to-1 post-generation grounding checks.
5. **Contextual Intelligence:** Automatic intent detection, target difficulty classification (Beginner, Intermediate, Advanced), and workplace context injection.
6. **Exploration & Usability:** Streamlit frontend featuring a live Glossary Explorer, one-click related-term navigation, and clean Markdown notes export.
7. **Production Hardening:** In-memory caching (< 1 ms warm retrieval), credential protection, query length bounds (300 chars), path traversal immunity, and Docker readiness.

### 5. Scope Boundaries
- **Supported:** Job Roles, Technical Skills, Employment Terms, Professional Qualifications, Industry Terminology.
- **Strictly Excluded:** Job recommendation, candidate matching, resume builders, interview simulators, salary predictors, persistent user profiles, external web scraping.
