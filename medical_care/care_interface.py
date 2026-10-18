"""
Unified interface for CardioTwin medical-care features.

This module connects the individual medical-care components
behind one simple interface for the future frontend/API.

It does NOT diagnose diseases or provide medical clearance.
"""
from __future__ import annotations

from typing import Any

from medical_care.knowledge import KnowledgeEntry, load_disease_entries
from medical_care.problem_analyzer import analyze_problem
from medical_care.injury_engine import analyze_injury
from medical_care.exercise_safety import check_exercise_safety
from medical_care.diet_engine import get_diet_guidance
from medical_care.condition_manager import (
    add_confirmed_condition,
    get_condition_management,
)
from medical_care.medication_manager import (
    add_medication,
    record_medication_status,
)


class MedicalCareEngine:
    """Single interface to CardioTwin's medical-care features."""

    def __init__(
        self,
        disease_entries: list[KnowledgeEntry] | None = None,
    ) -> None:
        if disease_entries is None:
            disease_entries = load_disease_entries(
                "data/diseases.json"
            )

        self.disease_entries = disease_entries

    def analyze_problem(
        self,
        symptoms: list[str],
    ) -> dict[str, Any]:
        return analyze_problem(
            symptoms,
            self.disease_entries,
        )

    def analyze_injury(
        self,
        injury_type: str,
        symptoms: list[str] | None = None,
    ) -> dict[str, Any]:
        return analyze_injury(
            injury_type,
            symptoms,
        )

    def check_exercise(
        self,
        exercise_type: str,
        intensity: str | None = None,
        symptoms: list[str] | None = None,
    ) -> dict[str, Any]:
        return check_exercise_safety(
            exercise_type,
            intensity,
            symptoms,
        )

    def get_diet(
        self,
        condition: str | None = None,
    ) -> dict[str, Any]:
        return get_diet_guidance(condition)

    def add_confirmed_condition(
        self,
        condition_id: str,
        condition_name: str,
        confirmed_by: str,
        confirmation_date: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        condition = add_confirmed_condition(
            condition_id=condition_id,
            condition_name=condition_name,
            confirmed_by=confirmed_by,
            confirmation_date=confirmation_date,
            notes=notes,
        )

        return condition

    def get_condition_management(
        self,
        condition: dict[str, Any],
    ) -> dict[str, Any]:
        return get_condition_management(condition)

    def add_medication(
        self,
        name: str,
        dose: str,
        frequency: str,
        scheduled_time: str | None = None,
        before_or_after_food: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        source: str = "user_entered",
    ) -> dict[str, Any]:
        medication = add_medication(
            name=name,
            dose=dose,
            frequency=frequency,
            scheduled_time=scheduled_time,
            before_or_after_food=before_or_after_food,
            start_date=start_date,
            end_date=end_date,
            source=source,
        )

        return medication

    def record_medication_status(
        self,
        medication: dict[str, Any],
        taken: bool,
    ) -> dict[str, Any]:
        return record_medication_status(
            medication,
            taken,
        )
