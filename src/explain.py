import pandas as pd
import shap


FEATURE_DESCRIPTIONS = {
    "age": "Age",
    "sex": "Sex",
    "cp": "Chest-pain category",
    "trestbps": "Resting blood pressure",
    "chol": "Cholesterol",
    "fbs": "Fasting blood sugar",
    "restecg": "Resting ECG result",
    "thalach": "Maximum heart rate",
    "exang": "Exercise-induced angina",
    "oldpeak": "ST depression",
    "slope": "ST segment slope",
    "ca": "Number of major vessels",
    "thal": "Thalassemia-related feature"
}


def get_feature_importance(model):
    """
    Get global feature importance from the Random Forest.

    This shows which features the model generally relies on
    across the training data.

    It does NOT show causation.
    """

    random_forest = model.named_steps["model"]

    importance = random_forest.feature_importances_

    feature_names = list(FEATURE_DESCRIPTIONS.keys())

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importance
    })

    importance_df = importance_df.sort_values(
        by="importance",
        ascending=False
    )

    importance_df = importance_df.reset_index(drop=True)

    return importance_df


def get_top_features(model, number_of_features=5):

    importance_df = get_feature_importance(model)

    return importance_df.head(number_of_features)


def create_explanation(model, number_of_features=5):

    top_features = get_top_features(
        model,
        number_of_features
    )

    explanations = []

    for _, row in top_features.iterrows():

        feature = row["feature"]

        importance = row["importance"]

        description = FEATURE_DESCRIPTIONS.get(
            feature,
            feature
        )

        explanations.append({
            "feature": feature,
            "description": description,
            "importance": float(importance)
        })

    return explanations


def display_explanation(model, number_of_features=5):

    explanations = create_explanation(
        model,
        number_of_features
    )

    print("\n")
    print("-" * 60)
    print("GLOBAL MODEL EXPLANATION")
    print("-" * 60)

    print(
        "\nThe following features were among the most influential "
        "features used by the model:"
    )

    for index, item in enumerate(explanations, start=1):

        percentage = item["importance"] * 100

        print(f"\n{index}. {item['description']}")
        print(f"   Feature: {item['feature']}")
        print(
            f"   Relative importance: "
            f"{percentage:.2f}%"
        )

    print("\n")
    print(
        "Important: Feature importance describes model behavior, "
        "not medical causation."
    )

    return explanations


def get_patient_explanation(model, patient_df):

    """
    Generate patient-specific feature contributions using SHAP.

    Positive SHAP values push the prediction toward the
    disease class.

    Negative SHAP values push the prediction away from
    the disease class.

    SHAP values describe model behavior and do NOT establish
    medical causation.
    """

    # Get the Random Forest from the pipeline
    random_forest = model.named_steps["model"]

    # Apply the same preprocessing used during prediction
    imputer = model.named_steps["imputer"]

    patient_imputed = imputer.transform(patient_df)

    # Create SHAP explainer
    explainer = shap.TreeExplainer(random_forest)

    shap_values = explainer.shap_values(patient_imputed)

    # Handle SHAP output format
    if isinstance(shap_values, list):

        patient_shap = shap_values[1][0]

    else:

        patient_shap = shap_values[0]

        if len(patient_shap.shape) > 1:
            patient_shap = patient_shap[:, 1]

    feature_names = list(FEATURE_DESCRIPTIONS.keys())

    explanation_df = pd.DataFrame({
        "feature": feature_names,
        "value": patient_df.iloc[0][feature_names].values,
        "shap_value": patient_shap
    })

    explanation_df["description"] = explanation_df[
        "feature"
    ].map(FEATURE_DESCRIPTIONS)

    # Largest absolute contributions first
    explanation_df["absolute_shap"] = (
        explanation_df["shap_value"].abs()
    )

    explanation_df = explanation_df.sort_values(
        by="absolute_shap",
        ascending=False
    )

    explanation_df = explanation_df.reset_index(drop=True)

    return explanation_df


def display_patient_explanation(
    model,
    patient_df,
    number_of_features=5
):

    explanation_df = get_patient_explanation(
        model,
        patient_df
    )

    top_features = explanation_df.head(
        number_of_features
    )

    print("\n")
    print("-" * 60)
    print("PATIENT-SPECIFIC EXPLANATION")
    print("-" * 60)

    print(
        "\nThese features had the largest influence "
        "on this patient's model prediction:"
    )

    for index, (_, row) in enumerate(
        top_features.iterrows(),
        start=1
    ):

        shap_value = row["shap_value"]

        if shap_value > 0:
            direction = "toward disease class"
        else:
            direction = "away from disease class"

        print(f"\n{index}. {row['description']}")

        print(
            f"   Feature: {row['feature']}"
        )

        print(
            f"   Patient value: {row['value']}"
        )

        print(
            f"   SHAP contribution: "
            f"{shap_value:.4f}"
        )

        print(
            f"   Direction: {direction}"
        )

    print("\n")
    print(
        "Important: SHAP values describe how the model "
        "used the patient's features."
    )

    print(
        "They do not establish medical causation."
    )

    return explanation_df