"""Knowledge-base data structures and loaders for CardioTwin."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Mapping


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DISEASES_PATH = DATA_DIR / "diseases.json"

SUPPORTED_CATEGORIES = frozenset(
    {
        "disease",
        "symptom",
        "red_flag",
        "injury",
        "diet_guidance",
        "general_health_guidance",
    }
)

OPTIONAL_MEDICAL_FIELDS = (
    "common_symptoms",
    "risk_factors",
    "relevant_measurements",
    "warning_signs",
    "general_lifestyle_information",
    "when_medical_evaluation_is_appropriate",
)


class KnowledgeEntryError(ValueError):
    """Raised when a knowledge-base entry has invalid structure."""


def _require_non_empty_text(field_name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeEntryError(
            f"{field_name} is required and must be non-empty text."
        )
    return value.strip()


def _optional_string_list(
    field_name: str,
    value: object,
) -> list[str]:
    if value is None:
        return []

    if not isinstance(value, list):
        raise KnowledgeEntryError(
            f"{field_name} must be a list of text values."
        )

    cleaned: list[str] = []

    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise KnowledgeEntryError(
                f"{field_name} must contain only non-empty text values."
            )

        cleaned.append(item.strip())

    return cleaned


@dataclass(frozen=True)
class KnowledgeEntry:
    """One sourced knowledge-base record. This is not a diagnosis."""

    id: str
    category: str
    title: str
    summary: str
    source_name: str
    source_url: str

    common_symptoms: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    relevant_measurements: list[str] = field(default_factory=list)
    warning_signs: list[str] = field(default_factory=list)
    general_lifestyle_information: list[str] = field(
        default_factory=list
    )
    when_medical_evaluation_is_appropriate: list[str] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id",
            _require_non_empty_text("id", self.id),
        )

        object.__setattr__(
            self,
            "category",
            _require_non_empty_text("category", self.category),
        )

        if self.category not in SUPPORTED_CATEGORIES:
            raise KnowledgeEntryError(
                f"Unsupported category: {self.category!r}. "
                f"Supported categories: "
                f"{', '.join(sorted(SUPPORTED_CATEGORIES))}."
            )

        object.__setattr__(
            self,
            "title",
            _require_non_empty_text("title", self.title),
        )

        object.__setattr__(
            self,
            "summary",
            _require_non_empty_text("summary", self.summary),
        )

        object.__setattr__(
            self,
            "source_name",
            _require_non_empty_text(
                "source_name",
                self.source_name,
            ),
        )

        object.__setattr__(
            self,
            "source_url",
            _require_non_empty_text(
                "source_url",
                self.source_url,
            ),
        )

        for field_name in OPTIONAL_MEDICAL_FIELDS:
            object.__setattr__(
                self,
                field_name,
                _optional_string_list(
                    field_name,
                    getattr(self, field_name),
                ),
            )

    @classmethod
    def from_mapping(
        cls,
        data: Mapping[str, object],
    ) -> "KnowledgeEntry":
        if not isinstance(data, Mapping):
            raise KnowledgeEntryError(
                "Knowledge entry must be a mapping."
            )

        return cls(
            id=data.get("id"),
            category=data.get("category"),
            title=data.get("title"),
            summary=data.get("summary"),
            source_name=data.get("source_name"),
            source_url=data.get("source_url"),
            common_symptoms=_optional_string_list(
                "common_symptoms",
                data.get("common_symptoms"),
            ),
            risk_factors=_optional_string_list(
                "risk_factors",
                data.get("risk_factors"),
            ),
            relevant_measurements=_optional_string_list(
                "relevant_measurements",
                data.get("relevant_measurements"),
            ),
            warning_signs=_optional_string_list(
                "warning_signs",
                data.get("warning_signs"),
            ),
            general_lifestyle_information=_optional_string_list(
                "general_lifestyle_information",
                data.get("general_lifestyle_information"),
            ),
            when_medical_evaluation_is_appropriate=_optional_string_list(
                "when_medical_evaluation_is_appropriate",
                data.get("when_medical_evaluation_is_appropriate"),
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def load_knowledge_file(
    path: Path | str,
    *,
    expected_category: str | None = None,
) -> list[KnowledgeEntry]:

    file_path = Path(path)

    try:
        raw = json.loads(
            file_path.read_text(encoding="utf-8")
        )
    except FileNotFoundError as exc:
        raise KnowledgeEntryError(
            f"Knowledge file not found: {file_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise KnowledgeEntryError(
            f"Knowledge file is not valid JSON: {file_path}"
        ) from exc

    if not isinstance(raw, dict) or "entries" not in raw:
        raise KnowledgeEntryError(
            f"Knowledge file must contain an 'entries' list: {file_path}"
        )

    entries = raw["entries"]

    if not isinstance(entries, list):
        raise KnowledgeEntryError(
            f"'entries' must be a list: {file_path}"
        )

    loaded: list[KnowledgeEntry] = []

    for index, item in enumerate(entries):
        if not isinstance(item, Mapping):
            raise KnowledgeEntryError(
                f"Entry {index} in {file_path} must be an object."
            )

        entry = KnowledgeEntry.from_mapping(item)

        if (
            expected_category is not None
            and entry.category != expected_category
        ):
            raise KnowledgeEntryError(
                f"Entry {entry.id!r} has category "
                f"{entry.category!r}, expected "
                f"{expected_category!r}."
            )

        loaded.append(entry)

    return loaded


def load_disease_entries(
    path: Path | str | None = None,
) -> list[KnowledgeEntry]:
    """Load disease knowledge entries."""

    return load_knowledge_file(
        path or DISEASES_PATH,
        expected_category="disease",
    )
