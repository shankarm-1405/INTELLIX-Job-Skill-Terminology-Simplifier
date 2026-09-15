"""
EMP-12: Job & Skill Terminology Simplifier
Main Streamlit Application with Phase 9 Useful Features:
- Glossary Explorer with category filtering and keyword search
- One-click explanation of glossary terms
- Interactive related-term navigation
- Copy explanation functionality
- Instant reset/clear capabilities
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.application.glossary import GlossaryService
from src.application.service import TerminologyService
from src.config import GEMINI_API_KEY, SUPPORTED_CATEGORIES
from src.ui.components import (
    format_copy_text,
    format_fallback_guidance,
    is_valid_query_input,
    render_difficulty_badge,
)


# Page setup
st.set_page_config(
    page_title="EMP-12: Job & Skill Terminology Simplifier",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_terminology_service() -> TerminologyService:
    """Initializes and caches the TerminologyService once across sessions."""
    return TerminologyService()


@st.cache_resource
def get_glossary_service() -> GlossaryService:
    """Initializes and caches the GlossaryService once across sessions."""
    return GlossaryService()


# Session State Initialization
if "user_query_input" not in st.session_state:
    st.session_state["user_query_input"] = ""
if "active_response" not in st.session_state:
    st.session_state["active_response"] = None


def run_explanation(query_to_run: str):
    """Executes the controlled RAG pipeline and saves the response into session state."""
    is_valid, validation_msg = is_valid_query_input(query_to_run)
    if not is_valid:
        st.session_state["active_response"] = None
        st.warning(validation_msg)
        return

    with st.spinner("Finding relevant terminology and preparing a beginner-friendly explanation..."):
        try:
            service = get_terminology_service()
            response = service.explain_term(query_to_run)
            st.session_state["active_response"] = response
            st.session_state["user_query_input"] = query_to_run
        except Exception:
            st.session_state["active_response"] = None
            st.error("Sorry, I couldn't process the explanation right now. Please try again.")


def clear_state():
    """Resets input fields and active response."""
    st.session_state["user_query_input"] = ""
    st.session_state["active_response"] = None


# ---------------------------------------------------------------------------
# Sidebar: Project Scope & Educational Guidance
# ---------------------------------------------------------------------------
glossary_service = get_glossary_service()
category_counts = glossary_service.get_category_counts()

with st.sidebar:
    st.header("About EMP-12")
    st.markdown(
        "**Job & Skill Terminology Simplifier** is a specialized domain-specific assistant "
        "designed to help beginners, students, and career switchers navigate complex employment "
        "and technology terminology with confidence."
    )

    st.markdown("---")
    st.subheader("Knowledge Base Taxonomy")
    st.markdown(f"**Total Approved Records:** `{category_counts.get('Total', 60)}`")
    for cat in SUPPORTED_CATEGORIES:
        st.markdown(f"- **{cat}:** `{category_counts.get(cat, 0)} terms`")

    st.markdown("---")
    st.subheader("💡 Beginner Tips")
    st.markdown(
        "- Ask about specific roles (*'Software Developer'*)\n"
        "- Ask about technical tools (*'Docker'*, *'Git'*)\n"
        "- Clarify hiring terms (*'Probation'*, *'Notice Period'*)\n"
        "- Click any related term to explore companion concepts!"
    )
    st.caption("EMP-12 Academic RAG System • Strictly Grounded")


# ---------------------------------------------------------------------------
# Main Page Header & Introduction
# ---------------------------------------------------------------------------
st.title("📘 EMP-12: Job & Skill Terminology Simplifier")
st.markdown(
    "##### Understand employment and technology terms in simple, beginner-friendly language."
)
st.markdown(
    "New to the tech industry or entering the job market? EMP-12 translates technical job roles, "
    "programming skills, credentials, and workplace contracts into clear plain English, supported "
    "by real-world examples and verifiable citations."
)

if not GEMINI_API_KEY:
    st.info(
        "ℹ️ **Configuration Notice**: `GEMINI_API_KEY` is not set. You can explore all 60 terms in the "
        "Glossary Explorer below. Set `GEMINI_API_KEY` in your environment or `.env` file to enable grounded AI explanations."
    )

st.markdown("---")


# ---------------------------------------------------------------------------
# Start Exploring: Suggested Terminology Chips
# ---------------------------------------------------------------------------
st.markdown("##### 🚀 Quick Start — Popular Concepts")
suggested_terms = [
    ("Python", "Technical Skills"),
    ("Software Developer", "Job Roles"),
    ("Machine Learning Engineer", "Job Roles"),
    ("Internship", "Employment Terms"),
    ("Technical Certification", "Qualifications"),
    ("API", "Industry Terminology"),
    ("Cloud Computing", "Industry Terminology"),
]

sugg_cols = st.columns(len(suggested_terms))
for idx, (term_name, _) in enumerate(suggested_terms):
    col = sugg_cols[idx]
    with col:
        if st.button(term_name, key=f"sugg_{term_name}", use_container_width=True):
            run_explanation(term_name)


# ---------------------------------------------------------------------------
# Query Input & Action Controls
# ---------------------------------------------------------------------------
st.markdown("### 🔍 Explain a Term")
st.caption("Ask about any job role, technical skill, qualification, employment term, or industry acronym:")

input_col, btn_col, clr_col = st.columns([5, 2, 1])
with input_col:
    query_text = st.text_input(
        label="Enter an employment or technology term/question:",
        value=st.session_state["user_query_input"],
        placeholder='Try: "What is Python?" or "Explain Machine Learning Engineer for beginners"',
        key="query_text_box",
        label_visibility="collapsed",
    )

with btn_col:
    explain_clicked = st.button("Explain Term", type="primary", use_container_width=True)

with clr_col:
    clear_clicked = st.button("Clear", use_container_width=True)

if explain_clicked:
    run_explanation(query_text)

if clear_clicked:
    clear_state()
    st.rerun()


# ---------------------------------------------------------------------------
# Result Display Area
# ---------------------------------------------------------------------------
response = st.session_state.get("active_response")

if response is not None:
    if not response.success:
        if getattr(response, "is_configuration_error", False):
            st.error(f"⚙️ **Configuration Error**: {response.error_message}")
        else:
            st.warning(response.error_message or "Unable to process query.")

    elif response.is_fallback:
        st.markdown("---")
        st.info(format_fallback_guidance())

    elif response.answer:
        ans = response.answer
        term_difficulty = glossary_service.get_term_difficulty(ans.term)
        diff_badge = render_difficulty_badge(term_difficulty)

        st.markdown("---")
        # Visual Term Header & Metadata Badges
        st.subheader(f"📌 {ans.term}")
        badge_col1, badge_col2 = st.columns([1, 1])
        with badge_col1:
            st.info(f"📁 **Category:** {ans.category}")
        with badge_col2:
            st.success(f"🎯 **Target Level:** {diff_badge}")

        # Section 1: Simple Meaning
        st.markdown("#### 💡 Simple Meaning")
        st.write(ans.simple_meaning)

        # Section 2: Why It Matters (Phase 7 Context)
        if ans.why_it_matters:
            st.markdown("#### 🎯 Why It Matters")
            st.write(ans.why_it_matters)

        # Section 3: Workplace Context
        if ans.job_context:
            st.markdown("#### 🏢 Where It Fits in Work")
            st.write(ans.job_context)

        # Section 4: Beginner Example
        if ans.example:
            st.markdown("#### 🔍 Practical Beginner Example")
            st.write(ans.example)

        # Section 5: Interactive Related Terms Navigation
        if ans.related_terms:
            st.markdown("#### 🔗 Related Terms (Click to Explore)")
            rel_cols = st.columns(min(4, len(ans.related_terms)))
            for r_idx, r_term in enumerate(ans.related_terms):
                col = rel_cols[r_idx % len(rel_cols)]
                with col:
                    if st.button(r_term, key=f"rel_{ans.term}_{r_idx}", use_container_width=True):
                        run_explanation(r_term)
                        st.rerun()

        # Section 6: Authoritative Sources
        if ans.sources:
            st.markdown("#### 📚 Authoritative Sources")
            for src in ans.sources:
                st.markdown(f"- {src}")

        st.caption("Grounding verified by EMP-12 Phase 6 guardrails against official knowledge-base records.")

        # Section 7: Copy Explanation Text
        st.markdown("##### 📋 Study & Reference")
        with st.expander("Copy Explanation Text (Markdown format for notes)"):
            st.code(format_copy_text(ans), language="markdown")


# ---------------------------------------------------------------------------
# Feature 1 — Explore EMP-12 Glossary
# ---------------------------------------------------------------------------
st.markdown("---")
st.header("📖 Explore the EMP-12 Glossary")
st.markdown("Browse and discover all 60 verified terminology records directly from the domain repository.")

filter_col1, filter_col2 = st.columns([1, 1])

with filter_col1:
    category_options = ["All Categories"] + SUPPORTED_CATEGORIES
    selected_category = st.selectbox("Filter by Category:", category_options, index=0)

with filter_col2:
    search_input = st.text_input("Search terms or keywords:", placeholder="e.g., Software Developer or API")

# Fetch filtered glossary items
glossary_results = glossary_service.get_glossary_terms(
    category=selected_category,
    search_query=search_input,
)

total_kb_count = glossary_service.get_total_count()
st.caption(f"Showing **{len(glossary_results)}** of **{total_kb_count}** verified terminology items.")

if not glossary_results:
    st.info("No matching EMP-12 terminology found. Try another employment or technology term.")
else:
    for item in glossary_results:
        with st.container():
            c1, c2 = st.columns([4, 1])
            with c1:
                item_diff_badge = render_difficulty_badge(item.difficulty)
                st.markdown(f"**{item.term}** &nbsp; `{item.category}` &nbsp; *({item_diff_badge})*")
                st.caption(f"Domain: {item.domain} — {item.short_definition}")
            with c2:
                if st.button("Explain", key=f"gloss_{item.id}", use_container_width=True):
                    run_explanation(item.term)
                    st.rerun()
            st.divider()
