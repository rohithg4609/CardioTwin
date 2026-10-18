"""
Problem analysis engine for the CardioTwin prototype.

Combines symptom matching and safety checks into a structured result.

This module does NOT diagnose medical conditions.
"""

from __future__ import annotations

from typing import Any

from medical_care.disease_matcher import match_disease
from medical_care.knowledge import KnowledgeEntry
from medical_care.safety_engine import check_red_flags


def analyze_problem(
    symptoms: list[str],
    disease_entries: list[KnowledgeEntry],
) -> dict[str, Any]:
    """
    Analyze reported symptoms using the disease knowledge base
    and safety rules.

    The result describes potentially relevant information.
    It does not confirm a diagnosis.
    """

    clean_symptoms = [
        symptom.strip()
        for symptom in symptoms
        if isinstance(symptom, str) and symptom.strip()
    ]

    safety_result = check_red_flags(clean_symptoms)

    potential_matches = match_disease(
        clean_symptoms,
        disease_entries,
    )

    if safety_result["red_flags_detected"]:
        overall_status = "urgent"
        next_step = (
            "Seek urgent medical evaluation because potentially "
            "serious warning signs were reported."
        )
    elif potential_matches:
        overall_status = "medical_review"
        next_step = (
            "Some reported information overlaps with documented "
            "conditions. Consider discussing the symptoms with "
            "a healthcare professional."
        )
    else:
        overall_status = "no_specific_match"
        next_step = (
            "No specific condition was matched by the prototype "
            "knowledge base. This does not rule out a medical problem."
        )

    return {
        "reported_symptoms": clean_symptoms,
        "status": overall_status,
        "potentially_relevant_conditions": potential_matches,
        "safety": safety_result,
        "next_step": next_step,
        "is_diagnosis": False,
        "disclaimer": (
            "This prototype provides informational support only "
            "and does not diagnose medical conditions."
        ),
    }