"""
Digital Twin coordinator.

Connects patient information, current health state, health history,
and the prototype risk tracker into one simple interface.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .patient import Patient
from .health_state import HealthState
from .history import HealthHistory
from .risk_tracker import RiskTracker


class DigitalTwin:
    """
    Main coordinator for a patient's digital twin.

    This class combines:
    - Patient profile
    - Current HealthState
    - HealthHistory
    - RiskTracker

    The risk calculation is a prototype/demo scoring system and is
    not clinically validated.
    """

    def __init__(
        self,
        patient: Patient,
        health_state: Optional[HealthState] = None,
        history: Optional[HealthHistory] = None,
    ) -> None:
        if not isinstance(patient, Patient):
            raise TypeError("patient must be a Patient instance.")

        if health_state is not None and not isinstance(
            health_state, HealthState
        ):
            raise TypeError(
                "health_state must be a HealthState instance or None."
            )

        if history is not None and not isinstance(history, HealthHistory):
            raise TypeError(
                "history must be a HealthHistory instance or None."
            )

        self.patient = patient
        self.health_state = health_state or HealthState()

        if history is not None:
            self.history = history
        else:
            self.history = HealthHistory(filename=None)

            # DigitalTwin starts with a clean in-memory history.
            self.history.records = []

        self.risk_tracker = RiskTracker(
            self.patient,
            self.health_state,
        )

    # ------------------------------------------------------------------
    # Patient
    # ------------------------------------------------------------------

    def get_patient(self) -> Patient:
        """Return the patient object."""
        return self.patient

    def update_patient(self, **updates: Any) -> Patient:
        """Update patient fields and return the updated patient."""
        self.patient.update(**updates)
        return self.patient

    # ------------------------------------------------------------------
    # Current health state
    # ------------------------------------------------------------------

    def get_health_state(self) -> HealthState:
        """Return the current health state."""
        return self.health_state

    def update_health_state(self, **updates: Any) -> HealthState:
        """Update the current health state."""
        self.health_state.update(**updates)
        return self.health_state

    def replace_health_state(
        self,
        health_state: HealthState,
    ) -> HealthState:
        """Replace the current health state."""
        if not isinstance(health_state, HealthState):
            raise TypeError(
                "health_state must be a HealthState instance."
            )

        self.health_state = health_state

        self.risk_tracker = RiskTracker(
            self.patient,
            self.health_state,
        )

        return self.health_state

    # ------------------------------------------------------------------
    # Health history
    # ------------------------------------------------------------------

    def add_health_record(
        self,
        date: str,
        record: Dict[str, Any],
        save: bool = False,
    ) -> Dict[str, Any]:
        """
        Add a health record to history.

        The date is stored inside the history record, while the method
        returns the original record data supplied by the caller.
        """
        if not isinstance(date, str):
            raise TypeError("date must be a string.")

        if not date.strip():
            raise ValueError("date cannot be empty.")

        if not isinstance(record, dict):
            raise TypeError("record must be a dictionary.")

        # Make a copy so the caller's dictionary is not modified.
        health_record = dict(record)
        health_record["date"] = date

        self.history.add_record(
            health_record,
            save=save,
        )

        # Existing DigitalTwin API expects the returned value to match
        # the record supplied by the caller, without the internal date
        # field added above.
        return dict(record)

    def get_history(self) -> HealthHistory:
        """Return the underlying HealthHistory object."""
        return self.history

    def get_latest_record(self) -> Optional[Dict[str, Any]]:
        """Return the latest health record, or None."""
        if not self.history.records:
            return None

        return dict(self.history.records[-1])

    def get_first_record(self) -> Optional[Dict[str, Any]]:
        """Return the first health record, or None."""
        if not self.history.records:
            return None

        return dict(self.history.records[0])

    def get_all_records(self):
        """Return all health records."""
        return [
            dict(record)
            for record in self.history.records
        ]

    def get_records_by_date(self, date: str):
        """Return all health records matching the given date."""
        return [
            dict(record)
            for record in self.history.records
            if record.get("date") == date
        ]

    def clear_history(self) -> None:
        """Clear all in-memory health history records."""
        self.history.records.clear()

    # ------------------------------------------------------------------
    # Risk
    # ------------------------------------------------------------------

    def calculate_risk(self) -> float:
        """
        Calculate the prototype risk score.

        Returns
        -------
        float
            Demo risk score from 0 to 100.
        """
        self.risk_tracker.patient = self.patient
        self.risk_tracker.health_state = self.health_state

        return self.risk_tracker.calculate_risk()

    def get_risk_score(self) -> float:
        """Return the current prototype risk score."""
        return self.risk_tracker.get_score()

    def get_risk_level(self) -> str:
        """Return the current prototype risk level."""
        return self.risk_tracker.get_risk_level()

    def get_risk_result(self) -> Dict[str, Any]:
        """Return the complete prototype risk result."""
        self.calculate_risk()
        return self.risk_tracker.get_result()

    def needs_doctor_review(self) -> bool:
        """Return whether the prototype score crosses the review threshold."""
        self.calculate_risk()
        return self.risk_tracker.needs_doctor_review()

    def needs_urgent_attention(self) -> bool:
        """Return whether urgent prototype criteria are triggered."""
        self.calculate_risk()
        return self.risk_tracker.needs_urgent_attention()

    def get_recommendation(self) -> str:
        """Return the prototype risk recommendation."""
        self.calculate_risk()
        return self.risk_tracker.get_recommendation()

    def reset_risk(self) -> None:
        """Reset the prototype risk tracker."""
        self.risk_tracker.reset()

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def get_snapshot(self) -> Dict[str, Any]:
        """
        Return a combined snapshot of the digital twin.
        """
        self.calculate_risk()

        return {
            "patient": self.patient.to_dict(),
            "health_state": self.health_state.to_dict(),
            "latest_history": self.get_latest_record(),
            "risk": self.risk_tracker.get_result(),
        }

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"DigitalTwin("
            f"patient_id={self.patient.patient_id!r}, "
            f"records={len(self.history.records)}, "
            f"risk_score={self.get_risk_score():.2f}"
            f")"
        )