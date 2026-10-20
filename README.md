# CardioTwin — AI-Powered Cardiovascular Digital Twin

## 1. Project Overview

CardioTwin is a prototype that combines machine learning-based cardiovascular risk assessment with a digital twin concept. It brings patient information, health-state data, historical health records, model assessments, and digital twin snapshots into one system.

The project aims to demonstrate how AI and digital health data can support the understanding and tracking of cardiovascular risk. It is a research and educational prototype, not a medical diagnostic system.

## 2. Problem Statement

Cardiovascular risk assessment can involve multiple health indicators and records that are difficult to understand together. CardioTwin explores how machine learning predictions and organized health-state history can be integrated into a single software platform.

## 3. Proposed Solution

CardioTwin combines:

- A machine learning model for cardiovascular risk prediction.
- A FastAPI backend for API access and system integration.
- Patient and health-state data management.
- Health-record history and digital twin snapshots.
- Model assessments and prediction explanations.
- A React-based frontend for user interaction.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| Machine Learning | scikit-learn, Random Forest |
| Model Persistence | Joblib / serialized model |
| Explainability | SHAP |
| Data Processing | pandas |
| Testing | pytest |
| Data Storage | Local JSON files and project data files |

## 5. Machine Learning Model

The project uses a trained Random Forest model for cardiovascular risk prediction.

Reported evaluation results from the development experiments:

- Accuracy: 90.16%
- ROC-AUC: 0.9643
- Dataset: UCI Cleveland heart disease dataset, containing 303 records.

The trained model is stored at `models/cardio_model.pkl`.

These are experimental dataset results, not a guarantee of performance on real-world patients. The model must not be used to make clinical decisions.

## 6. System Architecture

The application follows a frontend-backend architecture.

1. The React frontend provides the user interface.
2. The FastAPI backend receives requests and manages application logic.
3. The prediction module loads the trained model and generates assessments.
4. The backend exposes patient, health-state, record-history, and digital-twin endpoints.
5. Digital twin modules maintain health-state history, risk tracking, and snapshots.

## 7. API Documentation

When the backend is running, interactive API documentation is available at:

`http://127.0.0.1:8000/docs`

The implemented API includes endpoints for:

- Health checks.
- Patient information.
- Health-state retrieval and updates.
- Digital twin snapshots.
- Health-record creation and retrieval.
- Digital twin checkpoints.
- Model assessments and predictions.

Refer to the live API documentation for the exact request schemas and supported methods.

## 8. Running the Project Locally

### Prerequisites

- Python and the project's virtual environment.
- Node.js and npm.
- The project repository and trained model file.

### Start the backend

From the project root:

```powershell
.\venv\Scripts\python.exe -m uvicorn src.api:app --reload
```

Backend API: `http://127.0.0.1:8000`

API documentation: `http://127.0.0.1:8000/docs`

### Start the frontend

Open a second terminal:

```powershell
cd "D:\MODELS for ML\CardioTwin\frontend"
npm install
npm run dev
```

Open the local URL printed by Vite in the terminal.

## 9. Testing

Run the backend test suites from the project root:

```powershell
.\venv\Scripts\python.exe -m pytest tests tests_medical_care -q
```

Build the frontend:

```powershell
cd "D:\MODELS for ML\CardioTwin\frontend"
npm run build
```

During development, the backend test suites passed with 211 tests and 8 subtests. The frontend production build also succeeded. Re-run both commands before submission to confirm the current state.

## 10. Current Scope and Limitations

CardioTwin is a prototype under development. The available backend includes patient, health-state, health-record, digital twin, and assessment functionality. The degree of frontend integration may vary by module.

The model's experimental performance does not establish clinical validity. Data quality, generalization, privacy, security, and clinical evaluation require further work before real-world deployment.

## 11. Team

- **Rohith G** — Rajalakshmi Institute of Technology — Project integration and overall development.
- **Bryan Evan** — Rajalakshmi Institute of Technology — Medical-care modules.
- **Deepak S** — Saveetha University — Digital twin and health history.
- **James** — SA Engineering College — Frontend development.

## 12. Intended Use and Disclaimer

CardioTwin is intended for demonstration, research, and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Do not use its predictions to make healthcare decisions.

## 13. License

License: To be confirmed by the project team.

Do not describe the project as MIT-licensed until the team agrees to that license and adds the corresponding `LICENSE` file.
