from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EmergencyCreate(BaseModel):
    facility_id: Optional[int] = None
    emergency_type: str
    note: Optional[str] = None


class EmergencyOut(EmergencyCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
