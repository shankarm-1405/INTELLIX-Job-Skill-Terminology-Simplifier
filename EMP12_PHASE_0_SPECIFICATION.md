# EMP-12: Job & Skill Terminology Simplifier
## Comprehensive Project Specification & Architecture Document (Phase 0)

---

### Project Metadata

- **Problem ID**: EMP-12
- **Project Title**: Job & Skill Terminology Simplifier
- **Domain**: Domain-Specific Glossary, Contextual Terminology Simplification, Retrieval-Augmented Generation (RAG)
- **Official Description**: Develop a domain-specific glossary and RAG system for employment terminology such as job roles, technical skills, professional qualifications, employment terms, and industry-specific terminology.
- **Official Requirement**: Build a contextual terminology assistant that explains unfamiliar employment and technology terms to beginners.
- **Project Stage**: **Phase 0 — Project Definition, Planning & Architecture** (Specification Finalized)

---

## 1. Problem Understanding

### 1.1 The Core Problem
Entering the modern workforce or transitioning into the technology sector requires navigating a dense barrier of complex jargon. Job advertisements, onboarding guides, technical documentation, and employment contracts are filled with acronyms (e.g., CI/CD, API, IAM, K8s), ambiguous employment conditions (e.g., probation period, notice period, CTC vs. in-hand salary), hierarchical skill stacks (e.g., Git vs. GitHub, Docker vs. Kubernetes), and varying qualification requirements. 

Beginners frequently experience:
- Imposter syndrome and intimidation when reading job descriptions.
- Misunderstanding of basic employment clauses and offer letters.
- Difficulty recognizing how foundational academic knowledge maps to industry buzzwords.

**EMP-12** solves this problem by building an authoritative, domain-grounded **Job & Skill Terminology Simplifier** that translates complex employment and technology vocabulary into clear, accessible, contextualized, and reliable explanations.

### 1.2 Why Employment & Technical Terminology is Difficult for Beginners
1. **Pervasive Jargon & Acronyms**: Terms like "PR", "SLA", "CI/CD", or "Probation" are routinely used in job descriptions without foundational explanations.
2. **Contextual Polysemy**: Technical terms carry different operational meanings depending on the job role. For instance, "Deployment" means committing clean code to a junior software developer, but means managing container clusters, canary rollouts, and load balancers to a cloud/DevOps engineer.
3. **Implicit Prerequisite Knowledge**: Technical definitions often rely on other technical concepts (e.g., understanding "Docker" requires already understanding "containers", "OS virtualization", and "images").
4. **Opaque Employment & Legal Nuances**: Terms like "Probationary Period", "At-will Employment", or "Non-Compete" carry legal and career implications that standard web search engines explain only in generic, abstract, or intimidating legal language.

### 1.3 Target Audience Experiencing This Problem
- **College Students**: Preparing for campus placements and technical internships.
- **Fresh Graduates**: Deciphering job descriptions, offer letters, and corporate onboarding documentation.
- **Internship & Entry-Level Job Seekers**: Navigating skill prerequisites and job portal postings.
- **Non-Technical Career Transitioners**: Professionals pivoting into software engineering, data analysis, or cloud administration from non-STEM backgrounds.

### 1.4 Why Keyword Search is Insufficient
- **Keyword Blindness**: A keyword search returns generic, SEO-optimized definitions or Wikipedia articles written for senior engineers, heavy with mathematical abstractions and recursive jargon.
- **Lack of Role Context**: Keyword search cannot parse compound intent like *"Explain deployment to me as a junior frontend developer vs. a DevOps intern"*.
- **Fragmented Experience**: Users must open multiple tabs to piece together the definition, workplace examples, practical usage, and related companion skills.

### 1.5 Why a Static Glossary Alone is Insufficient
- **Rigid & Unresponsive**: Static glossaries offer one fixed, static sentence per term. They cannot adapt to varying beginner questions, adjust for different job roles, or provide custom analogies.
- **No Natural Language Query Understanding**: If a user asks *"What is that tool people use to save versions of code and collaborate?"*, a static glossary fails because the user does not already know the term "Git".
- **Scalability Bottlenecks**: Maintaining cross-references between thousands of skills, job roles, and industry buzzwords in static tables becomes brittle and unnavigable.

