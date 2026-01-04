from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import MaternalEmergency
from app.db.models import NotificationLog
from sqlalchemy.orm import Session

def send_sms(db: Session, emergency_id: int, escalation_level: int):
    # MOCK SMS — no real provider yet
    recipient = "Subdistrict Emergency Contact"

    log = NotificationLog(
        emergency_id=emergency_id,
        escalation_level=escalation_level,
        channel="SMS",
        recipient=recipient,
        status="sent"
    )

    db.add(log)
    db.commit()

    print(
        f"[SMS MOCK] Emergency {emergency_id} escalated to level {escalation_level}"
    )
ESCALATION_MINUTES = 15  # configurable later

def escalate_unacknowledged_emergencies(db: Session):
    threshold_time = datetime.utcnow() - timedelta(minutes=ESCALATION_MINUTES)

    emergencies = db.query(MaternalEmergency).filter(
        MaternalEmergency.status == "active",
        MaternalEmergency.created_at <= threshold_time,
        MaternalEmergency.escalation_level == 0
    ).all()

    for emergency in emergencies:send_sms(db, emergency.id, emergency.escalation_level)
    emergency.escalation_level = 1
    emergency.escalated_at = datetime.utcnow()

    db.commit()
    return len(emergencies)