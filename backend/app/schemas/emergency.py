from pydantic import BaseModel, Field
from typing import Optional

class EmergencyCreate(BaseModel):
    facility_id: str = Field(..., example="ZAWSE_CHPS")
    emergency_type: str = Field(..., example="Postpartum Hemorrhage")
    note: Optional[str] = Field(None, max_length=200)