# EMP-12: Job & Skill Terminology Simplifier
## Technical Reference & API Module Specification

This document provides a comprehensive developer and academic reference mapping the source code structure, module responsibilities, core classes, and key functions in `src/`.

---

### 1. Master Module Mapping

| Module Name | Package Path | Architectural Responsibility |
| :--- | :--- | :--- |
| **`config`** | `src/config.py` | Centralized paths, environment settings, limits (`MAX_QUERY_LENGTH`), error sanitization. |
| **`ingestion`** | `src/ingestion/` | Loading, schema validation, normalization, and semantic chunking of knowledge base records. |
| **`retrieval`** | `src/retrieval/` | Dense vector embedding, FAISS IndexFlatIP management, and canonical phrase re-ranking. |
| **`generator`** | `src/generator/` | Grounded prompt construction and low-temperature Gemini 2.5 Flash structured generation. |
| **`guardrails`**| `src/guardrails/` | Scope gating, 0.55 similarity threshold sufficiency, post-generation grounding, and fallback routing. |
| **`context`** | `src/context/` | Query intent classification, category guidance injection, and difficulty calibration. |
| **`application`**| `src/application/` | `TerminologyService` pipeline coordinator and `GlossaryService` in-memory browser. |
| **`ui`** | `src/ui/`, `app.py` | Streamlit user interface rendering, badges, copy text formatting, and query validation. |
| **`evaluation`** | `src/evaluation/` | 92-case benchmark runner, Recall@K calculator, and confusion matrix evaluator. |

---

### 2. Detailed Subsystem Specifications

#### 2.1 Configuration & Security (`src/config.py`)
- **Key Constants:**
  - `MAX_QUERY_LENGTH = 300`: Maximum permitted character count for user queries.
  - `RETRIEVAL_SCORE_THRESHOLD = 0.55`: Minimum cosine score required for evidence sufficiency.
  - `DEFAULT_GENERATION_TEMPERATURE = 0.2`: Strict factual generation temperature.
- **Core Functions:**
  - `sanitize_error_message(text: str) -> str`: Redacts `AIza...`, tokens, and local file paths.
  - `validate_config(require_api_key: bool = False) -> tuple[bool, str]`: Validates environment health.

#### 2.2 Ingestion Subsystem (`src/ingestion/`)
- **`schemas.py`:** Pydantic schemas `TerminologyRecord`, `ProcessedDocument`, `DocumentChunk`.
- **`loader.py`:** `KnowledgeBaseLoader` with `_KB_RECORDS_CACHE` caching.
- **`processor.py`:** `DocumentProcessor` standardizing IDs (`DOC-001` to `DOC-060`).
- **`chunker.py`:** `DocumentChunker` creating single-concept atomic semantic chunks.
- **`pipeline.py`:** `IngestionPipeline` orchestrating full ingestion and disk persistence.

#### 2.3 Retrieval Subsystem (`src/retrieval/`)
- **`models.py`:** `SearchResult` schema containing chunk IDs, scores, texts, and source citations.
- **`embedder.py`:** `TerminologyEmbedder` wrapping `SentenceTransformer` with process-level `_MODEL_CACHE`.
- **`vector_store.py`:** `VectorStore` managing `faiss.IndexFlatIP` with timestamped `_INDEX_CACHE`.
- **`retriever.py`:** `TerminologyRetriever` applying canonical phrase-aware re-ranking to candidate vectors.

#### 2.4 Generator Subsystem (`src/generator/`)
- **`models.py`:** `GeneratedAnswer` schema with term, category, simple meaning, context, and sources.
- **`prompt_builder.py`:** `PromptBuilder.build_prompt()` assembling grounded system instructions and evidence.
- **`generator.py`:** `TerminologyGenerator.generate()` invoking Gemini API via `google-genai` SDK.

#### 2.5 Guardrail Subsystem (`src/guardrails/`)
- **`models.py`:** `GuardrailDecision`, `GroundingValidationResult`, and `SafeFallbackResponse`.
- **`scope.py`:** `validate_query_scope()` pre-retrieval query filter.
- **`relevance.py`:** `evaluate_evidence()` multi-signal cosine and lexical evaluator.
- **`grounding.py`:** `validate_grounding()` post-generation term, category, and source check.
- **`controller.py`:** `GuardrailController.process_query()` master RAG pipeline controller.

#### 2.6 Contextual Intelligence Subsystem (`src/context/`)
- **`models.py`:** `QueryIntent`, `ContextType`, `TerminologyContext`.
- **`intent.py`:** `detect_intent()` heuristic pattern matcher across 7 query intent types.
- **`context_builder.py`:** `ContextBuilder.build()` assembling category and difficulty guidance.

#### 2.7 Application & UI Subsystems (`src/application/`, `src/ui/`)
- **`service.py`:** `TerminologyService.explain_term()` single high-level API entrypoint with exception containment.
- **`glossary.py`:** `GlossaryService` read-only category filtering, search, and difficulty lookup.
- **`components.py`:** `is_valid_query_input()`, `render_difficulty_badge()`, `format_copy_text()`.
- **`app.py`:** Main Streamlit application file.
