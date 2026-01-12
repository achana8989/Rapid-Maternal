from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import MaternalEmergency
from app.db.models import Facility
from app.schemas.emergency import EmergencyCreate
from app.schemas.acknowledge import AcknowledgeRequest
from app.services.escalation import escalate_unacknowledged_emergencies
from app.routers.ws import broadcast_update
from app.dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/emergencies",
    tags=["Emergencies"]
)


@router.post("/", status_code=201)
async def create_emergency(payload: EmergencyCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # If the requester is a midwife, enforce their facility_id
    facility_id = payload.facility_id
    role = (current_user.get("role") or "").upper()
    if role == "MIDWIFE":
        facility_id = current_user.get("facility_id")

    # For other roles, facility_id must be provided
    if not facility_id:
        raise HTTPException(status_code=400, detail="facility_id is required")

    emergency = MaternalEmergency(
        facility_id=facility_id,
        emergency_type=payload.emergency_type,
        note=payload.note,
    )
    db.add(emergency)
    db.commit()
    db.refresh(emergency)

    await broadcast_update()

    # include facility_name in response when available
    facility = db.query(Facility).filter(Facility.id == emergency.facility_id).first()
    return {
        "id": emergency.id,
        "status": emergency.status,
        "created_at": emergency.created_at,
        "facility_id": emergency.facility_id,
        "facility_name": facility.name if facility else None,
    }


@router.post("/{emergency_id}/acknowledge")
async def acknowledge_emergency(
    emergency_id: int,
    payload: AcknowledgeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    emergency = db.query(MaternalEmergency).filter_by(id=emergency_id).first()

    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency not found")

    if emergency.status != "active":
        raise HTTPException(status_code=400, detail="Emergency already acknowledged")

    role = (current_user.get("role") or "").upper()
    # If midwife, only allow acknowledging emergencies for their facility
    if role == "MIDWIFE":
        if emergency.facility_id != current_user.get("facility_id"):
            raise HTTPException(status_code=403, detail="Cannot acknowledge emergencies outside your facility")

    # SUBDISTRICT_ADMIN or ADMIN can acknowledge any emergency

    emergency.status = "acknowledged"
    emergency.acknowledged_at = datetime.utcnow()
    emergency.acknowledged_by = payload.acknowledged_by
    db.commit()

    await broadcast_update()

    return {"status": "acknowledged"}


@router.get("/")
def list_emergencies(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    q = db.query(MaternalEmergency)
    # Midwives only see emergencies for their facility
    if current_user.get("role") == "MIDWIFE":
        facility_id = current_user.get("facility_id")
        rows = q.filter(MaternalEmergency.facility_id == facility_id).order_by(
            MaternalEmergency.created_at.desc()
        ).all()
    else:
        rows = q.order_by(MaternalEmergency.created_at.desc()).all()

    # attach facility_name for each row
    results = []
    for e in rows:
        facility = db.query(Facility).filter(Facility.id == e.facility_id).first()
        results.append({
            "id": e.id,
            "facility_id": e.facility_id,
            "facility_name": facility.name if facility else None,
            "emergency_type": e.emergency_type,
            "status": e.status,
            "acknowledged_by": getattr(e, 'acknowledged_by', None),
            "escalation_level": getattr(e, 'escalation_level', None),
            "note": getattr(e, 'note', None),
            "created_at": e.created_at,
        })

    return results


@router.post("/escalate/run")
async def run_escalation(db: Session = Depends(get_db), current_user: dict = Depends(require_role(["SUBDISTRICT_ADMIN", "ADMIN"]))):
    """Only `SUBDISTRICT_ADMIN` or `ADMIN` can trigger escalation run."""
    count = escalate_unacknowledged_emergencies(db)

    if count > 0:
        await broadcast_update()

    return {"escalated": count}
