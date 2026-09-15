"""
EMP-12 Ingestion Pipeline
Coordinates loading, validation, normalization, chunking, and persistence of retrieval-ready documents.
"""

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import KNOWLEDGE_BASE_DIR, PROCESSED_DATA_DIR, SUPPORTED_CATEGORIES
from src.ingestion.chunker import DocumentChunker
from src.ingestion.loader import KnowledgeBaseLoader
from src.ingestion.processor import DocumentProcessor
from src.ingestion.schemas import DocumentChunk, ProcessedDocument


class IngestionPipeline:
    """
    End-to-end pipeline that ingests Phase 2 JSON datasets and produces
    normalized documents and retrieval-ready chunks.
    """

    def __init__(
        self,
        kb_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        max_chunk_chars: int = 1600,
    ):
        self.kb_dir = kb_dir or KNOWLEDGE_BASE_DIR
        self.output_dir = output_dir or PROCESSED_DATA_DIR
        self.loader = KnowledgeBaseLoader(kb_dir=self.kb_dir)
        self.processor = DocumentProcessor()
        self.chunker = DocumentChunker(max_chunk_chars=max_chunk_chars)

    def run(self) -> Dict[str, Any]:
        """
        Executes the ingestion pipeline:
        1. Load and validate raw records
        2. Normalize and create ProcessedDocuments
        3. Generate DocumentChunks with rich metadata
        4. Persist documents.json and chunks.json
        5. Return quantitative statistics report
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Load and validate
        raw_records = self.loader.load_all()
        source_records_count = len(raw_records)

        # 2. Process documents
        processed_docs = self.processor.process_records(raw_records)

        # Validate unique document IDs
        doc_ids = [doc.id for doc in processed_docs]
        duplicate_doc_ids = [doc_id for doc_id, count in Counter(doc_ids).items() if count > 1]
        if duplicate_doc_ids:
            raise ValueError(f"Duplicate document IDs detected: {duplicate_doc_ids}")

        # 3. Chunk documents
        chunks = self.chunker.chunk_documents(processed_docs)

        # Validate unique chunk IDs
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        duplicate_chunk_ids = [chunk_id for chunk_id, count in Counter(chunk_ids).items() if count > 1]
        if duplicate_chunk_ids:
            raise ValueError(f"Duplicate chunk IDs detected: {duplicate_chunk_ids}")

        # Count multi-chunk documents
        doc_chunk_counts = Counter(chunk.document_id for chunk in chunks)
        multi_chunk_docs_count = sum(1 for count in doc_chunk_counts.values() if count > 1)

        # Records by category
        category_counts = Counter(doc.category for doc in processed_docs)

        # 4. Persist outputs deterministically
        documents_path = self.output_dir / "documents.json"
        chunks_path = self.output_dir / "chunks.json"

        with open(documents_path, "w", encoding="utf-8") as f:
            json.dump([doc.model_dump() for doc in processed_docs], f, indent=2, ensure_ascii=False)

        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump([chunk.model_dump() for chunk in chunks], f, indent=2, ensure_ascii=False)

        stats = {
            "source_records": source_records_count,
            "processed_documents": len(processed_docs),
            "generated_chunks": len(chunks),
            "records_by_category": {cat: category_counts.get(cat, 0) for cat in SUPPORTED_CATEGORIES},
            "multi_chunk_documents": multi_chunk_docs_count,
            "processing_errors": 0,
            "duplicate_document_ids": len(duplicate_doc_ids),
            "duplicate_chunk_ids": len(duplicate_chunk_ids),
            "documents_file": str(documents_path),
            "chunks_file": str(chunks_path),
        }

        self._print_stats(stats)
        return stats

    def _print_stats(self, stats: Dict[str, Any]) -> None:
        """Prints a clean summary of the ingestion run."""
        print("=" * 60)
        print("         EMP-12 Document Ingestion Statistics        ")
        print("=" * 60)
        print(f"Source records: {stats['source_records']}")
        print(f"Processed documents: {stats['processed_documents']}")
        print(f"Generated chunks: {stats['generated_chunks']}")
        print("-" * 60)
        print("Records by category:")
        for cat, count in stats["records_by_category"].items():
            print(f"  - {cat}: {count}")
        print("-" * 60)
        print(f"Documents requiring multiple chunks: {stats['multi_chunk_documents']}")
        print(f"Processing errors: {stats['processing_errors']}")
        print(f"Duplicate document IDs: {stats['duplicate_document_ids']}")
        print(f"Duplicate chunk IDs: {stats['duplicate_chunk_ids']}")
        print("=" * 60)
        print(f"[SAVED] Documents: {stats['documents_file']}")
        print(f"[SAVED] Chunks:    {stats['chunks_file']}")
        print("=" * 60)


def run_ingestion() -> Dict[str, Any]:
    """Helper entrypoint to execute the complete ingestion pipeline."""
    pipeline = IngestionPipeline()
    return pipeline.run()


if __name__ == "__main__":
    run_ingestion()
