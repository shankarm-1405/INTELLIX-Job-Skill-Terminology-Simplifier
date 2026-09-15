# EMP-12: Job & Skill Terminology Simplifier
## System Limitations & Future Scope Specification

This document explicitly defines the boundaries, constraints, and operational limitations of the implemented EMP-12 system, alongside viable future research and engineering trajectories.

---

### 1. System Limitations & Boundaries

The following limitations represent intentional architectural and academic design decisions:

1. **Single-Instance Deployment Scope:**
   - EMP-12 is designed for standalone local execution or single-container execution.
   - It does not incorporate cluster synchronization, distributed worker queues, or multi-node coordination.

2. **No User Authentication or Multi-Tenancy:**
   - The application does not require login, passwords, OAuth2, or SAML credentials.
   - All users interact with a shared, read-only application instance. There is no user-specific persistent history, bookmarking, or saved preferences.

3. **External API Connectivity for Generation:**
   - While the Glossary Explorer, keyword search, dense embeddings, and FAISS vector retrieval operate 100% offline and locally on CPU, final natural language explanation synthesis requires external connectivity to Google Gemini API servers.
   - If internet access is unavailable or API quota is exhausted, answer generation falls back to an administrative configuration notice, while glossary browsing remains fully functional.

4. **No Centralized Rate Limiting:**
   - The application does not deploy a local Redis token-bucket rate limiter; traffic pacing relies on upstream Google Gemini API rate limits.

5. **Local Vector Index & Static File Knowledge Base:**
   - The knowledge base is stored in static JSON files (`data/knowledge_base/`) and FAISS is stored as a local serialized file (`index.faiss`). It is not backed by a relational database or dynamic cloud vector database.

6. **Local Docker Build Verification Constraint:**
   - The containerization configuration (`Dockerfile`, `.dockerignore`, `.streamlit/config.toml`) was constructed and validated according to best practices, but local container building was marked `NOT TESTED` due to the absence of the Docker daemon on the local Windows development machine.

---

### 2. Future Scope & Engineering Roadmap

The following enhancements represent natural extensions for future academic cohorts or production deployments:

1. **Knowledge Base Scaling:**
   - Expand the current 60-record foundation to 500+ records covering emerging technological disciplines such as Quantum Computing, Bioinformatics, Embedded Systems, and FinTech.
2. **Multilingual Terminology Assistance:**
   - Introduce multilingual query translation and explanation synthesis to assist international students and non-native English speakers.
3. **Neural Cross-Encoder Re-Ranking:**
   - Integrate a lightweight cross-encoder model (e.g., `ms-marco-MiniLM-L-6-v2`) to re-rank top candidates for complex, multi-sentence queries.
4. **Institutional Authentication & Telemetry:**
   - Add institutional single sign-on (SSO) and privacy-preserving learning analytics for deployment in university career centers.
5. **Interactive Concept Graph Visualization:**
   - Provide an interactive 2D graph visualizer allowing visual exploration of relationships between job roles, skills, and certifications.
