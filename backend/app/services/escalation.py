from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import MaternalEmergency

ESCALATION_MINUTES = 15  # configurable later

def escalate_unacknowledged_emergencies(db: Session):
    threshold_time = datetime.utcnow() - timedelta(minutes=ESCALATION_MINUTES)

    emergencies = db.query(MaternalEmergency).filter(
        MaternalEmergency.status == "active",
        MaternalEmergency.created_at <= threshold_time,
        MaternalEmergency.escalation_level == 0
    ).all()

    for emergency in emergencies:
        emergency.escalation_level = 1
        emergency.escalated_at = datetime.utcnow()

    db.commit()
    return len(emergencies)