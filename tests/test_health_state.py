"""
Tests for CardioTwin HealthState.

Run from the CardioTwin project folder with:

    python -m unittest tests.test_health_state -v
"""

import unittest

from digital_twin.health_state import HealthState


class TestHealthState(unittest.TestCase):

    def make_health_state(self):
        """Create a valid sample HealthState for testing."""

        return HealthState(
            heart_rate=84,
            systolic_bp=132,
            diastolic_bp=85,
            spo2=97,
            glucose=103,
            cholesterol=190,
            sleep_hours=6.5,
            water_intake=1.8,
            steps=5200,
            exercise_minutes=20,
            stress_level=5,
            weight=72.2,
            bmi=24.3,
        )

    # ---------------------------------------------------------
    # Basic creation
    # ---------------------------------------------------------

    def test_health_state_creation(self):
        health = self.make_health_state()

        self.assertEqual(health.heart_rate, 84.0)
        self.assertEqual(health.systolic_bp, 132.0)
        self.assertEqual(health.diastolic_bp, 85.0)
        self.assertEqual(health.spo2, 97.0)

        self.assertEqual(health.glucose, 103.0)
        self.assertEqual(health.cholesterol, 190.0)

        self.assertEqual(health.sleep_hours, 6.5)
        self.assertEqual(health.water_intake, 1.8)

        self.assertEqual(health.steps, 5200)
        self.assertEqual(health.exercise_minutes, 20)

        self.assertEqual(health.stress_level, 5.0)
        self.assertEqual(health.weight, 72.2)
        self.assertEqual(health.bmi, 24.3)

    # ---------------------------------------------------------
    # Empty health state
    # ---------------------------------------------------------

    def test_empty_health_state_is_allowed(self):
        health = HealthState()

        self.assertIsNone(health.heart_rate)
        self.assertIsNone(health.systolic_bp)
        self.assertIsNone(health.diastolic_bp)
        self.assertIsNone(health.spo2)
        self.assertIsNone(health.glucose)
        self.assertIsNone(health.cholesterol)

        self.assertIsNone(health.sleep_hours)
        self.assertIsNone(health.water_intake)
        self.assertIsNone(health.steps)
        self.assertIsNone(health.exercise_minutes)
        self.assertIsNone(health.stress_level)

        self.assertIsNone(health.weight)
        self.assertIsNone(health.bmi)

    # ---------------------------------------------------------
    # Dictionary conversion
    # ---------------------------------------------------------

    def test_to_dict(self):
        health = self.make_health_state()

        data = health.to_dict()

        self.assertIsInstance(data, dict)

        self.assertEqual(data["heart_rate"], 84.0)
        self.assertEqual(data["systolic_bp"], 132.0)
        self.assertEqual(data["diastolic_bp"], 85.0)
        self.assertEqual(data["spo2"], 97.0)

        self.assertEqual(data["glucose"], 103.0)
        self.assertEqual(data["cholesterol"], 190.0)

        self.assertEqual(data["sleep_hours"], 6.5)
        self.assertEqual(data["water_intake"], 1.8)

        self.assertEqual(data["steps"], 5200)
        self.assertEqual(data["exercise_minutes"], 20)

        self.assertEqual(data["stress_level"], 5.0)
        self.assertEqual(data["weight"], 72.2)
        self.assertEqual(data["bmi"], 24.3)

    def test_from_dict(self):
        original = self.make_health_state()

        data = original.to_dict()

        restored = HealthState.from_dict(data)

        self.assertEqual(
            restored.to_dict(),
            original.to_dict(),
        )

    # ---------------------------------------------------------
    # Blood pressure
    # ---------------------------------------------------------

    def test_blood_pressure_values(self):
        health = HealthState(
            systolic_bp=120,
            diastolic_bp=80,
        )

        self.assertEqual(health.systolic_bp, 120.0)
        self.assertEqual(health.diastolic_bp, 80.0)

    def test_invalid_systolic_blood_pressure(self):
        with self.assertRaises(ValueError):
            HealthState(systolic_bp=0)

    def test_invalid_diastolic_blood_pressure(self):
        with self.assertRaises(ValueError):
            HealthState(diastolic_bp=-1)

    # ---------------------------------------------------------
    # SpO2
    # ---------------------------------------------------------

    def test_valid_spo2(self):
        health = HealthState(spo2=98)

        self.assertEqual(health.spo2, 98.0)

    def test_spo2_upper_limit(self):
        health = HealthState(spo2=100)

        self.assertEqual(health.spo2, 100.0)

    def test_spo2_above_valid_range(self):
        with self.assertRaises(ValueError):
            HealthState(spo2=101)

    def test_spo2_below_valid_range(self):
        with self.assertRaises(ValueError):
            HealthState(spo2=-1)

    # ---------------------------------------------------------
    # Sleep
    # ---------------------------------------------------------

    def test_valid_sleep_hours(self):
        health = HealthState(sleep_hours=8)

        self.assertEqual(health.sleep_hours, 8.0)

    def test_sleep_hours_upper_limit(self):
        health = HealthState(sleep_hours=24)

        self.assertEqual(health.sleep_hours, 24.0)

    def test_sleep_hours_above_limit(self):
        with self.assertRaises(ValueError):
            HealthState(sleep_hours=25)

    def test_negative_sleep_hours(self):
        with self.assertRaises(ValueError):
            HealthState(sleep_hours=-1)

    # ---------------------------------------------------------
    # Hydration
    # ---------------------------------------------------------

    def test_zero_water_intake_is_allowed(self):
        health = HealthState(water_intake=0)

        self.assertEqual(health.water_intake, 0.0)

    def test_negative_water_intake_is_rejected(self):
        with self.assertRaises(ValueError):
            HealthState(water_intake=-1)

    # ---------------------------------------------------------
    # Steps
    # ---------------------------------------------------------

    def test_valid_steps(self):
        health = HealthState(steps=5000)

        self.assertEqual(health.steps, 5000)

    def test_zero_steps_is_allowed(self):
        health = HealthState(steps=0)

        self.assertEqual(health.steps, 0)

    def test_negative_steps_are_rejected(self):
        with self.assertRaises(ValueError):
            HealthState(steps=-100)

    def test_decimal_steps_are_rejected(self):
        with self.assertRaises(TypeError):
            HealthState(steps=5000.5)

    # ---------------------------------------------------------
    # Exercise
    # ---------------------------------------------------------

    def test_valid_exercise_minutes(self):
        health = HealthState(exercise_minutes=30)

        self.assertEqual(
            health.exercise_minutes,
            30,
        )

    def test_negative_exercise_minutes_are_rejected(self):
        with self.assertRaises(ValueError):
            HealthState(exercise_minutes=-10)

    def test_decimal_exercise_minutes_are_rejected(self):
        with self.assertRaises(TypeError):
            HealthState(exercise_minutes=30.5)

    # ---------------------------------------------------------
    # Stress
    # ---------------------------------------------------------

    def test_valid_stress_level(self):
        health = HealthState(stress_level=5)

        self.assertEqual(
            health.stress_level,
            5.0,
        )

    def test_stress_level_zero(self):
        health = HealthState(stress_level=0)

        self.assertEqual(
            health.stress_level,
            0.0,
        )

    def test_stress_level_ten(self):
        health = HealthState(stress_level=10)

        self.assertEqual(
            health.stress_level,
            10.0,
        )

    def test_stress_level_above_ten(self):
        with self.assertRaises(ValueError):
            HealthState(stress_level=11)

    def test_negative_stress_level(self):
        with self.assertRaises(ValueError):
            HealthState(stress_level=-1)

    # ---------------------------------------------------------
    # Body measurements
    # ---------------------------------------------------------

    def test_valid_weight(self):
        health = HealthState(weight=72.5)

        self.assertEqual(
            health.weight,
            72.5,
        )

    def test_invalid_weight(self):
        with self.assertRaises(ValueError):
            HealthState(weight=0)

    def test_negative_weight(self):
        with self.assertRaises(ValueError):
            HealthState(weight=-10)

    def test_valid_bmi(self):
        health = HealthState(bmi=24.3)

        self.assertEqual(
            health.bmi,
            24.3,
        )

    def test_invalid_bmi(self):
        with self.assertRaises(ValueError):
            HealthState(bmi=0)

    # ---------------------------------------------------------
    # Type validation
    # ---------------------------------------------------------

    def test_heart_rate_must_be_numeric(self):
        with self.assertRaises(TypeError):
            HealthState(heart_rate="84")

    def test_glucose_must_be_numeric(self):
        with self.assertRaises(TypeError):
            HealthState(glucose="103")

    def test_cholesterol_must_be_numeric(self):
        with self.assertRaises(TypeError):
            HealthState(cholesterol="190")

    def test_boolean_is_not_accepted_as_numeric_health_data(self):
        with self.assertRaises(TypeError):
            HealthState(heart_rate=True)

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def test_update_changes_values(self):
        health = self.make_health_state()

        health.update(
            heart_rate=90,
            systolic_bp=135,
            steps=7000,
        )

        self.assertEqual(
            health.heart_rate,
            90.0,
        )

        self.assertEqual(
            health.systolic_bp,
            135.0,
        )

        self.assertEqual(
            health.steps,
            7000,
        )

    def test_update_preserves_unchanged_values(self):
        health = self.make_health_state()

        health.update(heart_rate=90)

        self.assertEqual(
            health.heart_rate,
            90.0,
        )

        self.assertEqual(
            health.spo2,
            97.0,
        )

        self.assertEqual(
            health.steps,
            5200,
        )

    def test_update_revalidates_values(self):
        health = self.make_health_state()

        with self.assertRaises(ValueError):
            health.update(spo2=150)

    def test_update_unknown_field_is_rejected(self):
        health = self.make_health_state()

        with self.assertRaises(ValueError):
            health.update(
                unknown_measurement=123
            )

    # ---------------------------------------------------------
    # Missing dictionary values
    # ---------------------------------------------------------

    def test_from_dict_allows_missing_values(self):
        data = {
            "heart_rate": 80,
            "spo2": 98,
        }

        health = HealthState.from_dict(data)

        self.assertEqual(
            health.heart_rate,
            80.0,
        )

        self.assertEqual(
            health.spo2,
            98.0,
        )

        self.assertIsNone(
            health.glucose
        )

        self.assertIsNone(
            health.steps
        )

    # ---------------------------------------------------------
    # Invalid dictionary
    # ---------------------------------------------------------

    def test_from_dict_requires_dictionary(self):
        with self.assertRaises(TypeError):
            HealthState.from_dict("invalid")

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def test_repr_contains_basic_information(self):
        health = self.make_health_state()

        representation = repr(health)

        self.assertIn(
            "heart_rate=84.0",
            representation,
        )

        self.assertIn(
            "spo2=97.0",
            representation,
        )

    # ---------------------------------------------------------
    # Import behavior
    # ---------------------------------------------------------

    def test_module_has_no_global_demo_health_state(self):
        import digital_twin.health_state as module

        self.assertFalse(
            hasattr(module, "today")
        )


if __name__ == "__main__":
    unittest.main()