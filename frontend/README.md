# CardioTwin Patient Portal — frontend starter

A responsive React + TypeScript interface for the existing CardioTwin FastAPI `GET /health` and `POST /predict` endpoints. It uses a calm navy/teal palette, accessible form labels, a three-step assessment, clear prototype disclaimers, and subtle GSAP transitions that respect reduced-motion preferences.

## Important scope and safety notes

- This frontend is a prototype, not a clinical product or a diagnostic tool.
- The model score is displayed as a score out of 100, not as a validated individual probability.
- Several fields are clinician-oriented values. The user interface asks people to use a clinical record and not guess.
- The `thal` selector only offers `3`, `6`, and `7`, which were observed in the project's 303-row training file. The current hard-coded example in `src/predict.py` uses `thal=2`; that example is outside the training data's observed values and should be corrected to a verified value before using it as a test case.
- The current frontend does not save assessment history. The repository's `digital_twin` and `medical_care` Python modules are not yet exposed through frontend API endpoints. The UI clearly labels those parts as not connected.
- This development proxy avoids browser CORS issues locally. Production deployment needs an explicit backend URL/reverse proxy, authentication, privacy/security review, server-side validation, and clinical-content review.

## Requirements

- Node.js 20.19+ or 22.12+ (required by the current Vite release)
- npm
- The existing CardioTwin Python environment and saved model file

Check Node/npm first:

```powershell
node -v
npm -v
```

## Install and run

Extract this folder as `D:\MODELS for ML\CardioTwin\frontend` so the project looks like:

```text
CardioTwin/
  src/
  models/
  frontend/
    package.json
    vite.config.ts
    src/
```

Terminal 1 — from `D:\MODELS for ML\CardioTwin`, start the current API:

```powershell
.\venv\Scripts\python.exe -m uvicorn src.api:app --reload --host 127.0.0.1 --port 8000
```

If that command says `No module named uvicorn`, install it inside the project venv with `.[venv\Scripts\python.exe -m pip install uvicorn` (without the unusual marker; use the command below instead):

```powershell
.\venv\Scripts\python.exe -m pip install uvicorn
```

Terminal 2 — install and start the frontend:

```powershell
cd "D:\MODELS for ML\CardioTwin\frontend"
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://127.0.0.1:5173`.

## Build verification

From the `frontend` folder:

```powershell
npm run build
```

## API contract used

- `GET /health` — checks whether the FastAPI app responds.
- `POST /predict` — submits the existing 13 feature keys: `age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, `thal`.

The current API has only basic missing-field validation. This UI performs client-side range/category checks, but a real deployment also needs matching server-side validation because client checks can be bypassed.
