"""
CardioTwin Risk Tracker.

This module provides a simple prototype risk-scoring engine for the
CardioTwin student proof-of-concept.

IMPORTANT:
- This is NOT a medical diagnostic system.
- The score is NOT clinically validated.
- The thresholds and weights are demonstration logic only.
- A real healthcare system would require clinical validation,
  appropriate guidelines, and qualified medical oversight.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .health_state import HealthState
from .patient import Patient


class RiskTracker:
    """
    Calculate a prototype health-risk score from Patient and HealthState.

    The score is normalized to 0-100.

    Thresholds:
        < 40  -> lower demo-risk range
        40-79 -> doctor-review warning
        >= 80 -> urgent/emergency guidance flag

    These thresholds are project/demo requirements and are not medical
    decision thresholds.
    """

    DOCTOR_WARNING_THRESHOLD = 40.0
    URGENT_THRESHOLD = 80.0

    def __init__(
        self,
        patient: Patient,
        health_state: HealthState,
    ) -> None:
        if not isinstance(patient, Patient):
            raise TypeError("patient must be a Patient instance.")

        if not isinstance(health_state, HealthState):
            raise TypeError(
                "health_state must be a HealthState instance."
            )

        self.patient = patient
        self.health_state = health_state

        self.score: float = 0.0
        self.factors: List[Dict[str, Any]] = []
        self.severe_flags: List[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_risk(self) -> float:
        """
        Calculate and store the prototype risk score.

        Returns
        -------
        float
            Risk score from 0 to 100.
        """
        self.factors = []
        self.severe_flags = []

        self._evaluate_patient_factors()
        self._evaluate_health_factors()

        total_score = sum(
            float(factor["points"])
            for factor in self.factors
        )

        self.score = round(
            min(max(total_score, 0.0), 100.0),
            2,
        )

        return self.score

    def get_score(self) -> float:
        """
        Return the current stored score as a float.

        If no calculation has been performed yet, calculate it first.
        """
        if not self.factors and self.score == 0.0:
            return float(self.calculate_risk())

        return float(self.score)

    def get_risk_level(self) -> str:
        """
        Return a simple project risk category.
        """
        score = self.get_score()

        if score >= self.URGENT_THRESHOLD:
            return "urgent"

        if score >= self.DOCTOR_WARNING_THRESHOLD:
            return "doctor_review"

        return "lower_risk"

    def needs_doctor_review(self) -> bool:
        """Return True when the score reaches the doctor-review threshold."""
        return self.get_score() >= self.DOCTOR_WARNING_THRESHOLD

    def needs_urgent_attention(self) -> bool:
        """
        Return True for an urgent score or a severe measurement flag.
        """
        self.get_score()

        return (
            self.score >= self.URGENT_THRESHOLD
            or len(self.severe_flags) > 0
        )

    def get_recommendation(self) -> str:
        """
        Return a project-level action message.

        This is guidance for the prototype UI and is not medical advice.
        """
        if self.needs_urgent_attention():
            return (
                "Urgent attention may be needed. "
                "Contact local emergency medical services or seek "
                "immediate medical care."
            )

        if self.needs_doctor_review():
            return (
                "The prototype risk score is elevated. "
                "Consider discussing the result with a qualified doctor."
            )

        return (
            "The prototype risk score is below the configured "
            "doctor-review threshold. Continue monitoring health data."
        )

    def get_result(self) -> Dict[str, Any]:
        """
        Return the complete risk assessment for use by other modules.
        """
        self.get_score()

        return {
            "risk_score": self.score,
            "risk_level": self.get_risk_level(),
            "doctor_review": self.needs_doctor_review(),
            "urgent_attention": self.needs_urgent_attention(),
            "recommendation": self.get_recommendation(),
            "factors": [dict(factor) for factor in self.factors],
            "severe_flags": list(self.severe_flags),
        }

    # ------------------------------------------------------------------
    # Patient factors
    # ------------------------------------------------------------------

    def _evaluate_patient_factors(self) -> None:
        """Evaluate profile-level factors."""
        patient = self.patient

        # Age contribution.
        if patient.age >= 65:
            self._add_factor(
                "age",
                "Age 65 or above",
                10,
            )
        elif patient.age >= 50:
            self._add_factor(
                "age",
                "Age 50-64",
                6,
            )
        elif patient.age >= 40:
            self._add_factor(
                "age",
                "Age 40-49",
                3,
            )

        # Smoking contribution.
        if patient.smoking is True:
            self._add_factor(
                "smoking",
                "Smoking recorded",
                10,
            )

        # Family history contribution.
        if patient.family_history:
            points = min(
                8,
                2 * len(patient.family_history),
            )

            self._add_factor(
                "family_history",
                "Documented family-history factors",
                points,
            )

        # Existing documented conditions.
        if patient.existing_conditions:
            points = min(
                12,
                3 * len(patient.existing_conditions),
            )

            self._add_factor(
                "existing_conditions",
                "Documented existing condition(s)",
                points,
            )

        # BMI from patient profile, if available.
        if patient.height and patient.weight:
            bmi = patient.weight / (
                (patient.height / 100.0) ** 2
            )

            self._evaluate_bmi(
                bmi,
                source="patient_profile",
            )

    # ------------------------------------------------------------------
    # Health measurements
    # ------------------------------------------------------------------

    def _evaluate_health_factors(self) -> None:
        """Evaluate current health measurements."""
        state = self.health_state

        if state.heart_rate is not None:
            self._evaluate_heart_rate(state.heart_rate)

        if (
            state.systolic_bp is not None
            or state.diastolic_bp is not None
        ):
            self._evaluate_blood_pressure(
                state.systolic_bp,
                state.diastolic_bp,
            )

        if state.spo2 is not None:
            self._evaluate_spo2(state.spo2)

        if state.glucose is not None:
            self._evaluate_glucose(state.glucose)

        if state.cholesterol is not None:
            self._evaluate_cholesterol(state.cholesterol)

        if state.sleep_hours is not None:
            self._evaluate_sleep(state.sleep_hours)

        if state.water_intake is not None:
            self._evaluate_water(state.water_intake)

        if state.exercise_minutes is not None:
            self._evaluate_exercise(
                state.exercise_minutes
            )

        if state.stress_level is not None:
            self._evaluate_stress(state.stress_level)

        if state.bmi is not None:
            self._evaluate_bmi(
                state.bmi,
                source="health_state",
            )

    # ------------------------------------------------------------------
    # Individual measurement evaluators
    # ------------------------------------------------------------------

    def _evaluate_heart_rate(self, value: float) -> None:
        if value < 50:
            self._add_factor(
                "heart_rate",
                "Low recorded heart rate",
                7,
            )

        elif value > 120:
            self._add_factor(
                "heart_rate",
                "High recorded heart rate",
                10,
            )

        elif value > 100:
            self._add_factor(
                "heart_rate",
                "Elevated recorded heart rate",
                5,
            )

    def _evaluate_blood_pressure(
        self,
        systolic: Optional[float],
        diastolic: Optional[float],
    ) -> None:
        if systolic is not None and systolic >= 180:
            self._add_factor(
                "blood_pressure",
                "Very high systolic blood pressure",
                25,
                severe=True,
            )

        elif systolic is not None and systolic >= 160:
            self._add_factor(
                "blood_pressure",
                "High systolic blood pressure",
                12,
            )

        elif systolic is not None and systolic >= 140:
            self._add_factor(
                "blood_pressure",
                "Elevated systolic blood pressure",
                8,
            )

        if diastolic is not None and diastolic >= 120:
            self._add_factor(
                "blood_pressure",
                "Very high diastolic blood pressure",
                25,
                severe=True,
            )

        elif diastolic is not None and diastolic >= 100:
            self._add_factor(
                "blood_pressure",
                "High diastolic blood pressure",
                10,
            )

        elif diastolic is not None and diastolic >= 90:
            self._add_factor(
                "blood_pressure",
                "Elevated diastolic blood pressure",
                6,
            )

    def _evaluate_spo2(self, value: float) -> None:
        if value < 90:
            self._add_factor(
                "spo2",
                "Very low recorded SpO2",
                35,
                severe=True,
            )

        elif value < 94:
            self._add_factor(
                "spo2",
                "Low recorded SpO2",
                20,
            )

        elif value < 96:
            self._add_factor(
                "spo2",
                "Borderline recorded SpO2",
                8,
            )

    def _evaluate_glucose(self, value: float) -> None:
        if value >= 200:
            self._add_factor(
                "glucose",
                "Very high recorded glucose",
                15,
            )

        elif value >= 140:
            self._add_factor(
                "glucose",
                "High recorded glucose",
                8,
            )

        elif value >= 100:
            self._add_factor(
                "glucose",
                "Elevated recorded glucose",
                4,
            )

    def _evaluate_cholesterol(self, value: float) -> None:
        if value >= 240:
            self._add_factor(
                "cholesterol",
                "High recorded cholesterol",
                8,
            )

        elif value >= 200:
            self._add_factor(
                "cholesterol",
                "Borderline recorded cholesterol",
                4,
            )

    def _evaluate_sleep(self, hours: float) -> None:
        if hours < 5:
            self._add_factor(
                "sleep",
                "Very low recorded sleep duration",
                8,
            )

        elif hours < 6:
            self._add_factor(
                "sleep",
                "Low recorded sleep duration",
                5,
            )

    def _evaluate_water(self, liters: float) -> None:
        if liters < 1.0:
            self._add_factor(
                "hydration",
                "Low recorded water intake",
                5,
            )

        elif liters < 1.5:
            self._add_factor(
                "hydration",
                "Moderately low recorded water intake",
                2,
            )

    def _evaluate_exercise(self, minutes: int) -> None:
        if minutes < 10:
            self._add_factor(
                "exercise",
                "Very low recorded exercise duration",
                5,
            )

        elif minutes < 20:
            self._add_factor(
                "exercise",
                "Low recorded exercise duration",
                2,
            )

    def _evaluate_stress(self, value: float) -> None:
        if value >= 8:
            self._add_factor(
                "stress",
                "High recorded stress level",
                7,
            )

        elif value >= 6:
            self._add_factor(
                "stress",
                "Elevated recorded stress level",
                4,
            )

    def _evaluate_bmi(
        self,
        bmi: float,
        source: str,
    ) -> None:
        if bmi >= 35:
            self._add_factor(
                "bmi",
                f"High BMI from {source}",
                10,
            )

        elif bmi >= 30:
            self._add_factor(
                "bmi",
                f"Elevated BMI from {source}",
                7,
            )

        elif bmi >= 25:
            self._add_factor(
                "bmi",
                f"Above-reference BMI from {source}",
                3,
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _add_factor(
        self,
        factor: str,
        description: str,
        points: float,
        severe: bool = False,
    ) -> None:
        """Add a scoring factor."""
        self.factors.append(
            {
                "factor": factor,
                "description": description,
                "points": float(points),
            }
        )

        if severe:
            self.severe_flags.append(description)

    def reset(self) -> None:
        """Clear the current calculated result."""
        self.score = 0.0
        self.factors = []
        self.severe_flags = []

    def __repr__(self) -> str:
        """Return a concise representation."""
        return (
            f"RiskTracker("
            f"patient_id={self.patient.patient_id!r}, "
            f"score={self.score!r}, "
            f"risk_level={self.get_risk_level()!r})"
        )


if __name__ == "__main__":
    # Manual smoke test.
    demo_patient = Patient(
        patient_id="P001",
        name="Demo User",
        age=45,
        sex="Male",
        height=172,
        weight=72,
        family_history=[],
        smoking=False,
        existing_conditions=[],
        medications=[],
    )

    demo_health = HealthState(
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

    tracker = RiskTracker(
        demo_patient,
        demo_health,
    )

    print("CardioTwin RiskTracker")
    print("----------------------")
    print(tracker.get_result())