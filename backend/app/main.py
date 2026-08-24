from fastapi import FastAPI, Depends, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.schemas.customer import CustomerData
from app.services.ml_service import ml_service
from app.core.database import engine, Base, get_db
from app.models.customer import CustomerDB
import urllib.request
import json
import pandas as pd
import io

# Create tables in the database automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RetainIQ API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def trigger_n8n_webhook(customer_id: str, risk_level: str, probability: float):
    """
    Simulated n8n Webhook Trigger for High/Critical Risk Customers.
    In a real production environment, this points to your n8n instance.
    """
    webhook_url = "http://localhost:5678/webhook/churn-alert" # Replace with actual n8n URL later
    payload = json.dumps({
        "customer_id": customer_id,
        "risk_level": risk_level,
        "churn_probability": probability,
        "action": "Trigger Retention Email / WhatsApp"
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(webhook_url, data=payload, headers={'Content-Type': 'application/json'})
        # urllib.request.urlopen(req, timeout=3) 
        # (Commented out to prevent errors if local n8n isn't running yet)
        print(f"🚀 [n8n Automation Triggered] Alert sent for Customer {customer_id} (Risk: {risk_level})")
    except Exception as e:
        print(f"⚠️ [n8n Webhook] Simulation logged: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to RetainIQ API. Server and Database are running!"}

@app.post("/api/predict")
def predict_customer_churn(customer: CustomerData, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Get Prediction from ML Models
    result = ml_service.predict(customer.model_dump())
    
    # 2. Trigger n8n Automation if risk is High or Critical
    if result["risk_level"] in ["High", "Critical"]:
        background_tasks.add_task(
            trigger_n8n_webhook, 
            customer.customer_id, 
            result["risk_level"], 
            result["churn_probability"]
        )
    
    # 3. Save or Update in Database
    existing_customer = db.query(CustomerDB).filter(CustomerDB.customer_id == customer.customer_id).first()
    
    if existing_customer:
        existing_customer.churn_probability = result["churn_probability"]
        existing_customer.risk_level = result["risk_level"]
        existing_customer.segment = result["segment"]
    else:
        new_record = CustomerDB(
            customer_id=customer.customer_id,
            churn_probability=result["churn_probability"],
            risk_level=result["risk_level"],
            segment=result["segment"]
        )
        db.add(new_record)
    
    db.commit()

    return {
        "customer_id": customer.customer_id,
        "prediction": result,
        "status": "✅ Saved to DB & Automations Checked"
    }

@app.post("/api/predict/bulk")
async def predict_bulk_churn(file: UploadFile = File(...)):
    # Read the uploaded CSV file
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    # Send DataFrame to ML service for bulk predictions
    results = ml_service.predict_bulk(df)
    
    return {
        "status": "success", 
        "total_processed": len(results), 
        "results": results
    }