import os

print("Setting up Database architecture...")

# Ensure directories exist
os.makedirs("backend/app/core", exist_ok=True)
os.makedirs("backend/app/models", exist_ok=True)

# 1. Database Connection (SQLite for local storage in D Drive)
db_code = """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./retainiq.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

# 2. Database Models (Tables)
model_code = """from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base
import datetime

class CustomerDB(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    churn_probability = Column(Float)
    risk_level = Column(String)
    segment = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
"""

# 3. Update main.py to integrate Database & Save Predictions
main_code = """from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.schemas.customer import CustomerData
from app.services.ml_service import ml_service
from app.core.database import engine, Base, get_db
from app.models.customer import CustomerDB

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

@app.get("/")
def read_root():
    return {"message": "Welcome to RetainIQ API. Server and Database are running!"}

@app.post("/api/predict")
def predict_customer_churn(customer: CustomerData, db: Session = Depends(get_db)):
    # 1. Get Prediction from ML Models
    result = ml_service.predict(customer.model_dump())
    
    # 2. Save or Update in Database
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
        "status": "✅ Successfully saved to database!"
    }
"""

# Write files
with open("backend/app/core/database.py", "w", encoding="utf-8") as f: f.write(db_code)
with open("backend/app/models/customer.py", "w", encoding="utf-8") as f: f.write(model_code)
with open("backend/app/main.py", "w", encoding="utf-8") as f: f.write(main_code)

# Add __init__.py files
open("backend/app/core/__init__.py", "a").close()
open("backend/app/models/__init__.py", "a").close()

print("✅ Database architecture and models created successfully!")