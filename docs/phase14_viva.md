# EMP-12: Job & Skill Terminology Simplifier
## Comprehensive Viva Voce Examination Preparation (69 Questions & Answers)

This guide provides concise, technically precise, and easily spoken answers to 69 potential viva voce questions, categorized across all core areas of EMP-12.

---

### A. Problem Understanding

**Q1: What is the official problem statement of EMP-12?**
> *“Develop a domain-specific glossary and RAG system for employment terminology such as job roles, technical skills, professional qualifications, employment terms, and industry-specific terminology.”*

**Q2: What is the required outcome of the project?**
> *“A contextual terminology assistant that explains unfamiliar employment and technology terms to beginners.”*

**Q3: Why did you choose this problem?**
> *“Beginners, students, and career changers often struggle with recruitment descriptions because corporate acronyms and technical terms are defined using complex or circular jargon. We wanted to build an assistant that gives simple, grounded explanations with workplace context.”*

**Q4: Who are the target users?**
> *“College students preparing for placements, self-taught programming beginners, and career switchers entering corporate or technical environments.”*

**Q5: What are the five official terminology categories in EMP-12?**
> *“1. Job Roles, 2. Technical Skills, 3. Employment Terms, 4. Professional Qualifications, and 5. Industry Terminology.”*

**Q6: What is the scope of EMP-12?**
> *“It strictly covers explaining terminology across these five categories using a verified 60-record knowledge base, vector retrieval, and grounded generation.”*

**Q7: What features are intentionally excluded from EMP-12?**
> *“We intentionally excluded job recommendations, candidate matching, resume building, interview simulations, salary predictions, user profiles, and general open-domain web search.”*

---

### B. Knowledge Base

**Q8: What is a domain knowledge base?**
> *“It is a curated, structured collection of verified facts and definitions representing the ground truth for our application domain.”*

**Q9: Why create a custom domain glossary instead of scraping Wikipedia?**
> *“A custom glossary ensures that every definition is pedagogical, beginner-friendly, structured, validated by Pydantic schemas, and anchored in authoritative standards without noisy web text.”*

**Q10: How many records are in the EMP-12 knowledge base?**
> *“Exactly 60 records across five JSON files in `data/knowledge_base/`.”*

**Q11: How are records distributed across categories?**
> *“12 Job Roles, 15 Technical Skills, 12 Employment Terms, 9 Professional Qualifications, and 12 Industry Terminology.”*

**Q12: What are the difficulty levels of the records?**
> *“41 terms are Beginner, 16 are Intermediate, and 3 are Advanced.”*

**Q13: Why are authoritative sources important in the knowledge base?**
> *“Authoritative sources like BLS, O*NET, IEEE, and the Python Software Foundation ensure our definitions reflect real-world labor and industry standards rather than personal opinions.”*

---

### C. Embeddings

**Q14: What is a text embedding?**
> *“An embedding is a numerical vector that captures the semantic meaning of a piece of text in high-dimensional mathematical space.”*

**Q15: Why use dense embeddings instead of simple keyword matching?**
> *“Dense embeddings understand semantic synonyms and intent. For example, they understand that 'coding language' is semantically close to 'Python' even if the exact words differ.”*

**Q16: Which embedding model does EMP-12 use?**
> *“`sentence-transformers/all-MiniLM-L6-v2`.”*

**Q17: What is the dimensionality of the embeddings?**
> *“384 dimensions.”*

**Q18: Why do you normalize the embedding vectors?**
> *“Normalizing vectors to unit length ($\|\vec{v}\|_2 = 1$) allows us to compute cosine similarity using a fast dot product without division.”*

---

### D. FAISS (Vector Store)

**Q19: What is FAISS?**
> *“FAISS stands for Facebook AI Similarity Search. It is an optimized open-source library for efficient similarity search over dense vectors.”*

**Q20: Why did you choose FAISS for this project?**
> *“FAISS provides high-speed, local vector search that runs on CPU without needing complex cloud database infrastructure.”*

**Q21: What is `IndexFlatIP` in FAISS?**
> *“`IndexFlatIP` is an exact, uncompressed index that calculates the inner product between vectors, guaranteeing exact nearest neighbors without approximation loss.”*

**Q22: What does similarity search do during retrieval?**
> *“It takes the user's query vector and finds the Top-$K$ chunk vectors in the index that have the highest cosine similarity.”*

