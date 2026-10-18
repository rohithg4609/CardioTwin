import unittest

from medical_care.disease_matcher import match_disease
from medical_care.knowledge import load_disease_entries


class DiseaseMatcherTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.diseases = load_disease_entries()

    def test_hypertension_can_match_documented_symptom(self):
        results = match_disease(
            ["headache"],
            self.diseases,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["disease_id"],
            "hypertension",
        )
        self.assertIn(
            "headache",
            results[0]["matched_symptoms"],
        )

    def test_unknown_symptom_does_not_create_match(self):
        results = match_disease(
            ["completely_unknown_symptom"],
            self.diseases,
        )

        self.assertEqual(results, [])

    def test_match_is_not_a_diagnosis(self):
        results = match_disease(
            ["headache"],
            self.diseases,
        )

        self.assertEqual(
            results[0]["status"],
            "potentially_relevant",
        )

        self.assertNotEqual(
            results[0]["status"],
            "diagnosed",
        )


if __name__ == "__main__":
    unittest.main()