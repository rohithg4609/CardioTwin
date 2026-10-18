"""
CardioTwin Health State Model.

Stores the patient's current health measurements used by the
CardioTwin Digital Twin.

This class is responsible for:
- storing health measurements
- validating data
- converting the state to/from dictionaries

It does NOT diagnose diseases or make clinical decisions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class HealthState:
    """
    Represents the patient's current health measurements.

    All measurements are optional so that the system can handle
    incomplete wearable/manual health data safely.
    """

    heart_rate: Optional[float] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    spo2: Optional[float] = None
    glucose: Optional[float] = None
    cholesterol: Optional[float] = None

    sleep_hours: Optional[float] = None
    water_intake: Optional[float] = None
    steps: Optional[int] = None
    exercise_minutes: Optional[int] = None
    stress_level: Optional[float] = None

    weight: Optional[float] = None
    bmi: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate all supplied health measurements."""

        self.heart_rate = self._positive_number(
            self.heart_rate, "heart_rate"
        )

        self.systolic_bp = self._positive_number(
            self.systolic_bp, "systolic_bp"
        )

        self.diastolic_bp = self._positive_number(
            self.diastolic_bp, "diastolic_bp"
        )

        self.spo2 = self._percentage(
            self.spo2, "spo2"
        )

        self.glucose = self._positive_number(
            self.glucose, "glucose"
        )

        self.cholesterol = self._positive_number(
            self.cholesterol, "cholesterol"
        )

        self.sleep_hours = self._range_number(
            self.sleep_hours,
            "sleep_hours",
            minimum=0,
            maximum=24,
        )

        self.water_intake = self._non_negative_number(
            self.water_intake,
            "water_intake",
        )

        self.steps = self._non_negative_integer(
            self.steps,
            "steps",
        )

        self.exercise_minutes = self._non_negative_integer(
            self.exercise_minutes,
            "exercise_minutes",
        )

        self.stress_level = self._range_number(
            self.stress_level,
            "stress_level",
            minimum=0,
            maximum=10,
        )

        self.weight = self._positive_number(
            self.weight,
            "weight",
        )

        self.bmi = self._positive_number(
            self.bmi,
            "bmi",
        )

    # ---------------------------------------------------------
    # Validation helpers
    # ---------------------------------------------------------

    @staticmethod
    def _positive_number(
        value: Optional[float],
        field_name: str,
    ) -> Optional[float]:
        """Validate an optional number greater than zero."""

        if value is None:
            return None

        if isinstance(value, bool):
            raise TypeError(f"{field_name} must be a number or None.")

        if not isinstance(value, (int, float)):
            raise TypeError(f"{field_name} must be a number or None.")

        if value <= 0:
            raise ValueError(f"{field_name} must be greater than 0.")

        return float(value)

    @staticmethod
    def _non_negative_number(
        value: Optional[float],
        field_name: str,
    ) -> Optional[float]:
        """Validate an optional number greater than or equal to zero."""

        if value is None:
            return None

        if isinstance(value, bool):
            raise TypeError(f"{field_name} must be a number or None.")

        if not isinstance(value, (int, float)):
            raise TypeError(f"{field_name} must be a number or None.")

        if value < 0:
            raise ValueError(
                f"{field_name} cannot be negative."
            )

        return float(value)

    @staticmethod
    def _non_negative_integer(
        value: Optional[int],
        field_name: str,
    ) -> Optional[int]:
        """Validate an optional non-negative integer."""

        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                f"{field_name} must be an integer or None."
            )

        if value < 0:
            raise ValueError(
                f"{field_name} cannot be negative."
            )

        return value

    @staticmethod
    def _range_number(
        value: Optional[float],
        field_name: str,
        minimum: float,
        maximum: float,
    ) -> Optional[float]:
        """Validate an optional number within an inclusive range."""

        if value is None:
            return None

        if isinstance(value, bool):
            raise TypeError(f"{field_name} must be a number or None.")

        if not isinstance(value, (int, float)):
            raise TypeError(f"{field_name} must be a number or None.")

        if value < minimum or value > maximum:
            raise ValueError(
                f"{field_name} must be between "
                f"{minimum} and {maximum}."
            )

        return float(value)

    @staticmethod
    def _percentage(
        value: Optional[float],
        field_name: str,
    ) -> Optional[float]:
        """Validate a percentage-style measurement from 0 to 100."""

        return HealthState._range_number(
            value,
            field_name,
            minimum=0,
            maximum=100,
        )

    # ---------------------------------------------------------
    # Conversion methods
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the health state into a dictionary.

        The returned dictionary can be passed to JSON serialization.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthState":
        """
        Create a HealthState from a dictionary.

        Missing values are treated as None.
        """

        if not isinstance(data, dict):
            raise TypeError("Health state data must be a dictionary.")

        allowed_fields = {
            "heart_rate",
            "systolic_bp",
            "diastolic_bp",
            "spo2",
            "glucose",
            "cholesterol",
            "sleep_hours",
            "water_intake",
            "steps",
            "exercise_minutes",
            "stress_level",
            "weight",
            "bmi",
        }

        values = {
            key: data[key]
            for key in allowed_fields
            if key in data
        }

        return cls(**values)

    def update(self, **changes: Any) -> None:
        """
        Safely update one or more health measurements.

        Validation is performed again after applying the changes.
        """

        allowed_fields = {
            "heart_rate",
            "systolic_bp",
            "diastolic_bp",
            "spo2",
            "glucose",
            "cholesterol",
            "sleep_hours",
            "water_intake",
            "steps",
            "exercise_minutes",
            "stress_level",
            "weight",
            "bmi",
        }

        unknown_fields = set(changes) - allowed_fields

        if unknown_fields:
            unknown = ", ".join(sorted(unknown_fields))
            raise ValueError(
                f"Unknown health state field(s): {unknown}"
            )

        current_data = self.to_dict()
        current_data.update(changes)

        validated = type(self).from_dict(current_data)

        for field_name in allowed_fields:
            setattr(
                self,
                field_name,
                getattr(validated, field_name),
            )

    def __repr__(self) -> str:
        """Return a concise representation of the health state."""

        return (
            "HealthState("
            f"heart_rate={self.heart_rate!r}, "
            f"systolic_bp={self.systolic_bp!r}, "
            f"diastolic_bp={self.diastolic_bp!r}, "
            f"spo2={self.spo2!r})"
        )


if __name__ == "__main__":
    # Manual smoke test only.
    # Importing this module does not execute this section.

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

    print("HealthState model loaded successfully.")
    print(demo_health)
    print(demo_health.to_dict())