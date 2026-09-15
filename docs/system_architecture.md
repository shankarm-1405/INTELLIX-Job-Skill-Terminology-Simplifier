# EMP-12: Job & Skill Terminology Simplifier
## System Architecture & Component Specification

This document provides the definitive architectural design, component responsibilities, data flow, and subsystem interactions of the EMP-12 system.

---

### 1. High-Level Architectural Flow

EMP-12 is organized into decoupled, single-responsibility layers connecting the user interface to retrieval, guardrails, and generation services.

```mermaid
flowchart TD
    subgraph UI_Layer [Presentation Layer]
        A[Student / User] -->|Query input or click| B[Streamlit UI app.py]
    end

    subgraph Service_Layer [Application Service Layer]
        B -->|explain_term| C[TerminologyService]
        B -->|browse / search| D[GlossaryService]
    end

    subgraph Guardrail_Layer [Reliability & Guardrail Layer]
        C --> E[GuardrailController]
        E --> F[Scope Detector validate_query_scope]
        F -->|Out of Scope| Z1[SafeFallbackResponse]
    end

    subgraph Retrieval_Layer [Dense Semantic Retrieval Layer]
        F -->|In Scope| G[TerminologyRetriever]
        G --> H[TerminologyEmbedder all-MiniLM-L6-v2]
        H -->|384-dim normalized vector| I[(FAISS IndexFlatIP index.faiss)]
        I -->|Top-K Candidate IDs| J[(Chunk Metadata metadata.json)]
        J --> K[Canonical Term Re-ranker]
        K --> L[Evidence Evaluator evaluate_query]
        L -->|Score < 0.55| Z2[SafeFallbackResponse]
    end

    subgraph Context_Layer [Contextual Intelligence Layer]
        L -->|Approved Evidence| M[ContextBuilder]
        M --> N[Intent Classifier detect_intent]
    end

    subgraph Generation_Layer [LLM Answer Generation Layer]
        N --> O[PromptBuilder]
        O --> P[Google Gemini 2.5 Flash]
        P -->|Raw JSON| Q[extract_json_payload]
    end

    subgraph Grounding_Layer [Post-Generation Grounding Layer]
        Q --> R[GroundingValidator validate_grounding]
        R -->|Ungrounded Sources / Term Miss| Z3[SafeFallbackResponse]
        R -->|Verified Valid| S[GeneratedAnswer Model]
    end

    S --> C
    Z1 --> C
    Z2 --> C
    Z3 --> C
    C -->|ApplicationResponse| B
    B -->|Educational Cards / Badges| A
```

---

### 2. Component Responsibilities

| Subsystem | Module | Key Classes / Functions | Primary Responsibility |
| :--- | :--- | :--- | :--- |
| **Config** | `src/config.py` | `validate_config()`, `sanitize_error_message()` | Global settings, paths, limits (`MAX_QUERY_LENGTH`), and diagnostic redaction. |
| **Ingestion** | `src/ingestion/` | `KnowledgeBaseLoader`, `DocumentProcessor`, `DocumentChunker` | Loads 60 JSON records, validates schemas, and builds 60 normalized single-concept chunks. |
| **Retrieval** | `src/retrieval/` | `TerminologyEmbedder`, `VectorStore`, `TerminologyRetriever` | Embeds text into 384-dim vectors, searches FAISS IndexFlatIP, and applies canonical re-ranking. |
| **Generator** | `src/generator/` | `PromptBuilder`, `TerminologyGenerator`, `extract_json_payload` | Builds grounded prompts and calls Gemini 2.5 Flash to synthesize structured explanations. |
| **Guardrails** | `src/guardrails/` | `GuardrailController`, `validate_query_scope`, `validate_grounding` | Dual-scope gating, 0.55 similarity threshold, evidence sufficiency, and grounding validation. |
| **Context** | `src/context/` | `ContextBuilder`, `detect_intent` | Infers 7 query intents and injects workplace scenarios, difficulty tags, and related terms. |
| **Application** | `src/application/` | `TerminologyService`, `GlossaryService` | Coordinates RAG pipeline, enforces query bounds, and powers the interactive glossary. |
| **UI** | `src/ui/`, `app.py` | `render_difficulty_badge()`, `format_copy_text()` | Streamlit web presentation, cards, quick-start chips, and student study notes export. |
| **Evaluation**| `src/evaluation/` | `TerminologyEvaluator`, `calculate_retrieval_metrics` | Runs automated 92-case benchmark and computes Recall@K, confusion matrix, and latencies. |

---

### 3. Data Flow and State Contracts

Data passes strictly between components through immutable Pydantic models:

```mermaid
classDiagram
    class TerminologyRecord {
        +str id
        +str term
        +str category
        +str definition
        +str simple_explanation
        +str job_context
        +str real_world_example
        +List~str~ related_terms
        +List~str~ sources
        +str difficulty_level
        +List~str~ aliases
    }

    class SearchResult {
        +str chunk_id
        +str doc_id
        +str term
        +str category
        +str text
        +float score
        +str source
    }

    class GeneratedAnswer {
        +str query
        +str term
        +str category
        +str simple_meaning
        +str why_it_matters
        +str job_context
        +str real_world_example
        +List~str~ related_terms
        +List~str~ sources
    }

    class SafeFallbackResponse {
        +str query
        +str message
        +str reason
        +bool is_fallback
        +str confidence
    }

    class ApplicationResponse {
        +str query
        +bool success
        +bool is_fallback
        +bool is_configuration_error
        +GeneratedAnswer answer
        +SafeFallbackResponse fallback
        +str error_message
    }

    TerminologyRecord ..> SearchResult : Ingestion & FAISS
    SearchResult ..> GeneratedAnswer : Generation & Grounding
    GeneratedAnswer ..> ApplicationResponse : UI Packaging
    SafeFallbackResponse ..> ApplicationResponse : Fallback Packaging
```

---

### 4. Guardrail and Fallback Flow

```mermaid
flowchart LR
    Q[User Query] --> S{Scope Check}
    S -->|Invalid / Gibberish| F1[Safe Fallback: Out-of-Scope]
    S -->|Valid| R[FAISS Retrieval]
    R --> T{Cosine Score >= 0.55?}
    T -->|No| F2[Safe Fallback: Insufficient Evidence]
    T -->|Yes| G[Gemini Generation]
    G --> V{Grounding Valid?}
    V -->|No| F3[Safe Fallback: Grounding Mismatch]
    V -->|Yes| A[Deliver Grounded Answer]
```

---

### 5. Deployment Container Architecture

```mermaid
flowchart TD
    subgraph Host_Machine [Host Environment / Docker Engine]
        Port[Host Port: 8501] -->|TCP Forwarding| ContPort[Container Port: 8501]
        EnvVar[Runtime: -e GEMINI_API_KEY] -.->|Injects secret| AppRuntime
    end

    subgraph Container_Filesystem [/app (emp12user)]
        ConfigToml[.streamlit/config.toml] --> AppRuntime[Streamlit Engine]
        AppPy[app.py] --> AppRuntime
        SrcDir[src/] --> AppRuntime
        DataDir[data/knowledge_base/ + processed/] --> AppRuntime
        ModelsDir[models/vector_store/index.faiss] --> AppRuntime
    end

    subgraph Excluded_By_Dockerignore [Protected by .dockerignore]
        EnvFile[.env]
        GitDir[.git/]
        Pycache[__pycache__/]
        TestDir[tests/]
    end
```
