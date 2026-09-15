# Phase 8: User Interface

## 1. Phase 8 Objective

The primary objective of Phase 8 for **EMP-12: Job & Skill Terminology Simplifier** is to provide a clean, accessible, and beginner-friendly **Streamlit User Interface**.

The interface empowers students, job seekers, and career transitioners to:
1. Enter an unfamiliar employment, skill, qualification, or industry term.
2. Submit the query through a single intuitive action (`Explain Term`).
3. Receive grounded, contextual explanations synthesized across Phases 4–7.
4. Clearly view canonical terminology, category classification, plain-English meaning, career significance ("Why It Matters"), workplace context, practical examples, related skills, and authoritative citations.
5. Receive transparent, deterministic safe fallbacks when evidence is absent, weak, or out-of-scope.

---

## 2. UI Technology

The frontend is implemented in **Streamlit**, the locked presentation framework for EMP-12:
- Built in Python using standard Streamlit components.
- Main entrypoint: `app.py` at the project root.
- Execution command:
  ```bash
  streamlit run app.py
  ```
- No secondary JavaScript frameworks (React, Vue, Next.js) or separate API microservices were introduced.

---

## 3. Application Structure

The interface strictly adheres to a thin-client architecture:

```text
app.py (Streamlit UI Layer)
       │
       ▼
src/application/service.py (TerminologyService)
       │
       ▼
src/guardrails/controller.py (GuardrailController)
 ┌─────┴─────────────────────────┐
 ▼                               ▼
Phase 4 Retrieval            Phase 6 Scope & Evidence
(FAISS & Embedder)           Guardrails
 │                               │
 └──────────────┬────────────────┘
                ▼
      Phase 7 Context Layer
      (ContextBuilder & Intent)
                │
                ▼
      Phase 5 LLM Generation
      (Grounded Gemini Client)
                │
                ▼
      Phase 6 Grounding Check
      (Term, Category, Sources)
                │
                ▼
      ApplicationResponse
                │
                ▼
       Streamlit Rendering
```

---

## 4. User Flow

```text
                    USER
                      │
                      ▼
              Enter terminology
                      │
                      ▼
                Explain Term
                      │
                      ▼
              Existing EMP-12
                RAG Pipeline
                      │
                      ▼
             Phase 6 Guardrails
                      │
                      ▼
             Phase 7 Context
                      │
                      ▼
             Phase 5 Generation
                      │
                      ▼
             Phase 6 Grounding
                      │
             ┌────────┴────────┐
             │                 │
          VALID             INVALID
             │                 │
             ▼                 ▼
       Show Answer        Show Fallback
```

---

## 5. Query Input & Quick Suggestions

1. **Text Input:** A prominent text input box accepting questions or standalone terminology items with clear placeholders (e.g., `"e.g., What is Python?"`).
2. **Quick Example Buttons:** Six curated query buttons spanning different EMP-12 categories to guide beginners:
   - *"What is Python?"* (Technical Skills)
   - *"What does a software developer do?"* (Job Roles)
   - *"What does internship mean?"* (Employment Terms)
   - *"What is professional certification?"* (Professional Qualifications)
   - *"What is an API?"* (Industry Terminology)
   - *"What is cloud computing?"* (Industry Terminology)
3. **Empty Input Prevention:** Submitting empty or whitespace-only queries immediately displays a gentle warning:
   > *"Please enter a term or question to continue."*
   without invoking backend retrieval or LLM generation.

---

## 6. Answer Display Architecture

When a query is verified and grounded, the answer is rendered in an educational sequence:

1. **Visual Term Header:** Canonical term displayed prominently with an icon badge (`📌 Python`).
2. **Category Badge:** Highlighted box displaying the official taxonomy category (`Category: Technical Skills`).
3. **Simple Meaning (`💡`):** 2–3 sentence definition written in plain, jargon-free English.
4. **Why It Matters (`🎯`):** Educational rationale explaining why the term is critical for career development and workplace literacy.
5. **Where It Fits in Work (`🏢`):** Practical workplace context derived from evidence text.
6. **Beginner Example (`🔍`):** Concrete workplace application scenario.
7. **Related Terms (`🔗`):** Traceable companion skills or concepts formatted as a clean bullet list.
8. **Authoritative Sources (`📚`):** Official standards bodies, government agencies, or foundation documentation citations.

---

## 7. Safe Fallback Presentation

