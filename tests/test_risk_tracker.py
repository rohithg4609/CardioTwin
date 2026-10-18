import unittest

from digital_twin.patient import Patient
from digital_twin.health_state import HealthState
from digital_twin.risk_tracker import RiskTracker


class TestRiskTracker(unittest.TestCase):

    def make_patient(self, **changes):
        data = {
            "patient_id": "P001",
            "name": "Test User",
            "age": 30,
            "sex": "Male",
            "height": 175,
            "weight": 70,
            "family_history": [],
            "smoking": False,
            "existing_conditions": [],
            "medications": [],
        }

        data.update(changes)
        return Patient(**data)

    def make_health(self, **changes):
        data = {
            "heart_rate": 75,
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "spo2": 98,
            "glucose": 90,
            "cholesterol": 180,
            "sleep_hours": 7,
            "water_intake": 2.0,
            "steps": 7000,
            "exercise_minutes": 30,
            "stress_level": 3,
            "weight": 70,
            "bmi": 22.9,
        }

        data.update(changes)
        return HealthState(**data)

    def test_requires_patient_object(self):
        with self.assertRaises(TypeError):
            RiskTracker("not a patient", self.make_health())

    def test_requires_health_state_object(self):
        with self.assertRaises(TypeError):
            RiskTracker(self.make_patient(), "not health state")

    def test_score_is_between_zero_and_hundred(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(),
        )

        score = tracker.calculate_risk()

        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_normal_profile_has_low_demo_risk(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(),
        )

        self.assertLess(
            tracker.calculate_risk(),
            RiskTracker.DOCTOR_WARNING_THRESHOLD,
        )

    def test_smoking_adds_risk(self):
        normal = RiskTracker(
            self.make_patient(),
            self.make_health(),
        )

        smoker = RiskTracker(
            self.make_patient(smoking=True),
            self.make_health(),
        )

        self.assertGreater(
            smoker.calculate_risk(),
            normal.calculate_risk(),
        )

    def test_family_history_adds_risk(self):
        tracker = RiskTracker(
            self.make_patient(
                family_history=["heart disease"]
            ),
            self.make_health(),
        )

        self.assertGreater(
            tracker.calculate_risk(),
            0,
        )

    def test_existing_condition_adds_risk(self):
        tracker = RiskTracker(
            self.make_patient(
                existing_conditions=["hypertension"]
            ),
            self.make_health(),
        )

        self.assertGreater(
            tracker.calculate_risk(),
            0,
        )

    def test_high_blood_pressure_adds_risk(self):
        normal = RiskTracker(
            self.make_patient(),
            self.make_health(),
        )

        high_bp = RiskTracker(
            self.make_patient(),
            self.make_health(
                systolic_bp=170,
                diastolic_bp=105,
            ),
        )

        self.assertGreater(
            high_bp.calculate_risk(),
            normal.calculate_risk(),
        )

    def test_severe_blood_pressure_triggers_urgent(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(
                systolic_bp=185,
                diastolic_bp=125,
            ),
        )

        result = tracker.get_result()

        self.assertTrue(result["urgent_attention"])
        self.assertGreaterEqual(
            len(result["severe_flags"]),
            1,
        )

    def test_low_spo2_triggers_urgent(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(spo2=88),
        )

        result = tracker.get_result()

        self.assertTrue(result["urgent_attention"])
        self.assertGreaterEqual(
            result["risk_score"],
            0,
        )

    def test_borderline_spo2_adds_risk(self):
        normal = RiskTracker(
            self.make_patient(),
            self.make_health(spo2=98),
        )

        borderline = RiskTracker(
            self.make_patient(),
            self.make_health(spo2=95),
        )

        self.assertGreater(
            borderline.calculate_risk(),
            normal.calculate_risk(),
        )

    def test_high_glucose_adds_risk(self):
        normal = RiskTracker(
            self.make_patient(),
            self.make_health(glucose=90),
        )

        high = RiskTracker(
            self.make_patient(),
            self.make_health(glucose=180),
        )

        self.assertGreater(
            high.calculate_risk(),
            normal.calculate_risk(),
        )

    def test_high_cholesterol_adds_risk(self):
        normal = RiskTracker(
            self.make_patient(),
            self.make_health(cholesterol=180),
        )

        high = RiskTracker(
            self.make_patient(),
            self.make_health(cholesterol=250),
        )

        self.assertGreater(
            high.calculate_risk(),
            normal.calculate_risk(),
        )

    def test_low_sleep_adds_risk(self):
        normal = RiskTracker(
            self.make_patient(),
            self.make_health(sleep_hours=7),
        )

        low_sleep = RiskTracker(
            self.make_patient(),
            self.make_health(sleep_hours=4),
        )

        self.assertGreater(
            low_sleep.calculate_risk(),
            normal.calculate_risk(),
        )

    def test_low_water_intake_adds_risk(self):
        normal = RiskTracker(
            self.make_patient(),
            self.make_health(water_intake=2.0),
        )

        low_water = RiskTracker(
            self.make_patient(),
            self.make_health(water_intake=0.5),
        )

        self.assertGreater(
            low_water.calculate_risk(),
            normal.calculate_risk(),
        )

    def test_high_stress_adds_risk(self):
        normal = RiskTracker(
            self.make_patient(),
            self.make_health(stress_level=3),
        )

        high_stress = RiskTracker(
            self.make_patient(),
            self.make_health(stress_level=9),
        )

        self.assertGreater(
            high_stress.calculate_risk(),
            normal.calculate_risk(),
        )

    def test_low_exercise_adds_risk(self):
        normal = RiskTracker(
            self.make_patient(),
            self.make_health(exercise_minutes=30),
        )

        low_exercise = RiskTracker(
            self.make_patient(),
            self.make_health(exercise_minutes=5),
        )

        self.assertGreater(
            low_exercise.calculate_risk(),
            normal.calculate_risk(),
        )

    def test_high_bmi_adds_risk(self):
        normal = RiskTracker(
            self.make_patient(),
            self.make_health(bmi=22),
        )

        high_bmi = RiskTracker(
            self.make_patient(),
            self.make_health(bmi=36),
        )

        self.assertGreater(
            high_bmi.calculate_risk(),
            normal.calculate_risk(),
        )

    def test_doctor_review_threshold(self):
        tracker = RiskTracker(
            self.make_patient(
                age=65,
                smoking=True,
                family_history=[
                    "heart disease",
                    "diabetes",
                    "hypertension",
                ],
                existing_conditions=[
                    "hypertension",
                    "diabetes",
                ],
            ),
            self.make_health(
                systolic_bp=170,
                diastolic_bp=105,
                glucose=180,
                cholesterol=250,
                sleep_hours=4,
                stress_level=9,
            ),
        )

        self.assertTrue(
            tracker.needs_doctor_review()
        )

    def test_result_contains_expected_keys(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(),
        )

        result = tracker.get_result()

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

    def test_result_factors_are_list(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(),
        )

        result = tracker.get_result()

        self.assertIsInstance(
            result["factors"],
            list,
        )

    def test_reset_clears_result(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(
                systolic_bp=170,
                diastolic_bp=105,
            ),
        )

        tracker.calculate_risk()
        tracker.reset()

        self.assertEqual(
            tracker.score,
            0.0,
        )
        self.assertEqual(
            tracker.factors,
            [],
        )
        self.assertEqual(
            tracker.severe_flags,
            [],
        )

    def test_recalculate_replaces_old_factors(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(
                systolic_bp=170,
                diastolic_bp=105,
            ),
        )

        first_score = tracker.calculate_risk()

        tracker.health_state.update(
            systolic_bp=120,
            diastolic_bp=80,
        )

        second_score = tracker.calculate_risk()

        self.assertLess(
            second_score,
            first_score,
        )

    def test_get_score_returns_float(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(),
        )

        score = tracker.get_score()

        self.assertIsInstance(
            score,
            float,
        )

    def test_risk_level_is_valid(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(),
        )

        level = tracker.get_risk_level()

        self.assertIn(
            level,
            {
                "lower_risk",
                "doctor_review",
                "urgent",
            },
        )

    def test_recommendation_is_string(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(),
        )

        recommendation = tracker.get_recommendation()

        self.assertIsInstance(
            recommendation,
            str,
        )

    def test_severe_flag_can_trigger_urgent_below_80(self):
        tracker = RiskTracker(
            self.make_patient(),
            self.make_health(spo2=88),
        )

        tracker.calculate_risk()

        # The important requirement is that the severe flag itself
        # causes urgent_attention to become True.
        self.assertTrue(
            tracker.needs_urgent_attention()
        )


if __name__ == "__main__":
    unittest.main()