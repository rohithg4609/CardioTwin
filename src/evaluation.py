import os
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
    RocCurveDisplay
)

from preprocessing import load_dataset, prepare_data


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

DATA_PATH = "data/raw/heart_disease/processed.cleveland.data"

MODEL_PATH = "models/cardio_model.pkl"

RANDOM_STATE = 42


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print("\nLoading CardioTwin dataset...")

df = load_dataset(DATA_PATH)

print("Dataset loaded successfully!")

X, y = prepare_data(df)


# --------------------------------------------------
# SAME TRAIN / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=RANDOM_STATE,

    stratify=y
)


# --------------------------------------------------
# LOAD TRAINED MODEL
# --------------------------------------------------

print("\nLoading trained CardioTwin model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully!")


# --------------------------------------------------
# PREDICTIONS
# --------------------------------------------------

print("\nGenerating predictions...")

y_pred = model.predict(X_test)

y_prob = model.predict_proba(X_test)[:, 1]


# --------------------------------------------------
# CALCULATE METRICS
# --------------------------------------------------

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


# --------------------------------------------------
# PRINT RESULTS
# --------------------------------------------------

print("\n")

print("=" * 60)

print("             CARDIOTWIN MODEL EVALUATION")

print("=" * 60)


print("\nDataset:")
print("UCI Cleveland Heart Disease Dataset")

print("\nTest samples:")
print(len(y_test))


print("\n")

print("-" * 60)

print("PERFORMANCE METRICS")

print("-" * 60)


print(
    f"\nAccuracy : {accuracy:.4f} "
    f"({accuracy * 100:.2f}%)"
)

print(
    f"Precision: {precision:.4f} "
    f"({precision * 100:.2f}%)"
)

print(
    f"Recall   : {recall:.4f} "
    f"({recall * 100:.2f}%)"
)

print(
    f"F1 Score : {f1:.4f}"
)

print(
    f"ROC-AUC  : {roc_auc:.4f}"
)


# --------------------------------------------------
# CONFUSION MATRIX
# --------------------------------------------------

print("\n")

print("-" * 60)

print("CONFUSION MATRIX")

print("-" * 60)

print("\n")

print(cm)


# --------------------------------------------------
# CLASSIFICATION REPORT
# --------------------------------------------------

print("\n")

print("-" * 60)

print("CLASSIFICATION REPORT")

print("-" * 60)

print("\n")

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


# --------------------------------------------------
# CREATE OUTPUT FOLDER
# --------------------------------------------------

os.makedirs(
    "data/processed/evaluation",
    exist_ok=True
)


# --------------------------------------------------
# CONFUSION MATRIX PLOT
# --------------------------------------------------

print("Generating confusion matrix plot...")

fig, ax = plt.subplots(
    figsize=(6, 5)
)

ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=[
        "No Disease",
        "Disease"
    ]
).plot(
    ax=ax
)

ax.set_title(
    "CardioTwin Confusion Matrix"
)

plt.tight_layout()

confusion_path = (
    "data/processed/evaluation/"
    "confusion_matrix.png"
)

plt.savefig(
    confusion_path,
    dpi=300
)

plt.close()


# --------------------------------------------------
# ROC CURVE
# --------------------------------------------------

print("Generating ROC curve...")

fig, ax = plt.subplots(
    figsize=(6, 5)
)

RocCurveDisplay.from_predictions(
    y_test,
    y_prob,
    ax=ax
)

ax.set_title(
    f"CardioTwin ROC Curve "
    f"(AUC = {roc_auc:.3f})"
)

plt.tight_layout()

roc_path = (
    "data/processed/evaluation/"
    "roc_curve.png"
)

plt.savefig(
    roc_path,
    dpi=300
)

plt.close()


# --------------------------------------------------
# SAVE METRICS
# --------------------------------------------------

metrics_path = (
    "data/processed/evaluation/"
    "metrics.txt"
)

with open(
    metrics_path,
    "w"
) as file:

    file.write(
        "CARDIOTWIN MODEL EVALUATION\n"
    )

    file.write(
        "===========================\n\n"
    )

    file.write(
        f"Accuracy : {accuracy:.4f}\n"
    )

    file.write(
        f"Precision: {precision:.4f}\n"
    )

    file.write(
        f"Recall   : {recall:.4f}\n"
    )

    file.write(
        f"F1 Score : {f1:.4f}\n"
    )

    file.write(
        f"ROC-AUC  : {roc_auc:.4f}\n"
    )

    file.write(
        "\nConfusion Matrix:\n"
    )

    file.write(
        str(cm)
    )


# --------------------------------------------------
# FINAL MESSAGE
# --------------------------------------------------

print("\n")

print("=" * 60)

print("EVALUATION COMPLETE")

print("=" * 60)


print("\nGenerated files:")

print(
    "\n1. "
    "data/processed/evaluation/"
    "confusion_matrix.png"
)

print(
    "\n2. "
    "data/processed/evaluation/"
    "roc_curve.png"
)

print(
    "\n3. "
    "data/processed/evaluation/"
    "metrics.txt"
)


print("\n")

print("CardioTwin evaluation complete! 🫀🔥")