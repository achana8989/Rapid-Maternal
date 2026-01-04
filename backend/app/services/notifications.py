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