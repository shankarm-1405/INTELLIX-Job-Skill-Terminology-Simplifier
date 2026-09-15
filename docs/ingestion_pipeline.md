# EMP-12 Document Processing & Ingestion Pipeline Specification

## 1. Purpose
The Document Processing & Ingestion pipeline bridges the curated Phase 2 Knowledge Base with downstream retrieval indexing. It is responsible for loading raw JSON records, validating data schemas, performing text normalization, formatting records into consistent searchable documents, attaching rich metadata, chunking documents into retrieval-ready units, and persisting deterministic JSON artifacts.

---

## 2. Input Data
The pipeline consumes exclusively the five verified category JSON files located in `data/knowledge_base/`:
- `data/knowledge_base/job_roles.json` (12 records)
- `data/knowledge_base/technical_skills.json` (15 records)
- `data/knowledge_base/employment_terms.json` (12 records)
- `data/knowledge_base/professional_qualifications.json` (9 records)
- `data/knowledge_base/industry_terminology.json` (12 records)

Total input: **60 structured terminology records**.

---

## 3. Processing Pipeline

```
Phase 2 Knowledge Base JSON Files
             │
             ▼
KnowledgeBaseLoader (src/ingestion/loader.py)
  - Safe discovery of all 5 category files
  - UTF-8 JSON parsing
  - Strict Pydantic schema validation (TerminologyRecord)
  - Global ID uniqueness validation
             │
             ▼
DocumentProcessor (src/ingestion/processor.py)
  - Safe text normalization (whitespace, linebreaks, punctuation preservation)
  - Assembly of canonical searchable document layout
  - Metadata encapsulation (ProcessedDocument)
             │
             ▼
DocumentChunker (src/ingestion/chunker.py)
  - Deterministic chunking logic
  - Chunk ID assignment ({doc_id}_chunk_{index:03d})
  - Header preservation (Term + Category on all chunks)
  - Rich metadata attachment (DocumentChunk)
             │
             ▼
Persistence & Ingestion Statistics (src/ingestion/pipeline.py)
  - data/processed/documents.json
  - data/processed/chunks.json
```

---

## 4. Normalization Strategy
Text normalization is executed deterministically without changing semantics or invoking LLMs:
- **Line Ending Standardization**: Converts `\r\n` and `\r` to standard UNIX `\n`.
- **Space Collapsing**: Replaces non-breaking spaces (`\u00a0`) and horizontal tabs (`\t`) with single spaces; collapses multiple consecutive spaces.
- **Line Break Cleaning**: Collapses 3 or more consecutive blank lines down to 2, ensuring clean visual separation between sections.
- **Punctuation & Syntax Preservation**: Preserves all meaningful technical symbols, hyphens, slashes (e.g., `CI/CD`, `UI/UX`), brackets, and source citations verbatim.

---

## 5. Document Representation
Each record is transformed into a standardized, human-readable searchable text block:

```text
Term: Python

Category: Technical Skills

Short Definition:
A versatile, high-level programming language known for clean, readable syntax and a massive ecosystem of libraries.

Simple Explanation:
Python is designed to look like straightforward English text, which makes it one of the easiest languages for beginners to learn. It is used widely to build web backends, automate repetitive tasks, crunch data, and develop artificial intelligence models.

Job Context:
Python is commonly listed as a mandatory or preferred skill for software development, data analysis, automation, machine learning, and cloud administration job openings.

Example:
A data analyst writes a 20-line Python script using the pandas library to clean 50,000 spreadsheet rows and calculate monthly sales numbers in 3 seconds.

Related Skills:
Programming, SQL, Git, Data Analysis, Problem Solving

Related Terms:
Programming Language, Data Scientist, Machine Learning, Software Developer, Scripting

Difficulty:
Beginner

Domain:
Software Development

Source:
Python Software Foundation Official Documentation (python.org)
```

---