### 1.6 Why RAG (Retrieval-Augmented Generation) is the Optimal Solution
Retrieval-Augmented Generation combines the precision and veracity of a curated, domain-specific knowledge base with the communicative versatility of a modern Large Language Model (LLM):
- **Grounded Veracity**: The response is strictly anchored in verified documents (glossary records, standard occupational classifications, curriculum guides), preventing hallucinations.
- **Dynamic Simplification**: The LLM synthesizes verified technical facts into beginner-friendly analogies and intuitive language.
- **Auditability**: Every generated definition references exact source identifiers from the curated knowledge repository.

### 1.7 What Makes This a "Contextual Terminology Assistant"
Unlike a generic dictionary, EMP-12 integrates **Contextual Intelligence**:
- The assistant accepts both the **Term** and an optional **Target Context / Job Role** (e.g., Software Developer, Data Analyst, Cloud Engineer, Product Manager).
- It dynamically adapts the operational framing, workplace examples, and companion skills to that specific career lens.

---

## 2. Project Objectives

### 2.1 Primary Objective
Create a robust, RAG-powered terminology assistant that helps beginners understand employment, job-role, technical-skill, qualification, and industry terminology using simple, beginner-friendly, and contextual explanations strictly grounded in a curated, trusted knowledge base.

### 2.2 Secondary Objectives
1. **Semantic Terminology Understanding**: Enable natural language querying where users can describe a concept, search by acronym, or ask conversational questions rather than needing exact keyword matches.
2. **Context-Aware Explanations**: Provide distinct explanations and workplace applications of terms based on selected or inferred job roles (e.g., Software Engineer vs. Cloud Architect).
3. **Strict Source Grounding & Attribution**: Ensure 100% of factual claims are traced back to trusted knowledge base documents with verifiable citations.
4. **Jargon-Free Layman's Language**: Utilize intuitive analogies, progressive disclosure (simple definition first, deeper context second), and plain English suitable for beginners.
5. **Skill Graph & Related Term Linking**: Identify and output relevant prerequisites, companion technical skills, and complementary industry terms for every explained concept.
6. **Robust Unknown / Out-of-Domain Guardrails**: Detect queries outside the employment/technology domain or missing from the knowledge base, refusing to hallucinate and returning clear, polite boundaries.
7. **Structured & Deterministic Response Schema**: Standardize all outputs into a consistent 9-point layout for predictable UI rendering and high user comprehension.
8. **Low Latency & Lightweight Footprint**: Build an efficient architecture runnable in standard academic/prototyping environments using local or lightweight vector stores (FAISS) and cost-effective LLM APIs.

---

## 3. Target Users

| User Persona | Background | Pain Point | Core Benefit from EMP-12 |
| :--- | :--- | :--- | :--- |
| **Placements / College Student** | Final year undergraduate, limited industry exposure | Overwhelmed by campus recruitment job descriptions listing 20+ technologies and abbreviations. | Breaks down job requirements into clear definitions, role contexts, and prerequisite skills. |
| **Fresh Graduate** | Recent degree holder reviewing offer letters | Confused by legalistic terms like "probation period", "notice period", "CTC breakdown", and "IP assignment". | Provides clear, non-intimidating explanations of workplace contracts and employment expectations. |
| **Career Switcher / Bootcamp Learner** | Transitioning from non-tech domain (e.g., sales, operations) to IT | Struggling with recursive technical jargon in online documentation. | Offers plain-English analogies without condescension or confusing jargon. |
| **Junior Intern** | First 90 days at a technology company | Hesitant to ask senior engineers basic questions like *"What is staging vs. production?"* or *"What is CI/CD?"*. | Serves as a safe, private, always-available terminology mentor grounded in industry best practices. |

*Strict Boundary: Unrelated user groups (e.g., enterprise recruiters evaluating candidate resumes, hiring managers screening candidates, salary negotiators) are explicitly excluded.*

---

## 4. Core Use Cases

### UC-01: Technical Concept Query — "What is DevOps?"
- **User Input**: `"What is DevOps?"`
- **System Processing**:
  1. Identifies canonical term `"DevOps"` under Category `"Industry Terminology / Practice"`.
  2. Retrieves verified knowledge base chunks for `KB-IND-DEVOPS-001`.
  3. Prompts LLM with strict grounding instructions to formulate an analogy (e.g., kitchen chefs working directly with delivery staff to serve food fresh and fast).
- **Expected Output**: Structured 9-part card defining DevOps as a collaborative culture and practice bridging software developers and IT operations, complete with workplace examples and CI/CD/Docker as related skills.

### UC-02: Programming Language / Skill Query — "What is Python?"
- **User Input**: `"What is Python?"`
- **System Processing**:
  1. Identifies term `"Python"`, maps to Category `"Technical Skills"`.
  2. Fetches vector-indexed records covering Python's nature, uses, and ecosystem.
  3. Structures explanation highlighting simplicity, readability, and diverse applications (Web, AI, Automation).
