"""
Safety and red-flag engine for the CardioTwin prototype.

This module provides rule-based safety checks.
It does not diagnose medical conditions.
"""

from typing import Any, Dict, List


# These are prototype safety rules, not medically validated
# universal thresholds.
RED_FLAG_SYMPTOMS = {
    "chest_pain",
    "severe_breathing_difficulty",
    "fainting",
    "sudden_weakness",
    "sudden_numbness",
    "speech_difficulty",
    "sudden_vision_change",
    "severe_confusion",
}


def normalize_symptom(symptom: str) -> str:
    """Convert a symptom into a simple normalized form."""
    return symptom.strip().lower().replace(" ", "_").replace("-", "_")


def check_red_flags(symptoms: List[str]) -> Dict[str, Any]:
    """
    Check whether reported symptoms contain prototype red flags.

    Returns a structured result that can later be consumed by
    the CardioTwin API or frontend.
    """

    normalized = {
        normalize_symptom(symptom)
        for symptom in symptoms
        if isinstance(symptom, str)
    }

    detected = sorted(normalized.intersection(RED_FLAG_SYMPTOMS))

    if detected:
        return {
            "status": "urgent",
            "red_flags_detected": True,
            "matched_signs": detected,
            "message": (
                "Potentially serious warning signs were reported. "
                "Seek urgent medical evaluation. "
                "This prototype cannot determine the cause."
            ),
        }

    return {
        "status": "no_red_flags_detected",
        "red_flags_detected": False,
        "matched_signs": [],
        "message": (
            "No prototype red-flag symptoms were detected. "
            "This does not mean the person is medically safe."
        ),
    }


def apply_safety_override(
    symptoms: List[str],
    risk_score: float | None = None,
) -> Dict[str, Any]:
    """
    Apply safety rules before considering an ML risk score.

    A detected red flag takes priority over the numerical risk score.
    """

    safety_result = check_red_flags(symptoms)

    if safety_result["red_flags_detected"]:
        safety_result["risk_score_ignored_for_safety"] = True
        safety_result["risk_score"] = risk_score
        return safety_result

    safety_result["risk_score_ignored_for_safety"] = False
    safety_result["risk_score"] = risk_score

    return safety_result