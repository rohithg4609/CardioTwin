"""
CardioTwin Health History Manager.

This module manages historical health records stored in JSON format.

Responsibilities:
- Load health history
- Save health history
- Add new records
- Retrieve records
- Retrieve records by date
- Retrieve the latest/first record
- Validate basic record structure

This module does not diagnose medical conditions or make clinical decisions.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


HealthRecord = Dict[str, Any]


class HealthHistory:
    """
    Manages a collection of historical health records.

    Parameters
    ----------
    filename:
        Optional path to the JSON history file.

        If omitted, the default CardioTwin history file is used:

            data/health_records/history.json
    """

    def __init__(self, filename: Optional[str | Path] = None) -> None:
        self.filename = self._resolve_filename(filename)
        self.records: List[HealthRecord] = []

        self.load()

    # ---------------------------------------------------------
    # File/path handling
    # ---------------------------------------------------------

    @staticmethod
    def _project_root() -> Path:
        """
        Return the CardioTwin project root.

        history.py is located at:

            CardioTwin/digital_twin/history.py

        Therefore the project root is two directories above this file.
        """

        return Path(__file__).resolve().parent.parent

    @classmethod
    def _resolve_filename(
        cls,
        filename: Optional[str | Path],
    ) -> Path:
        """Resolve the history file path safely."""

        if filename is None:
            return (
                cls._project_root()
                / "data"
                / "health_records"
                / "history.json"
            )

        path = Path(filename)

        if not path.is_absolute():
            path = cls._project_root() / path

        return path

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_record(record: HealthRecord) -> HealthRecord:
        """
        Validate the basic structure of a health record.

        A record must be a dictionary.

        The record may contain any combination of health fields because
        wearable/manual data can be incomplete.
        """

        if not isinstance(record, dict):
            raise TypeError("Health record must be a dictionary.")

        cleaned_record = dict(record)

        if "date" in cleaned_record:
            if not isinstance(cleaned_record["date"], str):
                raise TypeError("Record date must be a string.")

            if not cleaned_record["date"].strip():
                raise ValueError("Record date cannot be empty.")

        return cleaned_record

    # ---------------------------------------------------------
    # Loading
    # ---------------------------------------------------------

    def load(self) -> List[HealthRecord]:
        """
        Load health records from the JSON file.

        Returns
        -------
        list
            Loaded health records.

        Missing files are treated as an empty history.

        Invalid JSON raises ValueError rather than silently destroying
        or replacing existing data.
        """

        if not self.filename.exists():
            self.records = []
            return self.records

        try:
            with self.filename.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in health history file: "
                f"{self.filename}"
            ) from exc

        if not isinstance(data, list):
            raise ValueError(
                "Health history JSON must contain a list of records."
            )

        validated_records = []

        for index, record in enumerate(data):
            try:
                validated_records.append(
                    self._validate_record(record)
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid health record at index {index}: {exc}"
                ) from exc

        self.records = validated_records

        return self.records

    # ---------------------------------------------------------
    # Saving
    # ---------------------------------------------------------

    def save(self) -> None:
        """
        Save all current records to the JSON history file.
        """

        self.filename.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_file = self.filename.with_suffix(
            self.filename.suffix + ".tmp"
        )

        try:
            with temporary_file.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    self.records,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )
                file.write("\n")

            # Replace the old file only after writing succeeds.
            temporary_file.replace(self.filename)

        except OSError:
            if temporary_file.exists():
                temporary_file.unlink()
            raise

    # ---------------------------------------------------------
    # Record management
    # ---------------------------------------------------------

    def add_record(
        self,
        record: HealthRecord,
        save: bool = True,
    ) -> HealthRecord:
        """
        Add a new health record.

        Parameters
        ----------
        record:
            Dictionary containing health data.

        save:
            If True, immediately save the updated history to disk.

        Returns
        -------
        dict
            The stored record.
        """

        validated_record = self._validate_record(record)

        self.records.append(validated_record)

        if save:
            try:
                self.save()
            except Exception:
                # Roll back the in-memory change if saving failed.
                self.records.pop()
                raise

        return dict(validated_record)

    def remove_record(
        self,
        index: int,
        save: bool = True,
    ) -> HealthRecord:
        """
        Remove a record by its list index.

        Returns the removed record.
        """

        if not isinstance(index, int):
            raise TypeError("Record index must be an integer.")

        if index < 0 or index >= len(self.records):
            raise IndexError(
                f"Record index out of range: {index}"
            )

        removed = self.records.pop(index)

        if save:
            try:
                self.save()
            except Exception:
                # Restore the record if disk saving fails.
                self.records.insert(index, removed)
                raise

        return dict(removed)

    def clear(self, save: bool = True) -> None:
        """Remove all records."""

        old_records = self.records.copy()

        self.records = []

        if save:
            try:
                self.save()
            except Exception:
                self.records = old_records
                raise

    # ---------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------

    def get_all_records(self) -> List[HealthRecord]:
        """
        Return all health records.

        A new list and copied dictionaries are returned so callers
        cannot accidentally modify the internal history.
        """

        return [
            dict(record)
            for record in self.records
        ]

    def get_latest_record(self) -> Optional[HealthRecord]:
        """
        Return the most recently stored record.

        Returns None when history is empty.
        """

        if not self.records:
            return None

        return dict(self.records[-1])

    def get_first_record(self) -> Optional[HealthRecord]:
        """
        Return the first stored record.

        Returns None when history is empty.
        """

        if not self.records:
            return None

        return dict(self.records[0])

    def get_record_count(self) -> int:
        """Return the number of stored records."""

        return len(self.records)

    # ---------------------------------------------------------
    # Date-based retrieval
    # ---------------------------------------------------------

    def get_records_by_date(
        self,
        target_date: str | date | datetime,
    ) -> List[HealthRecord]:
        """
        Return records matching a specific date.

        Supported input:
        - YYYY-MM-DD string
        - datetime.date
        - datetime.datetime
        """

        normalized_date = self._normalize_date(target_date)

        matching_records = []

        for record in self.records:
            record_date = record.get("date")

            if record_date == normalized_date:
                matching_records.append(dict(record))

        return matching_records

    @staticmethod
    def _normalize_date(
        value: str | date | datetime,
    ) -> str:
        """Convert supported date types to YYYY-MM-DD."""

        if isinstance(value, datetime):
            return value.date().isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError("Date cannot be empty.")

            try:
                parsed = datetime.strptime(
                    value,
                    "%Y-%m-%d",
                )
            except ValueError as exc:
                raise ValueError(
                    "Date must use YYYY-MM-DD format."
                ) from exc

            return parsed.date().isoformat()

        raise TypeError(
            "Date must be a YYYY-MM-DD string, "
            "date, or datetime."
        )

    # ---------------------------------------------------------
    # Utility methods
    # ---------------------------------------------------------

    def is_empty(self) -> bool:
        """Return True if no health records exist."""

        return len(self.records) == 0

    def reload(self) -> List[HealthRecord]:
        """Reload records from disk."""

        return self.load()

    def __len__(self) -> int:
        """Allow len(history)."""

        return len(self.records)

    def __repr__(self) -> str:
        """Return a concise representation."""

        return (
            f"HealthHistory("
            f"records={len(self.records)}, "
            f"filename={str(self.filename)!r})"
        )


if __name__ == "__main__":
    # Manual smoke test.
    # Nothing runs when this module is imported.

    history = HealthHistory()

    print("CardioTwin Health History")
    print("-------------------------")
    print(f"History file: {history.filename}")
    print(f"Records: {history.get_record_count()}")

    latest = history.get_latest_record()

    if latest is not None:
        print("Latest record:")
        print(json.dumps(latest, indent=4))
    else:
        print("No health records available.")