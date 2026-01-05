from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import MaternalEmergency
from app.db.models import NotificationLog
from sqlalchemy.orm import Session
from app.services.notifications import send_sms

ESCALATION_MINUTES = 15  # configurable later


def escalate_unacknowledged_emergencies(db: Session):
    threshold_time = datetime.utcnow() - timedelta(minutes=ESCALATION_MINUTES)

    emergencies = db.query(MaternalEmergency).filter(
        MaternalEmergency.status == "active",
        MaternalEmergency.created_at <= threshold_time,
        MaternalEmergency.escalation_level == 0
    ).all()

    for emergency in emergencies:
        send_sms(db, emergency.id, emergency.escalation_level)
        emergency.escalation_level = 1
        emergency.escalated_at = datetime.utcnow()
        db.add(emergency)

    if emergencies:
        db.commit()

    return len(emergencies)