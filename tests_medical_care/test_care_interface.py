from medical_care.care_interface import MedicalCareEngine


def test_engine_loads_diseases():
    engine = MedicalCareEngine()

    assert len(engine.disease_entries) >= 1


def test_problem_analysis():
    engine = MedicalCareEngine()

    result = engine.analyze_problem(["headache"])

    assert result["status"] == "medical_review"
    assert result["is_diagnosis"] is False
    assert len(result["potentially_relevant_conditions"]) >= 1


def test_red_flag_problem():
    engine = MedicalCareEngine()

    result = engine.analyze_problem(["chest pain"])

    assert result["status"] == "urgent"
    assert result["safety"]["status"] == "urgent"


def test_injury_analysis():
    engine = MedicalCareEngine()

    result = engine.analyze_injury(
        "minor injury",
        ["mild pain"],
    )

    assert result["is_diagnosis"] is False


def test_exercise_safety():
    engine = MedicalCareEngine()

    result = engine.check_exercise(
        "walking",
        "light",
        [],
    )

    assert result["is_medical_clearance"] is False


def test_diet_guidance():
    engine = MedicalCareEngine()

    result = engine.get_diet("hypertension")

    assert result["condition"] == "hypertension"
    assert result["personalized_medical_diet"] is False


def test_confirmed_condition():
    engine = MedicalCareEngine()

    condition = engine.add_confirmed_condition(
        condition_id="hypertension",
        condition_name="Hypertension",
        confirmed_by="doctor",
    )

    result = engine.get_condition_management(condition)

    assert result["status"] == "doctor_confirmed"
    assert result["is_diagnosis"] is False


def test_medication_tracking():
    engine = MedicalCareEngine()

    medication = engine.add_medication(
        name="Example Medicine",
        dose="As prescribed",
        frequency="As prescribed",
    )

    result = engine.record_medication_status(
        medication,
        taken=True,
    )

    assert result["status"] == "taken"
    assert result["treatment_changed"] is False