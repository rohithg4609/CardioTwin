"""
CardioTwin Patient Model.

This module contains the patient profile used by the Digital Twin.

The Patient class is intentionally limited to storing and validating
patient-profile data. It does not diagnose conditions, recommend
medications, or make clinical decisions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Patient:
    """
    Represents a patient's profile for the CardioTwin Digital Twin.

    Parameters
    ----------
    patient_id:
        Unique identifier for the patient. It should be a non-empty string.
    name:
        Patient's display name.
    age:
        Age in years. Must be an integer from 0 through 150.
    sex:
        Recorded sex as provided by the user/authorized data source.
        The value is stored as text and is not used to infer anything.
    height:
        Height in centimeters. Optional.
    weight:
        Weight in kilograms. Optional.
    family_history:
        List of documented family-history items. Optional.
    smoking:
        Whether smoking is recorded as true/false. Optional.
    existing_conditions:
        List of clinician-confirmed/documented conditions. Optional.
    medications:
        List of medication records. These are stored as supplied and
        are not modified or clinically interpreted by this class.
    """

    patient_id: str
    name: str
    age: int
    sex: str
    height: Optional[float] = None
    weight: Optional[float] = None
    family_history: List[str] = field(default_factory=list)
    smoking: Optional[bool] = None
    existing_conditions: List[str] = field(default_factory=list)
    medications: List[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate and normalize patient data after construction."""
        self.patient_id = self._validate_non_empty_string(
            self.patient_id, "patient_id"
        )
        self.name = self._validate_non_empty_string(self.name, "name")
        self.sex = self._validate_non_empty_string(self.sex, "sex")

        if isinstance(self.age, bool) or not isinstance(self.age, int):
            raise TypeError("age must be an integer.")
        if not 0 <= self.age <= 150:
            raise ValueError("age must be between 0 and 150.")

        self.height = self._validate_optional_positive_number(
            self.height, "height"
        )
        self.weight = self._validate_optional_positive_number(
            self.weight, "weight"
        )

        if self.smoking is not None and not isinstance(self.smoking, bool):
            raise TypeError("smoking must be True, False, or None.")

        self.family_history = self._validate_string_list(
            self.family_history, "family_history"
        )
        self.existing_conditions = self._validate_string_list(
            self.existing_conditions, "existing_conditions"
        )

        if not isinstance(self.medications, list):
            raise TypeError("medications must be a list.")

        # Copy mutable lists so callers cannot accidentally share list state.
        self.family_history = list(self.family_history)
        self.existing_conditions = list(self.existing_conditions)
        self.medications = list(self.medications)

    @staticmethod
    def _validate_non_empty_string(value: Any, field_name: str) -> str:
        """Validate a required non-empty string."""
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        value = value.strip()
        if not value:
            raise ValueError(f"{field_name} cannot be empty.")

        return value

    @staticmethod
    def _validate_optional_positive_number(
        value: Optional[float], field_name: str
    ) -> Optional[float]:
        """Validate an optional positive numeric measurement."""
        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{field_name} must be a number or None.")

        if value <= 0:
            raise ValueError(f"{field_name} must be greater than 0.")

        return float(value)

    @staticmethod
    def _validate_string_list(
        value: Any, field_name: str
    ) -> List[str]:
        """Validate a list containing only non-empty strings."""
        if value is None:
            return []

        if not isinstance(value, list):
            raise TypeError(f"{field_name} must be a list.")

        cleaned: List[str] = []

        for item in value:
            if not isinstance(item, str):
                raise TypeError(
                    f"Every item in {field_name} must be a string."
                )

            item = item.strip()
            if not item:
                raise ValueError(
                    f"{field_name} cannot contain empty strings."
                )

            cleaned.append(item)

        return cleaned

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the patient profile into a JSON-serializable dictionary.

        A copy is returned so modifying the result does not modify the
        Patient object.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Patient":
        """
        Create a Patient from a dictionary.

        Raises
        ------
        TypeError:
            If data is not a dictionary.
        """
        if not isinstance(data, dict):
            raise TypeError("Patient data must be a dictionary.")

        return cls(
            patient_id=data.get("patient_id"),
            name=data.get("name"),
            age=data.get("age"),
            sex=data.get("sex"),
            height=data.get("height"),
            weight=data.get("weight"),
            family_history=data.get("family_history", []),
            smoking=data.get("smoking"),
            existing_conditions=data.get("existing_conditions", []),
            medications=data.get("medications", []),
        )

    def update(self, **changes: Any) -> None:
        """
        Update one or more patient fields with the same validation used
        during construction.

        Unknown fields are rejected to prevent accidental data corruption.
        """
        allowed_fields = {
            "patient_id",
            "name",
            "age",
            "sex",
            "height",
            "weight",
            "family_history",
            "smoking",
            "existing_conditions",
            "medications",
        }

        unknown_fields = set(changes) - allowed_fields
        if unknown_fields:
            unknown = ", ".join(sorted(unknown_fields))
            raise ValueError(f"Unknown patient field(s): {unknown}")

        current = self.to_dict()
        current.update(changes)

        validated = type(self).from_dict(current)

        for field_name in allowed_fields:
            setattr(self, field_name, getattr(validated, field_name))

    def __repr__(self) -> str:
        """Return a concise representation without exposing medication data."""
        return (
            f"Patient("
            f"patient_id={self.patient_id!r}, "
            f"name={self.name!r}, "
            f"age={self.age!r}, "
            f"sex={self.sex!r})"
        )


if __name__ == "__main__":
    # Small manual smoke test. Importing this module has no side effects.
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

    print("Patient model loaded successfully.")
    print(demo_patient)
    print(demo_patient.to_dict())
