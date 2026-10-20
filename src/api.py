from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from src.predict import predict_patient
from digital_twin.digital_twin import DigitalTwin
from digital_twin.health_state import HealthState
from digital_twin.history import HealthHistory
from digital_twin.patient import Patient as DigitalPatient


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "digital_twin_api"
PATIENT_FILE = DATA_DIR / "patient.json"
HEALTH_STATE_FILE = DATA_DIR / "health_state.json"
HISTORY_FILE = DATA_DIR / "history.json"


app = FastAPI(
    title="CardioTwin ML API",
    description=(
        "Cardiovascular model API plus local digital-twin profile, "
        "health-state, and history endpoints. Prototype only; not a diagnostic tool."
    ),
    version="1.1.0",
)


# -----------------------------
# Request models
# -----------------------------
class PredictionPatient(BaseModel):
    age: float
    sex: float
    cp: float
    trestbps: float
    chol: float
    fbs: float
    restecg: float
    thalach: float
    exang: float
    oldpeak: float
    slope: float
    ca: float
    thal: float


class PatientProfileInput(BaseModel):
    patient_id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=120)
    age: int = Field(ge=0, le=150)
    sex: str = Field(min_length=1, max_length=40)
    height: float | None = Field(default=None, gt=0)
    weight: float | None = Field(default=None, gt=0)
    family_history: list[str] = Field(default_factory=list)
    smoking: bool | None = None
    existing_conditions: list[str] = Field(default_factory=list)
    medications: list[Any] = Field(default_factory=list)


class PatientProfilePatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    age: int | None = Field(default=None, ge=0, le=150)
    sex: str | None = Field(default=None, min_length=1, max_length=40)
    height: float | None = Field(default=None, gt=0)
    weight: float | None = Field(default=None, gt=0)
    family_history: list[str] | None = None
    smoking: bool | None = None
    existing_conditions: list[str] | None = None
    medications: list[Any] | None = None


class HealthStateUpdate(BaseModel):
    heart_rate: float | None = Field(default=None, gt=0)
    systolic_bp: float | None = Field(default=None, gt=0)
    diastolic_bp: float | None = Field(default=None, gt=0)
    spo2: float | None = Field(default=None, ge=0, le=100)
    glucose: float | None = Field(default=None, gt=0)
    cholesterol: float | None = Field(default=None, gt=0)
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    water_intake: float | None = Field(default=None, ge=0)
    steps: int | None = Field(default=None, ge=0)
    exercise_minutes: int | None = Field(default=None, ge=0)
    stress_level: float | None = Field(default=None, ge=0, le=10)
    weight: float | None = Field(default=None, gt=0)
    bmi: float | None = Field(default=None, gt=0)


from datetime import date as DateType

class HealthRecordInput(BaseModel):
    date: DateType | None = None
    record: dict[str, Any] = Field(default_factory=dict)


class CheckpointInput(BaseModel):
    note: str | None = Field(default=None, max_length=500)


# -----------------------------
# JSON persistence helpers
# -----------------------------
def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read local CardioTwin data file: {path.name}",
        ) from exc


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(jsonable_encoder(value), handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        temporary_path.replace(path)
    except (OSError, TypeError, ValueError) as exc:
        try:
            if temporary_path.exists():
                temporary_path.unlink()
        except OSError:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"Could not save local CardioTwin data file: {path.name}",
        ) from exc


def _load_patient() -> DigitalPatient:
    raw = _read_json(PATIENT_FILE, None)
    if raw is None:
        raise HTTPException(
            status_code=404,
            detail="No patient profile exists yet. Create one with POST /api/patient first.",
        )
    if not isinstance(raw, dict):
        raise HTTPException(status_code=500, detail="Stored patient profile has an invalid format.")
    try:
        return DigitalPatient.from_dict(raw)
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=500, detail="Stored patient profile failed validation.") from exc


def _load_health_state() -> HealthState:
    raw = _read_json(HEALTH_STATE_FILE, {})
    if not isinstance(raw, dict):
        raise HTTPException(status_code=500, detail="Stored health state has an invalid format.")
    try:
        return HealthState.from_dict(raw)
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=500, detail="Stored health state failed validation.") from exc


def _load_history() -> HealthHistory:
    try:
        return HealthHistory(filename=HISTORY_FILE)
    except (OSError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=500, detail="Could not load CardioTwin health history.") from exc


def _load_twin() -> DigitalTwin:
    # Passing the history object is important: DigitalTwin's default constructor
    # intentionally starts with an empty in-memory history.
    return DigitalTwin(
        patient=_load_patient(),
        health_state=_load_health_state(),
        history=_load_history(),
    )