## 6. Metadata Structure
Both `ProcessedDocument` and `DocumentChunk` carry explicit structured metadata:
- `id` / `document_id`: Original record identifier (e.g., `tech_python`)
- `chunk_id`: Deterministic chunk identifier (e.g., `tech_python_chunk_001`)
- `term`: Canonical term name
- `category`: Exactly one of the 5 official categories
- `difficulty`: `Beginner`, `Intermediate`, or `Advanced`
- `domain`: Controlled functional domain (e.g., `Software Development`, `DevOps`)
- `source`: Authoritative reference string
- `related_skills`: List of companion skill strings
- `related_terms`: List of related concept strings
- `chunk_index`: 1-based index
- `total_chunks`: Total chunk count for the parent document

---

## 7. Chunking Strategy
- **Context Preservation Principle**: In a domain-specific glossary for beginners, splitting concise terminology records damages retrieval accuracy because definitions, analogies, workplace usage, and companion skills belong to the same semantic unit.
- **Threshold-Based Chunking**:
  - If a document's searchable text fits within `max_chunk_chars` (default 1600 characters), it forms a single, comprehensive chunk (`_chunk_001`).
  - If a document exceeds the threshold, it splits into two balanced contextual chunks: Part 1 (Definition & Beginner Analogy) and Part 2 (Job Context, Example & Relationships).
  - Every split chunk prepends `Term: {term}\nCategory: {category}\n\n` to guarantee the term identity is never lost in vector search.
- In our current 60-term dataset, all records are under 1600 characters, producing **60 optimal, cohesive chunks**.

---

## 8. Output Files
The pipeline writes two deterministic JSON files to `data/processed/`:
1. `data/processed/documents.json`: Complete normalized document representations with structured fields and full searchable text.
2. `data/processed/chunks.json`: Final retrieval-ready text chunks with deterministic IDs and rich metadata tags.

---

## 9. Data Integrity & Validation
The pipeline enforces strict guarantees:
- **100% Record Preservation**: Exactly 60 source records yield 60 processed documents and 60 chunks.
- **Zero Duplicate IDs**: All `document_id` and `chunk_id` strings are strictly unique.
- **Foreign Key Integrity**: Every chunk's `document_id` references an existing document in `documents.json`.
- **Non-Empty Text**: Every chunk text begins with `Term: ` and exceeds minimum character thresholds.

---

## 10. Automated Testing
Test coverage is implemented in `tests/test_ingestion.py`:
- `test_01_all_five_input_files_can_be_loaded`: Verifies discovery of all 5 files.
- `test_02_all_input_records_pass_schema`: Validates raw records against `TerminologyRecord`.
- `test_03_expected_number_of_records_preserved`: Verifies 60 source records are preserved.
- `test_04_no_duplicate_document_ids`: Verifies document ID uniqueness.
- `test_05_processed_documents_are_non_empty`: Verifies document field contents.
- `test_06_chunks_are_non_empty`: Verifies chunk text non-emptiness.
- `test_07_no_duplicate_chunk_ids`: Verifies chunk ID uniqueness.
- `test_08_every_chunk_maps_to_valid_document`: Verifies parent-child ID mapping.
- `test_09_required_metadata_exists`: Verifies all metadata keys exist.
- `test_10_category_and_term_information_preserved`: Verifies category and term consistency.
- `test_11_source_information_preserved`: Verifies source citation integrity.
- `test_12_chunk_indices_are_valid`: Verifies `1 <= chunk_index <= total_chunks`.
- `test_13_total_chunk_count_is_consistent`: Verifies total chunk count integrity.
- `test_14_reproducibility`: Verifies back-to-back runs produce identical data.

Test result: **14/14 tests passing (100%)**.

---

## 11. Reproducibility
The pipeline is 100% deterministic:
- No non-deterministic timestamps are stored in document records.
- No random UUIDs are generated; all IDs derive directly from canonical terms.
- Repeated pipeline runs produce identical JSON output byte-for-byte.

---

## 12. Downstream Phase 4 Dependency
The output file `data/processed/chunks.json` serves as the direct input for **PHASE 4 — RAG Retrieval System**:
- The `text` field will be encoded into 384-dimensional dense vectors using `sentence-transformers/all-MiniLM-L6-v2`.
- Vectors and metadata will be indexed in a local FAISS flat/IP index for cosine similarity search.

> [!NOTE]
> **Phase Boundary Confirmation**: Embeddings, FAISS indexing, similarity search, LLM prompts, and user interfaces have **NOT** been implemented in Phase 3.
