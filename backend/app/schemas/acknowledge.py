from pydantic import BaseModel, Field

class AcknowledgeRequest(BaseModel):
    acknowledged_by: str = Field(..., example="Subdistrict Focal Person")