import os

print("Setting up FastAPI Backend architecture...")

# 1. Schema File (Pydantic Models)
schema_code = """from pydantic import BaseModel
from typing import Optional

class CustomerData(BaseModel):
    customer_id: Optional[str] = "CUS-TEST"
    tenure: int
    monthly_charges: float
    total_charges: float
    contract: str
    usage_frequency: str
    support_tickets: int
    engagement_score: int
    last_activity_days: int
"""

# 2. ML Service File (Joblib loading & Inference)
ml_service_code = """import joblib
import pandas as pd
import os

class MLService:
    def __init__(self):
        # We need to go up one directory since this runs from backend folder
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Load Churn Models
        self.preprocessor = joblib.load(os.path.join(base_path, "ml/artifacts/preprocessors/preprocessor.joblib"))
        self.churn_model = joblib.load(os.path.join(base_path, "ml/artifacts/models/best_model.joblib"))
        
        # Load Segmentation Models
        self.seg_pipeline = joblib.load(os.path.join(base_path, "ml/artifacts/models/segmentation_pipeline.joblib"))
        self.kmeans_model = joblib.load(os.path.join(base_path, "ml/artifacts/models/kmeans_model.joblib"))
        
        self.cluster_mapping = {
            0: "High Value / Loyal",
            1: "Low Value / Dormant",
            2: "Mid Value / Moderate",
            3: "New / At-Risk"
        }

    def predict(self, customer_data: dict):
        df = pd.DataFrame([customer_data])
        
        # 1. Churn Prediction
        X_processed = self.preprocessor.transform(df)
        churn_prob = self.churn_model.predict_proba(X_processed)[0][1]
        
        # 2. Segmentation
        seg_features = ['tenure', 'monthly_charges', 'total_charges', 'engagement_score']
        X_seg = df[seg_features]
        X_seg_scaled = self.seg_pipeline.transform(X_seg)
        cluster_id = self.kmeans_model.predict(X_seg_scaled)[0]
        segment_name = self.cluster_mapping[cluster_id]
        
        # Determine Risk Level
        if churn_prob < 0.25: risk = "Low"
        elif churn_prob < 0.50: risk = "Medium"
        elif churn_prob < 0.75: risk = "High"
        else: risk = "Critical"
        
        return {
            "churn_probability": round(float(churn_prob), 4),
            "risk_level": risk,
            "segment": segment_name
        }
        
ml_service = MLService()
"""

# 3. Main FastAPI App File
main_code = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.customer import CustomerData
from app.services.ml_service import ml_service

app = FastAPI(title="RetainIQ API", version="1.0")

# Allow Frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to RetainIQ API. Server is running!"}

@app.post("/api/predict")
def predict_customer_churn(customer: CustomerData):
    result = ml_service.predict(customer.model_dump())
    return {
        "customer_id": customer.customer_id,
        "prediction": result
    }
"""

# Ensure directories exist
os.makedirs("backend/app/schemas", exist_ok=True)
os.makedirs("backend/app/services", exist_ok=True)

# Write files
with open("backend/app/schemas/customer.py", "w") as f:
    f.write(schema_code)
with open("backend/app/services/ml_service.py", "w") as f:
    f.write(ml_service_code)
with open("backend/app/main.py", "w") as f:
    f.write(main_code)

# Add __init__.py files to make them proper Python packages
open("backend/app/__init__.py", "a").close()
open("backend/app/schemas/__init__.py", "a").close()
open("backend/app/services/__init__.py", "a").close()

print("✅ FastAPI Backend structure created successfully!")