- **Expected Output**: Explanation emphasizing beginner-friendly syntax, highlighting data analysis and backend development, listing related skills (SQL, Pandas, Django), and citing official documentation.

### UC-03: Job Role Scope Query — "What does a Data Analyst do?"
- **User Input**: `"What does a Data Analyst do?"`
- **System Processing**:
  1. Identifies category `"Job Roles"`.
  2. Retrieves occupational knowledge (day-to-day responsibilities, core tools, business value).
  3. LLM synthesizes actionable explanation: turning raw numbers into visual charts to help companies make business decisions.
- **Expected Output**: Clear description of daily tasks (cleaning data, writing SQL queries, building dashboards in Tableau/PowerBI), key skills (SQL, Excel, Statistics), and distinction from Data Scientists.

### UC-04: Employment Term Query — "What is probation?"
- **User Input**: `"What is probation in an employment offer?"`
- **System Processing**:
  1. Identifies category `"Employment Terms"`.
  2. Retrieves verified employment definitions regarding trial employment periods.
  3. LLM frames explanation clearly without legal jargon, explaining mutual evaluation, typical durations (3-6 months), and notice period differences.
- **Expected Output**: Plain explanation of the trial period between employee and employer, rights during probation, confirmation milestones, and related terms (Notice Period, Confirmation Letter, Performance Review).

### UC-05: Professional Qualification Query — "What is a certification?"
- **User Input**: `"What is an IT certification?"`
- **System Processing**:
  1. Identifies category `"Professional Qualifications"`.
  2. Retrieves verified taxonomy of vendor vs. vendor-neutral certifications.
  3. LLM synthesizes explanation comparing degrees vs. certifications.
- **Expected Output**: Explanation of credential verification by industry bodies (e.g., AWS Certified Cloud Practitioner), industry validity, practical preparation, and related terms (Accreditation, Continuing Education, Professional License).

### UC-06: Context-Dependent Term Query — Role Disambiguation
- **User Input**: Term: `"Deployment"`, Context: `"Software Developer"` vs Context: `"Cloud Engineer"`
- **System Processing**:
  1. Query Processing extracts term `"Deployment"` and role context parameter.
  2. For `Software Developer`: Retrieves chunks highlighting writing unit tests, creating Pull Requests, and merging code into main branch.
  3. For `Cloud Engineer`: Retrieves chunks highlighting infrastructure provisioning, container orchestration, zero-downtime canary rollouts, and server monitoring.
- **Expected Output**: Distinct contextual explanations illustrating the specific day-to-day responsibilities under each respective role.

### UC-07: Related Skills & Prerequisites Discovery
- **User Input**: `"What skills are related to Docker?"`
- **System Processing**:
  1. Identifies term `"Docker"` in category `"Technical Skills"`.
  2. Queries the knowledge base metadata for prerequisite and companion skill nodes.
  3. Synthesizes an intuitive skill tree: Containers $\rightarrow$ Linux Basics $\rightarrow$ Kubernetes $\rightarrow$ CI/CD Pipelines.
- **Expected Output**: Comprehensive breakdown of companion technologies, categorized by "Prerequisites" (Linux CLI) and "Next Steps" (Kubernetes, Helm).

### UC-08: Unknown / Out-of-Domain Query Handling
- **User Input**: `"What is Quantum Photosynthesis in cellular biology?"` or `"XYZ999Unknown"`
- **System Processing**:
  1. Query processing detects out-of-domain scope or vector retrieval scores fall below confidence threshold ($\text{similarity} < 0.65$).
  2. Guardrail module halts LLM generation and triggers fallback response.
- **Expected Output**: Controlled, polite message: *"The term 'Quantum Photosynthesis' is not recognized within our Employment & Technology Knowledge Base. EMP-12 specializes in job roles, technical skills, employment contracts, and IT terminology. Please check the spelling or explore our supported categories."*

---

## 5. Terminology Categories

