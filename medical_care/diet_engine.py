"""
General diet guidance engine for the CardioTwin prototype.

This module provides general, condition-aware nutrition information.
It does not prescribe a medical diet or replace advice from a
qualified healthcare professional.
"""

from __future__ import annotations

from typing import Any


GENERAL_GUIDANCE = {
    "include_more": [
        "Vegetables",
        "Fruits",
        "Whole grains",
        "Beans and other legumes",
        "Nuts and seeds where appropriate",
    ],
    "consider_limiting": [
        "Foods high in sodium",
        "Highly processed foods",
        "Foods high in added sugars",
        "Excessive saturated fat",
    ],
}


CONDITION_GUIDANCE = {
    "hypertension": {
        "include_more": [
            "Vegetables and fruits",
            "Whole grains",
            "Beans and other legumes",
        ],
        "consider_limiting": [
            "High-sodium foods",
            "Highly processed foods",
        ],
    }
}


def normalize_condition(condition: str) -> str:
    """Normalize a condition identifier."""

    return (
        condition.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def get_diet_guidance(
    condition: str | None = None,
) -> dict[str, Any]:
    """
    Return general diet guidance.

    Condition-specific guidance is only applied when a condition
    has already been explicitly identified by the application.

    This function does not diagnose a condition.
    """

    include_more = list(GENERAL_GUIDANCE["include_more"])
    consider_limiting = list(
        GENERAL_GUIDANCE["consider_limiting"]
    )

    normalized_condition = None

    if isinstance(condition, str) and condition.strip():
        normalized_condition = normalize_condition(condition)

        condition_guidance = CONDITION_GUIDANCE.get(
            normalized_condition
        )

        if condition_guidance:
            include_more.extend(
                condition_guidance["include_more"]
            )

            consider_limiting.extend(
                condition_guidance["consider_limiting"]
            )

    return {
        "condition": normalized_condition,
        "include_more": sorted(set(include_more)),
        "consider_limiting": sorted(set(consider_limiting)),
        "personalized_medical_diet": False,
        "message": (
            "This is general nutrition information. "
            "Follow any diet instructions provided by your "
            "healthcare professional."
        ),
        "disclaimer": (
            "CardioTwin does not prescribe a medical diet. "
            "Individual dietary needs should be discussed with "
            "a qualified healthcare professional."
        ),
    }