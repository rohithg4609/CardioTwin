import unittest

from medical_care.knowledge import load_disease_entries
from medical_care.problem_analyzer import analyze_problem


class ProblemAnalyzerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.diseases = load_disease_entries()

    def test_potential_condition_is_returned(self):
        result = analyze_problem(
            ["headache"],
            self.diseases,
        )

        self.assertEqual(
            result["status"],
            "medical_review",
        )

        self.assertFalse(
            result["is_diagnosis"],
        )

        self.assertGreaterEqual(
            len(result["potentially_relevant_conditions"]),
            1,
        )

    def test_red_flag_takes_priority(self):
        result = analyze_problem(
            ["chest pain"],
            self.diseases,
        )

        self.assertEqual(
            result["status"],
            "urgent",
        )

        self.assertTrue(
            result["safety"]["red_flags_detected"],
        )

        self.assertFalse(
            result["is_diagnosis"],
        )

    def test_unknown_symptom_is_not_diagnosed(self):
        result = analyze_problem(
            ["completely_unknown_symptom"],
            self.diseases,
        )

        self.assertEqual(
            result["status"],
            "no_specific_match",
        )

        self.assertFalse(
            result["is_diagnosis"],
        )

    def test_empty_input_is_handled(self):
        result = analyze_problem(
            [],
            self.diseases,
        )

        self.assertEqual(
            result["reported_symptoms"],
            [],
        )

        self.assertFalse(
            result["is_diagnosis"],
        )


if __name__ == "__main__":
    unittest.main()