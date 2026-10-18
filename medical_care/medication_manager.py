"""
Medication tracking for the CardioTwin prototype.

This module stores medication information that has already been
provided by the user, healthcare professional, or verified record.

It does not prescribe medication or recommend treatment changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Medication:
    """A medication record supplied by an authorized source."""

    name: str
    dose: str
    frequency: str
    scheduled_time: str | None = None
    before_or_after_food: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    source: str = "user_entered"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Medication name is required.")

        if not self.dose.strip():
            raise ValueError("Medication dose is required.")

        if not self.frequency.strip():
            raise ValueError("Medication frequency is required.")

        if not self.source.strip():
            raise ValueError("Medication source is required.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "dose": self.dose,
            "frequency": self.frequency,
            "scheduled_time": self.scheduled_time,
            "before_or_after_food": self.before_or_after_food,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "source": self.source,
        }


def add_medication(
    name: str,
    dose: str,
    frequency: str,
    scheduled_time: str | None = None,
    before_or_after_food: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    source: str = "user_entered",
) -> Medication:
    """
    Create a medication record.

    The values must come from an authorized input source.
    This function does not generate or alter treatment instructions.
    """

    return Medication(
        name=name.strip(),
        dose=dose.strip(),
        frequency=frequency.strip(),
        scheduled_time=scheduled_time,
        before_or_after_food=before_or_after_food,
        start_date=start_date,
        end_date=end_date,
        source=source.strip(),
    )


def record_medication_status(
    medication: Medication,
    taken: bool,
) -> dict[str, Any]:
    """
    Record whether a scheduled medication was taken.

    This only records adherence information.
    It does not advise the user to take an extra dose or change treatment.
    """

    return {
        "medication": medication.to_dict(),
        "taken": bool(taken),
        "status": "taken" if taken else "missed",
        "message": (
            "Medication status recorded. Follow the treatment plan "
            "provided by the healthcare professional."
        ),
        "treatment_changed": False,
    }