# EMP-12 RAG Retrieval System Specification

## 1. Phase 4 Objective
The objective of Phase 4 is to construct an authoritative, local, and persistent semantic retrieval engine that indexes the 60 processed knowledge chunks from Phase 3 and performs fast cosine similarity searches for user terminology queries across EMP-12's five domain categories:
1. **Job Roles**
2. **Technical Skills**
3. **Employment Terms**
4. **Professional Qualifications**
5. **Industry Terminology**

> [!NOTE]
> **Architectural Boundary**: Phase 4 is solely responsible for retrieving relevant chunk evidence and metadata with similarity scores. It does **NOT** generate answers or invoke Large Language Models. Phase 5 will consume these retrieval results.

---

## 2. Input Data
The retrieval system consumes exclusively the validated Phase 3 output:
- **Location**: [`data/processed/chunks.json`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/data/processed/chunks.json)
- **Content**: 60 retrieval-ready terminology chunks with full contextual text, deterministic chunk IDs (`{doc_id}_chunk_001`), and rich metadata attributes (`category`, `difficulty`, `domain`, `source`, `related_skills`, `related_terms`).

---

## 3. Embedding Model
- **Library**: `sentence-transformers` (v6.0.1)
- **Model**: `all-MiniLM-L6-v2` (configured via `EMBEDDING_MODEL_NAME` in `src/config.py`)
- **Dimensionality**: **384 dimensions** (dense floating-point vectors)
- **Consistency**: The exact same model is utilized symmetrically for embedding knowledge chunks and runtime user queries.

---

## 4. Embedding Process
1. Complete searchable chunk texts from `chunks.json` are passed to `TerminologyEmbedder.embed_texts()`.
2. Raw sentence embeddings are generated via `model.encode(batch_size=32)`.
3. Every vector is cast to `float32` and normalized to unit length ($\ell_2$-norm):
   $$\mathbf{v}_{\text{norm}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2}$$
4. Unit normalization guarantees that subsequent inner product calculations directly equal mathematical cosine similarity.

---

## 5. Vector Store Architecture & FAISS Configuration
- **Engine**: FAISS (`faiss-cpu` v1.15.0)
- **Index Type**: `faiss.IndexFlatIP(384)` (Inner Product index on normalized vectors)
- **Storage Strategy**:
  - Binary index file: [`models/vector_store/index.faiss`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/models/vector_store/index.faiss) (92 KB)
  - Metadata mapping file: [`models/vector_store/metadata.json`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/models/vector_store/metadata.json) (113 KB)
- **Zero-Server Local Footprint**: Runs in-process with millisecond response time on CPU without external vector databases.

---

## 6. Similarity Metric & Mathematical Equivalence
Cosine similarity between query vector $\mathbf{q}$ and chunk vector $\mathbf{d}$ is defined as:
$$\text{CosineSimilarity}(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\|_2 \|\mathbf{d}\|_2}$$
Because both query and chunk vectors are $\ell_2$-normalized prior to search ($\|\mathbf{q}\|_2 = 1$, $\|\mathbf{d}\|_2 = 1$), FAISS `IndexFlatIP` computes:
$$\text{InnerProduct}(\mathbf{q}, \mathbf{d}) = \mathbf{q} \cdot \mathbf{d} \equiv \text{CosineSimilarity}(\mathbf{q}, \mathbf{d})$$
Similarity scores range between $0.0$ and $1.0$ (or near $1.0$ for exact semantic alignment).

---

## 7. Metadata Mapping & Traceability
FAISS stores only numerical floating-point vectors and integer row positions ($0, 1, \dots, 59$). To ensure absolute traceability, `FAISSVectorStore` maintains a parallel array in `metadata.json` where row index $i$ maps to the full chunk object:
```
Vector Row i
     │
     ▼
metadata[i]
  ├── chunk_id: "tech_python_chunk_001"
  ├── document_id: "tech_python"
  ├── term: "Python"
  ├── category: "Technical Skills"
  ├── difficulty: "Beginner"
  ├── domain: "Software Development"
  ├── source: "Python Software Foundation..."
  ├── related_skills: ["Programming", "SQL", ...]
  └── text: "Term: Python\n\nCategory: Technical Skills..."
```

---

## 8. Query Flow
```
User Query: "What does a software developer do?"
                 │
                 ▼
TerminologyRetriever.search()
  - Validates query (non-empty, >= 2 chars)
  - Validates top_k (integer >= 1)
  - Validates optional category filter
                 │
                 ▼
TerminologyEmbedder.embed_text()
  - Generates 384-dimensional dense vector
  - Applies L2 normalization
                 │
                 ▼
FAISSVectorStore.search()
  - Executes IndexFlatIP.search(query_vec, k)
  - Obtains top candidate indices and inner product scores
  - Filters by category (if specified)
                 │
                 ▼
Ranked SearchResult List
  - Rank 1: Software Developer (Score: 0.6974)
  - Rank 2: Backend Developer (Score: 0.5176)
  - Rank 3: Full Stack Developer (Score: 0.4511)
```