### A. Job Roles
- **Software Developer / Engineer**: Builds executable software applications, writes clean code, debugs, and collaborates using version control.
- **Data Analyst**: Collects, processes, and performs statistical analysis on data to help organizations make data-driven business decisions.
- **Data Scientist**: Designs predictive machine learning models, statistical experiments, and algorithms to extract deep patterns from complex data.
- **Cloud Engineer**: Architects, deploys, and maintains infrastructure services across cloud platforms (AWS, Azure, GCP).
- **DevOps Engineer**: Automates the pipeline between software development and IT infrastructure operations (CI/CD, monitoring, containerization).
- **Cybersecurity Analyst**: Protects networks, servers, and data assets from vulnerabilities, unauthorized access, and cyber attacks.
- **UI/UX Designer**: Researches user behaviors and crafts wireframes, visual prototypes, and accessible user interaction flows.
- **Quality Assurance (QA) Engineer**: Designs automated and manual test suites to verify software functionality, reliability, and security prior to release.

### B. Technical Skills
- **Python**: High-level, dynamically typed language prized for readability, data analysis, automation, and AI development.
- **SQL (Structured Query Language)**: Standard declarative language for managing, querying, and manipulating relational databases.
- **Git**: Distributed version control system used to track code revisions, manage branches, and collaborate across engineering teams.
- **Docker**: Platform for packaging applications and their dependencies into standardized units called containers.
- **Kubernetes**: Production-grade container orchestration system for automating application deployment, scaling, and operations.
- **AWS (Amazon Web Services)**: Broad cloud computing platform providing on-demand computing power, database storage, and delivery services.
- **REST APIs**: Architectural style for networked systems enabling distinct software programs to exchange data via standard HTTP verbs.
- **Linux CLI**: Command-line interface operating system environment essential for server management, script automation, and cloud deployments.

### C. Employment Terms
- **Internship**: Supervised, temporary work arrangement intended to provide practical on-the-job training for students or novices.
- **Probation Period**: Initial evaluation period (typically 3–6 months) during which employee suitability is evaluated under modified notice terms.
- **Notice Period**: Mandatory time duration an employee or employer must give prior to terminating the employment contract.
- **CTC (Cost to Company) vs. In-Hand**: Difference between the total annual expense incurred by the employer (including benefits, PF, bonuses) and the actual net monthly take-home salary.
- **Full-Time vs. Part-Time**: Classifications dictating weekly working hours (typically 35–40+ hours for full-time) and entitlement to benefits.
- **Non-Disclosure Agreement (NDA)**: Legally binding confidentiality agreement prohibiting employees from sharing proprietary company trade secrets.
- **Performance Review**: Formal structured assessment evaluating an employee's work output, accomplishments, and professional growth against target KPIs.

### D. Professional Qualifications
- **Bachelor's Degree**: Undergraduate academic credential (e.g., B.S., B.Tech, B.C.A.) establishing fundamental theoretical and applied training.
- **Master's Degree**: Post-graduate specialized degree (e.g., M.S., M.Tech, M.B.A.) indicating advanced mastery in a technical discipline.
- **Industry Certification**: Standardized credential issued by an industry vendor or consortium verifying specific operational competence (e.g., AWS Solutions Architect, CompTIA Security+).
- **Diploma**: Focused vocational or technical qualification oriented toward practical, industry-specific skills.
- **Bootcamp Credential**: Certificate of completion from an intensive, immersive training curriculum centered on job-ready software engineering or data skills.

### E. Industry Terminology
- **API (Application Programming Interface)**: Set of rules and protocols enabling one software application to access services or data from another.
- **CI/CD (Continuous Integration / Continuous Deployment)**: Automated practice of testing, integrating code changes, and releasing software builds to production reliably.
- **Deployment**: Process of transferring tested software builds from a development environment to live production servers accessible by end users.
- **Repository (Repo)**: Centralized storage location where project files, source code, and historical change logs are managed by version control systems.
- **Production vs. Staging**: Staging is a safe sandbox environment mirroring production for final integration tests; Production is the live environment serving actual end users.
- **Agile / Scrum**: Iterative software development methodology where cross-functional teams deliver work in short, time-boxed cycles called sprints.

---

## 6. Expected Answer Structure

Every terminology response delivered by EMP-12 conforms to a standardized 9-element schema:

1. **Term**: The canonical name of the job role, skill, qualification, or term.
2. **Category**: One of the 5 locked EMP-12 taxonomy categories.
3. **Simple Meaning**: A 1-sentence plain-language definition understandable by a 10-year-old.
4. **Beginner-Friendly Explanation**: A 2–3 paragraph intuitive breakdown utilizing analogies and eliminating recursive technical jargon.
5. **Context / Job Usage**: Explicit description of how this term functions on the job in daily industry practice.
6. **Concrete Example**: A realistic workplace scenario demonstrating the term in action.
7. **Related Skills**: 3–5 complementary technologies or competencies.
8. **Related Terms**: 3–5 sibling concepts or vocabulary words frequently encountered together.
9. **Sources / Citations**: The exact knowledge-base document ID and reference name used to verify the facts.

