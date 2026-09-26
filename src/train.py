import os
import joblib

from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    StratifiedKFold
)

from sklearn.impute import SimpleImputer

from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

from preprocessing import load_dataset, prepare_data


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/raw/heart_disease/processed.cleveland.data"

MODEL_PATH = "models/cardio_model.pkl"

RANDOM_STATE = 42


# ============================================================
# 1. LOAD DATASET
# ============================================================

print("\nLoading CardioTwin dataset...")

df = load_dataset(DATA_PATH)

print("Dataset loaded successfully!")
print("Total records:", len(df))


# ============================================================
# 2. PREPARE DATA
# ============================================================

X, y = prepare_data(df)

print("\nFeatures:", X.shape[1])
print("Target distribution:")
print(y.value_counts().sort_index())


# ============================================================
# 3. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# ============================================================
# 4. CREATE MACHINE LEARNING PIPELINE
# ============================================================

pipeline = Pipeline([
    
    (
        "imputer",
        SimpleImputer(strategy="median")
    ),

    (
        "model",
        RandomForestClassifier(
            random_state=RANDOM_STATE,
            n_jobs=-1
        )
    )
])


# ============================================================
# 5. HYPERPARAMETER SEARCH
# ============================================================

parameters = {

    "model__n_estimators": [
        100,
        200,
        300
    ],

    "model__max_depth": [
        None,
        5,
        10
    ],

    "model__min_samples_split": [
        2,
        5
    ],

    "model__min_samples_leaf": [
        1,
        2
    ],

    "model__max_features": [
        "sqrt",
        "log2"
    ]
}


# ============================================================
# 6. STRATIFIED CROSS VALIDATION
# ============================================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=RANDOM_STATE
)


# ============================================================
# 7. GRID SEARCH
# ============================================================

grid = GridSearchCV(
    estimator=pipeline,
    param_grid=parameters,
    cv=cv,

    # ROC-AUC is more informative than accuracy
    # for a probability/risk-oriented system.
    scoring="roc_auc",

    n_jobs=-1,
    verbose=1
)


# ============================================================
# 8. TRAIN MODEL
# ============================================================

print("\n")
print("=" * 60)
print("STARTING CARDIOTWIN MODEL TRAINING")
print("=" * 60)

print("\nHyperparameter tuning started...")
print("Using 5-fold stratified cross-validation.")

grid.fit(X_train, y_train)


# ============================================================
# 9. GET BEST MODEL
# ============================================================

best_model = grid.best_estimator_

print("\n")
print("=" * 60)
print("BEST MODEL")
print("=" * 60)

print("\nBest parameters:")

for key, value in grid.best_params_.items():
    print(f"{key}: {value}")

print("\nBest cross-validation ROC-AUC:")
print(f"{grid.best_score_:.4f}")


# ============================================================
# 10. TEST SET PREDICTION
# ============================================================

y_pred = best_model.predict(X_test)

y_prob = best_model.predict_proba(X_test)[:, 1]


# ============================================================
# 11. CALCULATE METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_prob
)

cm = confusion_matrix(
    y_test,
    y_pred
)


# ============================================================
# 12. DISPLAY FINAL RESULTS
# ============================================================

print("\n")
print("=" * 60)
print("CARDIOTWIN FINAL TEST RESULTS")
print("=" * 60)

print(f"\nAccuracy : {accuracy:.4f} ({accuracy * 100:.2f}%)")

print(f"Precision: {precision:.4f} ({precision * 100:.2f}%)")

print(f"Recall   : {recall:.4f} ({recall * 100:.2f}%)")

print(f"F1 Score : {f1:.4f}")

print(f"ROC-AUC  : {roc_auc:.4f}")


# ============================================================
# 13. CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")

print(cm)


# ============================================================
# 14. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "No Disease",
            "Disease"
        ],
        zero_division=0
    )
)


# ============================================================
# 15. SAVE MODEL
# ============================================================

os.makedirs(
    "models",
    exist_ok=True
)

joblib.dump(
    best_model,
    MODEL_PATH
)


# ============================================================
# 16. VERIFY MODEL FILE
# ============================================================

if os.path.exists(MODEL_PATH):

    print("\n")
    print("=" * 60)
    print("MODEL SAVED SUCCESSFULLY")
    print("=" * 60)

    print("\nModel file:")
    print(MODEL_PATH)

else:

    print("\nERROR: Model was not saved.")


# ============================================================
# 17. COMPLETION
# ============================================================

print("\n")
print("CardioTwin ML training complete! 🫀")