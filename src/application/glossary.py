"""
EMP-12 Glossary Service Module
Provides deterministic terminology discovery, category filtering, search,
and navigation over the curated Phase 2 knowledge base.
"""

from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from src.config import SUPPORTED_CATEGORIES
from src.ingestion.loader import load_knowledge_base


class GlossaryItem(BaseModel):
    """
    Standardized glossary preview representation for beginner browsing and discovery.
    """
    id: str = Field(..., description="Unique terminology identifier")
    term: str = Field(..., description="Canonical terminology name")
    category: str = Field(..., description="Official EMP-12 taxonomy category")
    difficulty: str = Field(..., description="Difficulty level: Beginner, Intermediate, Advanced")
    domain: str = Field(..., description="Functional technology or workplace domain")
    short_definition: str = Field(..., description="Brief, beginner-friendly definition")
    related_terms: List[str] = Field(default_factory=list, description="Traceable companion terms")
    source: str = Field(..., description="Authoritative reference citation")


class GlossaryService:
    """
    Glossary explorer service providing deterministic browsing and search
    directly over the existing Phase 2 knowledge base without duplicating data.
    """

    def __init__(self, kb_dir: Optional[Path] = None):
        records = load_knowledge_base(kb_dir=kb_dir)
        self._items: List[GlossaryItem] = [
            GlossaryItem(
                id=r.id,
                term=r.term.strip(),
                category=r.category.strip(),
                difficulty=r.difficulty.strip(),
                domain=r.domain.strip(),
                short_definition=r.short_definition.strip(),
                related_terms=[t.strip() for t in r.related_terms if t.strip()],
                source=r.source.strip(),
            )
            for r in records
        ]

    def get_total_count(self) -> int:
        """Returns the total number of approved terminology records."""
        return len(self._items)

    def get_term_difficulty(self, term: str) -> str:
        """Looks up the difficulty level for a canonical term, defaulting to Beginner."""
        if not term:
            return "Beginner"
        t_norm = term.strip().lower()
        for item in self._items:
            if item.term.strip().lower() == t_norm:
                return item.difficulty
        return "Beginner"

    def get_category_counts(self) -> Dict[str, int]:
        """
        Dynamically calculates terminology counts across all five categories and total.
        """
        counts = {"Total": len(self._items)}
        for cat in SUPPORTED_CATEGORIES:
            counts[cat] = sum(1 for item in self._items if item.category == cat)
        return counts

    def get_glossary_terms(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> List[GlossaryItem]:
        """
        Retrieves matching glossary terms based on category filter and search query.

        - Case-insensitive search
        - Whitespace-tolerant
        - Searches term names, categories, domains, and related terms (aliases)
        - Alphabetically sorted by term name
        """
        filtered = list(self._items)

        # 1. Filter by category
        if category and category != "All Categories":
            filtered = [item for item in filtered if item.category == category]

        # 2. Filter by difficulty (optional)
        if difficulty and difficulty != "All Levels":
            filtered = [item for item in filtered if item.difficulty.lower() == difficulty.lower()]

        # 3. Search query matching
        if search_query and search_query.strip():
            q = search_query.strip().lower()

            def match_score(item: GlossaryItem) -> int:
                norm_term = item.term.lower()
                # Exact match has highest priority
                if norm_term == q:
                    return 0
                # Prefix match
                if norm_term.startswith(q):
                    return 1
                # Substring match in term
                if q in norm_term:
                    return 2
                # Substring match in aliases/related terms
                for rel in item.related_terms:
                    if q in rel.lower():
                        return 3
                # Substring match in domain or category
                if q in item.domain.lower() or q in item.category.lower():
                    return 4
                return -1

            scored = [(match_score(item), item) for item in filtered]
            filtered = [item for score, item in scored if score != -1]

        # 4. Sort alphabetically by term name
        filtered.sort(key=lambda x: x.term.lower())

        return filtered
