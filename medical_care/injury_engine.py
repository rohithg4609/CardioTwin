"""
Minor injury safety engine for the CardioTwin prototype.

This module provides basic rule-based guidance for reported injuries.
It does not diagnose injuries and does not replace medical care.
"""

from __future__ import annotations

from typing import Any


URGENT_INJURY_SIGNALS = {
    "heavy_bleeding",
    "deep_wound",
    "severe_pain",
    "loss_of_function",
    "major_swelling",
    "deformity",
    "numbness",
}


def normalize_text(value: str) -> str:
    """Normalize a user-provided injury description."""

    return (
        value.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def analyze_injury(
    injury_type: str,
    symptoms: list[str] | None = None,
) -> dict[str, Any]:
    """
    Analyze a reported injury using simple safety rules.

    This is not a medical diagnosis.
    """

    normalized_type = normalize_text(injury_type)

    reported_symptoms = {
        normalize_text(symptom)
        for symptom in (symptoms or [])
        if isinstance(symptom, str) and symptom.strip()
    }

    urgent_signals = sorted(
        reported_symptoms.intersection(URGENT_INJURY_SIGNALS)
    )

    if urgent_signals:
        status = "medical_evaluation"
        message = (
            "The reported injury includes potentially concerning "
            "features. Seek medical evaluation."
        )

    else:
        status = "basic_care_information"
        message = (
            "No prototype urgent injury signal was detected. "
            "This does not rule out a significant injury."
        )

    return {
        "injury_type": normalized_type,
        "reported_signs": sorted(reported_symptoms),
        "urgent_signals": urgent_signals,
        "status": status,
        "message": message,
        "is_diagnosis": False,
        "disclaimer": (
            "This prototype provides general safety information "
            "and does not diagnose or replace professional care."
        ),
    }