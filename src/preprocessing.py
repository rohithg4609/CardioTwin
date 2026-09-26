import pandas as pd


# ============================================================
# CARDIOTWIN FEATURE DEFINITIONS
# ============================================================

FEATURE_COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal"
]


# ============================================================
# LOAD UCI HEART DISEASE DATASET
# ============================================================

def load_dataset(file_path):
    """
    Load the UCI Cleveland heart disease dataset.
    """

    columns = FEATURE_COLUMNS + ["target"]

    df = pd.read_csv(
        file_path,
        names=columns,
        na_values="?"
    )

    return df


# ============================================================
# PREPARE TRAINING DATA
# ============================================================

def prepare_data(df):
    """
    Separate features and target.

    Original UCI target:
        0 = no disease
        1,2,3,4 = disease

    CardioTwin target:
        0 = no disease
        1 = disease
    """

    df = df.copy()

    # Convert target into binary classification
    df["target"] = (df["target"] > 0).astype(int)

    X = df[FEATURE_COLUMNS]
    y = df["target"]

    return X, y


# ============================================================
# PREPARE PATIENT DATA
# ============================================================

def prepare_patient(patient):
    """
    Convert a patient's information into the exact
    feature format expected by the trained model.
    """

    # Convert dictionary to DataFrame
    patient_df = pd.DataFrame([patient])

    # Check that every required feature exists
    missing_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature not in patient_df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing patient features: {missing_features}"
        )

    # Keep ONLY the features used by the model
    patient_df = patient_df[FEATURE_COLUMNS]

    return patient_df


# ============================================================
# VALIDATE PATIENT DATA
# ============================================================

def validate_patient(patient):
    """
    Basic validation for patient input.

    This is NOT medical validation.
    It only checks whether the input is reasonable
    for the ML pipeline.
    """

    required_features = set(FEATURE_COLUMNS)

    provided_features = set(patient.keys())

    missing = required_features - provided_features

    if missing:
        raise ValueError(
            f"Missing required features: {sorted(missing)}"
        )

    return True