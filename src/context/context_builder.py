"""
EMP-12 Context Builder Module
Transforms Phase 4 SearchResult candidates into structured TerminologyContext
anchored strictly in retrieved evidence.
"""

from typing import List, Optional

from src.config import CONTEXT_MAX_EVIDENCE_ITEMS, CONTEXT_MAX_RELATED_TERMS
from src.context.intent import detect_query_intent
from src.context.models import ContextType, QueryIntent, TerminologyContext
from src.retrieval.models import SearchResult


class ContextBuilder:
    """
    Synthesizes structured, category-aware, and difficulty-aware contextual representations
    from retrieved SearchResult candidates without introducing external facts.
    """

    def __init__(
        self,
        max_related_terms: int = CONTEXT_MAX_RELATED_TERMS,
        max_evidence_items: int = CONTEXT_MAX_EVIDENCE_ITEMS,
    ):
        self.max_related_terms = max_related_terms
        self.max_evidence_items = max_evidence_items

    def determine_context_type(self, category: str, intent: QueryIntent) -> ContextType:
        """
        Maps taxonomy category and user intent to an explainable ContextType.
        """
        if intent == QueryIntent.RELATED_TERMS:
            return ContextType.RELATED_TERMS_CONTEXT

        mapping = {
            "Job Roles": ContextType.JOB_CONTEXT,
            "Technical Skills": ContextType.SKILL_CONTEXT,
            "Employment Terms": ContextType.EMPLOYMENT_CONTEXT,
            "Professional Qualifications": ContextType.QUALIFICATION_CONTEXT,
            "Industry Terminology": ContextType.INDUSTRY_CONTEXT,
        }
        return mapping.get(category, ContextType.TERM_CONTEXT)

    def extract_workplace_context(self, primary: SearchResult, category: str) -> str:
        """
        Extracts evidence-grounded workplace application context based on the primary chunk and category.
        """
        domain = primary.domain
        term = primary.term
        text = primary.text.strip()

        if category == "Job Roles":
            return f"In the workplace, a {term} operates within {domain}, performing tasks such as: {text}"
        elif category == "Technical Skills":
            return f"In professional environments, {term} is utilized in {domain} to accomplish development, automation, and operational goals."
        elif category == "Employment Terms":
            return f"Within employment and HR frameworks, {term} defines workplace conditions, career stages, or agreements."
        elif category == "Professional Qualifications":
            return f"In professional development, {term} represents a credential or standard verifying competence in {domain}."
        elif category == "Industry Terminology":
            return f"Across {domain} organizations, {term} serves as standard technical infrastructure or operational terminology."
        
        return f"{term} is relevant to workplace practices in {domain}."

    def build_why_it_matters(self, term: str, category: str, domain: str, difficulty: str) -> str:
        """
        Generates beginner-oriented guidance on why the terminology matters in employment.
        """
        if category == "Job Roles":
            return (
                f"Understanding the {term} role helps beginners identify career pathways, "
                f"workplace responsibilities, and expected competencies in {domain}."
            )
        elif category == "Technical Skills":
            return (
                f"Learning about {term} is valuable because it is a {difficulty.lower()}-level skill "
                f"frequently required in {domain} positions."
            )
        elif category == "Employment Terms":
            return (
                f"Familiarity with {term} is crucial for understanding workplace rights, "
                f"employment contracts, and career advancement."
            )
        elif category == "Professional Qualifications":
            return (
                f"Understanding {term} helps candidates evaluate recognized credentials "
                f"and career progression requirements in {domain}."
            )
        elif category == "Industry Terminology":
            return (
                f"Grasping {term} builds technical literacy needed to collaborate effectively "
                f"with engineering and product teams in {domain}."
            )

        return f"Understanding {term} provides essential foundational knowledge for careers in {domain}."

    def build(
        self,
        query: str,
        retrieved_results: List[SearchResult],
    ) -> TerminologyContext:
        """
        Constructs a validated TerminologyContext from query and retrieved SearchResult list.
        
        Args:
            query: User's original query string
            retrieved_results: Ranked list of SearchResult chunks from Phase 4
            
        Returns:
            Structured TerminologyContext instance
        """
        if not retrieved_results:
            raise ValueError("Cannot build TerminologyContext without retrieved SearchResults.")

        # Highest-ranked result serves as the primary canonical term
        primary = retrieved_results[0]
        term = primary.term.strip()
        category = primary.category.strip()
        domain = primary.domain.strip()
        difficulty = primary.difficulty.strip()

        # Classify intent & context type
        intent = detect_query_intent(query, category=category)
        context_type = self.determine_context_type(category, intent)

        # Merge related terms strictly from retrieved evidence
        distinct_related: List[str] = []
        for res in retrieved_results[:self.max_evidence_items]:
            for r in res.related_terms:
                cleaned_r = r.strip()
                if cleaned_r and cleaned_r not in distinct_related and cleaned_r != term:
                    distinct_related.append(cleaned_r)
                if len(distinct_related) >= self.max_related_terms:
                    break
            if len(distinct_related) >= self.max_related_terms:
                break

        # Merge authoritative sources strictly from retrieved evidence
        distinct_sources: List[str] = []
        for res in retrieved_results:
            src = res.source.strip()
            if src and src not in distinct_sources:
                distinct_sources.append(src)

        # Consolidate evidence text
        evidence_snippets = [
            f"[{r.term} ({r.category})]: {r.text.strip()}"
            for r in retrieved_results[:self.max_evidence_items]
        ]
        consolidated_text = "\n\n".join(evidence_snippets)

        # Build workplace context and why it matters
        workplace_context = self.extract_workplace_context(primary, category)
        why_it_matters = self.build_why_it_matters(term, category, domain, difficulty)

        return TerminologyContext(
            term=term,
            category=category,
            domain=domain,
            difficulty=difficulty,
            context_type=context_type,
            query_intent=intent,
            workplace_context=workplace_context,
            why_it_matters=why_it_matters,
            related_terms=distinct_related,
            sources=distinct_sources,
            evidence_text=consolidated_text,
        )
