"""Tests for the disease knowledge base."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from medical_care.knowledge import (
    DISEASES_PATH,
    KnowledgeEntry,
    load_disease_entries,
    load_knowledge_file,
)


PLANNED_OPTIONAL_FIELDS = (
    "common_symptoms",
    "risk_factors",
    "relevant_measurements",
    "warning_signs",
    "general_lifestyle_information",
    "when_medical_evaluation_is_appropriate",
)


class TestDiseaseCollectionStructure(unittest.TestCase):

    def test_diseases_json_exists(self):
        self.assertTrue(DISEASES_PATH.is_file())

    def test_diseases_json_structure_is_valid(self):
        raw = json.loads(DISEASES_PATH.read_text(encoding="utf-8"))

        self.assertIsInstance(raw, dict)
        self.assertEqual(raw.get("collection"), "diseases")
        self.assertEqual(raw.get("entry_category"), "disease")
        self.assertIsInstance(raw.get("entries"), list)

        required = raw.get("required_fields")
        self.assertIsInstance(required, list)
        self.assertIn("source_name", required)
        self.assertIn("source_url", required)
        self.assertIn("category", required)

        planned = raw.get("planned_optional_fields")
        self.assertIsInstance(planned, list)

        for field in PLANNED_OPTIONAL_FIELDS:
            self.assertIn(field, planned)

    def test_hypertension_entry_exists(self):
        loaded = load_disease_entries()

        hypertension = [
            entry for entry in loaded
            if entry.id == "hypertension"
        ]

        self.assertEqual(len(hypertension), 1)

        entry = hypertension[0]

        self.assertEqual(entry.category, "disease")
        self.assertEqual(entry.title, "Hypertension")
        self.assertTrue(entry.summary)
        self.assertTrue(entry.source_name)
        self.assertTrue(entry.source_url)

    def test_hypertension_has_expected_information(self):
        raw = json.loads(DISEASES_PATH.read_text(encoding="utf-8"))

        hypertension = next(
            item
            for item in raw["entries"]
            if item.get("id") == "hypertension"
        )

        for field in PLANNED_OPTIONAL_FIELDS:
            self.assertIn(field, hypertension)
            self.assertIsInstance(hypertension[field], list)

    def test_no_unsourced_medical_entries(self):
        raw = json.loads(DISEASES_PATH.read_text(encoding="utf-8"))

        for item in raw["entries"]:
            self.assertTrue(str(item.get("source_name", "")).strip())
            self.assertTrue(str(item.get("source_url", "")).strip())

    def test_can_be_loaded_by_knowledge_infrastructure(self):
        loaded = load_knowledge_file(
            DISEASES_PATH,
            expected_category="disease",
        )

        self.assertGreaterEqual(len(loaded), 1)
        self.assertTrue(
            all(isinstance(item, KnowledgeEntry) for item in loaded)
        )

        also_loaded = load_disease_entries()
        self.assertEqual(len(also_loaded), len(loaded))


if __name__ == "__main__":
    unittest.main()