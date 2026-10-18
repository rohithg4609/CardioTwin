import unittest

from medical_care.condition_manager import (
    ConfirmedCondition,
    add_confirmed_condition,
    get_condition_management,
)


class ConditionManagerTests(unittest.TestCase):

    def test_confirmed_condition_can_be_created(self):
        condition = add_confirmed_condition(
            condition_id="hypertension",
            condition_name="Hypertension",
            confirmed_by="doctor",
            confirmation_date="2026-09-23",
        )

        self.assertIsInstance(
            condition,
            ConfirmedCondition,
        )

        self.assertEqual(
            condition.condition_id,
            "hypertension",
        )

        self.assertEqual(
            condition.confirmed_by,
            "doctor",
        )

    def test_condition_requires_confirmation_source(self):
        with self.assertRaises(ValueError):
            add_confirmed_condition(
                condition_id="hypertension",
                condition_name="Hypertension",
                confirmed_by="",
            )

    def test_management_does_not_invent_medication(self):
        condition = add_confirmed_condition(
            condition_id="hypertension",
            condition_name="Hypertension",
            confirmed_by="doctor",
        )

        result = get_condition_management(condition)

        self.assertEqual(
            result["status"],
            "doctor_confirmed",
        )

        self.assertEqual(
            result["management"]["medications"],
            [],
        )

        self.assertFalse(
            result["is_diagnosis"],
        )

    def test_management_preserves_confirmed_condition(self):
        condition = add_confirmed_condition(
            condition_id="hypertension",
            condition_name="Hypertension",
            confirmed_by="doctor",
        )

        result = get_condition_management(condition)

        self.assertEqual(
            result["condition"]["condition_id"],
            "hypertension",
        )

        self.assertEqual(
            result["condition"]["condition_name"],
            "Hypertension",
        )


if __name__ == "__main__":
    unittest.main()