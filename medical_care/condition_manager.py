"""
Doctor-confirmed condition management for CardioTwin.

Only conditions explicitly entered as confirmed by the user or
healthcare professional should be managed here.

This module does not diagnose conditions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConfirmedCondition:
    """A condition explicitly marked as confirmed."""

    condition_id: str
    condition_name: str
    confirmed_by: str
    confirmation_date: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "condition_name": self.condition_name,
            "confirmed_by": self.confirmed_by,
            "confirmation_date": self.confirmation_date,
            "notes": self.notes,
        }


def add_confirmed_condition(
    condition_id: str,
    condition_name: str,
    confirmed_by: str,
    confirmation_date: str | None = None,
    notes: str | None = None,
) -> ConfirmedCondition:
    """
    Create a doctor-confirmed condition record.

    The caller is responsible for ensuring that the condition
    was actually confirmed by an appropriate healthcare professional
    or explicitly entered as such by the user.
    """

    if not condition_id.strip():
        raise ValueError("condition_id is required.")

    if not condition_name.strip():
        raise ValueError("condition_name is required.")

    if not confirmed_by.strip():
        raise ValueError("confirmed_by is required.")

    return ConfirmedCondition(
        condition_id=condition_id.strip(),
        condition_name=condition_name.strip(),
        confirmed_by=confirmed_by.strip(),
        confirmation_date=confirmation_date,
        notes=notes,
    )


def get_condition_management(
    condition: ConfirmedCondition,
) -> dict[str, Any]:
    """
    Return a management record for a confirmed condition.

    This deliberately does not invent medications, doses,
    treatment changes, or personalized medical instructions.
    """

    return {
        "condition": condition.to_dict(),
        "status": "doctor_confirmed",
        "management": {
            "monitoring": [],
            "medications": [],
            "lifestyle_guidance": [],
            "follow_up": [],
        },
        "message": (
            "This condition is recorded as doctor-confirmed. "
            "Treatment and medication details should come from "
            "the patient's healthcare professional or verified "
            "medical records."
        ),
        "is_diagnosis": False,
    }