### Fallback Schema for Unknown or Unindexed Queries
```json
{
  "status": "unsupported_term",
  "term": "<Query>",
  "message": "We could not find verified information for this term in our Employment & Skill Knowledge Base.",
  "reason": "Out of domain or unindexed terminology.",
  "suggested_categories": ["Job Roles", "Technical Skills", "Employment Terms", "Professional Qualifications", "Industry Terminology"],
  "closest_matches": ["<Nearest Term 1>", "<Nearest Term 2>"]
}
```

---

## 7. Contextual Intelligence Design

### 7.1 The Mechanism: TERM + CONTEXT $\rightarrow$ CONTEXTUAL EXPLANATION
When a beginner explores a term, its practical implications vary depending on their intended career track. EMP-12 implements a **Context Fusion Engine**:
- **Explicit Role Selection**: User selects a career lens from a pre-set list (e.g., Software Developer, Data Analyst, Cloud Engineer, DevOps Engineer, Product Management, General).
- **Context Conditioning in Prompt**: The prompt explicitly instructs the LLM:
  > *"Explain the term '[TERM]' through the professional lens of a '[CONTEXT]'. Focus on their specific day-to-day interactions, typical tooling, and responsibilities."*

### 7.2 Detailed Dual-Context Comparison

#### Example 1: Term = "Deployment"
- **Context A: Junior Software Developer**: Focuses on code completion, running unit tests, opening Pull Requests (PRs), merging code into the main branch, and checking if the automated build passes in GitHub Actions.
- **Context B: Cloud / DevOps Engineer**: Focuses on container orchestration, cloud server provisioning, configuring load balancers, rolling out canary updates, maintaining uptime, and executing automated rollbacks if latency spikes.

#### Example 2: Term = "Git"
- **Context A: Data Analyst**: Focuses on saving iterations of SQL queries, versioning Jupyter notebooks, and sharing clean data transformation scripts with team members.
- **Context B: Full-Stack Developer**: Focuses on complex feature branching, resolving merge conflicts, rebasing, running pre-commit hooks, and triggering automated staging deployments.

---

## 8. RAG Architecture

### 8.1 Step-by-Step Flow
```
User Query + Context
        │
        ▼
Streamlit Web Interface (Module 1)
        │
        ▼
Query Preprocessing & Intent Classification (Module 2)
        │
        ▼
Query Vector Embedding via Sentence-Transformers (Module 5)
        │
        ▼
FAISS Vector Database Similarity Search (Module 6)
        │
 ┌──────┴───────────────────────────────────┐
 │ Similarity >= 0.65                       │ Similarity < 0.65
 ▼                                          ▼
Context Assembly & Grounded Prompt (M7)    Unknown Query Guardrail (M10)
        │                                          │
        ▼                                          ▼
Google Gemini LLM Synthesis (T=0.2)        Controlled Fallback Response
        │                                          │
        ▼                                          │
Response Validation & Citations (M8, M9)    │
        │                                          │
        └───────────────────┬──────────────────────┘
                            │
                            ▼
           Rendered 9-Point Structured Card
```

### 8.2 Why RAG is Strictly Preferred Over Raw LLM
1. **Elimination of Hallucinations**: LLMs frequently invent realistic-sounding but incorrect technical nuances or non-existent employment rights. RAG forces the LLM to restrict answers strictly to retrieved context.
2. **Deterministic Citations**: Pure LLMs cannot cite verifiable internal records; RAG injects document IDs (`KB-ROLE-DEV-001`) directly into the prompt context.
3. **Data Freshness and Control**: Employment laws, cloud tools, and terminology evolve. Updating a RAG system requires adding or updating a JSON/Markdown file without expensive model fine-tuning.
4. **Domain Boundaries**: By measuring embedding retrieval distance against our indexed corpus, we mathematically detect out-of-scope questions before invoking the LLM, reducing token waste and avoiding out-of-scope replies.

---

## 9. Knowledge Base Design

