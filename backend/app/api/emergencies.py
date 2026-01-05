from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import MaternalEmergency
from app.schemas.emergency import EmergencyCreate
from app.db.models import NotificationLog

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

from datetime import datetime
from fastapi import HTTPException
from app.schemas.acknowledge import AcknowledgeRequest
from app.services.escalation import escalate_unacknowledged_emergencies

@router.post("/{emergency_id}/acknowledge")
def acknowledge_emergency(
    emergency_id: int,
    payload: AcknowledgeRequest,
    db: Session = Depends(get_db)
):
    emergency = db.query(MaternalEmergency).filter(
        MaternalEmergency.id == emergency_id
    ).first()

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
        "acknowledged_by": emergency.acknowledged_by
    }
    
@router.get("/")
def list_emergencies(db: Session = Depends(get_db)):
    emergencies = db.query(MaternalEmergency).order_by(
        MaternalEmergency.created_at.desc()
    ).all()

    return [
        {
            "id": e.id,
            "facility_id": e.facility_id,
            "emergency_type": e.emergency_type,
            "status": e.status,
            "created_at": e.created_at,
            "acknowledged_at": e.acknowledged_at,
            "acknowledged_by": e.acknowledged_by
        }
        for e in emergencies
    ]



@router.post("/escalate/run")
def run_escalation(db: Session = Depends(get_db)):
    count = escalate_unacknowledged_emergencies(db)
    return {"escalated": count}

@router.get("/")
def list_emergencies(db: Session = Depends(get_db)):
    emergencies = db.query(MaternalEmergency).order_by(
        MaternalEmergency.created_at.desc()
    ).all()

    return [
        {
            "id": e.id,
            "facility_id": e.facility_id,
            "emergency_type": e.emergency_type,
            "status": e.status,
            "escalation_level": e.escalation_level,
            "is_escalated": e.escalation_level > 0,
            "created_at": e.created_at,
            "acknowledged_at": e.acknowledged_at,
            "acknowledged_by": e.acknowledged_by,
            "escalated_at": e.escalated_at
        }
        for e in emergencies
    ]
    
    @router.get("/escalated")
    def escalated_emergencies(db: Session = Depends(get_db)):
        emergencies = db.query(MaternalEmergency).filter(
        MaternalEmergency.escalation_level > 0
    ).order_by(MaternalEmergency.created_at.desc()).all()

    return emergencies

@router.get("/active")
def active_emergencies(db: Session = Depends(get_db)):
    emergencies = db.query(MaternalEmergency).filter(
        MaternalEmergency.status == "active"
    ).order_by(MaternalEmergency.created_at.desc()).all()

    return emergencies

@router.get("/summary")
def emergency_summary(db: Session = Depends(get_db)):
    total = db.query(MaternalEmergency).count()
    active = db.query(MaternalEmergency).filter(
        MaternalEmergency.status == "active"
    ).count()
    escalated = db.query(MaternalEmergency).filter(
        MaternalEmergency.escalation_level > 0
    ).count()

    return {
        "total_emergencies": total,
        "total": total,
        "active": active,
        "escalated": escalated
    }
    from app.db.models import NotificationLog

@router.get("/notifications/logs")
def notification_logs(db: Session = Depends(get_db)):
    logs = db.query(NotificationLog).order_by(
        NotificationLog.sent_at.desc()
    ).all()
    return [
        {
            "id": l.id,
            "emergency_id": l.emergency_id,
            "escalation_level": l.escalation_level,
            "channel": l.channel,
            "recipient": l.recipient,
            "sent_at": l.sent_at,
            "status": l.status
        }
        for l in logs
    ]


@router.get("/{emergency_id}")
def get_emergency(
    emergency_id: int,
    db: Session = Depends(get_db)
):
    emergency = db.query(MaternalEmergency).filter(
        MaternalEmergency.id == emergency_id
    ).first()

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
        "resolved_at": emergency.resolved_at
    }