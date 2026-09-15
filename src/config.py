"""
EMP-12: Configuration and Paths Management
Centralized configuration loader supporting local environments and defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
VECTOR_STORE_DIR = MODELS_DIR / "vector_store"
DOCS_DIR = BASE_DIR / "docs"

# Load .env if present
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Core Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_GENERATION_TEMPERATURE = float(os.getenv("DEFAULT_GENERATION_TEMPERATURE", "0.2"))
MAX_CONTEXT_RESULTS = int(os.getenv("MAX_CONTEXT_RESULTS", "5"))
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.65"))
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "3"))
APP_ENV = os.getenv("APP_ENV", "development")

# Phase 6 Guardrail & Hallucination Control Settings
RETRIEVAL_SCORE_THRESHOLD = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.55"))
MIN_RELEVANT_RESULTS = int(os.getenv("MIN_RELEVANT_RESULTS", "1"))
SCORE_GAP_AMBIGUITY_THRESHOLD = float(os.getenv("SCORE_GAP_AMBIGUITY_THRESHOLD", "0.03"))
USE_CATEGORY_CONSISTENCY = os.getenv("USE_CATEGORY_CONSISTENCY", "true").lower() == "true"
USE_TERM_MATCH_SIGNAL = os.getenv("USE_TERM_MATCH_SIGNAL", "true").lower() == "true"

SAFE_FALLBACK_MESSAGE = (
    "I don't have enough information in the EMP-12 knowledge base to explain this term reliably.\n\n"
    "Please ask about a job role, technical skill, employment term, "
    "professional qualification, or industry terminology covered by the knowledge base."
)

# Phase 7 Contextual Intelligence Settings
CONTEXT_MAX_RELATED_TERMS = int(os.getenv("CONTEXT_MAX_RELATED_TERMS", "5"))
CONTEXT_MAX_EVIDENCE_ITEMS = int(os.getenv("CONTEXT_MAX_EVIDENCE_ITEMS", "3"))

# Supported Terminology Categories (EMP-12 Taxonomy)
SUPPORTED_CATEGORIES = [
    "Job Roles",
    "Technical Skills",
    "Employment Terms",
    "Professional Qualifications",
    "Industry Terminology",
]

# Supported Career Contexts for Disambiguation
SUPPORTED_CONTEXTS = [
    "General / Foundational",
    "Software Developer",
    "Data Analyst",
    "Cloud Engineer",
    "DevOps Engineer",
    "Cybersecurity Analyst",
    "UI/UX Designer",
]

# Phase 12 Security & Input Limits
MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "300"))

# Core Paths
CHUNKS_PATH = PROCESSED_DATA_DIR / "chunks.json"
DOCUMENTS_PATH = PROCESSED_DATA_DIR / "documents.json"
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
VECTOR_METADATA_PATH = VECTOR_STORE_DIR / "metadata.json"
DEFAULT_TOP_K = 5

# Ensure critical directories exist
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_error_message(text: str) -> str:
    """
    Sanitizes diagnostic strings and error messages before presenting or logging,
    redacting API credentials, authentication tokens, and internal filesystem paths.
    """
    if not text or not isinstance(text, str):
        return ""

    import re

    # 1. Redact Google API keys (AIza...)
    sanitized = re.sub(r"AIza[0-9A-Za-z\-_]+", "[REDACTED_API_KEY]", text)

    # 2. Redact generic key/token/secret assignments
    sanitized = re.sub(
        r"(?i)\b(api[_-]?key|secret|token|password|auth)\b(\s*[:=]\s*['\"]?)[a-zA-Z0-9_\-\.]{8,}['\"]?",
        r"\1\2[REDACTED_CREDENTIAL]",
        sanitized,
    )

    # 3. Redact local user directory absolute paths
    sanitized = re.sub(
        r"(?:[a-zA-Z]:[\\/](?:Users|Documents and Settings)[\\/][^\\/\s\"'>]+[\\/])",
        r"[LOCAL_USER_PATH]/",
        sanitized,
    )
    sanitized = re.sub(
        r"(?:/(?:home|Users|root)/[^/\s\"'>]+/)",
        r"[LOCAL_USER_PATH]/",
        sanitized,
    )

    return sanitized


def validate_config(require_api_key: bool = False) -> tuple[bool, str]:
    """
    Validates application environment configuration and core file dependencies.
    Returns (is_valid, status_or_error_message).
    Never exposes credentials or raw paths.
    """
    if MAX_QUERY_LENGTH <= 0:
        return False, "Invalid MAX_QUERY_LENGTH: must be a positive integer."

    if not KNOWLEDGE_BASE_DIR.exists():
        return False, "Knowledge base directory not found. Please ensure data/knowledge_base exists."

    if require_api_key and not GEMINI_API_KEY.strip():
        return (
            False,
            "GEMINI_API_KEY is not configured. Please set GEMINI_API_KEY in your environment or .env file.",
        )

    return True, "Configuration is valid."

