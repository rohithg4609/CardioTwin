import joblib

from src.preprocessing import (
    prepare_patient,
    validate_patient
)

from src.explain import (
    get_patient_explanation
)


MODEL_PATH = "models/cardio_model.pkl"


def load_model():
    model = joblib.load(MODEL_PATH)
    return model


def get_risk_category(risk_score):

    if risk_score < 40:
        return "Lower model-estimated risk"

    elif risk_score < 80:
        return "Elevated model-estimated risk"

    else:
        return "Higher model-estimated risk"


def predict_patient(patient):

    # Check whether all required features are present
    validate_patient(patient)

    # Convert patient dictionary into DataFrame
    patient_df = prepare_patient(patient)

    # Load trained model
    model = load_model()

    # Predict class
    prediction = model.predict(patient_df)

    # Get model-estimated score
    probability = model.predict_proba(patient_df)[0][1]

    risk_score = probability * 100

    # Convert score into prototype category
    risk_category = get_risk_category(risk_score)

    # Convert prediction into readable class
    if prediction[0] == 1:
        predicted_class = "Disease class"
    else:
        predicted_class = "No disease class"

    # Generate SHAP explanation
    explanation_df = get_patient_explanation(
        model,
        patient_df
    )

    explanations = []

    for _, row in explanation_df.head(5).iterrows():

        if row["shap_value"] > 0:
            direction = "toward disease class"
        else:
            direction = "away from disease class"

        explanations.append({
            "feature": row["feature"],
            "description": row["description"],
            "patient_value": float(row["value"]),
            "shap_contribution": float(row["shap_value"]),
            "direction": direction
        })

    # Final API result
    result = {
        "risk_score": round(risk_score, 2),
        "risk_category": risk_category,
        "predicted_class": predicted_class,
        "raw_model_class": int(prediction[0]),
        "explanations": explanations
    }

    return result


# ---------------------------------------------------------
# TESTING THE MODEL DIRECTLY
# ---------------------------------------------------------

if __name__ == "__main__":

    patient = {
        "age": 55,
        "sex": 1,
        "cp": 2,
        "trestbps": 140,
        "chol": 250,
        "fbs": 0,
        "restecg": 1,
        "thalach": 150,
        "exang": 0,
        "oldpeak": 1.5,
        "slope": 2,
        "ca": 0,
        "thal": 2
    }

    print("\nLoading CardioTwin model...")

    result = predict_patient(patient)

    print("Model loaded successfully!")

    print("\n")
    print("=" * 60)
    print("                    CARDIOTWIN")
    print("           CARDIOVASCULAR RISK ENGINE")
    print("=" * 60)

    print("\nPatient information loaded.")

    print("\nModel-estimated score:")
    print(f"{result['risk_score']:.2f}%")

    print("\nPrototype risk category:")
    print(result["risk_category"])

    print("\nPredicted class:")
    print(result["predicted_class"])

    print("\nRaw model class:")
    print(result["raw_model_class"])

    print("\n")
    print("-" * 60)
    print("PATIENT-SPECIFIC EXPLANATION")
    print("-" * 60)

    for index, item in enumerate(
        result["explanations"],
        start=1
    ):

        print(f"\n{index}. {item['description']}")

        print(
            f"   Feature: "
            f"{item['feature']}"
        )

        print(
            f"   Patient value: "
            f"{item['patient_value']}"
        )

        print(
            f"   SHAP contribution: "
            f"{item['shap_contribution']:.4f}"
        )

        print(
            f"   Direction: "
            f"{item['direction']}"
        )

    print("\n")
    print("-" * 60)
    print("IMPORTANT")
    print("-" * 60)

    print(
        "\nThis score is a model-estimated output "
        "from a prototype trained on the UCI "
        "Cleveland heart-disease dataset."
    )

    print(
        "\nIt is NOT a medical diagnosis and should "
        "not be interpreted as a clinically validated "
        "probability for an individual patient."
    )

    print(
        "\nSHAP values describe model behavior and "
        "do not establish medical causation."
    )

    print(
        "\nMedical decisions should be made with "
        "qualified healthcare professionals."
    )

    print("\n")
    print("=" * 60)
    print("CardioTwin prediction complete! 🫀")
    print("=" * 60)