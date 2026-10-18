"""
Exercise safety checker for the CardioTwin prototype.

This module identifies reported warning signs during exercise.
It does not prescribe exercise or determine whether exercise
is medically safe for an individual.
"""

from __future__ import annotations

from typing import Any


EXERCISE_WARNING_SIGNS = {
    "chest_pain",
    "severe_breathing_difficulty",
    "fainting",
    "severe_dizziness",
    "sudden_weakness",
    "new_confusion",
}


def normalize_text(value: str) -> str:
    """Normalize a reported exercise symptom."""

    return (
        value.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def check_exercise_safety(
    exercise_type: str,
    intensity: str | None = None,
    symptoms: list[str] | None = None,
) -> dict[str, Any]:
    """
    Check for prototype warning signs associated with exercise.

    This is a safety check, not a medical clearance tool.
    """

    normalized_type = normalize_text(exercise_type)

    normalized_intensity = (
        normalize_text(intensity)
        if isinstance(intensity, str) and intensity.strip()
        else None
    )

    reported_symptoms = {
        normalize_text(symptom)
        for symptom in (symptoms or [])
        if isinstance(symptom, str) and symptom.strip()
    }

    warning_signs = sorted(
        reported_symptoms.intersection(EXERCISE_WARNING_SIGNS)
    )

    if warning_signs:
        status = "stop_and_seek_medical_help"

        message = (
            "Potentially serious warning signs were reported during "
            "exercise. Stop the activity and seek appropriate "
            "medical evaluation."
        )

    else:
        status = "no_warning_detected"

        message = (
            "No prototype exercise warning signs were detected. "
            "This does not provide medical clearance or guarantee "
            "that exercise is safe."
        )

    return {
        "exercise_type": normalized_type,
        "intensity": normalized_intensity,
        "reported_symptoms": sorted(reported_symptoms),
        "warning_signs": warning_signs,
        "status": status,
        "message": message,
        "is_medical_clearance": False,
        "disclaimer": (
            "This prototype provides a safety check only. "
            "It does not prescribe exercise or provide medical clearance."
        ),
    }