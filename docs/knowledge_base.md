# EMP-12 Knowledge Base Architecture & Curation Guide

## 1. Knowledge Base Purpose
The EMP-12 Knowledge Base serves as the single source of truth for the **Job & Skill Terminology Simplifier**. Its primary mission is to provide an authoritative, beginner-friendly, and structured corpus of employment and technology terminology. 

Unlike general-purpose encyclopedias or search engines, every record in this knowledge base is curated specifically to:
- Demystify technical and corporate jargon for students, fresh graduates, and career transitioners.
- Provide practical workplace contexts explaining how terms function in actual jobs.
- Map semantic relationships (companion skills and related terms) to support progressive learning.
- Supply verifiable, grounded citations to eliminate hallucination when ingested into the RAG pipeline.

---

## 2. The Five Primary Categories

The knowledge base is partitioned into five distinct JSON files in `data/knowledge_base/`:

```
data/knowledge_base/
├── job_roles.json                    # 12 terms
├── technical_skills.json             # 15 terms
├── employment_terms.json             # 12 terms
├── professional_qualifications.json  # 9 terms
└── industry_terminology.json         # 12 terms
```

### Category 1: Job Roles (`job_roles.json`)
Covers foundational modern computing and digital job profiles (e.g., *Software Developer*, *Data Analyst*, *Cloud Engineer*, *DevOps Engineer*, *Cybersecurity Analyst*, *UI/UX Designer*). Each record outlines core responsibilities, day-to-day duties, and distinguishing characteristics.

### Category 2: Technical Skills (`technical_skills.json`)
Covers dominant programming languages, platforms, and technical competencies (e.g., *Python*, *SQL*, *Git*, *Docker*, *Kubernetes*, *AWS*, *REST API*, *Linux*). Focuses on practical purpose rather than compiler minutiae.

### Category 3: Employment Terms (`employment_terms.json`)
Demystifies standard employment conditions, contract structures, and work modalities (e.g., *Internship*, *Probation*, *Notice Period*, *Job Offer*, *Employment Contract*, *Remote Work*, *Hybrid Work*). Clarifies employee rights, evaluation periods, and expectations.

### Category 4: Professional Qualifications (`professional_qualifications.json`)
Distinguishes between academic credentials, industry certifications, and vocational qualifications (e.g., *Bachelor's Degree*, *Master's Degree*, *Diploma*, *Technical Certification*, *Industry Certification*). Explains what credentials signify to employers.

### Category 5: Industry Terminology (`industry_terminology.json`)
Explains ubiquitous software engineering workflows, infrastructure concepts, and organizational practices (e.g., *API*, *CI/CD*, *Deployment*, *Framework*, *Repository*, *Cloud Computing*, *Agile*, *Scrum*, *SDLC*).

---

## 3. Data Schema & Metadata Specification

All records strictly adhere to the Pydantic schema defined in `src/ingestion/schemas.py`:

```json
{
  "id": "tech_python",
  "term": "Python",
  "category": "Technical Skills",
  "short_definition": "A versatile, high-level programming language known for clean, readable syntax and a massive ecosystem of libraries.",
  "simple_explanation": "Python is designed to look like straightforward English text, which makes it one of the easiest languages for beginners to learn. It is used widely to build web backends, automate repetitive tasks, crunch data, and develop artificial intelligence models.",
  "job_context": "Python is commonly listed as a mandatory or preferred skill for software development, data analysis, automation, machine learning, and cloud administration job openings.",
  "example": "A data analyst writes a 20-line Python script using the pandas library to clean 50,000 spreadsheet rows and calculate monthly sales numbers in 3 seconds.",
  "related_skills": ["Programming", "SQL", "Git", "Data Analysis", "Problem Solving"],
  "related_terms": ["Programming Language", "Data Scientist", "Machine Learning", "Software Developer", "Scripting"],
  "difficulty": "Beginner",
  "domain": "Software Development",
  "source": "Python Software Foundation Official Documentation (python.org)"
}
```

### Schema Field Constraints
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | `string` | Unique, prefix-coded, min length 3 | Identifier (e.g., `role_*`, `tech_*`, `emp_*`, `qual_*`, `ind_*`) |
| `term` | `string` | Unique, min length 3 | Official canonical terminology name |
| `category` | `string` | Strict Enum (5 categories) | The assigned primary taxonomy category |
| `short_definition` | `string` | 1–2 sentences, no placeholders | Concise technical definition |
| `simple_explanation`| `string` | 2–4 sentences, beginner analogy | Jargon-free explanation accessible to novices |
| `job_context` | `string` | Workplace-oriented, min length 3 | How the term appears in job listings and duties |
| `example` | `string` | Concrete, realistic scenario | A real-world workplace story demonstrating the term |
| `related_skills` | `list[str]`| $\ge 2$ non-empty strings | Complementary technologies or professional competencies |
| `related_terms` | `list[str]`| $\ge 2$ non-empty strings | Conceptually adjacent vocabulary items |
| `difficulty` | `string` | Enum: `Beginner`, `Intermediate`, `Advanced` | Target learner complexity level |
| `domain` | `string` | Controlled Domain Vocabulary | Functional domain (e.g., `Software Development`, `DevOps`) |
| `source` | `string` | Verifiable authoritative reference | Real organization, standard, or official documentation |

