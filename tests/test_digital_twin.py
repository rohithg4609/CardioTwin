import unittest

from digital_twin.digital_twin import DigitalTwin
from digital_twin.health_state import HealthState
from digital_twin.history import HealthHistory
from digital_twin.patient import Patient


class TestDigitalTwin(unittest.TestCase):

    def make_patient(self):
        return Patient(
            patient_id="P001",
            name="Test User",
            age=45,
            sex="Male",
            height=172,
            weight=72,
            family_history=[],
            smoking=False,
            existing_conditions=[],
            medications=[],
        )

    def make_health_state(self):
        return HealthState(
            heart_rate=80,
            systolic_bp=120,
            diastolic_bp=80,
            spo2=98,
            glucose=95,
            cholesterol=180,
            sleep_hours=7,
            water_intake=2.0,
            steps=6000,
            exercise_minutes=30,
            stress_level=3,
            weight=72,
            bmi=24.3,
        )

    # --------------------------------------------------------------
    # Constructor tests
    # --------------------------------------------------------------

    def test_creation_with_patient_only(self):
        patient = self.make_patient()

        twin = DigitalTwin(patient)

        self.assertIs(twin.patient, patient)
        self.assertIsInstance(twin.health_state, HealthState)
        self.assertIsInstance(twin.history, HealthHistory)

    def test_creation_with_all_components(self):
        patient = self.make_patient()
        health = self.make_health_state()
        history = HealthHistory()

        twin = DigitalTwin(
            patient=patient,
            health_state=health,
            history=history,
        )

        self.assertIs(twin.patient, patient)
        self.assertIs(twin.health_state, health)
        self.assertIs(twin.history, history)

    def test_requires_patient_object(self):
        with self.assertRaises(TypeError):
            DigitalTwin("not a patient")

    def test_rejects_invalid_health_state(self):
        patient = self.make_patient()

        with self.assertRaises(TypeError):
            DigitalTwin(
                patient,
                health_state="invalid",
            )

    def test_rejects_invalid_history(self):
        patient = self.make_patient()

        with self.assertRaises(TypeError):
            DigitalTwin(
                patient,
                history="invalid",
            )

    # --------------------------------------------------------------
    # Patient tests
    # --------------------------------------------------------------

    def test_get_patient(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        result = twin.get_patient()

        self.assertIs(result, patient)

    def test_update_patient(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        result = twin.update_patient(
            age=50,
            weight=75,
        )

        self.assertIs(result, patient)
        self.assertEqual(twin.patient.age, 50)
        self.assertEqual(twin.patient.weight, 75)

    def test_patient_update_is_seen_by_risk_tracker(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        twin.update_patient(
            smoking=True,
        )

        result = twin.get_risk_result()

        factor_names = [
            factor["factor"]
            for factor in result["factors"]
        ]

        self.assertIn("smoking", factor_names)

    # --------------------------------------------------------------
    # Health state tests
    # --------------------------------------------------------------

    def test_get_health_state(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        result = twin.get_health_state()

        self.assertIs(result, health)

    def test_update_health_state(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        result = twin.update_health_state(
            heart_rate=110,
            systolic_bp=145,
        )

        self.assertIs(result, health)
        self.assertEqual(
            twin.health_state.heart_rate,
            110,
        )
        self.assertEqual(
            twin.health_state.systolic_bp,
            145,
        )

    def test_health_update_is_seen_by_risk_tracker(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        twin.update_health_state(
            systolic_bp=170,
        )

        result = twin.get_risk_result()

        factor_names = [
            factor["factor"]
            for factor in result["factors"]
        ]

        self.assertIn("blood_pressure", factor_names)

    def test_replace_health_state(self):
        patient = self.make_patient()
        old_health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            old_health,
        )

        new_health = HealthState(
            heart_rate=130,
            systolic_bp=170,
            diastolic_bp=105,
            spo2=95,
        )

        result = twin.replace_health_state(
            new_health,
        )

        self.assertIs(result, new_health)
        self.assertIs(twin.health_state, new_health)

    def test_replace_health_state_rejects_invalid_object(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        with self.assertRaises(TypeError):
            twin.replace_health_state("invalid")

    # --------------------------------------------------------------
    # History tests
    # --------------------------------------------------------------

    def test_get_history(self):
        patient = self.make_patient()
        history = HealthHistory()

        twin = DigitalTwin(
            patient,
            history=history,
        )

        self.assertIs(
            twin.get_history(),
            history,
        )

    def test_add_health_record(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        record = {
            "heart_rate": 82,
            "systolic_bp": 122,
            "diastolic_bp": 81,
            "spo2": 98,
        }

        result = twin.add_health_record(
            "2026-09-25",
            record,
        )

        self.assertEqual(result, record)
        self.assertEqual(
            len(twin.get_all_records()),
            1,
        )

    def test_add_health_record_without_save(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        result = twin.add_health_record(
            "2026-09-25",
            {"heart_rate": 85},
            save=False,
        )

        self.assertEqual(
            result["heart_rate"],
            85,
        )

    def test_get_latest_record(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        twin.add_health_record(
            "2026-09-24",
            {"heart_rate": 80},
        )

        twin.add_health_record(
            "2026-09-25",
            {"heart_rate": 85},
        )

        latest = twin.get_latest_record()

        self.assertEqual(
            latest["heart_rate"],
            85,
        )

    def test_get_first_record(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        twin.add_health_record(
            "2026-09-24",
            {"heart_rate": 80},
        )

        twin.add_health_record(
            "2026-09-25",
            {"heart_rate": 85},
        )

        first = twin.get_first_record()

        self.assertEqual(
            first["heart_rate"],
            80,
        )

    def test_get_all_records(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        twin.add_health_record(
            "2026-09-24",
            {"heart_rate": 80},
        )

        twin.add_health_record(
            "2026-09-25",
            {"heart_rate": 85},
        )

        records = twin.get_all_records()

        self.assertEqual(len(records), 2)

    def test_get_records_by_date(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        twin.add_health_record(
            "2026-09-24",
            {"heart_rate": 80},
        )

        twin.add_health_record(
            "2026-09-25",
            {"heart_rate": 85},
        )

        records = twin.get_records_by_date(
            "2026-09-25",
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["heart_rate"],
            85,
        )

    # --------------------------------------------------------------
    # Risk tests
    # --------------------------------------------------------------

    def test_calculate_risk_returns_float(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        result = twin.calculate_risk()

        self.assertIsInstance(result, float)

    def test_get_risk_score_returns_float(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        result = twin.get_risk_score()

        self.assertIsInstance(result, float)

    def test_get_risk_level_returns_string(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        result = twin.get_risk_level()

        self.assertIsInstance(result, str)

    def test_get_risk_result_contains_expected_keys(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        result = twin.get_risk_result()

        expected_keys = {
            "risk_score",
            "risk_level",
            "doctor_review",
            "urgent_attention",
            "recommendation",
            "factors",
            "severe_flags",
        }

        self.assertEqual(
            set(result.keys()),
            expected_keys,
        )

    def test_needs_doctor_review_returns_boolean(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        result = twin.needs_doctor_review()

        self.assertIsInstance(result, bool)

    def test_needs_urgent_attention_returns_boolean(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        result = twin.needs_urgent_attention()

        self.assertIsInstance(result, bool)

    def test_get_recommendation_returns_string(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        result = twin.get_recommendation()

        self.assertIsInstance(result, str)

    # --------------------------------------------------------------
    # Snapshot tests
    # --------------------------------------------------------------

    def test_get_snapshot_contains_expected_keys(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        snapshot = twin.get_snapshot()

        expected_keys = {
            "patient",
            "health_state",
            "latest_history",
            "latest_ml_assessment",
            "risk_source",
            "risk",
        }

        self.assertEqual(
            set(snapshot.keys()),
            expected_keys,
        )
        self.assertEqual(
            snapshot["risk_source"],
            "rule_based_prototype",
        )
        self.assertIsNone(snapshot["latest_ml_assessment"])

    def test_snapshot_contains_patient_data(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        snapshot = twin.get_snapshot()

        self.assertEqual(
            snapshot["patient"]["patient_id"],
            "P001",
        )

        self.assertEqual(
            snapshot["patient"]["name"],
            "Test User",
        )

    def test_snapshot_contains_health_data(self):
        patient = self.make_patient()
        health = self.make_health_state()

        twin = DigitalTwin(
            patient,
            health,
        )

        snapshot = twin.get_snapshot()

        self.assertEqual(
            snapshot["health_state"]["heart_rate"],
            80,
        )

        self.assertEqual(
            snapshot["health_state"]["spo2"],
            98,
        )

    def test_snapshot_contains_latest_history(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        twin.add_health_record(
            "2026-09-25",
            {
                "heart_rate": 88,
                "spo2": 97,
            },
        )

        snapshot = twin.get_snapshot()

        self.assertIsNotNone(
            snapshot["latest_history"],
        )

        self.assertEqual(
            snapshot["latest_history"]["heart_rate"],
            88,
        )

    # --------------------------------------------------------------
    # Reset tests
    # --------------------------------------------------------------

    def test_reset_risk(self):
        patient = self.make_patient()

        health = HealthState(
            heart_rate=130,
            systolic_bp=180,
            diastolic_bp=120,
            spo2=88,
        )

        twin = DigitalTwin(
            patient,
            health,
        )

        twin.calculate_risk()

        self.assertGreater(
            twin.get_risk_score(),
            0,
        )

        twin.reset_risk()

        self.assertEqual(
            twin.risk_tracker.score,
            0.0,
        )

        self.assertEqual(
            twin.risk_tracker.factors,
            [],
        )

        self.assertEqual(
            twin.risk_tracker.severe_flags,
            [],
        )

    def test_clear_history(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        twin.add_health_record(
            "2026-09-25",
            {"heart_rate": 80},
        )

        self.assertEqual(
            len(twin.get_all_records()),
            1,
        )

        twin.clear_history()

        self.assertEqual(
            len(twin.get_all_records()),
            0,
        )

    # --------------------------------------------------------------
    # Representation test
    # --------------------------------------------------------------

    def test_repr_contains_patient_id(self):
        patient = self.make_patient()
        twin = DigitalTwin(patient)

        result = repr(twin)

        self.assertIn(
            "P001",
            result,
        )

        self.assertIn(
            "DigitalTwin",
            result,
        )


if __name__ == "__main__":
    unittest.main()