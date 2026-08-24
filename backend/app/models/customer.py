from sqlalchemy import Column, Integer, String, Float, DateTime
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