### 9.1 Data Taxonomy & Metadata Schema
Each terminology document in the curated knowledge repository adheres to a strict JSON schema:
- `term_id`: Unique identifier (e.g., `KB-SKILL-PY-001`)
- `term`: Canonical name (e.g., `Python`)
- `aliases`: List of synonyms/acronyms (e.g., `["Python 3", "py"]`)
- `category`: `[Job Roles, Technical Skills, Employment Terms, Professional Qualifications, Industry Terminology]`
- `domain`: Sub-domain (e.g., `Software Engineering`, `Data Science`, `Human Resources`)
- `difficulty_level`: `[Beginner, Intermediate, Advanced]`
- `definition`: Authoritative formal definition
- `simple_explanation`: Plain-language explanation using analogies
- `job_contexts`: Object containing specific role descriptions (`{"Software Developer": "...", "Data Analyst": "..."}`)
- `workplace_example`: Concrete, realistic workplace scenario
- `related_skills`: Array of companion skills
- `related_terms`: Array of related terminology
- `source_reference`: Object with `source_id`, `title`, and `url_or_standard`

### 9.2 Authoritative Reference Foundations
- **O\*NET OnLine & US Bureau of Labor Statistics**: Standard Occupational Classification.
- **IEEE & ACM Computer Society Taxonomies**: Software engineering and computing standards.
- **Official Documentation**: Python Software Foundation, Docker Inc., Git SCM, Linux Foundation, AWS Whitepapers.
- **Statutory Employment Guidance**: Standard labor definitions for probation, contracts, and employment rights.

---

## 10. Functional Requirements

- **FR-01**: The system shall accept natural language queries or single terms through a clean search interface.
- **FR-02**: The system shall recognize aliases, acronyms, and common misspellings.
- **FR-03**: The system shall allow users to specify an optional career context to personalize explanations.
- **FR-04**: The system shall retrieve top-$k$ relevant knowledge chunks from the local FAISS vector store using cosine similarity.
- **FR-05**: The system shall synthesize beginner-friendly explanations with relatable analogies.
- **FR-06**: The system shall tailor workplace usage and daily duties to the selected role context.
- **FR-07**: The system shall output 3–5 companion skills and prerequisites.
- **FR-08**: The system shall provide interactive related terms for exploratory discovery.
- **FR-09**: The system shall display verified source citations with unique document identifiers.
- **FR-10**: The system shall safely reject out-of-domain and unindexed terms without hallucinating.
- **FR-11**: The system shall provide category-based browsing across all 5 terminology groups.
- **FR-12**: The system shall format responses according to the deterministic 9-point layout.

---

## 11. Non-Functional Requirements

- **Accuracy & Grounding**: $\ge 95\%$ factual alignment with knowledge base chunks; $0\%$ ungrounded hallucination on benchmark tests.
- **Response Latency**: End-to-end response time under 2.5 seconds.
- **Retrieval Precision**: Top-3 retrieval recall $\ge 90\%$ for indexed canonical terms and synonyms.
- **Readability**: Flesch-Kincaid Grade Level between 6.0 and 8.5 (plain, clear language).
- **Reliability**: Graceful handling of network timeouts or invalid queries with descriptive error states.
- **Security & Privacy**: Zero storage of personally identifiable information (PII); API keys secured via `.env`.
- **Maintainability**: Clean modular Python code conforming to PEP 8 standards with comprehensive type annotations.
- **Cost Efficiency**: Lightweight vector index (FAISS) running on CPU; compact LLM prompts minimizing token consumption.

---

## 12. Technology Stack

- **Programming Language**: **Python 3.10+** (Core runtime, modular scripts, comprehensive AI libraries).
- **User Interface**: **Streamlit** (Rapid, responsive, aesthetic pure-Python web interface).
- **RAG Orchestrator**: **LangChain (Modular Core)** (Prompt management, document loaders, retrieval chains).
- **Embedding Model**: **Sentence-Transformers (`all-MiniLM-L6-v2`)** (Fast, 384-dimensional, CPU-optimized, zero-cost offline embeddings).
- **Vector Database**: **FAISS (Facebook AI Similarity Search)** (Lightweight, local file-based vector indexing, millisecond search).
- **Large Language Model**: **Google Gemini API (`gemini-2.5-flash`)** (State-of-the-art instruction following, fast latency, cost-effective).
- **Data Storage**: **Structured JSON + Markdown** (Human-readable, git-trackable, version-controlled terminology records).

---

## 13. System Modules