**Q23: Why does normalized inner product correspond to cosine similarity?**
> *“When vectors are $L_2$-normalized to length 1, the cosine formula denominator becomes $1 \times 1 = 1$, making the cosine similarity mathematically identical to the dot product $\vec{q} \cdot \vec{d}$.”*

---

### E. Retrieval-Augmented Generation (RAG)

**Q24: What is RAG?**
> *“RAG stands for Retrieval-Augmented Generation. It is an architecture where an AI retrieves relevant factual documents from a knowledge store and provides them as context to an LLM to generate an answer.”*

**Q25: Why use RAG instead of asking an LLM directly?**
> *“Direct LLM prompts can hallucinate or invent plausible-sounding but false definitions. RAG forces the model to synthesize answers strictly from retrieved, verified project evidence.”*

**Q26: Explain the EMP-12 RAG pipeline in simple terms.**
> *“First, the query is validated for scope. Second, it is converted to a vector to search FAISS. Third, the evidence is checked against a 0.55 threshold. Fourth, Gemini generates a structured explanation using that evidence. Finally, grounding is verified before displaying the result.”*

**Q27: What happens when no relevant evidence is found?**
> *“If the similarity score is below 0.55, the pipeline halts and immediately returns a deterministic safe fallback without invoking Gemini.”*

**Q28: How does RAG reduce unsupported answers in EMP-12?**
> *“By restricting Gemini's prompt to synthesize only facts from the retrieved evidence chunks and locking temperature at 0.2.”*

---

### F. Google Gemini LLM

**Q29: Which LLM is used in EMP-12?**
> *“Google Gemini 2.5 Flash via the official `google-genai` SDK.”*

**Q30: Why did you choose Gemini 2.5 Flash?**
> *“It provides state-of-the-art fast reasoning, low latency, native JSON schema enforcement, and cost-efficient execution.”*

**Q31: What does temperature mean in LLM generation?**
> *“Temperature controls the randomness of generation. High values make output creative and unpredictable, while low values make output focused and deterministic.”*

**Q32: Why did you use a low temperature of 0.2?**
> *“Because EMP-12 is an educational terminology system where factual accuracy, determinism, and adherence to evidence are critical.”*

**Q33: How is model output validated?**
> *“We parse the JSON payload and validate it against our Pydantic `GeneratedAnswer` schema to ensure all required fields are present and correctly typed.”*

---

### G. Guardrails & Reliability

**Q34: What is an AI hallucination?**
> *“A hallucination is when an LLM generates information that sounds convincing but is factually incorrect or unsupported by the reference data.”*

**Q35: How does EMP-12 handle unknown terms?**
> *“Unknown terms score below our 0.55 cosine threshold during retrieval, which triggers our deterministic safe fallback response.”*

**Q36: What is the retrieval relevance threshold in EMP-12?**
> *“`RETRIEVAL_SCORE_THRESHOLD = 0.55`.”*

**Q37: How are out-of-scope queries handled?**
> *“Our pre-retrieval scope filter detects general-domain topics like weather, cooking, or arithmetic and returns a safe fallback before retrieval runs.”*

**Q38: What is post-generation grounding validation?**
> *“It is a deterministic check verifying that the generated term, category, and cited sources match the retrieved evidence chunks.”*

**Q39: What is prompt injection?**
> *“Prompt injection is an adversarial attempt by a user to override system instructions or extract sensitive configuration by manipulating the input prompt.”*

**Q40: How does EMP-12 protect against prompt injection?**
> *“Adversarial queries fail domain scope checks and relevance thresholds, triggering safe fallback without exposing system prompts or API keys.”*

---

### H. Contextual Intelligence

**Q41: What is contextual intelligence in EMP-12?**
> *“It is the ability to understand how a term is used in the workplace, identify user intent, and adjust the explanation to the beginner's level.”*

**Q42: What query intents are supported?**
> *“Seven intents: Definition, Employment Context, Usage, Role Context, Qualification Context, Industry Context, and Related Terms.”*

**Q43: Why is workplace context important for beginners?**
> *“Because beginners need to know more than just a dictionary definition; they need to understand who uses the tool, during what tasks, and why it matters in real jobs.”*

---

### I. User Interface (Streamlit)

