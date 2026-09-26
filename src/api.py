from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.predict import predict_patient


# --------------------------------------------------
# CREATE FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="CardioTwin ML API",
    description="Cardiovascular risk prediction engine",
    version="1.0.0"
)


# --------------------------------------------------
# PATIENT DATA MODEL
# --------------------------------------------------

class Patient(BaseModel):

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


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "CardioTwin ML API is running",
        "status": "online"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# --------------------------------------------------
# PREDICTION ENDPOINT
# --------------------------------------------------

@app.post("/predict")
def predict(patient: Patient):

    try:

        # Convert Pydantic model
        # into normal Python dictionary
        patient_data = patient.model_dump()

        # Run ML prediction
        result = predict_patient(
            patient_data
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )