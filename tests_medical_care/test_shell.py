"""Small tests for the Medical Intelligence + Care module shell."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from medical_care import (
    PROTOTYPE_DISCLAIMER,
    has_source_information,
    is_valid_knowledge_entry,
)


class TestModuleShell(unittest.TestCase):
    def test_disclaimer_exists_and_is_non_empty(self):
        self.assertIsInstance(PROTOTYPE_DISCLAIMER, str)
        self.assertTrue(PROTOTYPE_DISCLAIMER.strip())

    def test_knowledge_entry_is_invalid_without_source_information(self):
        entry_missing_source = {
            "id": "example-id",
            "title": "Example title",
            "summary": "Example summary",
        }
        self.assertFalse(has_source_information(entry_missing_source))
        self.assertFalse(is_valid_knowledge_entry(entry_missing_source))

        entry_empty_source = {
            "id": "example-id",
            "title": "Example title",
            "summary": "Example summary",
            "source_name": "   ",
            "source_url": "",
        }
        self.assertFalse(has_source_information(entry_empty_source))
        self.assertFalse(is_valid_knowledge_entry(entry_empty_source))

    def test_knowledge_schema_requires_source_fields(self):
        schema_path = ROOT / "data" / "knowledge_schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        required = schema.get("required", [])
        self.assertIn("source_name", required)
        self.assertIn("source_url", required)


if __name__ == "__main__":
    unittest.main()