- **Module 1: User Interface (`src/ui/app.py`)**: Streamlit web interface with search bar, context selector, and response cards.
- **Module 2: Query Processing & Intent Analyzer (`src/query/processor.py`)**: Sanitizes queries, detects acronyms, and resolves intent.
- **Module 3: Knowledge Base Repository (`data/knowledge_base/`)**: Curated JSON terminology records across the 5 categories.
- **Module 4: Document Ingestion Engine (`src/ingestion/indexer.py`)**: Validates schemas and chunks documents with rich metadata.
- **Module 5: Embedding Generation Service (`src/retrieval/embedder.py`)**: Generates vector representations using `all-MiniLM-L6-v2`.
- **Module 6: Vector Retrieval & Similarity Search (`src/retrieval/vector_store.py`)**: Executes FAISS cosine similarity searches.
- **Module 7: Contextual RAG Generator (`src/generator/rag_chain.py`)**: Prompts Gemini LLM with grounded context and role conditioning.
- **Module 8: Response Formatter & Validator (`src/generator/formatter.py`)**: Validates and structures outputs into the 9-part schema.
- **Module 9: Source & Citation Handler (`src/retrieval/citations.py`)**: Binds document IDs and source references to the output.
- **Module 10: Unknown Query Guardrail (`src/guardrails/validator.py`)**: Catches low-confidence searches and emits controlled fallbacks.

---

## 14. User Flow

1. User opens Streamlit application in web browser.
2. User enters a query (e.g., *"What is Git?"* or *"Explain CI/CD"*).
3. (Optional) User selects a career context (e.g., *"Software Developer"* or *"Data Analyst"*).
4. System processes query, checks domain boundaries, and generates embedding.
5. System queries local FAISS vector index for top-$k$ matching documents.
6. **Branch A (Match Found, $\text{Score} \ge 0.65$)**:
   - System injects retrieved chunks + role context into grounded prompt.
   - LLM synthesizes 9-part structured explanation.
   - UI renders formatted card with analogies, workplace usage, related skills, and verified citations.
7. **Branch B (No Match / Out of Domain, $\text{Score} < 0.65$)**:
   - Guardrail intercepts query.
   - UI renders safe fallback message explaining that the term was not found in the verified knowledge base and suggests supported categories.

---

## 15. Project Scope

### In-Scope (Strictly EMP-12)
- Domain-specific glossary across the 5 locked categories (Job Roles, Technical Skills, Employment Terms, Professional Qualifications, Industry Terminology).
- Semantic natural-language terminology search and retrieval.
- Contextual job-role disambiguation (e.g., explaining a term specifically for a Data Analyst vs. Software Engineer).
- 9-part structured explanation generation using beginner-friendly analogies.
- Extraction of companion skills and related terminology.
- Precise citation of curated knowledge base documents.
- Controlled fallback handling for unknown or out-of-domain terms.
- Clean, aesthetic, responsive Streamlit user interface.

### Out-of-Scope (Strictly Prohibited Unrelated Features)
- **NO Resume Building or CV Parsing**
- **NO Job Application Automation or Web Scraping**
- **NO Interview Simulation or Mock Interview Chatbots**
- **NO Job Recommendation Engine or Vacancy Matching**
- **NO Recruitment Automation or ATS Scoring**
- **NO Salary Prediction or Compensation Calculators**
- **NO Generic Unbounded AI Chatbot Features**

---

## 16. Minimum Viable Product (MVP) Definition

- **Must Have**: Curated knowledge base of 50+ core terms; FAISS index with `all-MiniLM-L6-v2`; search bar with role-context selector; grounded RAG generation via Gemini API; 9-part structured answer schema; citation attribution; unknown query guardrail; functional Streamlit UI.
- **Should Have**: Category browsing tabs; clickable related skill and term chips; collapsible grounding details drawer showing raw retrieved chunks.
- **Optional Enhancement**: Explanation depth toggle (summary vs. deep dive); downloadable PDF study note; side-by-side term comparison view.

---

## 17. Future Enhancements

1. **Expanded Knowledge Base (500+ Terms)**: Expanding coverage to emerging technical disciplines (e.g., Quantum Computing, Bioinformatics, Edge AI).
2. **Multilingual Simplification**: Explaining technical terms in regional languages while preserving standard English technical keywords.
3. **Voice-Assisted Queries**: Adding speech-to-text input to assist beginners with pronouncing and querying unfamiliar terms.
4. **Interactive Skill Dependency Graph**: Visual node-link graphs illustrating prerequisite and companion skills.
5. **Role Onboarding Roadmaps**: Pre-configured glossaries structured as "First 30 Days on the Job" guides for specific junior roles.
6. **Export to Educational Platforms**: Integration with flashcard systems (Anki) and campus placement portals.

---

## 18. Success Criteria & Metrics

