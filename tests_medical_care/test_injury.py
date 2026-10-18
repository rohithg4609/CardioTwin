import unittest

from medical_care.injury_engine import analyze_injury


class InjuryEngineTests(unittest.TestCase):

    def test_simple_injury_returns_basic_information(self):
        result = analyze_injury(
            "minor_cut",
            ["small_wound"],
        )

        self.assertEqual(
            result["status"],
            "basic_care_information",
        )

        self.assertFalse(
            result["is_diagnosis"],
        )

    def test_heavy_bleeding_requires_medical_evaluation(self):
        result = analyze_injury(
            "cut",
            ["heavy_bleeding"],
        )

        self.assertEqual(
            result["status"],
            "medical_evaluation",
        )

        self.assertIn(
            "heavy_bleeding",
            result["urgent_signals"],
        )

    def test_severe_pain_is_flagged(self):
        result = analyze_injury(
            "injury",
            ["severe_pain"],
        )

        self.assertEqual(
            result["status"],
            "medical_evaluation",
        )

    def test_empty_information_is_handled(self):
        result = analyze_injury(
            "",
            [],
        )

        self.assertEqual(
            result["injury_type"],
            "",
        )

        self.assertFalse(
            result["is_diagnosis"],
        )


if __name__ == "__main__":
    unittest.main()