When Phase 6 guardrails intercept an unsupported or out-of-scope query:
- A prominent, friendly warning card is rendered containing the fixed deterministic fallback:
  ```text
  I don't have enough information in the EMP-12 knowledge base to explain this term reliably.

  Please ask about a job role, technical skill, employment term, professional qualification, or industry terminology covered by the knowledge base.
  ```
- No internal engineering diagnostics (such as FAISS distances, cosine scores, or chunk identifiers) are exposed to the user.

---

## 8. Error Handling & Resilience

The application service (`TerminologyService`) catches and encapsulates all runtime errors:
- If a backend exception occurs (e.g., network failure, rate limit), a user-friendly error message is displayed:
  > *"Sorry, I couldn't process the explanation right now. Please try again."*
- Raw Python exception tracebacks, API keys, and internal file paths are strictly suppressed from the frontend.

---

## 9. Security & API Key Protection

- **No Hardcoded Keys:** `GEMINI_API_KEY` is loaded exclusively through `src/config.py` from local `.env` files.
- **No Client-Side Leaks:** No API credentials, tokens, or system prompt instructions are rendered in the HTML DOM or Streamlit session state.
- **Resource Caching:** The application service is initialized once using `@st.cache_resource`, ensuring dense index embeddings are loaded efficiently without redundant re-initializations.

---

## 10. Accessibility Considerations

- High-contrast visual structure with standard Markdown headings (`#`, `##`, `###`).
- Informative text labels for all interactive elements.
- Semantic color coding (e.g., blue for category metadata, amber for safe fallbacks, red for errors).
- Clean responsive layout compatible with varying screen resolutions.

---

## 11. Automated Testing

The dedicated test suite (`tests/test_ui.py`) contains 20 automated tests:
1. `test_01_application_module_imports`: Validates application imports.
2. `test_02_streamlit_app_can_initialize`: Verifies `app.py` initialization.
3. `test_03_empty_query_handled`: Verifies empty input validation.
4. `test_04_whitespace_query_handled`: Verifies whitespace input validation.
5. `test_05_valid_python_query`: Tests Technical Skills execution.
6. `test_06_job_role_query`: Tests Job Roles execution.
7. `test_07_employment_term_query`: Tests Employment Terms execution.
8. `test_08_qualification_query`: Tests Professional Qualifications execution.
9. `test_09_industry_term_query`: Tests Industry Terminology execution.
10. `test_10_successful_response_structure`: Tests answer dictionary extraction.
11. `test_11_safe_fallback_response_structure`: Tests fallback response packaging.
12. `test_12_unknown_query_does_not_produce_fake_answer`: Tests unknown query fallback behavior.
13. `test_13_out_of_scope_query_remains_controlled`: Tests out-of-scope query fallback behavior.
14. `test_14_generated_term_displayed`: Verifies canonical term extraction.
15. `test_15_category_displayed`: Verifies category badge formatting.
16. `test_16_simple_meaning_displayed`: Verifies definition formatting.
17. `test_17_why_it_matters_displayed_when_available`: Verifies Phase 7 context presentation.
18. `test_18_related_terms_displayed_when_available`: Verifies companion term list formatting.
19. `test_19_sources_displayed_when_available`: Verifies source citation preservation.
20. `test_20_backend_errors_handled_gracefully`: Verifies exception suppression and user protection.

---

## 12. Manual UI Validation Results

| Test ID | Query | Category / Scope | Result Status | Observed Behavior |
| :--- | :--- | :--- | :---: | :--- |
| **Test A** | *"What is Python?"* | Technical Skills | `[PASSED]` | Full grounded answer rendered: Category *Technical Skills*, simple meaning, why it matters, workplace context, and PSF citation. |
| **Test B** | *"What does a software developer do?"* | Job Roles | `[PASSED]` | Full grounded answer rendered: Category *Job Roles*, engineering responsibilities, BLS citation. |
| **Test C** | *"What does internship mean?"* | Employment Terms | `[PASSED]` | Full grounded answer rendered: Category *Employment Terms*, training framework, DOL FLSA citation. |
| **Test D** | *"What is quantum entanglement?"* | Unknown / Non-Glossary | `[PASSED]` | Deterministic safe fallback triggered cleanly without hallucinations. |
| **Test E** | *"What is the weather today?"* | Out-of-Scope Intent | `[PASSED]` | Deterministic safe fallback triggered cleanly without LLM invocation. |

---

## 13. Limitations

- **Stateless Single-Turn Design:** The UI processes each query independently; it does not maintain multi-turn conversational memory or follow-up dialog context.
- **Fixed Display Hierarchy:** All grounded answers follow the standardized EMP-12 card structure rather than free-form conversational responses.
