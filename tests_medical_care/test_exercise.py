import unittest

from medical_care.exercise_safety import check_exercise_safety


class ExerciseSafetyTests(unittest.TestCase):

    def test_normal_exercise_has_no_warning(self):
        result = check_exercise_safety(
            "walking",
            "moderate",
            [],
        )

        self.assertEqual(
            result["status"],
            "no_warning_detected",
        )

        self.assertFalse(
            result["is_medical_clearance"],
        )

    def test_chest_pain_during_exercise_is_flagged(self):
        result = check_exercise_safety(
            "running",
            "vigorous",
            ["chest pain"],
        )

        self.assertEqual(
            result["status"],
            "stop_and_seek_medical_help",
        )

        self.assertIn(
            "chest_pain",
            result["warning_signs"],
        )

    def test_fainting_is_flagged(self):
        result = check_exercise_safety(
            "cycling",
            "moderate",
            ["fainting"],
        )

        self.assertEqual(
            result["status"],
            "stop_and_seek_medical_help",
        )

    def test_unknown_symptom_does_not_trigger_warning(self):
        result = check_exercise_safety(
            "walking",
            "easy",
            ["normal_tiredness"],
        )

        self.assertEqual(
            result["status"],
            "no_warning_detected",
        )


if __name__ == "__main__":
    unittest.main()