# -----------------------------
# Existing API routes (preserved)
# -----------------------------
@app.get("/")
def home():
    return {"message": "CardioTwin ML API is running", "status": "online"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict(patient: PredictionPatient):
    try:
        return predict_patient(patient.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# -----------------------------
# Patient profile routes
# -----------------------------
@app.get("/api/patient")
def get_patient_profile():
    return _load_patient().to_dict()


@app.post("/api/patient")
def save_patient_profile(profile: PatientProfileInput):
    try:
        patient = DigitalPatient.from_dict(profile.model_dump())
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    _write_json(PATIENT_FILE, patient.to_dict())
    # Initialize a health state only when no state exists; preserve earlier measurements.
    if not HEALTH_STATE_FILE.exists():
        _write_json(HEALTH_STATE_FILE, HealthState().to_dict())

    return {"message": "Patient profile saved.", "patient": patient.to_dict()}


@app.patch("/api/patient")
def update_patient_profile(patch: PatientProfilePatch):
    patient = _load_patient()
    changes = patch.model_dump(exclude_unset=True)
    if not changes:
        return {"message": "No profile changes supplied.", "patient": patient.to_dict()}
    try:
        patient.update(**changes)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    _write_json(PATIENT_FILE, patient.to_dict())
    return {"message": "Patient profile updated.", "patient": patient.to_dict()}


# -----------------------------
# Current health-state routes
# -----------------------------
@app.get("/api/health-state")
def get_health_state():
    _load_patient()  # Require a profile before exposing its health data.
    return _load_health_state().to_dict()


@app.patch("/api/health-state")
def update_health_state(update: HealthStateUpdate):
    _load_patient()
    state = _load_health_state()
    changes = update.model_dump(exclude_unset=True)
    try:
        state.update(**changes)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    _write_json(HEALTH_STATE_FILE, state.to_dict())
    return {"message": "Current health state updated.", "health_state": state.to_dict()}


# -----------------------------
# Digital-twin snapshot and history routes
# -----------------------------
@app.get("/api/digital-twin/snapshot")
def get_digital_twin_snapshot():
    try:
        return _load_twin().get_snapshot()
    except HTTPException:
        raise
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/health-records")
def get_health_records():
    _load_patient()
    history = _load_history()
    records = history.get_all_records()
    return {"count": len(records), "records": records}


@app.post("/api/health-records")
def add_health_record(payload: HealthRecordInput):
    _load_patient()
    record_date = payload.date or date.today()
    record = {**payload.record, "date": record_date.isoformat()}
    try:
        stored = _load_history().add_record(record, save=True)
    except (OSError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"message": "Health record saved.", "record": stored}


@app.post("/api/digital-twin/checkpoint")
def save_digital_twin_checkpoint(payload: CheckpointInput):
    """Save the current measurements and prototype risk output to history."""
    try:
        twin = _load_twin()
        snapshot = twin.get_snapshot()
        now = datetime.now().astimezone()
        record = {
            "record_type": "digital_twin_checkpoint",
            "date": now.date().isoformat(),
            "created_at": now.isoformat(),
            "health_state": snapshot["health_state"],
            "risk": snapshot["risk"],
            "note": payload.note,
        }
        stored = twin.history.add_record(record, save=True)
        return {"message": "Digital-twin checkpoint saved.", "record": stored}
    except HTTPException:
        raise
    except (OSError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/assessment")
def run_and_save_assessment(patient: PredictionPatient):
    """Run the ML prediction and persist it to the digital-twin history."""
    active_patient = _load_patient()
    patient_data = patient.model_dump()
    patient_snapshot = {
        "patient_id": active_patient.patient_id,
        "name": active_patient.name,
        "age": active_patient.age,
        "sex": active_patient.sex,
    }
    try:
        result = jsonable_encoder(predict_patient(patient_data))
        now = datetime.now().astimezone()
        record = {
            "record_type": "ml_cardiovascular_assessment",
            "date": now.date().isoformat(),
            "created_at": now.isoformat(),
            "patient_snapshot": patient_snapshot,
            "model_inputs": patient_data,
            "prediction": result,
        }
        stored = _load_history().add_record(record, save=True)
        return {
            "assessment": result,
            "saved_record": stored,
            "notice": (
                "Prototype model output only. It is not a diagnosis or a clinically "
                "validated individual probability. Discuss health concerns with a qualified clinician."
            ),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