**Q44: Why did you choose Streamlit?**
> *“Streamlit enables fast, reactive, pure-Python web interfaces that integrate natively with Python AI and machine learning libraries.”*

**Q45: What features are present in the user interface?**
> *“Terminology search, quick-start chips, structured explanation cards, difficulty badges, related-term clickable navigation, Glossary Explorer, category filtering, and study card export.”*

**Q46: What is the Glossary Explorer?**
> *“It is a read-only browser in the UI allowing students to browse, filter, and search all 60 terms offline without consuming LLM tokens.”*

**Q47: How does related-term navigation work?**
> *“Each companion term chip on an answer card is an interactive button. Clicking it automatically sends that term through the RAG pipeline.”*

---

### J. Evaluation & Benchmarking

**Q48: How many evaluation cases were in the benchmark?**
> *“92 cases: 52 supported terms, 20 unknown terms, and 20 out-of-scope queries.”*

**Q49: What is Recall@1?**
> *“The percentage of supported queries where the correct canonical term was ranked as the number one search result.”*

**Q50: What was the final Recall@1, Recall@3, and Recall@5?**
> *“100% across Recall@1, Recall@3, and Recall@5.”*

**Q51: What was the final category accuracy?**
> *“100.0%, improved from 98.08% after implementing canonical phrase re-ranking in Phase 11.”*

**Q52: What was the final end-to-end success rate?**
> *“100.0% across the 92 evaluation benchmark cases.”*

**Q53: Why is benchmark accuracy not the same as universal real-world accuracy?**
> *“Because the 100% score is measured specifically on our curated 92-case benchmark. In the open world, linguistic variations and unsupported terms will naturally trigger safe fallbacks.”*

---

### K. Performance & Caching

**Q54: What was the main performance bottleneck before Phase 11?**
> *“Repeatedly initializing the SentenceTransformer model from disk on every call, which took over 3 seconds.”*

**Q55: How did caching improve performance?**
> *“By storing the model instance, vector index, and knowledge base in memory, reducing warm initialization from 3,025 ms to 0.4 ms.”*

**Q56: What is warm latency?**
> *“Warm latency is the execution time of subsequent requests after models and data structures are already loaded in memory.”*

**Q57: What is the average warm latency of your deterministic pipeline?**
> *“Approximately 17.8 milliseconds.”*

---

### L. Security & Hardening

**Q58: How is the Gemini API key protected?**
> *“It is loaded strictly from environment variables via `os.getenv('GEMINI_API_KEY')` and is never printed, logged, or stored in code.”*

**Q59: Where is the API key stored?**
> *“In a local `.env` file that is strictly ignored by `.gitignore` and `.dockerignore`.”*

**Q60: What is the maximum query length limit?**
> *“300 characters (`MAX_QUERY_LENGTH = 300`).”*

**Q61: How did you test path traversal?**
> *“We passed paths like `../../.env` and `/etc/passwd` to the query engine and verified that they are treated as literal text and safely rejected by guardrails.”*

**Q62: Did you perform secret scanning?**
> *“Yes, our automated test suite scans the entire repository for Google API keys and credentials, finding 0 leaked keys.”*

**Q63: Are user queries stored persistently?**
> *“No, EMP-12 is strictly stateless; queries are processed in memory and discarded without database persistence.”*

**Q64: Why is Docker build marked 'Not Tested'?**
> *“Because the local development host did not have the Docker daemon installed. We created a fully valid Dockerfile but documented execution as untested for honesty.”*

---

### M. Deployment & Operations

**Q65: How can the application be deployed?**
> *“Locally using `streamlit run app.py` or inside a container using our `Dockerfile` on port 8501.”*

**Q66: What base image is used in the Dockerfile?**
> *“`python:3.11-slim` with a non-root user (`emp12user`) for security.”*

**Q67: What does `.dockerignore` exclude?**
> *“`.env`, `.git`, `__pycache__`, `tests/`, and temporary build artifacts.”*

**Q68: What settings are in `.streamlit/config.toml`?**
> *“Headless mode, port 8501, and cross-site scripting protections.”*

**Q69: What happens if the Gemini API is unreachable during deployment?**
> *“The application displays a clean configuration notice while allowing users to browse and search all 60 terms in the Glossary Explorer offline.”*
