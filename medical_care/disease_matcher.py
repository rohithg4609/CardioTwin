"""
Prototype disease matching engine for CardioTwin.

This module identifies potentially relevant conditions based on
overlap between reported symptoms and sourced knowledge.

It does NOT diagnose diseases.
"""

from __future__ import annotations

from typing import Any

from medical_care.knowledge import KnowledgeEntry


def normalize_text(value: str) -> str:
    """Normalize text for simple comparison."""

    return (
        value.strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )


def symptom_matches(
    reported_symptom: str,
    documented_symptom: str,
) -> bool:
    """
    Determine whether a reported symptom overlaps with
    a documented symptom description.
    """

    reported = normalize_text(reported_symptom)
    documented = normalize_text(documented_symptom)

    if not reported or not documented:
        return False

    return (
        reported == documented
        or reported in documented
        or documented in reported
    )


def match_disease(
    symptoms: list[str],
    disease_entries: list[KnowledgeEntry],
) -> list[dict[str, Any]]:
    """
    Find potentially relevant diseases based on symptom overlap.

    This function does not diagnose a disease.
    """

    results: list[dict[str, Any]] = []

    for disease in disease_entries:
        matched: list[str] = []

        for reported_symptom in symptoms:
            if not isinstance(reported_symptom, str):
                continue

            if not reported_symptom.strip():
                continue

            for documented_symptom in disease.common_symptoms:
                if symptom_matches(
                    reported_symptom,
                    documented_symptom,
                ):
                    normalized = normalize_text(reported_symptom)

                    if normalized not in matched:
                        matched.append(normalized)

                    break

        if not matched:
            continue

        results.append(
            {
                "disease_id": disease.id,
                "title": disease.title,
                "matched_symptoms": sorted(matched),
                "match_count": len(matched),
                "status": "potentially_relevant",
                "message": (
                    "Some reported information overlaps with this "
                    "condition. This is not a diagnosis; medical "
                    "evaluation may be appropriate."
                ),
            }
        )

    results.sort(
        key=lambda result: result["match_count"],
        reverse=True,
    )

    return results