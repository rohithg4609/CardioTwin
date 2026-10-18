import unittest

from digital_twin.patient import Patient


class TestPatient(unittest.TestCase):

    def make_patient(self):
        return Patient(
            patient_id="P001",
            name="Test User",
            age=45,
            sex="Male",
            height=172,
            weight=72,
            family_history=["Hypertension"],
            smoking=False,
            existing_conditions=["Documented condition"],
            medications=[{"name": "Example Medication"}],
        )

    def test_patient_creation(self):
        patient = self.make_patient()

        self.assertEqual(patient.patient_id, "P001")
        self.assertEqual(patient.name, "Test User")
        self.assertEqual(patient.age, 45)
        self.assertEqual(patient.sex, "Male")
        self.assertEqual(patient.height, 172.0)
        self.assertEqual(patient.weight, 72.0)
        self.assertEqual(patient.family_history, ["Hypertension"])
        self.assertFalse(patient.smoking)

    def test_default_lists_are_independent(self):
        first = Patient("P001", "First", 30, "Male")
        second = Patient("P002", "Second", 30, "Female")

        first.family_history.append("Example")

        self.assertEqual(first.family_history, ["Example"])
        self.assertEqual(second.family_history, [])

    def test_to_dict(self):
        patient = self.make_patient()
        data = patient.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data["patient_id"], "P001")
        self.assertEqual(data["age"], 45)
        self.assertEqual(data["weight"], 72.0)

    def test_from_dict(self):
        original = self.make_patient()
        restored = Patient.from_dict(original.to_dict())

        self.assertEqual(restored.to_dict(), original.to_dict())

    def test_update(self):
        patient = self.make_patient()

        patient.update(age=46, weight=73)

        self.assertEqual(patient.age, 46)
        self.assertEqual(patient.weight, 73.0)

    def test_unknown_update_field_is_rejected(self):
        patient = self.make_patient()

        with self.assertRaises(ValueError):
            patient.update(unknown_field="bad")

    def test_empty_required_string_is_rejected(self):
        with self.assertRaises(ValueError):
            Patient("P001", "", 30, "Male")

    def test_invalid_age_type_is_rejected(self):
        with self.assertRaises(TypeError):
            Patient("P001", "Test", "30", "Male")

    def test_invalid_age_range_is_rejected(self):
        with self.assertRaises(ValueError):
            Patient("P001", "Test", -1, "Male")

        with self.assertRaises(ValueError):
            Patient("P001", "Test", 151, "Male")

    def test_invalid_height_is_rejected(self):
        with self.assertRaises(ValueError):
            Patient("P001", "Test", 30, "Male", height=0)

    def test_invalid_weight_is_rejected(self):
        with self.assertRaises(ValueError):
            Patient("P001", "Test", 30, "Male", weight=-1)

    def test_invalid_smoking_value_is_rejected(self):
        with self.assertRaises(TypeError):
            Patient("P001", "Test", 30, "Male", smoking="yes")

    def test_invalid_string_list_is_rejected(self):
        with self.assertRaises(TypeError):
            Patient(
                "P001",
                "Test",
                30,
                "Male",
                family_history=["Valid", 123],
            )

    def test_module_import_has_no_demo_side_effects(self):
        # The test itself imports Patient successfully. The important
        # architectural requirement is that importing patient.py does not
        # create a global demo patient or print output.
        import digital_twin.patient as patient_module

        self.assertFalse(hasattr(patient_module, "patient"))

    def test_repr_does_not_include_medication_data(self):
        patient = self.make_patient()
        representation = repr(patient)

        self.assertIn("P001", representation)
        self.assertIn("Test User", representation)
        self.assertNotIn("Example Medication", representation)


if __name__ == "__main__":
    unittest.main()
