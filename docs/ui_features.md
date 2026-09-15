# EMP-12: Job & Skill Terminology Simplifier
## User Interface & Experience Specification (Phase 8 & 9)

This document describes the design system, visual hierarchy, user experience flow, and functional components of the Streamlit web application ([`app.py`](file:///c:/Users/shank/Downloads/SKILL_DEVELOPMENT/app.py)).

---

### 1. Design Principles & Aesthetic Philosophy

The EMP-12 frontend is engineered as a clean, accessible, and structured educational interface:
- **Visual Hierarchy:** Distinct visual grouping separates the search input, explanation cards, related-term exploration, and the reference glossary.
- **Cognitive Load Reduction:** Complex terminology explanations are broken into digestible sections with intuitive iconography.
- **Accessibility:** High-contrast text, clear visual containers, and explicit category and difficulty tags ensure readability for all learners.
- **Safe State Management:** Transient session state allows instant clearing without residual history or cross-query pollution.

---

### 2. User Interface Layout & Component Hierarchy

#### 2.1 Educational Header & Scope Introduction
- **Application Title & Icon:** Displays `📘 EMP-12: Job & Skill Terminology Simplifier`.
- **Purpose Statement:** Clearly outlines the five supported categories (Job Roles, Technical Skills, Employment Terms, Qualifications, Industry Terminology).
- **Administrative Notice:** Dynamically checks `GEMINI_API_KEY`. If unconfigured, displays an informational notice explaining that glossary browsing works locally while grounded LLM generation requires the key.

#### 2.2 Quick-Start Terminology Chips
- Provides six popular one-click starter queries across the five domains:
  1. *"Python"* (Technical Skills)
  2. *"Software Developer"* (Job Roles)
  3. *"Machine Learning Engineer"* (Job Roles)
  4. *"Internship"* (Employment Terms)
  5. *"Technical Certification"* (Qualifications)
  6. *"API"* (Industry Terminology)
- Clicking any chip immediately triggers the controlled RAG pipeline without manual typing.

#### 2.3 Query Input Card
- **Text Input Box:** Placeholder with sample queries (*"What is Python?"* or *"Explain Machine Learning Engineer for beginners"*).
- **Length Bounds:** Rejects inputs shorter than 2 characters or longer than 300 characters with user-friendly notices.
- **Explain Term Button:** Primary action button launching the retrieval and generation pipeline.
- **Clear Button:** Resets active query, explanation card, and input fields.

#### 2.4 Structured Explanation Card
When a query is successfully explained, the UI displays a structured educational card:
1. **Title & Badges:** Large bold term header flanked by an informational **Category Badge** (📁) and an accessible **Difficulty Badge** (🟢 Beginner, 🟡 Intermediate, 🔴 Advanced).
2. **Simple Meaning (💡):** Highlighted callout card offering an intuitive, jargon-free plain English definition.
3. **Why It Matters (🎯):** Practical value proposition explaining why the concept is crucial in the professional world.
4. **Where It Fits in Work (🏢):** Concrete workplace context explaining which roles use the concept and during what tasks.
5. **Real-World Example (📝):** Realistic scenario grounding the abstract term in daily practice.
6. **Related Terms (🔗):** Clickable button chips for companion terminology. Clicking a companion chip automatically re-queries the system.
7. **Sources & Verification (📚):** Authoritative citations with source names and retrieval relevance scores.
8. **Copy Study Card (📋):** One-click copyable clean Markdown code block formatted for student notes.

#### 2.5 Actionable Fallback Guidance Card
When an unknown or out-of-scope query is submitted:
- Displays a clean information banner with `format_fallback_guidance()`.
- Explicitly lists the five supported categories and provides query reformulation advice without exposing internal diagnostic traces.

#### 2.6 Interactive Glossary Explorer
Located in the main content area, providing read-only exploration of all 60 knowledge-base records:
- **Category Filter Dropdown:** Filter by *All Categories* or isolate any of the 5 individual categories.
- **Live Search Field:** Instant, case-insensitive keyword and alias matching.
- **Dynamic Counters:** Displays real-time counts (e.g. `Showing 15 of 60 terms`).
- **Terminology Cards:** Expander cards for each term displaying difficulty badges, plain English definitions, workplace context, and a one-click *"Explain with AI"* button.

#### 2.7 Educational Sidebar
- **Project Taxonomy Counter:** Displays record counts per category (12 Job Roles, 15 Skills, 12 Employment Terms, 9 Qualifications, 12 Industry Terminology; 60 Total).
- **Beginner Tips:** Helpful suggestions guiding students on effective terminology queries.