---

## 4. Source Strategy & Verification Standards

To prevent ungrounded AI hallucinations in future RAG phases, all knowledge base records are drawn from verified, authoritative references:
1. **Government Occupational Classifications**:
   - U.S. Bureau of Labor Statistics (BLS) Occupational Outlook Handbook
   - O*NET OnLine Standard Occupational Classification (SOC)
   - U.S. Department of Labor (DOL) Fair Labor Standards & Training Administrations
2. **Recognized Scientific & Computing Standards**:
   - IEEE Computer Society Software Engineering Body of Knowledge (SWEBOK v3.0)
   - ACM Computing Classification System (CCS)
   - National Institute of Standards and Technology (NIST SP 800-145, Data Science & AI Frameworks)
   - World Wide Web Consortium (W3C) Specifications (HTML5, CSS, Web Architecture)
   - ISO/IEC/IEEE 12207 Software Life Cycle Processes
3. **Official Technology Vendor & Foundation Documentation**:
   - Python Software Foundation (python.org)
   - Docker Inc. Architecture Documentation (docs.docker.com)
   - Git SCM Documentation (git-scm.com)
   - Cloud Native Computing Foundation (CNCF) & Kubernetes Documentation
   - Amazon Web Services (AWS) Architecture Guides
   - Linux Foundation Training & Standards
4. **Professional HR & Accreditation Bodies**:
   - Society for Human Resource Management (SHRM)
   - Chartered Institute of Personnel and Development (CIPD)
   - UNESCO International Standard Classification of Education (ISCED)
   - Institute for Credentialing Excellence (ICE) Standard 1100

*Rule: No placeholder URLs or fictional citations are permitted in the knowledge base.*

---

## 5. Validation Strategy & Automated Quality Checks

Validation is enforced across two complementary layers:
1. **Pydantic Model Validation (`src/ingestion/schemas.py`)**:
   - Automatically executes field-type checks, enum validation, string trimming, and rejects common placeholder tokens (`TBD`, `TODO`, `Lorem ipsum`, `Unknown`, `N/A`).
2. **Automated Pytest Suite (`tests/test_knowledge_base.py`)**:
   - **Test 1**: All 5 category files exist on disk.
   - **Test 2**: All JSON files are well-formed JSON arrays.
   - **Test 3**: Every record validates against `TerminologyRecord`.
   - **Test 4**: All `id` fields are globally unique across all 5 files.
   - **Test 5**: Category labels strictly match their parent file.
   - **Test 6**: Difficulty ratings adhere to allowed literals.
   - **Test 7**: Mandatory string fields contain non-whitespace text ($\ge 3$ characters).
   - **Test 8**: Zero duplicate canonical terms across the dataset.
   - **Test 9**: Total record count falls within target range (55–65 records).
   - **Test 10**: `related_skills` and `related_terms` are valid non-empty lists ($\ge 2$ items).

All 10 validation tests pass with **100% success rate**.

---

## 6. Dataset Statistics

Generated via `python src/ingestion/kb_stats.py`:

```
============================================================
       EMP-12 Knowledge Base Statistics Report       
============================================================
Total Records: 60
Valid Records: 60
Invalid Records: 0
Duplicate IDs: 0
Duplicate Terms: 0
------------------------------------------------------------
Records per Category:
  - Job Roles: 12
  - Technical Skills: 15
  - Employment Terms: 12
  - Professional Qualifications: 9
  - Industry Terminology: 12
------------------------------------------------------------
Records per Difficulty:
  - Beginner: 41
  - Intermediate: 16
  - Advanced: 3
------------------------------------------------------------
Records per Domain:
  - Software Development: 18
  - Employment: 12
  - Data Science: 6
  - Web Development: 5
  - DevOps: 5
  - Education: 5
  - Professional Development: 4
  - Cloud Computing: 3
  - Cybersecurity: 1
  - Systems & Networking: 1
============================================================
```

---

## 7. How the Knowledge Base Will Be Used in Later RAG Phases

- **Phase 3 (Document Ingestion)**: Ingestion scripts will load these JSON records and compile each entry into rich, semantically cohesive document chunks with attached metadata tags (`id`, `category`, `domain`, `difficulty`, `source`).
- **Phase 4 (RAG Retrieval)**: Chunks will be embedded via `sentence-transformers/all-MiniLM-L6-v2` and indexed in FAISS for millisecond semantic similarity search.
- **Phase 5 & 7 (Contextual Generation)**: Retrieved knowledge records will be injected into Gemini system prompts to ground generated explanations, analogies, and role-conditioned answers.
- **Phase 6 (Anti-Hallucination Guardrails)**: Queries that do not match knowledge base entries with high confidence ($\text{similarity} \ge 0.65$) will trigger safe fallback responses instead of speculative generation.
