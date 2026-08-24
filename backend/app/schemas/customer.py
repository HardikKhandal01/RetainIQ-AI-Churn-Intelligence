from pydantic import BaseModel
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
