import unittest

from medical_care.medication_manager import (
    Medication,
    add_medication,
    record_medication_status,
)


class MedicationManagerTests(unittest.TestCase):

    def test_medication_can_be_recorded(self):
        medication = add_medication(
            name="Example Medicine",
            dose="User-entered dose",
            frequency="User-entered frequency",
            scheduled_time="08:00",
            source="doctor_record",
        )

        self.assertIsInstance(
            medication,
            Medication,
        )

        self.assertEqual(
            medication.name,
            "Example Medicine",
        )

        self.assertEqual(
            medication.source,
            "doctor_record",
        )

    def test_medication_requires_name(self):
        with self.assertRaises(ValueError):
            add_medication(
                name="",
                dose="10 mg",
                frequency="once daily",
            )

    def test_medication_requires_dose(self):
        with self.assertRaises(ValueError):
            add_medication(
                name="Example Medicine",
                dose="",
                frequency="once daily",
            )

    def test_taken_status_is_recorded(self):
        medication = add_medication(
            name="Example Medicine",
            dose="User-entered dose",
            frequency="once daily",
        )

        result = record_medication_status(
            medication,
            taken=True,
        )

        self.assertEqual(
            result["status"],
            "taken",
        )

        self.assertTrue(
            result["taken"],
        )

        self.assertFalse(
            result["treatment_changed"],
        )

    def test_missed_status_is_recorded_without_treatment_change(self):
        medication = add_medication(
            name="Example Medicine",
            dose="User-entered dose",
            frequency="once daily",
        )

        result = record_medication_status(
            medication,
            taken=False,
        )

        self.assertEqual(
            result["status"],
            "missed",
        )

        self.assertFalse(
            result["taken"],
        )

        self.assertFalse(
            result["treatment_changed"],
        )


if __name__ == "__main__":
    unittest.main()