| Criterion | Metric | Evaluation Method | Target |
| :--- | :--- | :--- | :--- |
| **Retrieval Relevance** | Hit Rate @ Top-3 | 50 benchmark queries evaluated against canonical records | $\ge 90\%$ |
| **Grounding Faithfulness** | Context Consistency | Automated evaluation verifying factual statements originate in context | $\ge 95\%$ |
| **Hallucination Prevention** | Out-of-Scope Precision | 20 adversarial / unrelated queries tested against guardrail | $100\%$ rejected |
| **Readability Score** | Flesch-Kincaid Grade | Automated readability index on generated explanations | Grade 6.0 – 8.5 |
| **Response Latency** | Wall-clock Turnaround | End-to-end execution time from query submit to render | $< 2.5$ seconds |
| **Schema Conformance** | Output Validity | Pydantic validation ensuring all 9 fields are present | $100\%$ valid |

---

## 19. Complete Project Development Roadmap (Phases 0 to 14)

- **PHASE 0 — Project Definition & Planning (Current Phase)**: Formulate complete specification, architecture, schemas, and roadmap. *[COMPLETED]*
- **PHASE 1 — Project Setup**: Initialize virtual environment, directory layout, Git configuration, and install dependencies.
- **PHASE 2 — Knowledge Base Design & Creation**: Author and validate 50+ structured JSON records across the 5 categories.
- **PHASE 3 — Document Processing & Ingestion**: Build ingestion pipeline to parse, clean, tag, and chunk terminology records.
- **PHASE 4 — RAG Retrieval System**: Implement Sentence-Transformers embedding service and FAISS vector index.
- **PHASE 5 — LLM Answer Generation**: Connect Gemini LLM API and author grounded prompt templates enforcing the 9-part schema.
- **PHASE 6 — Hallucination & Unknown Query Control**: Build similarity threshold guardrails and safe fallback handlers.
- **PHASE 7 — Contextual Intelligence Engine**: Implement role-based prompt conditioning for role disambiguation.
- **PHASE 8 — User Interface Development**: Build the core Streamlit web application with search bar, context selector, and cards.
- **PHASE 9 — Useful EMP-12 Features**: Implement category browsing tabs, clickable skill chips, and raw chunk inspection.
- **PHASE 10 — Evaluation & Testing**: Execute automated benchmark tests for retrieval recall, grounding, and latency.
- **PHASE 11 — UI/UX & Performance Improvement**: Optimize caching, style UI cards, eliminate layout shift, and streamline latency.
- **PHASE 12 — Security & Deployment**: Secure API keys, audit dependencies, and author deployment launcher scripts.
- **PHASE 13 — Documentation**: Create comprehensive README, Architecture Handbook, and Knowledge Base Curation Guide.
- **PHASE 14 — Final Presentation, Demo & Viva**: Prepare slide deck, live demo walkthrough script, and academic viva defense materials.

---

## 20. Development Rules for Future Phases

1. **Stay Strictly Within EMP-12**: Only build features directly relevant to job and skill terminology simplification for beginners.
2. **Sequential Phase Progression**: Complete and verify each phase before moving to the next.
3. **No Over-Engineering**: Prefer simple, reliable, and maintainable Python architectures.
4. **Prioritize Simplicity & Reliability**: Use proven libraries (Streamlit, FAISS, Sentence-Transformers, Gemini).
5. **Strict Knowledge Grounding**: All generated answers must be anchored in the curated knowledge base.
6. **Zero Hallucination Tolerance**: Reject unverified or out-of-domain terms safely using the standardized fallback schema.
7. **Preserve Source Attribution**: Always cite the knowledge base document ID and reference.
8. **Decoupled Modular Design**: Keep UI, retrieval, generation, and guardrail logic cleanly separated.
9. **Rigorous Component Testing**: Verify each module independently before system integration.
10. **Pre-Implementation Briefings**: Summarize planned file changes prior to execution.
11. **Protect Working Code**: Avoid modifying already tested and functioning modules.
12. **Professional Code Hygiene**: Adhere to PEP 8, type hints, docstrings, and clean directory structure.
13. **Synchronized Documentation**: Update documentation simultaneously with code changes.
14. **User Approval for Architectural Shifts**: Seek explicit approval before altering core models, schemas, or libraries.
15. **Verify Phase Prerequisites**: Ensure all dependent outputs are validated before commencing subsequent phases.

---

## 21. Sign-off & Next Steps

**Phase 0 is complete.** No application code has been written, no packages have been installed, and no RAG pipeline has been initiated.

Execution is paused awaiting user review and approval of this specification before advancing to **Phase 1: Project Setup**.
