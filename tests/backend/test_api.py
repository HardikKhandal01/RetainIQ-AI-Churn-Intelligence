import os
import sys
from fastapi.testclient import TestClient

# Path fix taaki test script backend folder ko access kar sake
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.main import app

client = TestClient(app)

print("Starting RetainIQ Automated Test Suite...")

def test_read_root():
    """Test if the API is awake and responding."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to RetainIQ API" in response.json()["message"]

def test_predict_churn_high_risk():
    """Test if ML model correctly identifies a high-risk customer format."""
    payload = {
        "customer_id": "TEST-9999",
        "tenure": 2,
        "monthly_charges": 95.0,
        "total_charges": 190.0,
        "contract": "Month-to-month",
        "usage_frequency": "Low",
        "support_tickets": 8,
        "engagement_score": 10,
        "last_activity_days": 45
    }
    
    response = client.post("/api/predict", json=payload)
    
    # 1. API Response Code Check
    assert response.status_code == 200
    
    data = response.json()
    
    # 2. Output Schema Check
    assert "prediction" in data
    assert "churn_probability" in data["prediction"]
    assert "risk_level" in data["prediction"]
    assert "segment" in data["prediction"]
    
    # 3. Data Integrity Check
    assert data["customer_id"] == "TEST-9999"
    assert data["status"] == "✅ Saved to DB & Automations Checked"

def test_predict_churn_low_risk():
    """Test if ML model correctly processes a low-risk customer."""
    payload = {
        "customer_id": "TEST-8888",
        "tenure": 60,
        "monthly_charges": 30.0,
        "total_charges": 1800.0,
        "contract": "Two year",
        "usage_frequency": "High",
        "support_tickets": 0,
        "engagement_score": 95,
        "last_activity_days": 2
    }
    
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["prediction"]["risk_level"] in ["Low", "Medium"]