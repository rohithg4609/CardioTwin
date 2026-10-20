# CardioTwin — AI-Powered Cardiovascular Digital Twin

## 1. Project Overview

CardioTwin is a software prototype that combines machine learning-based cardiovascular risk assessment with a digital twin concept. It brings patient profiles, health-state measurements, historical health records, saved ML assessments, and digital twin snapshots into one application.

The project demonstrates how machine learning and organized health data can be integrated to explore cardiovascular risk and track recorded health information over time.

**Intended use:** Educational, research, and hackathon demonstration only. CardioTwin is not a clinically validated medical diagnostic system.

## 2. Problem Statement

Health measurements, patient information, and risk predictions can be difficult to interpret when they are stored separately. CardioTwin explores a unified platform that combines these elements and makes them accessible through a web interface.

## 3. Proposed Solution

CardioTwin provides:

- **ML cardiovascular assessment:** A trained Random Forest model generates a prediction from submitted clinical inputs.
- **Patient profile:** Stores basic patient information.
- **Health-state management:** Organizes available measurements such as heart rate, blood pressure, oxygen saturation, glucose, and cholesterol.
- **Digital twin snapshot:** Combines the current profile, health state, risk-tracking output, and latest saved ML assessment.
- **Health-record history:** Displays saved records and assessments.
- **Prediction explanations:** Provides available model explanation information.
- **Web interface:** A React and TypeScript frontend connected to a FastAPI backend.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI, Uvicorn |
| Machine learning | scikit-learn, Random Forest |
| Model persistence | Joblib / serialized model |
| Explainability | SHAP |
| Data processing | NumPy, pandas |
| Testing | pytest |
| Frontend styling and animation | CSS, GSAP, Lucide React |
| Data storage | Local JSON files and project data files |

## 5. Machine Learning Model

The prototype uses a trained Random Forest model for cardiovascular risk prediction.

Reported development evaluation results:

- **Accuracy:** 90.16%
- **ROC-AUC:** 0.9643
- **Dataset:** UCI Cleveland heart disease dataset
- **Dataset size:** 303 records
- **Model artifact:** `models/cardio_model.pkl`

These figures describe experimental model evaluation, not guaranteed performance on new patients. They do not establish clinical validity, and they should not be interpreted as a patient's confirmed probability of developing cardiovascular disease.

The model, preprocessing, and evaluation workflow should be reviewed before using the results outside a demonstration setting.

## 6. System Architecture

CardioTwin uses a frontend-backend architecture.

1. The React frontend provides the patient-facing interface.
2. The FastAPI backend exposes API endpoints and coordinates application logic.
3. The prediction module loads the trained model and generates ML assessments.
4. Patient and health-state modules manage the available profile and measurement data.
5. Digital twin modules provide snapshots, risk-tracking information, and health-state history.
6. The history functionality displays saved records and ML assessments.

The rule-based digital twin risk score and the ML assessment are separate outputs. They should not be treated as interchangeable or independently clinically validated.

## 7. API Documentation

After starting the backend, open:

`http://127.0.0.1:8000/docs`

The interactive documentation lists the API endpoints and their supported request and response schemas. Available functionality includes health checks, patient information, health-state operations, health-record history, digital twin snapshots, and ML assessments.

Use the live API documentation as the source of truth for exact endpoint names and supported methods.

## 8. Installation and Setup

### Prerequisites

- Git
- Python with a version compatible with the pinned dependencies
- Node.js and npm
- The project repository, including the trained model artifact

### Step 1: Clone the repository

```powershell
git clone https://github.com/rohithg4609/CardioTwin.git
cd CardioTwin
```

### Step 2: Create and activate a Python virtual environment

On Windows PowerShell:

```powershell
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, use the virtual environment's Python executable directly in the commands below.

### Step 3: Install Python dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 4: Install frontend dependencies

Open a second terminal in the project root, then run:

```powershell
cd frontend
npm ci
```

### Step 5: Start the backend

From the project root:

```powershell
.\venv\Scripts\python.exe -m uvicorn src.api:app --reload
```

The backend API is available at `http://127.0.0.1:8000`.

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### Step 6: Start the frontend

In the second terminal:

```powershell
cd frontend
npm run dev
```

Open the local URL displayed by Vite, normally `http://127.0.0.1:5173`.

Keep both terminals running while using the application.

## 9. Testing

Run the backend tests from the project root:

```powershell
.\venv\Scripts\python.exe -m pytest tests -v
```

Build the frontend:

```powershell
cd frontend
npm run build
```

The latest recorded verification during development was **157 passing backend tests** and a successful frontend production build. Re-run these commands against the final submitted commit to verify the current state.

## 10. Current Scope and Limitations

CardioTwin is a prototype intended to demonstrate the integration of ML assessment, patient information, health-state tracking, and a web interface.

Important limitations:

- The model's reported performance comes from experimental dataset evaluation and does not establish real-world clinical performance.
- The rule-based digital twin risk score is a prototype, not a clinically validated scoring system.
- A saved ML assessment may use inputs that differ from the patient's current profile or health measurements.
- Results depend on the quality, completeness, and correctness of the available data.
- Local data storage is intended for development and demonstration, not production healthcare use.
- Privacy, authentication, authorization, secure deployment, clinical validation, and broader external evaluation require further work before real-world deployment.

Do not use CardioTwin to diagnose a condition or make treatment decisions.

## 11. Team

- **Rohith G** — Rajalakshmi Institute of Technology — Project integration and overall development
- **Bryan Evan** — Rajalakshmi Institute of Technology — Medical-care modules
- **Deepak S** — Saveetha University — Digital twin and health history
- **James** — SA Engineering College — Frontend development

## 12. Intended Use and Disclaimer

CardioTwin is intended for educational, research, and hackathon demonstration purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Its predictions and prototype risk scores must not be used to make healthcare decisions.

## 13. License

The project license is to be confirmed by the team. No open-source license should be assumed until the team agrees to one and adds the corresponding `LICENSE` file.