# EMP-12: Job & Skill Terminology Simplifier
## Deployment and Operations Guide (Phase 12)

This document provides complete instructions for configuring, packaging, and deploying EMP-12 in local and containerized environments.

---

### 1. Prerequisites

- **Python:** Python 3.10 to 3.14 (Verified in environment: `Python 3.14.3`)
- **System Memory:** Minimum 2 GB RAM (SentenceTransformer model + FAISS index occupy ~450 MB in memory)
- **Disk Space:** 500 MB for Python packages and pre-built vector indices
- **API Key:** Google Gemini API Key (optional for glossary browsing, required for grounded answer generation)
- **Container Engine (Optional):** Docker 20.10+ (if deploying via container)

---

### 2. Environment Variables

Configure environment variables in a local `.env` file (copied from `.env.example`):

| Variable | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `GEMINI_API_KEY` | String | *(None)* | Google Gemini API Key for grounded LLM answer generation |
| `GEMINI_MODEL` | String | `gemini-2.5-flash` | Gemini model variant |
| `DEFAULT_GENERATION_TEMPERATURE` | Float | `0.2` | Generation temperature for factual determinism |
| `MAX_QUERY_LENGTH` | Integer | `300` | Maximum character limit for user queries |
| `EMBEDDING_MODEL_NAME` | String | `all-MiniLM-L6-v2` | SentenceTransformer embedding model identifier |
| `RETRIEVAL_SCORE_THRESHOLD` | Float | `0.55` | Cosine similarity threshold for guardrail sufficiency |
| `TOP_K_RETRIEVAL` | Integer | `3` | Top-K candidate chunks passed to generator |
| `APP_ENV` | String | `development` | Application mode (`development` / `production`) |

---

### 3. Local Deployment Setup

#### Step 1: Clone Repository and Navigate to Workspace
```bash
cd SKILL_DEVELOPMENT
```

#### Step 2: Create and Activate Virtual Environment
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

#### Step 3: Install Locked Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Configure Credentials
```bash
cp .env.example .env
# Edit .env and supply your GEMINI_API_KEY
```

#### Step 5: Start Streamlit Application
```bash
streamlit run app.py
```
The application will launch at `http://localhost:8501`.

---

### 4. Docker Deployment

EMP-12 includes a hardened `Dockerfile` and `.dockerignore` for containerized deployment.

#### Container Build
```bash
docker build -t emp12-terminology-simplifier:latest .
```

#### Container Run
Inject the Gemini API key securely at runtime via the `-e` flag (never bake secrets into images):
```bash
docker run -d \
  --name emp12-app \
  -p 8501:8501 \
  -e GEMINI_API_KEY="your_actual_gemini_api_key" \
  emp12-terminology-simplifier:latest
```

#### Container Healthcheck
The container includes a built-in health check polling `http://localhost:8501/_stcore/health`:
```bash
docker inspect --format='{{json .State.Health}}' emp12-app
```

---

### 5. Production Streamlit Configuration (`.streamlit/config.toml`)

The application includes production-safe defaults:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

---

### 6. Verification and Health Testing

#### Verify Test Suite
Run the full automated test suite (229 tests):
```bash
python -m pytest tests/
```

#### Verify Evaluation Benchmark
Run the deterministic 92-case evaluation benchmark:
```bash
python src/evaluation/evaluator.py
```

---

### 7. Troubleshooting

| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| **"Configuration Notice: GEMINI_API_KEY is not set"** | Missing environment variable | Export `GEMINI_API_KEY` or create a `.env` file with your key. |
| **"Query is too long (maximum 300 characters)"** | Query length exceeds safety bound | Shorten the query to focus on a specific term or question. |
| **"No module named 'src'"** | Python path resolution issue | Ensure you run commands from the project root directory or set `PYTHONPATH=.`. |
| **Slow cold start (2-3 seconds)** | SentenceTransformer initial load | Expected on first query; subsequent queries leverage warm in-memory caching (< 1 ms). |

---

### 8. Deployment Limitations

- **Single-Instance Deployment:** Designed for standalone deployment or single container execution; does not implement distributed state.
- **Stateless Operation:** No persistent user database; queries and responses are not logged to disk or external stores.
- **External API Dependency:** Answer generation requires active internet connectivity to communicate with Google Gemini API endpoints.