---

## 9. Top-K & Category-Aware Retrieval
The retriever interface supports customizable depth and category scoping:
```python
retriever = TerminologyRetriever()

# Standard Top-K search
results = retriever.search("What is machine learning?", top_k=5)

# Category-filtered search
results = retriever.search(
    query="What is a cloud engineer?",
    top_k=3,
    category="Job Roles"
)
```
If an invalid category is supplied, a descriptive `ValueError` is raised immediately.

---

## 10. Index Persistence & Rebuilding
- **Building & Persisting**: Executable via CLI tool:
  ```bash
  python src/retrieval/build_index.py
  ```
- **Auto-Loading**: `TerminologyRetriever` automatically loads `index.faiss` and `metadata.json` on initialization if they exist on disk.
- **Rebuilding**: `retriever.rebuild_index()` re-encodes all chunks from `data/processed/chunks.json` and updates the on-disk index deterministically.

---

## 11. Automated Testing & Verification
All 20 retrieval test cases are implemented in [`tests/test_retrieval.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/tests/test_retrieval.py):
1. `test_01_embedding_model_loads_successfully`: Confirms 384 dimensions.
2. `test_02_all_60_chunks_can_be_embedded`: Verifies batch encoding of all 60 chunks.
3. `test_03_embedding_dimensions_are_consistent`: Verifies L2 normalization and vector shape.
4. `test_04_vector_count_equals_chunk_count`: Confirms 60 vectors indexed.
5. `test_05_faiss_index_can_be_saved`: Verifies disk persistence.
6. `test_06_faiss_index_can_be_loaded`: Verifies index loading.
7. `test_07_every_indexed_vector_maps_to_valid_chunk_id`: Confirms ID consistency.
8. `test_08_duplicate_chunk_ids_are_rejected`: Enforces uniqueness constraints.
9. `test_09_normal_terminology_query_returns_results`: Evaluates "What is Python?".
10. `test_10_job_role_query_returns_relevant_terminology`: Evaluates "What does a software developer do?".
11. `test_11_technical_skill_query_returns_relevant_terminology`: Evaluates "What is machine learning?".
12. `test_12_employment_term_query_returns_relevant_terminology`: Evaluates "What does internship mean?".
13. `test_13_professional_qualification_query_returns_relevant_terminology`: Evaluates "What is a professional certification?".
14. `test_14_industry_terminology_query_returns_relevant_terminology`: Evaluates "What is an API?".
15. `test_15_results_are_sorted_by_descending_similarity_score`: Verifies ranking order.
16. `test_16_top_k_works_correctly`: Tests $k \in \{1, 3, 5, 10\}$.
17. `test_17_empty_query_is_handled_correctly`: Validates query error boundaries.
18. `test_18_invalid_category_is_handled_correctly`: Validates category filtering constraints.
19. `test_19_retrieved_metadata_matches_original_chunk`: Verifies verbatim chunk data integrity.
20. `test_20_index_can_be_rebuilt_successfully`: Validates index rebuilding.

---

## 12. Retrieval Quality Inspection Results
Representative terminology queries evaluated via [`src/retrieval/inspect_retrieval.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/src/retrieval/inspect_retrieval.py):

| Query | Top Term Retrieved | Category | Cosine Similarity |
| :--- | :--- | :--- | :--- |
| *"What is Python?"* | **Python** | Technical Skills | 0.6864 |
| *"What does a software developer do?"* | **Software Developer** | Job Roles | 0.6974 |
| *"What is machine learning?"* | **Machine Learning** | Technical Skills | 0.7134 |
| *"What does internship mean?"* | **Internship** | Employment Terms | 0.7576 |
| *"What is a professional certification?"* | **Professional Certification** | Professional Qualifications | 0.7739 |
| *"What is DevOps?"* | **DevOps Engineer** | Job Roles | 0.6508 |
| *"What is cloud computing?"* | **Cloud Computing** | Industry Terminology | 0.7597 |
| *"What is an API?"* | **API** | Industry Terminology | 0.7212 |
| *"What is a cybersecurity skill?"* | **Cybersecurity Analyst** | Job Roles | 0.6832 |
| *"What is a technical qualification?"* | **Professional Qualification** | Professional Qualifications | 0.6392 |

---

## 13. System Limitations
- **Corpus Boundary**: The index represents the 60 curated Phase 2 terminology records. Out-of-domain terms (e.g., biological sciences or culinary terms) will naturally yield low cosine similarity scores ($< 0.40$).
- **No Generative Synthesis**: The retrieval system emits verbatim evidence chunks and scores; it does not synthesize plain-English conversational answers.

---

## 14. How Phase 5 Will Consume Retrieval Results
In **PHASE 5 — LLM Answer Generation**:
1. When a user enters a query, `TerminologyRetriever.search(query, top_k=3)` will retrieve the top 3 evidence chunks.
2. The retrieved chunks and their source identifiers will be formatted into a strictly grounded context prompt.
3. Google Gemini LLM API will synthesize the grounded evidence into the 9-part structured response format for beginners.
