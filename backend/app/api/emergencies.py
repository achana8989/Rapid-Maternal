from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import MaternalEmergency
from app.schemas.emergency import EmergencyCreate

router = APIRouter(
    prefix="/emergencies",
    tags=["Emergencies"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", status_code=201)
def trigger_emergency(
    payload: EmergencyCreate,
    db: Session = Depends(get_db)
):
    emergency = MaternalEmergency(
        facility_id=payload.facility_id,
        emergency_type=payload.emergency_type,
        note=payload.note
    )
    db.add(emergency)
    db.commit()
    db.refresh(emergency)

    return {
        "id": emergency.id,
        "status": emergency.status,
        "created_at": emergency.created_at
    }
