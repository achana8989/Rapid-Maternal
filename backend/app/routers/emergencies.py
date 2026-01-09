from fastapi import APIRouter, Depends
from app.dependencies import require_role
from app.schemas.emergency import EmergencyCreate

router = APIRouter(
    prefix="/emergency",
    tags=["Emergency"]
)

@router.post("/")
def create_emergency(
    data: EmergencyCreate,
    user=Depends(require_role(["midwife", "nurse"]))
):
    return {
        "status": "Emergency created",
        "created_by_role": user["role"]
    }
