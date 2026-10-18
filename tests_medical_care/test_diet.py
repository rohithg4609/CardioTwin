import unittest

from medical_care.diet_engine import get_diet_guidance


class DietEngineTests(unittest.TestCase):

    def test_general_guidance_is_available(self):
        result = get_diet_guidance()

        self.assertGreater(
            len(result["include_more"]),
            0,
        )

        self.assertGreater(
            len(result["consider_limiting"]),
            0,
        )

        self.assertFalse(
            result["personalized_medical_diet"],
        )

    def test_hypertension_guidance_is_available(self):
        result = get_diet_guidance(
            "hypertension",
        )

        self.assertEqual(
            result["condition"],
            "hypertension",
        )

        self.assertIn(
            "High-sodium foods",
            result["consider_limiting"],
        )

        self.assertFalse(
            result["personalized_medical_diet"],
        )

    def test_unknown_condition_does_not_create_fake_guidance(self):
        result = get_diet_guidance(
            "unknown_condition",
        )

        self.assertEqual(
            result["condition"],
            "unknown_condition",
        )

        self.assertFalse(
            result["personalized_medical_diet"],
        )

    def test_diet_engine_does_not_claim_to_diagnose(self):
        result = get_diet_guidance(
            "hypertension",
        )

        self.assertIn(
            "healthcare professional",
            result["message"],
        )


if __name__ == "__main__":
    unittest.main()
