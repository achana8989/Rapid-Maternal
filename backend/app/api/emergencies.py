from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import MaternalEmergency, NotificationLog
from app.schemas.emergency import EmergencyCreate
from app.schemas.acknowledge import AcknowledgeRequest
from app.services.escalation import escalate_unacknowledged_emergencies

router = APIRouter(
    prefix="/emergencies",
    tags=["Emergencies"]
)


# -------------------------
# Database dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Create emergency
# -------------------------
@router.post("/", status_code=201)
def trigger_emergency(payload: EmergencyCreate, db: Session = Depends(get_db)):
    emergency = MaternalEmergency(
        facility_id=payload.facility_id,
        emergency_type=payload.emergency_type,
        note=payload.note,
    )
    db.add(emergency)
    db.commit()
    db.refresh(emergency)

    return {
        "id": emergency.id,
        "status": emergency.status,
        "created_at": emergency.created_at,
    }


# -------------------------
# Acknowledge emergency
# -------------------------
@router.post("/{emergency_id}/acknowledge")
def acknowledge_emergency(
    emergency_id: int,
    payload: AcknowledgeRequest,
    db: Session = Depends(get_db),
):
    emergency = (
        db.query(MaternalEmergency)
        .filter(MaternalEmergency.id == emergency_id)
        .first()
    )

    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency not found")

    if emergency.status != "active":
        raise HTTPException(status_code=400, detail="Emergency already acknowledged")

    emergency.status = "acknowledged"
    emergency.acknowledged_at = datetime.utcnow()
    emergency.acknowledged_by = payload.acknowledged_by

    db.commit()

    return {
        "id": emergency.id,
        "status": emergency.status,
        "acknowledged_at": emergency.acknowledged_at,
        "acknowledged_by": emergency.acknowledged_by,
    }


# -------------------------
# List emergencies
# -------------------------
@router.get("/")
def list_emergencies(db: Session = Depends(get_db)):
    emergencies = (
        db.query(MaternalEmergency)
        .order_by(MaternalEmergency.created_at.desc())
        .all()
    )

    return [
        {
            "id": e.id,
            "facility_id": e.facility_id,
            "emergency_type": e.emergency_type,
            "status": e.status,
            "escalation_level": getattr(e, "escalation_level", 0),
            "created_at": e.created_at,
            "acknowledged_at": e.acknowledged_at,
            "acknowledged_by": e.acknowledged_by,
        }
        for e in emergencies
    ]


# -------------------------
# Run escalation job
# -------------------------
@router.post("/escalate/run")
def run_escalation(db: Session = Depends(get_db)):
    count = escalate_unacknowledged_emergencies(db)
    return {"escalated": count}


# -------------------------
# Active emergencies
# -------------------------
@router.get("/active")
def active_emergencies(db: Session = Depends(get_db)):
    return (
        db.query(MaternalEmergency)
        .filter(MaternalEmergency.status == "active")
        .order_by(MaternalEmergency.created_at.desc())
        .all()
    )


# -------------------------
# Escalated emergencies
# -------------------------
@router.get("/escalated")
def escalated_emergencies(db: Session = Depends(get_db)):
    return (
        db.query(MaternalEmergency)
        .filter(MaternalEmergency.escalation_level > 0)
        .order_by(MaternalEmergency.created_at.desc())
        .all()
    )


# -------------------------
# Summary
# -------------------------
@router.get("/summary")
def emergency_summary(db: Session = Depends(get_db)):
    total = db.query(MaternalEmergency).count()
    active = (
        db.query(MaternalEmergency)
        .filter(MaternalEmergency.status == "active")
        .count()
    )
    escalated = (
        db.query(MaternalEmergency)
        .filter(MaternalEmergency.escalation_level > 0)
        .count()
    )

    return {
        "total": total,
        "active": active,
        "escalated": escalated,
    }


# -------------------------
# Notification logs
# -------------------------
@router.get("/notifications/logs")
def notification_logs(db: Session = Depends(get_db)):
    logs = (
        db.query(NotificationLog)
        .order_by(NotificationLog.created_at.desc())
        .all()
    )

    return [
        {
            "id": l.id,
            "emergency_id": l.emergency_id,
            "channel": l.channel,
            "recipient": l.recipient,
            "status": l.status,
            "created_at": l.created_at,
        }
        for l in logs
    ]


# -------------------------
# Get single emergency
# -------------------------
@router.get("/{emergency_id}")
def get_emergency(emergency_id: int, db: Session = Depends(get_db)):
    emergency = (
        db.query(MaternalEmergency)
        .filter(MaternalEmergency.id == emergency_id)
        .first()
    )

    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency not found")

    return {
        "id": emergency.id,
        "facility_id": emergency.facility_id,
        "emergency_type": emergency.emergency_type,
        "status": emergency.status,
        "note": emergency.note,
        "created_at": emergency.created_at,
        "acknowledged_at": emergency.acknowledged_at,
        "acknowledged_by": emergency.acknowledged_by,
        "resolved_at": emergency.resolved_at,
    }
