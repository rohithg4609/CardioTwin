"""Tests for the reusable knowledge-base data structure."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from medical_care import PROTOTYPE_DISCLAIMER
from medical_care.knowledge import KnowledgeEntry, KnowledgeEntryError, SUPPORTED_CATEGORIES


PLACEHOLDER_ENTRY = {
    "id": "kb-placeholder-001",
    "category": "general_health_guidance",
    "title": "Placeholder title",
    "summary": "Placeholder summary used only to test the data structure.",
    "source_name": "Placeholder source name",
    "source_url": "https://example.invalid/placeholder-source",
}


class TestKnowledgeEntry(unittest.TestCase):
    def test_valid_knowledge_entry_can_be_created(self):
        entry = KnowledgeEntry.from_mapping(PLACEHOLDER_ENTRY)
        self.assertEqual(entry.id, PLACEHOLDER_ENTRY["id"])
        self.assertEqual(entry.category, "general_health_guidance")
        self.assertEqual(entry.source_name, PLACEHOLDER_ENTRY["source_name"])
        self.assertEqual(entry.source_url, PLACEHOLDER_ENTRY["source_url"])
        self.assertIn(entry.category, SUPPORTED_CATEGORIES)

    def test_entry_without_source_name_is_rejected(self):
        data = dict(PLACEHOLDER_ENTRY)
        data.pop("source_name")
        with self.assertRaises(KnowledgeEntryError):
            KnowledgeEntry.from_mapping(data)

        data_empty = dict(PLACEHOLDER_ENTRY)
        data_empty["source_name"] = "   "
        with self.assertRaises(KnowledgeEntryError):
            KnowledgeEntry.from_mapping(data_empty)

    def test_entry_without_source_url_is_rejected(self):
        data = dict(PLACEHOLDER_ENTRY)
        data.pop("source_url")
        with self.assertRaises(KnowledgeEntryError):
            KnowledgeEntry.from_mapping(data)

        data_empty = dict(PLACEHOLDER_ENTRY)
        data_empty["source_url"] = ""
        with self.assertRaises(KnowledgeEntryError):
            KnowledgeEntry.from_mapping(data_empty)

    def test_unsupported_category_is_rejected(self):
        data = dict(PLACEHOLDER_ENTRY)
        data["category"] = "not_a_supported_category"
        with self.assertRaises(KnowledgeEntryError):
            KnowledgeEntry.from_mapping(data)

    def test_disclaimer_remains_available(self):
        self.assertIsInstance(PROTOTYPE_DISCLAIMER, str)
        self.assertTrue(PROTOTYPE_DISCLAIMER.strip())


if __name__ == "__main__":
    unittest.main()
