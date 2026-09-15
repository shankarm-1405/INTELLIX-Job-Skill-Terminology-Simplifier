# EMP-12: Job & Skill Terminology Simplifier
## Performance Profiling & In-Memory Caching Specification (Phase 11)

This document details the performance profiling methodology, caching architecture, cold versus warm latency benchmarks, and memory characteristics of the EMP-12 system.

---

### 1. Profiling Methodology & Bottleneck Identification

Prior to Phase 11, profiling the end-to-end pipeline revealed that repeated model instantiation and disk deserialization represented the primary latency bottlenecks:
1. **SentenceTransformer Model Loading:** Initializing `SentenceTransformer("all-MiniLM-L6-v2")` requires loading PyTorch weights into memory (~90 MB), taking ~3,000 ms.
2. **FAISS Deserialization:** Reading `index.faiss` and `metadata.json` on each query incurred unnecessary filesystem I/O (~5 ms).
3. **Knowledge Base JSON Parsing:** Parsing 5 JSON files on every glossary request incurred repeated disk reads (~2 ms).

---

### 2. Multi-Tier In-Memory Caching Architecture

To eliminate redundant computation without adding external infrastructure (such as Redis), EMP-12 implements three thread-safe, process-level caches:

#### 2.1 Embedding Model Cache (`src/retrieval/embedder.py`)
- Module-level `_MODEL_CACHE` stores the initialized `SentenceTransformer` instance.
- Module-level `_DIMENSION_CACHE` stores the embedding dimension (384).
- Subsequent initializations reuse the in-memory singleton.

#### 2.2 Vector Store & Metadata Cache (`src/retrieval/vector_store.py`)
- `_INDEX_CACHE` maps filesystem paths to tuples of `(index, metadata, mtime)`.
- Automatically validates the file's modification timestamp (`st_mtime`). If the index file is rebuilt on disk, the cache invalidates and reloads transparently.

#### 2.3 Knowledge Base Records Cache (`src/ingestion/loader.py`)
- `_KB_RECORDS_CACHE` caches parsed `TerminologyRecord` lists keyed by directory path and latest modification timestamp.

---

### 3. Empirical Latency Measurements

Benchmarks were conducted in the verified Python 3.14.3 environment:

| Operation | Subsystem | Cold Latency (First Call) | Warm Latency (Subsequent Calls) | Latency Reduction |
| :--- | :--- | :---: | :---: | :---: |
| **Model Initialization** | `TerminologyEmbedder` | ~3,025 ms | **0.4 ms** | **99.98%** |
| **Vector Store Load** | `VectorStore.load()` | ~4.8 ms | **0.05 ms** | **98.9%** |
| **Knowledge Base Load** | `KnowledgeBaseLoader.load_all()` | ~2.1 ms | **0.04 ms** | **98.1%** |
| **End-to-End Pipeline** | Retrieval + Guardrails + Context | ~48.5 ms | **17.8 ms** | **63.3%** |

*(Note: These figures represent execution on a modern multi-core development workstation. They are academic benchmarks rather than high-throughput production load guarantees).*

---

### 4. Memory Footprint & Resource Utilization

- **Base Resident Memory:** ~350 MB (Python runtime + PyTorch + Streamlit core).
- **Loaded Model Footprint:** ~90 MB resident in RAM for `all-MiniLM-L6-v2`.
- **Vector Index Footprint:** < 1 MB for 60 records (92 KB index + 113 KB metadata).
- **Total Operational Memory:** ~450 MB RAM, well within standard container and desktop limits.
