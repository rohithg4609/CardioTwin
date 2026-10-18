"""CardioTwin Medical Intelligence + Care module (shell + knowledge structure)."""

from medical_care.disclaimer import PROTOTYPE_DISCLAIMER
from medical_care.knowledge import (
    DISEASES_PATH,
    KnowledgeEntry,
    KnowledgeEntryError,
    SUPPORTED_CATEGORIES,
    load_disease_entries,
    load_knowledge_file,
)

REQUIRED_KNOWLEDGE_FIELDS = (
    "id",
    "title",
    "summary",
    "source_name",
    "source_url",
)

SOURCE_FIELDS = ("source_name", "source_url")


def is_valid_knowledge_entry(entry):
    """Return True only if entry is a dict with all required fields filled in.

    Source fields are required. An entry with missing source information is invalid.
    This function does not evaluate medical content.
    """
    if not isinstance(entry, dict):
        return False
    for field in REQUIRED_KNOWLEDGE_FIELDS:
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            return False
    return True


def has_source_information(entry):
    """Return True if both source_name and source_url are present and non-empty."""
    if not isinstance(entry, dict):
        return False
    for field in SOURCE_FIELDS:
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            return False
    return True


__all__ = [
    "PROTOTYPE_DISCLAIMER",
    "REQUIRED_KNOWLEDGE_FIELDS",
    "SOURCE_FIELDS",
    "SUPPORTED_CATEGORIES",
    "DISEASES_PATH",
    "KnowledgeEntry",
    "KnowledgeEntryError",
    "is_valid_knowledge_entry",
    "has_source_information",
    "load_knowledge_file",
    "load_disease_entries",
]
