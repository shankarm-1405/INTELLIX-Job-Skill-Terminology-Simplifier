"""
EMP-12 Deterministic Document Chunker
Splits or packages ProcessedDocuments into retrieval-ready DocumentChunk objects with rich metadata.
"""

from typing import List
from src.ingestion.schemas import DocumentChunk, ProcessedDocument

# Default maximum characters per chunk before splitting
DEFAULT_MAX_CHUNK_CHARS = 1600


class DocumentChunker:
    """
    Chunker responsible for creating deterministic, retrieval-ready DocumentChunk objects
    from ProcessedDocuments.
    """

    def __init__(self, max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS):
        self.max_chunk_chars = max_chunk_chars

    def chunk_document(self, doc: ProcessedDocument) -> List[DocumentChunk]:
        """
        Chunks a single ProcessedDocument:
        - If document searchable_text fits within max_chunk_chars, it forms a single cohesive chunk.
        - If longer, it splits into logical sections while prepending the Term & Category header to each chunk.
        """
        full_text = doc.searchable_text.strip()

        # If document is within threshold, keep as a single unified chunk
        if len(full_text) <= self.max_chunk_chars:
            chunk = DocumentChunk(
                chunk_id=f"{doc.id}_chunk_001",
                document_id=doc.id,
                term=doc.term,
                category=doc.category,
                difficulty=doc.difficulty,
                domain=doc.domain,
                source=doc.source,
                chunk_index=1,
                total_chunks=1,
                related_skills=doc.related_skills,
                related_terms=doc.related_terms,
                text=full_text,
            )
            return [chunk]

        # Multi-chunk splitting strategy: divide logically into 2 contextual sections
        header = f"Term: {doc.term}\nCategory: {doc.category}\n\n"

        part1_body = (
            f"Short Definition:\n{doc.short_definition}\n\n"
            f"Simple Explanation:\n{doc.simple_explanation}\n\n"
            f"Difficulty: {doc.difficulty} | Domain: {doc.domain}"
        )
        part1_text = f"{header}{part1_body}".strip()

        part2_body = (
            f"Job Context:\n{doc.job_context}\n\n"
            f"Example:\n{doc.example}\n\n"
            f"Related Skills: {', '.join(doc.related_skills)}\n\n"
            f"Related Terms: {', '.join(doc.related_terms)}\n\n"
            f"Source: {doc.source}"
        )
        part2_text = f"{header}{part2_body}".strip()

        chunk1 = DocumentChunk(
            chunk_id=f"{doc.id}_chunk_001",
            document_id=doc.id,
            term=doc.term,
            category=doc.category,
            difficulty=doc.difficulty,
            domain=doc.domain,
            source=doc.source,
            chunk_index=1,
            total_chunks=2,
            related_skills=doc.related_skills,
            related_terms=doc.related_terms,
            text=part1_text,
        )

        chunk2 = DocumentChunk(
            chunk_id=f"{doc.id}_chunk_002",
            document_id=doc.id,
            term=doc.term,
            category=doc.category,
            difficulty=doc.difficulty,
            domain=doc.domain,
            source=doc.source,
            chunk_index=2,
            total_chunks=2,
            related_skills=doc.related_skills,
            related_terms=doc.related_terms,
            text=part2_text,
        )

        return [chunk1, chunk2]

    def chunk_documents(self, documents: List[ProcessedDocument]) -> List[DocumentChunk]:
        """Chunks a collection of ProcessedDocuments deterministically."""
        all_chunks: List[DocumentChunk] = []
        for doc in documents:
            doc_chunks = self.chunk_document(doc)
            all_chunks.extend(doc_chunks)
        return all_chunks
