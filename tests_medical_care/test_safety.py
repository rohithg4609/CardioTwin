import unittest

from medical_care.safety_engine import (
    check_red_flags,
    apply_safety_override,
)


class SafetyEngineTests(unittest.TestCase):

    def test_chest_pain_is_red_flag(self):
        result = check_red_flags(["chest pain"])

        self.assertTrue(result["red_flags_detected"])
        self.assertEqual(result["status"], "urgent")
        self.assertIn("chest_pain", result["matched_signs"])

    def test_normal_symptom_does_not_trigger_red_flag(self):
        result = check_red_flags(["mild tiredness"])

        self.assertFalse(result["red_flags_detected"])
        self.assertEqual(result["status"], "no_red_flags_detected")

    def test_red_flag_overrides_risk_score(self):
        result = apply_safety_override(
            ["severe breathing difficulty"],
            risk_score=0.10,
        )

        self.assertTrue(result["red_flags_detected"])
        self.assertTrue(result["risk_score_ignored_for_safety"])

    def test_low_risk_does_not_mean_safe(self):
        result = apply_safety_override(
            ["mild tiredness"],
            risk_score=0.05,
        )

        self.assertFalse(result["red_flags_detected"])
        self.assertFalse(result["risk_score_ignored_for_safety"])


if __name__ == "__main__":
    unittest.main()